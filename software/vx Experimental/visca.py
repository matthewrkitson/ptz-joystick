import logging
import queue
import select
import socket
import threading

class ViscaCamera():
    logger = logging.getLogger(__name__)

    def __init__(self, ip_address, port, camera_address):
        self.ip_address = ip_address
        self.port = port
        self.camera_send_address_byte = 0x80 | camera_address
        self.camera_receive_address_byte = (camera_address + 8) << 4
        self.timeout_seconds = 1
        self.finished = False
        self.socket = None

        self.zoom_pos = None
        self.pan_pos = None
        self.tilt_pos = None
        self.presets = [(0, 0, 0) for x in range(ViscaCamera.PRESET_MIN, ViscaCamera.PRESET_MAX+1)]

        self.pt_drive = (0x11, 0x11)
        self.pt_speed = (0x00, 0x00)

        self.command_queue = queue.Queue()

        self.position_monitor_thread = threading.Thread(target=self._monitor_position, daemon=True, group=None)
        self.position_monitor_thread.start()

    @staticmethod
    def _nibbles_to_int(*nibbles):
        value = 0
        for nibble in nibbles:
            if nibble & 0x80:
                nibble_text = "[" + ", ".join([f"0x{x:02x}" for x in nibbles]) + "]"
                raise ValueError(f"At least one nibble had high bits set in {nibble_text}")
            value = value << 4 | nibble
        
        # If the high bit is set, convert to a negative number
        if value & (1 << (len(nibbles) * 4 - 1)):
            value = -(1 << len(nibbles) * 4) + value

        return value

    @staticmethod
    def _int_to_nibbles(int):
        nibbles = [0, 0, 0, 0]
        for i in range(4):
            nibbles[3 - i] = int & 0x0F
            int = int >> 4
        
        return nibbles

    ENQ_PAN_TILT_POS       = [0x09, 0x06, 0x12]
    ENQ_ZOOM_POS           = [0x09, 0x04, 0x47]
    ENQ_FOCUS_POS          = [0x09, 0x04, 0x48]
    ENQ_PAN_TILT_MAX_SPEED = [0x09, 0x06, 0x11]

    CMD_PAN_TILT_DRIVE_REL = [0x01, 0x06, 0x02]
    CMD_ZOOM_DIRECT        = [0x01, 0x04, 0x47]
    CMD_PAN_TILT_DRIVE     = [0x01, 0x06, 0x01]

    ACK1                   = [0x41]
    ACK2                   = [0x42]
    COMPLETE1              = [0x51]
    COMPLETE2              = [0x52]
    SYNTAX_ERROR           = [0x60, 0x02]
    COMMAND_NOT_EXECUTABLE = [0x61, 0x41]

    ZOOM_PACKET_LENGTH = 5
    PT_PACKET_LENGTH = 9

    PRESET_MIN = 0
    PRESET_MAX = 255

    @classmethod
    def log_command(cls, message, show=True):
        if show: 
            ViscaCamera.logger.debug(f"--> {message}")

    @classmethod
    def log_response(cls, message, show=True):
        if show: 
            ViscaCamera.logger.debug(f"<--     {message}")

    @property
    def pan(self):
        return self.pan_pos
    
    @property
    def tilt(self):
        return self.tilt_pos

    @property
    def zoom(self):
        return self.zoom_pos

    @property
    def ptz(self):
        return (self.pan_pos, self.tilt_pos, self.zoom_pos)

    @classmethod
    def _invalid_preset(cls, n):
        return n < ViscaCamera.PRESET_MIN or n > ViscaCamera.PRESET_MAX

    def set_preset(self, n, p, t, z):
        if ViscaCamera._invalid_preset(n):
            ViscaCamera.logger.debug(f"Ignoring attempt to set out of range preset: {n}")
            return

        ViscaCamera.logger.debug(f"Seting preset {n} to ({p}, {t}, {z})")
        self.presets[n] = (p, t, z)

    def recall_preset(self, n):
        if ViscaCamera._invalid_preset(n):
            ViscaCamera.logger.debug(f"Ignoring attempt to recall out of range preset: {n}")
            return
        
        p1, t1, z1 = self.ptz
        p2, t2, z2 = self.presets[n]
        ViscaCamera.logger.debug(f"Recalling preset {n}: ({p2}, {t2}, {z2})")

        dp = p2 - p1
        dt = t2 - t1
        
        dpn = ViscaCamera._int_to_nibbles(dp)
        dtn = ViscaCamera._int_to_nibbles(dt)
        ps = 10
        ts = 10

        pt_drive_packet = [*ViscaCamera.CMD_PAN_TILT_DRIVE_REL, ps, ts, *dpn, *dtn]
        self.command_queue.put((pt_drive_packet, f"CMD_PAN_TILE_DRIVE_REL ({dp} @ {ps}, {dt} @ {ts})"))

        zz = ViscaCamera._int_to_nibbles(z2)
        z_direct_packet = [*ViscaCamera.CMD_ZOOM_DIRECT, *zz]
        self.command_queue.put((z_direct_packet, f"CMD_ZOOM_DIRECT ({z2})"))

    def ptz_abs(self, p, t, z, s):
        pass

    def _move_to_pan_pos(self, p, s):
        # Assuming this is running in a new thread
        # Start pan drive at speed s
        # Wait until we've arrived at the desired position
        # (possibly with some overshoot compensation)

        # Work out which direction we need to move in

        # CMD_PAN_TILT_DRIVE: 0x8x 0x01 0x06 0x01
        #                     pan_speed      tilt_speed
        #                     pan_direction  tilt_direction
        #                     0xFF 
        #
        #        Speed parameters
        #           pan  tilt    pan tilt
        # -------------------------------
        # up        0x03 0x01     11 01
        # down      0x03 0x02     11 10
        # left      0x01 0x03     01 11
        # right     0x02 0x03     10 11
        #
        # upleft    0x01 0x01     01 01
        # upright   0x02 0x01     10 01
        # downleft  0x01 0x02     01 10
        # downright 0x02 0x02     10 10
        #
        # stop      0x03 0x03     11 11
        #
        # Drive direction is encoded in the last two bits of the direction
        # parameters.
        #
        # bit        direction
        # ---        ---------
        # pan 0      right
        # pan 1      left
        # tilt 0     down
        # tilt 1     up
        #
        # Set to 0 to engage drive
        # Set to 1 to stop
        p0 = self.pan
        direction = 0 if p > p0 else 1

    def _drive_pan(self, speed):
        direction_mask = 0b01 if speed > 0 else 0b10 if speed < 0 else 0b00
        pan_direction = self._pan_direction & ~direction_mask

        command_packet = [*ViscaCamera.CMD_PAN_TILT_DRIVE, abs(speed), self._tilt_speed, pan_direction, self._tilt_direction]

        self._pan_direction = pan_direction
        self._pan_speed = abs(speed)

    def _monitor_position(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port))
        
        while not self.finished:
            try:
                self._send_command(ViscaCamera.ENQ_ZOOM_POS, "ENQ_ZOOM_POS", True)
                self._process_response()

                self._send_command(ViscaCamera.ENQ_PAN_TILT_POS, "ENQ_PAN_TILT_POS", True)
                self._process_response()

                while self.command_queue.qsize():
                    command, description = self.command_queue.get()
                    self._send_command(command, description)
                    self._process_response()
                        
            except:
                ViscaCamera.logger.exception("Error communicating with VISCA device.")
                # TODO Close socket and re-open? 

        self.socket.close()

    def _send_command(self, command, description, show=True):
        command_packet = [self.camera_send_address_byte, *command, 0xFF]
        bytes_sent = self.socket.send(bytes(command_packet))
        if bytes_sent != len(command_packet):
            raise IOError(f"Tried to send {len(command_packet)} bytes, but actually sent {bytes_sent}.")
        ViscaCamera.log_command(description, show)

    def _process_response(self):
        received_bytes = ViscaCamera._read_socket(self.socket)
        packets = ViscaCamera._packetise(received_bytes, self.camera_receive_address_byte);
        self._interpret_packets(packets)

    @classmethod
    def _read_socket(cls, the_socket):
        timeout_seconds = 0.2
        readables, writeables, exceptionals = select.select([the_socket], [], [the_socket], timeout_seconds)

        if exceptionals:
            raise IOError("An error occurred reading from the camera socket.")

        if not readables:
            ViscaCamera.logger.debug("Timeout occurred waiting for response from camera. ")
            return [];

        if len(readables) != 1 or readables[0] != the_socket:
            raise IOError("Unexpected socket or number of sockets returned by select.")
        
        received_bytes = readables[0].recv(4096)
        return received_bytes

    @classmethod
    def _packetise(cls, buffer, address_byte):
        packets = []
        packet = []
        for byte in buffer:
            if byte == 0xff:
                if not packet:
                    ViscaCamera.logger.debug("NULL PACKET")
                else:
                    address_byte = packet[0]
                    if address_byte != address_byte:
                        address = (address_byte >> 4) - 8
                        ViscaCamera.logger.debug(f"ADDRESSED TO 0x{address:02x} (not here)")
                    else:
                        packets.append(packet[1:])
                        packet = []
            else:
                packet.append(byte)

        return packets

    def _interpret_packets(self, packets):
        for packet in packets:
            if packet == []:
                ViscaCamera.log_response("[]")
            if packet == ViscaCamera.ACK1:
                ViscaCamera.log_response("ACK 1")
            elif packet == ViscaCamera.ACK2:
                ViscaCamera.log_response("ACK 2")
            elif packet == ViscaCamera.COMPLETE1:
                ViscaCamera.log_response("COMPLETE 1")
            elif packet == ViscaCamera.COMPLETE2:
                ViscaCamera.log_response("COMPLETE 2")
            elif packet == ViscaCamera.SYNTAX_ERROR:
                ViscaCamera.log_response("SYNTAX ERROR")
            elif packet == ViscaCamera.COMMAND_NOT_EXECUTABLE:
                ViscaCamera.log_response("COMMAND NOT EXECUTABLE")
            elif len(packet) == ViscaCamera.ZOOM_PACKET_LENGTH:
                self.zoom_pos = ViscaCamera._interpret_zoom_pos_response(packet)
            elif len(packet) == ViscaCamera.PT_PACKET_LENGTH:
                self.pan_pos, self.tilt_pos = ViscaCamera._interpret_pan_tilt_pos_response(packet)

    @classmethod
    def _interpret_zoom_pos_response(cls, bytes):
            _, z0, z1, z2, z3 = bytes
            zoom_pos = ViscaCamera._nibbles_to_int(z0, z1, z2, z3)
            ViscaCamera.log_response(f"ZOOM: {zoom_pos}", True)
            return zoom_pos

    @classmethod
    def _interpret_pan_tilt_pos_response(cls, bytes):
            _, p0, p1, p2, p3, t0, t1, t2, t3 = bytes
            pan_pos = ViscaCamera._nibbles_to_int(p0, p1, p2, p3)
            tilt_pos = ViscaCamera._nibbles_to_int(t0, t1, t2, t3)
            ViscaCamera.log_response(f"PAN TILT: {pan_pos}, {tilt_pos}", True)
            return pan_pos, tilt_pos
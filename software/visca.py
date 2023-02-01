import logging
import queue
import socket
import threading

class ViscaCamera():
    def __init__(self, ip_address, port, camera_address):
        self.ip_address = ip_address
        self.port = port
        self.camera_address_byte = 0x80 | camera_address
        self.timeout_seconds = 1
        self.finished = False
        self.socket = None

        self.zoom_pos = None
        self.pan_pos = None
        self.tilt_pos = None
        self.presets = [(0, 0, 0) for x in range(ViscaCamera.PRESET_MIN, ViscaCamera.PRESET_MAX+1)]

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

    def _invalid_preset(n):
        return n < ViscaCamera.PRESET_MIN or n > ViscaCamera.PRESET_MAX

    def set_preset(self, n, p, t, z):
        if self._invalid_preset(n):
            logging.debug(f"Ignoring attempt to set out of range preset: {n}")
            return

        logging.debug(f"Seting preset {n} to ({p}, {t}, {z})")
        self.presets[n] = (p, t, z)

    def recall_preset(self, n):
        if self._invalid_preset(n):
            logging.debug(f"Ignoring attempt to recall out of range preset: {n}")
            return
        
        p1, t1, z1 = self.ptz
        p2, t2, z2 = self.presets[n]

        dp = ViscaCamera._int_to_nibbles(p2 - p1)
        dt = ViscaCamera._int_to_nibbles(t2 - t1)
        
        ps = 1
        ts = 1

        pt_drive_packet = [*ViscaCamera.CMD_PAN_TILT_DRIVE_REL, ps, ts, *dp, *dt]
        self.command_queue.put(pt_drive_packet)

        zz = ViscaCamera._int_to_nibbles(z2)
        z_direct_packet = [*ViscaCamera.CMD_ZOOM_DIRECT, *zz]
        self.command_queue.put(z_direct_packet)

    def _monitor_position(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port))
        
        while not self.finished:
            try:
                self._send_command(ViscaCamera.ENQ_ZOOM_POS)
                self._send_command(ViscaCamera.ENQ_PAN_TILT_POS)
                while self.command_queue.qsize():
                    command = self.command_queue.get()
                    self._send_command(command)

                packets = self._receive_packets()
                for packet in packets:
                    if packet == []:
                        logging.debug("<-- []")
                    if packet == ViscaCamera.ACK1:
                        logging.debug("<-- ACK 1")
                    elif packet == ViscaCamera.ACK2:
                        logging.debug("<-- ACK 2")
                    elif packet == ViscaCamera.COMPLETE1:
                        logging.debug("<-- COMPLETE 1")
                    elif packet == ViscaCamera.COMPLETE2:
                        logging.debug("<-- COMPLETE 2")
                    elif packet == ViscaCamera.SYNTAX_ERROR:
                        logging.debug("<-- SYNTAX ERROR")
                    elif packet == ViscaCamera.COMMAND_NOT_EXECUTABLE:
                        logging.debug("<-- COMMAND NOT EXECUTABLE")
                    elif len(packet) == ViscaCamera.ZOOM_PACKET_LENGTH:
                        self.zoom_pos = self._interpret_zoom_pos_response(packet)
                    elif len(packet) == ViscaCamera.PT_PACKET_LENGTH:
                        self.pan_pos, self.tilt_pos = self._interpret_pan_tilt_pos_response(packet)
                        
            except:
                logging.exception("Error communicating with VISCA device.")
                # TODO Close socket and re-open? 

        self.socket.close()

    def _send_command(self, command):
            command_packet = [self.camera_address_byte, *command, 0xFF]
            bytes_sent = self.socket.send(bytes(command_packet))
            if bytes_sent != len(command_packet):
                raise IOError(f"Tried to send {len(command_packet)} bytes, but actually sent {bytes_sent}.")

    def _receive_packets(self):
        # TODO: Add a timeout here? 
        received_bytes = self.socket.recv(4096)
        packets = []
        packet = []
        for byte in received_bytes:
            if byte == 0xff:
                if not packet:
                    logging.debug("<-- NULL PACKET")
                else:
                    address = packet[0]
                    if address != self.camera_address_byte:
                        logging.debug(f"<-- ADDRESSED TO {address} (not here)")
                    else:
                        packets.append(packet[1:])
                        packet = []
            else:
                packet.append(byte)

        return packets

    def _interpret_zoom_pos_response(self, bytes):
            _, z0, z1, z2, z3, ff = bytes
            zoom_pos = ViscaCamera._nibbles_to_int(z0, z1, z2, z3)
            logging.debug(f"<-- ZOOM: {zoom_pos}")
            return zoom_pos

    def _interpret_pan_tilt_pos_response(self, bytes):
            _, p0, p1, p2, p3, t0, t1, t2, t3, ff = bytes
            pan_pos = ViscaCamera._nibbles_to_int(p0, p1, p2, p3)
            tilt_pos = ViscaCamera._nibbles_to_int(t0, t1, t2, t3)
            logging.debug(f"<-- PAN TILT: {pan_pos}, {tilt_pos}")
            return pan_pos, tilt_pos
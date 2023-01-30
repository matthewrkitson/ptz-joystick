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

    def _monitor_position(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port))
        
        while not self.finished:
            received_bytes = self._send_enquiry(ViscaCamera.ENQ_ZOOM_POS)
            self.zoom_pos = self._interpret_zoom_pos_response(received_bytes)

            received_bytes = self._send_enquiry(ViscaCamera.ENQ_PAN_TILT_POS)
            self.pan_pos, self.tilt_pos = self._interpret_pan_tilt_pos_response(received_bytes)

        self.socket.close()

    def _send_enquiry(self, enquiry):
            command_packet = [self.camera_address_byte, *enquiry, 0xFF]
            bytes_sent = self.socket.send(bytes(command_packet))
            received_bytes = self.socket.recv(4096)
            return received_bytes

    def _interpret_zoom_pos_response(self, bytes):
            y, _, z0, z1, z2, z3, ff = bytes
            zoom_pos = ViscaCamera._nibbles_to_int(z0, z1, z2, z3)
            return zoom_pos

    def _interpret_pan_tilt_pos_response(self, bytes):
            y, _, p0, p1, p2, p3, t0, t1, t2, t3, ff = bytes
            pan_pos = ViscaCamera._nibbles_to_int(p0, p1, p2, p3)
            tilt_pos = ViscaCamera._nibbles_to_int(t0, t1, t2, t3)
            return pan_pos, tilt_pos
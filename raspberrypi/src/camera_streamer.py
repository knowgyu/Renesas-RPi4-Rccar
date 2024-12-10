import io
import logging
import socketserver
from http import server
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import libcamera
import cv2
import numpy as np
from aruco_detector import ArucoDetector
from motor_controller import MotorController

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def __init__(self, *args, output=None, **kwargs):
        self.output = output
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with self.output.condition:
                        self.output.condition.wait()
                        frame = self.output.frame
                    
                    # ArUco 인식을 위해 프레임 처리
                    if frame is not None:
                        np_frame = np.frombuffer(frame, dtype=np.uint8)
                        img = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
                        if img is not None:
                            try:
                                img = self.output.aruco_detector.detect(img)
                                _, encoded_image = cv2.imencode('.jpg', img)
                                frame = encoded_image.tobytes()
                            except Exception as e:
                                logging.error(f"Error in ArUco processing: {e}")

                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class CameraStreamer:
    def __init__(self, motor_controller, server_url):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(
            main={"size": (640, 480)}, 
            transform=libcamera.Transform(hflip=1, vflip=1)
        ))
        self.output = StreamingOutput()
        self.motor_controller = motor_controller  # Motor controller instance
        self.aruco_detector = ArucoDetector(motor_controller, server_url)  # ArUco 탐지기 초기화
        self.output.aruco_detector = self.aruco_detector

    def start_streaming(self):
        self.picam2.start_recording(JpegEncoder(), FileOutput(self.output))
        return self.output

    def get_handler(self):
        return lambda *args, **kwargs: StreamingHandler(*args, output=self.output, **kwargs)
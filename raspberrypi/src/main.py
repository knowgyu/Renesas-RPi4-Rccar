from motor_controller import MotorController
from camera_streamer import CameraStreamer, StreamingServer
from web_server import WebServer
from threading import Thread

def main():
    # Initialize components
    motor_controller = MotorController()
    camera_streamer = CameraStreamer(motor_controller, "http://0.0.0.0:5000")
    web_server = WebServer(motor_controller)

    # Start camera streaming
    camera_streamer.start_streaming()

    # Create and start servers
    def run_streaming():
        address = ('', 8000)
        server = StreamingServer(address, camera_streamer.get_handler())
        server.serve_forever()

    # Create and start threads
    flask_thread = Thread(target=lambda: web_server.run())
    streaming_thread = Thread(target=run_streaming)

    flask_thread.start()
    streaming_thread.start()

    try:
        flask_thread.join()
        streaming_thread.join()
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()

import serial
import time

class MotorController:
    def __init__(self, port='/dev/ttyAMA0', baudrate=115200):
        self.uart = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=3
        )
        self.CENTER = 320
        self.current_status = "정지"
        self.current_speed = 100
        self.current_angle = self.CENTER

    def set_angle(self, angle):
        if angle < 0:
            angle = abs(angle)
            cmd = f"LE {angle}\n"
            print(f"좌회전 명령 : {cmd}")
            self.uart.write(cmd.encode('utf-8'))
            self.current_angle = self.CENTER - angle
        elif angle > 0:
            cmd = f"RI {angle}\n"
            print(f"우회전 명령 : {cmd}")
            self.uart.write(cmd.encode('utf-8'))
            self.current_angle = self.CENTER + angle
        else:
            cmd = f"MID\n"
            self.uart.write(cmd.encode('utf-8'))
            self.current_angle = self.CENTER
        self._delay()

    def set_speed(self, speed):
        self.current_speed = speed
        cmd = f"VE {self.current_speed}\n"
        self.uart.write(cmd.encode('utf-8'))
        self._delay()

    def go(self):
        print("직진")
        self.uart.write(b"FW\n")
        self.current_status = "직진"
        self._delay()

    def left(self):
        print("좌회전")
        self.uart.write(b"LEBTN")
        self.current_angle = self.CENTER - 25
        self._delay()

    def right(self):
        print("우회전")
        self.uart.write(b"RIBTN")
        self.current_angle = self.CENTER + 25
        self._delay()

    def back(self):
        print("후진")
        self.uart.write(b"BW\n")
        self.current_status = "후진"
        self._delay()

    def stop(self):
        print("정지")
        self.uart.write(b"QU\n")
        time.sleep(0.05)  # 원래 있던 50ms의 딜레이 유지
        self.uart.write(b"MID\n")
        self.current_angle = self.CENTER
        self.current_status = "정지"
        self._delay()

    def middle(self):
        print("중앙 정렬")
        self.uart.write(b"MID\n")
        self.current_angle = self.CENTER
        self._delay()

    def get_status(self):
        return self.current_status

    # 마커 번호 별 이벤트 함수    
    def handle_marker_0(self):
        self.stop()
        self._delay()

    def handle_marker_1(self):
        self.set_angle(-125)
        self.current_angle = self.CENTER - 125
        self._delay()

    def handle_marker_2(self):
        self.set_angle(125)
        self.current_angle = self.CENTER + 125
        self._delay()

    def handle_marker_3(self):
        self.set_angle(-125)
        self.current_angle = self.CENTER - 125
        self._delay()

    def handle_marker_4(self):
        self.set_angle(125)
        self.current_angle = self.CENTER + 125
        self._delay()

    def _delay(self):
        # 모든 함수의 끝에서 호출할 공통 지연 함수
        time.sleep(0.01)

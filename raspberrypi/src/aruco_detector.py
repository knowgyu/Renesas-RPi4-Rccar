import cv2
import numpy as np
import time
import requests  # HTTP 요청을 위해 requests 라이브러리 사용
from motor_controller import MotorController

# ArUco 마커 탐지를 처리하는 클래스
class ArucoDetector:
    def __init__(self, motor_controller, server_url):
        # ArUco 딕셔너리 및 파라미터 초기화
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters_create()
        self.motor_controller = motor_controller
        self.frame_width = 640 
        self.frame_height = 480
        self.center_tolerance = 15  # Tolerance for center alignment
        self.target_width = self.frame_width / 5  # Target width for the marker (160 pixels)
        self.max_angle = 125  # Maximum angle for motor adjustment
        self.server_url = server_url  # 웹 서버 URL
        self.last_command = None  # 마지막 명령
        self.target_marker_list = [4,3,1,2,0,0,0]
        self.last_target_idx = 0

    def detect(self, frame):
        try:
            # ArUco 마커 탐지
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejected = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)
            # 탐지된 마커 중 가장 큰 마커만 고려
            if ids is not None and len(ids) > 0:

                max_area = 0
                largest_marker = None
                largest_id = None

                for marker_id, corner in zip(ids.flatten(), corners):
                    x_coords = [point[0] for point in corner[0]]
                    y_coords = [point[1] for point in corner[0]]
                    min_x = min(x_coords)
                    max_x = max(x_coords)
                    min_y = min(y_coords)
                    max_y = max(y_coords)

                    # 마커의 넓이 계산
                    box_area = (max_x - min_x) * (max_y - min_y)

                    if box_area > max_area:
                        max_area = box_area
                        largest_marker = corner
                        largest_id = marker_id

                if largest_marker is not None:
                    # 마커의 가로 픽셀값이 목표 값 이상일 경우 동작 수행 (우선순위로 처리)
                    min_x = min([point[0] for point in largest_marker[0]])
                    max_x = max([point[0] for point in largest_marker[0]])
                    marker_width = max_x - min_x

                    # 마커를 화면에 표시하고, ID 값과 좌표 출력
                    frame = cv2.aruco.drawDetectedMarkers(frame, [largest_marker], np.array([largest_id]))
                    # print(f"Detected ArUco ID: {largest_id}, Corners: {largest_marker[0].tolist()}")
                    print(f"현재 상태 : {self.motor_controller.get_status()}")

                    # 마커를 인식했지만, 정지상태일 경우 프레임 반환
                    if self.motor_controller.get_status() == "정지":
                        return frame
                    
                    if largest_id == self.target_marker_list[self.last_target_idx+1]:
                        self.last_target_idx += 1
                    
                    if largest_id != self.target_marker_list[self.last_target_idx]:
                        return frame
                    
                    if marker_width >= self.target_width:
                        # 마커가 충분히 가까울 경우 해당 명령 수행
                        if largest_id == 0:
                            print("Marker ID 0 detected. Stopping and waiting for 5 seconds.")
                            self.motor_controller.handle_marker_0()
                            action = "stop"
                            # self.motor_controller.current_status = "정지"
                        elif largest_id == 1:
                            print("Marker ID 1 detected. Turning left with max angle and resetting to middle after 1 second.")
                            self.motor_controller.handle_marker_1()
                            action = "left"
                        elif largest_id == 2:
                            print("Marker ID 2 detected. Turning right with max angle and resetting to middle after 1 second.")
                            self.motor_controller.handle_marker_2()
                            action = "right"
                        elif largest_id == 3:
                            print("Marker ID 3 detected. Turning left with max angle and resetting to middle after 1 second.")
                            self.motor_controller.handle_marker_3()
                            action = "left"
                        elif largest_id == 4:
                            print("Marker ID 4 detected. Turning right with max angle and resetting to middle after 1 second.")
                            self.motor_controller.handle_marker_4()
                            action = "right"


                        # 명령 전송 후 웹 서버에 기록 (커맨드 테이블 업데이트)
                        self.send_command_data(action)
                        return frame  # 우선순위 동작 수행 후 함수 종료

                    # 마커를 인식했는데 정지 상태일 경우 동작
                    if self.motor_controller.get_status() == "정지":
                        self.motor_controller.go()
                        self.send_command_data("go")
                        # self.motor_controller.current_status = "직진"

                    center_x = (min_x + max_x) / 2
                    # 마커가 화면의 왼쪽 또는 오른쪽에 있을 경우 조향 각도 계산 및 명령 전송 (선형 비례)
                    if center_x < (self.frame_width / 2) - self.center_tolerance:
                        # 왼쪽으로 조향 각도 계산 (0부터 max_angle까지 비례)
                        distance_from_center = ((self.frame_width / 2) - center_x) / (self.frame_width / 2)
                        angle = min(int(distance_from_center * self.max_angle), self.max_angle)
                        print(f"Marker on the left side, turning left with angle {angle}.")
                        self.motor_controller.set_angle(-angle)
                        self.send_command_data("left")

                    elif center_x > (self.frame_width / 2) + self.center_tolerance:
                        # 오른쪽으로 조향 각도 계산 (0부터 max_angle까지 비례)
                        distance_from_center = (center_x - (self.frame_width / 2)) / (self.frame_width / 2)
                        angle = min(int(distance_from_center * self.max_angle), self.max_angle)
                        print(f"Marker on the right side, turning right with angle {angle}.")
                        self.motor_controller.set_angle(angle)
                        self.send_command_data("right")
                    else:
                        # 마커가 중앙에 위치할 경우 가운데로 정렬
                        print("Marker is centered. Executing middle alignment.")
                        self.motor_controller.middle()
                        self.send_command_data("middle")

            else:
                # 마커가 인식되지 않았을 때 직진일 경우 속도 제한하고 가운데로 진행
                if self.motor_controller.get_status() == "직진" and self.motor_controller.current_speed == 200:
                    self.motor_controller.set_speed(100)
                    # time.sleep(0.01)
                    # if self.motor_controller.current_angle != 320:
                    #     if self.motor_controller.current_angle <= 320-100:
                    #         self.motor_controller.set_angle(-90)
                    #     elif self.motor_controller.current_angle >= 320+100:
                    #         self.motor_controller.set_angle(90)

        except Exception as e:
            print(f"Error in ArUco detection: {e}")

        return frame

    def send_command_data(self, action):
        # 동일한 명령이 이미 전송된 경우 중복 방지
        if self.last_command == action:
            return

        current_time = time.strftime('%H:%M:%S')
        try:
            response = requests.post(f"{self.server_url}/control", json={"action": action, "time": current_time})
            if response.status_code != 200:
                print(f"Failed to send command data, server responded with status code: {response.status_code}")
            else:
                # 명령이 성공적으로 전송된 경우 마지막 명령 업데이트
                self.last_command = action
                # 명령 테이블 스크롤 자동 이동을 위해 JavaScript를 트리거하는 명령 추가
                requests.post(f"{self.server_url}/scroll_command_table")
        except requests.RequestException as e:
            print(f"Failed to send command data: {e}")

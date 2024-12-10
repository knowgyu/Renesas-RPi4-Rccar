import cv2

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)

# 생성할 마커 ID와 크기 설정
for marker_id in range(5):  # ID 0부터 4까지 생성
    marker = cv2.aruco.drawMarker(aruco_dict, marker_id, 600)  # 200x200 픽셀
    filename = f"aruco_marker_{marker_id}.png"
    cv2.imwrite(filename, marker)
    print(f"Saved: {filename}")

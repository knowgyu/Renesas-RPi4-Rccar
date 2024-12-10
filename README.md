# Renesas-RPi4-Rccar
 르네사스보드 FPB-RA6E1과 라즈베리파이4 Model B를 이용한 RC카 프로젝트입니다.

## Repo Tree
```
.
├── README.md
├── raspberrypi
│   └── src
│       ├── Gen_marker.py
│       ├── aruco_detector.py
│       ├── camera_streamer.py
│       ├── main.py
│       ├── motor_controller.py
│       ├── templates
│       │   └── status.html
│       └── web_server.py
├── renesas
│   └── src
│       ├── hal_entry.c
│       ├── motorhat.c
│       └── motorhat.h
└── tools
    └── Gen_marker.py
```

## 실행 방법
 ### Renesas
 - Renesas 프로젝트 생성
 - I2C, Uart 통신 설정
 - Generate Code
 - src 폴더에 위 3개의 파일 넣기

 ### RPi4
 ```bash
 python main.py
 ``` 
 
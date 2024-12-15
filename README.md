# Renesas-RPi4-Rccar
 르네사스보드 FPB-RA6E1과 라즈베리파이4 Model B를 이용한 RC카 프로젝트입니다.

## Repo Tree
```
.
├── README.md
├── raspberrypi
│   └── src
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
 
## 참고
[https://knowgyu.github.io/posts/Aruco-%EB%A7%88%EC%BB%A4%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%9C-%EC%9E%90%EC%9C%A8%EC%A3%BC%ED%96%89-RC%EC%B9%B4/](https://knowgyu.github.io/posts/Aruco-%EB%A7%88%EC%BB%A4%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%9C-%EC%9E%90%EC%9C%A8%EC%A3%BC%ED%96%89-RC%EC%B9%B4/)

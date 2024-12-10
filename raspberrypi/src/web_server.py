from flask import Flask, render_template, request, jsonify
import time
import openai  # openai 라이브러리 사용
import os

class WebServer:
    def __init__(self, motor_controller):
        self.app = Flask(__name__)
        self.motor_controller = motor_controller
        self.command_history = []  # 명령 기록 저장 리스트

        # OpenAI API 키 설정
        OPENAI_API_KEY = ""
        openai.api_key = OPENAI_API_KEY

        # Route definitions
        @self.app.route('/')
        def index():
            return render_template('status.html', 
                                   status=self.motor_controller.get_status(), 
                                   command_history=self.command_history)

        @self.app.route('/control', methods=['POST'])
        def control():
            action = request.json.get('action')
            if action == 'go':
                self.motor_controller.go()
            elif action == 'left':
                self.motor_controller.left()
            elif action == 'right':
                self.motor_controller.right()
            elif action == 'back':
                self.motor_controller.back()
            elif action == 'stop':
                self.motor_controller.stop()
            elif action == 'middle':
                self.motor_controller.middle()

            # 명령 기록 추가
            self.command_history.append({"time": time.strftime('%H:%M:%S'), "command": action})
            return jsonify(status=self.motor_controller.get_status())

        @self.app.route('/openai', methods=['POST'])
        def openai_prompt():
            prompt = request.json.get('prompt')
            if not prompt:
                return jsonify({"error": "No prompt provided"}), 400

            try:
                # OpenAI API 요청
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",  # GPT-4 mini 모델 지정
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                
                # 응답에서 텍스트 추출
                response_text = response['choices'][0]['message']['content'].strip()
                return jsonify({"response": response_text})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)

# MotorController와 WebServer 초기화 및 사용 예시
if __name__ == "__main__":
    from motor_controller import MotorController
    motor_controller = MotorController()
    web_server = WebServer(motor_controller)
    web_server.run()

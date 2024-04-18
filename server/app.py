import os
import subprocess

from flask import Flask, request, jsonify
from ppadb.client import Client as AdbClient
from com.dtmilano.android.viewclient import ViewClient

import openai

app = Flask(__name__)
openai.api_key = os.environ.get('API_KEY')

# 시리얼 번호
serial_no = None

# adb 서버 시작 함수
def start_adb_server():
    try:
        # adb start-server 명령어 실행
        subprocess.run(['adb', 'start-server'], check=True)
        print("ADB server started successfully.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)

# 디바이스 연결 확인
@app.route('/device-connection', methods=['GET'])
def adb_connect():
    global serial_no

    if request.method == 'GET':
        start_adb_server()
        client = AdbClient(host="127.0.0.1", port=5037)
        devices = client.devices()

        # 연결된 디바이스가 없는 경우
        if not devices:
            print("No devices found")
            return jsonify({'message': 'No devices found'})

        device = devices[0]
        serial_no = device.serial
        print(serial_no)

        return jsonify()

# 현재 계층 정보 추출
@app.route('/current-view', methods=['POST'])
def current_view():
    global serial_no

    if request.method == 'POST':
        vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
        vc.traverse(transform=vc.traverseShowClassIdTextAndUniqueId)  # vc의 디바이스 UI 트리를 순회. 현재 UI 상태를 출력

        return jsonify()

# 클라이언트의 input을 전달받음
@app.route('/test_gpt', methods=['POST'])
def test_gpt():
    if request.method == 'POST':
        prompt = request.json['prompt']
        image_url = "https://lily-parakeet-0ba.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F16a65ace-b6d6-4de9-9a32-f07129b8e3a6%2Fec407283-025f-4c9a-9325-b8de86793499%2FUntitled.png?table=block&id=4a6308ee-bd95-4829-b547-3656ca88f0b4&spaceId=16a65ace-b6d6-4de9-9a32-f07129b8e3a6&width=1600&userId=&cache=v2"
        openai.api_key
        pre_prompt = "한국어로 친절하게 대답해줘. 그리고 view ID만 출력해줘\n\n"
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful code assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type" : "text", "text": pre_prompt + prompt},
                        {"type": "image_url", "image_url": {
                            "url": image_url}
                         }
                    ]
                }
        ],
            max_tokens=3000,
            temperature=0.5
        )
        print(response)
        answer = response.choices[0].message.content.strip()

        return jsonify({'answer': answer})



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

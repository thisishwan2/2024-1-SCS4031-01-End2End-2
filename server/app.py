import re
import subprocess
import time

from com.dtmilano.android.viewclient import ViewClient
from flask import Flask, request, jsonify
from ppadb.client import Client as AdbClient
from pymongo import MongoClient
import xml.etree.ElementTree as elemTree
import boto3
import openai

app = Flask(__name__)

#Parse XML
tree = elemTree.parse('keys.xml')
openai.api_key = tree.find('string[@name="OPEN_API_KEY"]').text
AWS_ACCESS_KEY = tree.find('string[@name="AWS_ACCESS_KEY"]').text
AWS_SECRET_KEY = tree.find('string[@name="AWS_SECRET_KEY"]').text
BUCKET_NAME = tree.find('string[@name="BUCKET_NAME"]').text
location = 'ap-northeast-2'

# db 연동
client = MongoClient(host='localhost', port=27017)
# 'e2e_database' 데이터베이스 생성
db = client['e2e_database']
# 컬렉션 생성
hierarchy = db.ui_hierarchy

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

# S3 연결
def s3_connection():
    '''
    s3 bucket에 연결
    :return: 연결된 s3 객체
    '''
    try:
        s3 = boto3.client(
            service_name='s3',
            region_name=location,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3

s3 = s3_connection()

# s3에 파일 업로드
def s3_put_object(s3, BUCKET_NAME, AWS_ACCESS_KEY, file):
    '''
    s3 bucket에 지정 파일 업로드
    :param s3: 연결된 s3 객체(boto3 client)
    :param BUCKET_NAME: 버킷명
    :param AWS_ACCESS_KEY: 저장 파일명
    :return: 성공 시 True, 실패 시 False 반환
    '''
    try:
        s3.upload_file(
            BODY = file,
            Bucket = BUCKET_NAME,
            Key = AWS_ACCESS_KEY)

        image_url = f'https://{BUCKET_NAME}.s3.{location}.amazonaws.com/{file}'
    except Exception as e:
        print(e)
        return False
    return image_url

# 디바이스의 현재 화면 스크린샷
def take_screenshot():
    # 현재 시간을 이용하여 파일 이름 생성
    current_time = time.strftime("%H_%M_%S", time.localtime())

    # adb 명령을 실행하여 스크린샷 캡처
    capture_command = "adb shell screencap -p /sdcard/screen.png"
    subprocess.run(capture_command, shell=True)

    # 스크린샷 파일을 로컬로 가져오기
    pull_command = f"adb pull /sdcard/screen.png ~/Desktop/{current_time}.png"
    subprocess.run(pull_command, shell=True)

    # 디바이스에서 스크린샷 파일 삭제
    delete_command = "adb shell rm /sdcard/screen.png"
    subprocess.run(delete_command, shell=True)

    print(f"스크린샷이 ~/Desktop/{current_time}.png에 저장되었습니다.")

# 디바이스 연결 확인(+s3 연결)
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

        return jsonify({'message': 'Device connected'})

# 현재 계층 정보 추출 및 DB에 저장
@app.route('/current-view', methods=['POST'])
def current_view():
    global serial_no
    global hierarchy

    if request.method == 'POST':
        vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
        # traverse_to_list 메서드를 사용하여 디바이스의 UI 계층 구조를 리스트로 반환(ViewClient로 부터 재 정의함)
        ui_list = vc.traverse_to_list(transform=vc.traverseShowClassIdTextAndUniqueId)  # vc의 디바이스 UI 트리를 순회하여 리스트로 반환

        # 스크린샷을 찍어서 s3에 저장
        s3_put_object()
        print(ui_list)

        ui_data = {}
        for ui in ui_list:
            pattern_line_separator = '\n'
            ui = re.sub(pattern_line_separator, " ", ui)

            # 정규식을 사용하여 문자열을 분리합니다.
            pattern = r'(.+?) id/no_id/(\d+)'
            match = re.match(pattern, ui)

            component = match.group(1).strip()  # 앞뒤 공백 제거
            unique_id = match.group(2)

            ui_data[unique_id] = component

        # MongoDB 컬렉션에 딕셔너리 리스트를 저장합니다.
        hierarchy.insert_one(ui_data)

        return jsonify({'message': 'success'})

# DB에 저장되어 있는 시나리오 불러오기
@app.route('/load-scenario', methods=['GET'])
def load_scenario():
    global hierarchy

    if request.method == 'GET':
        documents = []
        for doc in hierarchy.find():
            doc['_id'] = str(doc['_id'])
            documents.append(doc)

        return jsonify(documents)





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
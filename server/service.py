import os
import re
import subprocess
import time
from pathlib import Path
from pymongo import ASCENDING

from com.dtmilano.android.viewclient import ViewClient
from flask import Flask, request, jsonify
from ppadb.client import Client as AdbClient
import xml.etree.ElementTree as elemTree
import boto3
import openai

from server import app

#Parse XML
tree = elemTree.parse('keys.xml')

openai.api_key = tree.find('string[@name="OPEN_API_KEY"]').text
AWS_ACCESS_KEY = tree.find('string[@name="AWS_ACCESS_KEY"]').text
AWS_SECRET_KEY = tree.find('string[@name="AWS_SECRET_KEY"]').text
BUCKET_NAME = tree.find('string[@name="BUCKET_NAME"]').text
location = 'ap-northeast-2'

# 시리얼 번호
serial_no = None

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
def s3_put_object(file_dir):
    '''
    s3 bucket에 지정 파일 업로드
    :param s3: 연결된 s3 객체(boto3 client)
    :param BUCKET_NAME: 버킷명
    :param AWS_ACCESS_KEY: 저장 파일명
    :return: 성공 시 True, 실패 시 False 반환
    '''
    try:
        upload_name = file_dir.split('/')[-1]
        s3.upload_file(
            Filename = file_dir,
            Bucket = BUCKET_NAME,
            Key = upload_name
        )

        image_url = f'https://{BUCKET_NAME}.s3.{location}.amazonaws.com/{upload_name}'
    except Exception as e:
        print(e)
        return False
    return image_url

# 디바이스의 현재 화면 스크린샷
def take_screenshot():
    # 현재 시간을 이용하여 파일 이름 생성
    current_time = "screenshot_"+ time.strftime("%H_%M_%S", time.localtime())

    # 사용자의 데스크톱 경로 가져오기
    screenshot_path = Path.home() / 'adb_screenshot'
    screenshot_path.mkdir(parents=True, exist_ok=True)  # 폴더가 없으면 생성

    # 스크린샷 저장할 파일의 전체 경로
    screenshot_file = screenshot_path / f"{current_time}.png"

    # adb 명령을 실행하여 스크린샷 캡처
    capture_command = "adb shell screencap -p /sdcard/screen.png"
    subprocess.run(capture_command, shell=True)

    # 스크린샷 파일을 로컬로 가져오기
    pull_command = f"adb pull /sdcard/screen.png {screenshot_file}"
    subprocess.run(pull_command, shell=True)

    # 디바이스에서 스크린샷 파일 삭제
    delete_command = "adb shell rm /sdcard/screen.png"
    subprocess.run(delete_command, shell=True)

    print(f"스크린샷이 {screenshot_file}에 저장되었습니다.")
    return str(screenshot_file) # 로컬 경로 반환

# 디바이스 연결 확인
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

# adb 서버 시작 함수
def start_adb_server():
    try:
        # adb start-server 명령어 실행
        subprocess.run(['adb', 'start-server'], check=True)
        print("ADB server started successfully.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)

# 현재 계층 정보 추출 및 DB에 저장
def current_view():
    global serial_no
    hierarchy = app.config['HIERARCHY']

    if request.method == 'POST':

        scenario_num = request.json['scenario_num']
        task_num = request.json['task_num']

        vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
        # traverse_to_list 메서드를 사용하여 디바이스의 UI 계층 구조를 리스트로 반환(ViewClient로 부터 재 정의함)
        ui_list = vc.traverse_to_list(transform=vc.traverseShowClassIdTextAndUniqueId)  # vc의 디바이스 UI 트리를 순회하여 리스트로 반환

        # 스크린샷을 찍어서 s3에 저장
        screenshot_dir = take_screenshot()
        screenshot_url = s3_put_object(screenshot_dir)

        # 로컬에서 이미지 삭제
        os.remove(screenshot_dir)

        insert_data = {"scenario_num": scenario_num,
                       "task_num":task_num,
                       "screenshot_url": screenshot_url}

        # mongodb에 저장
        for ui in ui_list:
            pattern_line_separator = '\n'
            ui = re.sub(pattern_line_separator, " ", ui)

            # 정규식을 사용하여 문자열을 분리합니다.
            pattern = r'(.+?) id/no_id/(\d+)'
            match = re.match(pattern, ui)

            component = match.group(1).strip()  # 앞뒤 공백 제거
            unique_id = match.group(2)

            insert_data[unique_id] = component

        # MongoDB 컬렉션에 딕셔너리 리스트를 저장합니다.
        inserted_data = hierarchy.insert_one(insert_data)
        object_id = str(inserted_data.inserted_id)

        # 응답으로 이미지 url과 db object id를 반환
        return jsonify({
            'object_id': object_id,
            'screenshot_url': screenshot_url,
            'scenario_num': scenario_num,
            'task_num': task_num
        })

# 액션 저장
def save_action():
    action_collection = app.config['ACTION_COLLECTION']

    if request.method == 'POST':
        scenario_num = request.json['scenario_num']
        action_num = request.json['action_num']
        action = request.json['action']

        action_document = {'scenario_num': scenario_num,
                           'action_num': action_num,
                           'action': action
                           }

        inserted_data = action_collection.insert_one(action_document)
        object_id = str(inserted_data.inserted_id)
        return jsonify({'object_id': object_id,
                        'scenario_num': scenario_num,
                        'task_num': action_num
        })

# 액션 수정


# 테스트 시나리오 실행
def run_scenario(): # input, output 의논해보기
    if request.method == 'POST':
        before_hierachy = request.json['before_hierachy']
        action = request.json['action']
        after_hierachy = request.json['after_hierachy']

        hierarchy = app.config['HIERARCHY']

        # 시나리오 실행(before_hierachy 와 action을 GPT에게 입력 후 결과를 받아온다.
        view_id, run_func = infer_viewid(before_hierachy, action)
        print(view_id)
        # 추론한 viewId를 바탕으로 adb 명령을 수행


def infer_viewid(hierarchy, action):
    '''
    action을 입력받아서 view id를 추론하는 함수
    :param hierarchy: 계층 정보
    :param action: 수행하고자 하는 action
    :return: 추론된 view id, 실행할 함수
    '''
    # action을 GPT에 입력
    openai.api_key
    pre_prompt = "한국어로 친절하게 대답해줘. 그리고 view ID만 출력해줘\n\n"
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful code assistant."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": pre_prompt +
                                             "ui 계층은 다음과 같아" + hierarchy +
                                             "다음 액션을 수행해줘" + action
                    }
                ]
            }
        ],
        max_tokens=3000,
        temperature=0.5
    )
    print(response)
    answer = response.choices[0].message.content.strip()

    # 추론된 view id를 반환
    return answer



# DB에 저장되어 있는 전체 시나리오 및 테스트 불러오기
def load_scenario():
    hierarchy = app.config['HIERARCHY']
    action_collection = app.config['ACTION_COLLECTION']

    if request.method == 'GET':
        # 시나리오 번호와 작업 번호별로 문서를 오름차순으로 정렬
        hierarchy_docs = hierarchy.find().sort([
            ("scenario_num", ASCENDING),  # 먼저 시나리오 번호로 정렬
            ("task_num", ASCENDING)  # 그 다음 작업 번호로 정렬
        ])

        action_docs = action_collection.find().sort([
            ("scenario_num", ASCENDING),  # 먼저 시나리오 번호로 정렬
            ("action_num", ASCENDING)  # 그 다음 액션 번호로 정렬
        ])

        hierarchy_dict = {} # 시나리오 번호: 계층 정보(작업 번호, 스크린샷 url, object id)
        action_dict = {} # 시나리오 번호: 액션 정보(액션, object id)
        for hierarchy_doc in hierarchy_docs:

            scenario_num = hierarchy_doc['scenario_num']
            if scenario_num not in hierarchy_dict:
                hierarchy_dict[scenario_num] = []
            hierarchy_dict[scenario_num].append({
                'task_num': hierarchy_doc['task_num'],
                'screenshot_url': hierarchy_doc['screenshot_url'],
                'object_id': str(hierarchy_doc['_id'])
            })

        for action_doc in action_docs:
            action_num = action_doc['scenario_num']
            if action_num not in action_dict:
                action_dict[action_num] = []
            action_dict[action_num].append({
                'action': action_doc['action'],
                'object_id': str(action_doc['_id'])
            })

        return jsonify({'hierarchy': hierarchy_dict, 'action': action_dict})
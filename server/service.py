import json
import os
import re
import subprocess
import time
from pathlib import Path

from bson import errors
from bson.objectid import ObjectId
from pymongo import ASCENDING, ReturnDocument

from com.dtmilano.android.viewclient import ViewClient
from flask import request, jsonify, make_response
from ppadb.client import Client as AdbClient
import xml.etree.ElementTree as elemTree
import boto3
import openai
from openai import OpenAI
from server.fine_tuning import init_train_data

from server import adb_function
from server import app

#Parse XML
tree = elemTree.parse('keys.xml')

openai.api_key = os.environ.get('OPENAI_API_KEY')
AWS_ACCESS_KEY = tree.find('string[@name="AWS_ACCESS_KEY"]').text
AWS_SECRET_KEY = tree.find('string[@name="AWS_SECRET_KEY"]').text
BUCKET_NAME = tree.find('string[@name="BUCKET_NAME"]').text
location = 'ap-northeast-2'

client = openai.OpenAI(api_key=openai.api_key)

# 시리얼 번호
serial_no = None
device = None

def error_response():
    response = make_response(
        jsonify(
            {"message": "error"}
        ),
        400,
    )
    response.headers["Content-Type"] = "application/json"
    return response


# 시나리오 리스트 조회
def scenarios():
    if request.method == 'GET':
        scenario_list = app.config['scenario']
        cursor = scenario_list.find({}, {'scenario_name': 1, 'run_status': 1})

        # 쿼리 결과를 JSON 직렬화 가능한 형태로 변환
        scenarios = []
        for doc in cursor:
            # ObjectId를 문자열로 변환
            doc['_id'] = str(doc['_id']) if '_id' in doc else None
            scenarios.append(doc)

        return jsonify(list(scenarios))

# 시나리오 상세 보기
def scenario(scenario_id):
    if request.method == 'GET':
        scenario_list = app.config['scenario']

        try:
            # MongoDB에서 시나리오 문서를 조회()
            scenario_doc = scenario_list.find_one({'_id': ObjectId(scenario_id)})

        # 잘못된 scenario_id를 전달받은 경우 예외처리가 안됨
        except errors.InvalidId:
            return jsonify({'error': 'Invalid scenario ID format'}), 400

        if scenario_doc:
            scenario_doc['_id'] = str(scenario_doc['_id'])
            return jsonify(scenario_doc)
        else:
            return jsonify({'error': 'Scenario not found'}), 404

# 시나리오 생성
def create_scenario():
    if request.method == 'POST':
        scenario_list = app.config['scenario']

        scenario_name = request.json['scenario_name']

        scenario_document = {'scenario_name': scenario_name,
                             'run_status': 'ready',
                             'scenario': [{'ui_data': "", 'screenshot_url': "", 'status': "ready"},{'action': "", 'status': "ready"},{'ui_data': "", 'screenshot_url': "", 'status': "ready"}]
                             }

        inserted_data = scenario_list.insert_one(scenario_document)
        return jsonify({'message': 'Success'})

# 시나리오 작업 추가
def add_task():
    if request.method == 'POST':
        scenario_list = app.config['scenario']
        object_id = request.json['object_id']

        try:
            # MongoDB에서 시나리오 문서를 조회
            scenario_doc = scenario_list.find_one({'_id': ObjectId(object_id)})
        except errors.InvalidId:
            return jsonify({'error': 'Invalid scenario ID format'}), 400

        if scenario_doc:
            # 시나리오 문서에 작업 추가
            new_tasks = [{'action': "", 'status': "ready"},{'ui_data': "", 'screenshot_url': "", 'status': "ready"}]
            updated_scenario = scenario_list.find_one_and_update(
                {'_id': ObjectId(object_id)},
                {'$push': {'scenario': {'$each': new_tasks}}},
                return_document=ReturnDocument.AFTER
            )

            if updated_scenario:
                return jsonify({'message': 'success'})
            else:
                return jsonify({'error': 'Update failed'}), 500
        else:
            return jsonify({'error': 'Scenario not found'}), 404

def transform(ui_list, ui_data):
    for ui in ui_list:
        pattern_line_separator = '\n'
        ui = re.sub(pattern_line_separator, " ", ui)

        # 정규식을 사용하여 문자열을 분리합니다.
        pattern = r'(.+?) id/no_id/(\d+)'
        match = re.match(pattern, ui)

        component = match.group(1).strip()  # 앞뒤 공백 제거
        unique_id = match.group(2)

        ui_data[unique_id] = component
    # print(ui_data)

# 현재 계층 정보 추출 및 DB에 저장
def extracted_hierarchy(scenario_id):
    global serial_no

    scenario_list = app.config['scenario']

    if request.method == 'POST':
        print("extracted_hierarchy")

        object_id = scenario_id
        index = int(request.json['index'])

        vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
        # traverse_to_list 메서드를 사용하여 디바이스의 UI 계층 구조를 리스트로 반환(ViewClient로 부터 재 정의함)
        ui_list = vc.traverse_to_list(transform=vc.traverseShowClassIdTextAndUniqueId)  # vc의 디바이스 UI 트리를 순회하여 리스트로 반환

        # 스크린샷을 찍어서 s3에 저장
        screenshot_dir = take_screenshot()
        screenshot_url = s3_put_object(screenshot_dir)

        # 로컬에서 이미지 삭제
        os.remove(screenshot_dir)

        ui_data = {}
        # mongodb에 저장
        transform(ui_list, ui_data)

        result = scenario_list.update_one(
            {'_id': ObjectId(object_id), f'scenario.{index}': {'$exists': True}},
            {'$set': {
                f'scenario.{index}': {
                    'ui_data': ui_data,  # UI 데이터
                    'screenshot_url': screenshot_url,  # 스크린샷 URL
                    'status': 'ready'  # 상태
                }
            }}
        )

        return jsonify({
            'screenshot_url': screenshot_url,
        })

# action 저장
def save_action(scenario_id):
    scenario_list = app.config['scenario']

    if request.method == 'POST':
        object_id = scenario_id
        index = int(request.json['index'])
        action = request.json['action']

        # MongoDB에서 특정 시나리오의 특정 인덱스에 action 데이터를 업데이트
        result = scenario_list.update_one(
            {'_id': ObjectId(object_id), f'scenario.{index}': {'$exists': True}},
            {'$set': {
                f'scenario.{index}.action': action,
                f'scenario.{index}.status': 'ready'
            }}
        )

    return jsonify({"message": "success"})


# 문자열로 받은 함수를 실행
def execute_function(function_name, *args, **kwargs):
    # file1 모듈의 함수를 동적으로 호출하면서, 인자와 키워드 인자 전달
    func = getattr(adb_function, function_name)
    func(*args, **kwargs)

# 실패한 지점부터 이후 지점은 전부 fail로 처리
def bulk_fail(index, length, scenario_id):
    scenario_list = app.config['scenario']
    # 현재 지점은 fail
    scenario_list.update_one(
        {'_id': ObjectId(scenario_id)},
        {'$set': {f'scenario.{index}.status': 'fail'}}
    )

    for i in range(index+1, length):
        scenario_list.update_one(
            {'_id': ObjectId(scenario_id)},
            {'$set': {f'scenario.{i}.status': 'cancel'}}
        )

def run_result(scenario_list, scenario_id):
    scenario_list.update_one(
        {'_id': ObjectId(scenario_id)},
        {'$set': {'run_status': 'fail'}}
    )

# 테스트 시나리오 실행
def run_scenario(scenario_id):
    scenario_list = app.config['scenario']
    scenario = scenario_list.find_one({'_id': ObjectId(scenario_id)})

    before_hierarchy = None
    now_index = 0
    scenario_seq = scenario['scenario']  # 시나리오 순서 추출(화면-액션-화면-액션...)

    # 전체 status 로딩으로 처리
    scenario_list.update_one(
        {'_id': ObjectId(scenario_id)},
        {'$set': {'run_status': 'loading'}}
    )

    # 모든 태스크를 로딩으로 처리
    for i in range(len(scenario_seq)):
        scenario_list.update_one(
            {'_id': ObjectId(scenario_id)},
            {'$set': {f'scenario.{i}.status': 'ready'}}
        )

    try:
        start = scenario_seq[0]
        start_hierarchy = start['ui_data']
        start_status = start['status']
        before_hierarchy = start_hierarchy

        # loading 처리
        scenario_list.update_one(
            {'_id': ObjectId(scenario_id)},
            {'$set': {'scenario.0.status': 'loading'}}
        )

        # 현재 화면 추출 및 변환
        vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
        ui_list = vc.traverse_to_list(transform=vc.traverseShowClassIdTextAndUniqueId)
        ui_data = {}
        transform(ui_list, ui_data)
        # 시작화면과 현재 화면이 같은지 비교(홈화면 기준으로 시간이 조금만 달라도 계층정보가 다르다고 판단함)
        if(ui_compare(ui_data, before_hierarchy)):
            # 시작은 성공
            scenario_list.update_one(
                {'_id': ObjectId(scenario_id)},
                {'$set': {'scenario.0.status': 'success'}}
            )

        else: # 다른화면인 경우
            ui_compare_fail(now_index, scenario_id, scenario_list, scenario_seq)
            return error_response()
    except Exception as e:
        # 첫 화면에서 실패했다면 모든 태스크는 실패 처리
        ui_compare_fail(now_index, scenario_id, scenario_list, scenario_seq)
        return error_response()
    result = None
    # 이후 태스크 실행 및 검증
    for index in range(1, len(scenario_seq)):
        # loading 처리
        scenario_list.update_one(
            {'_id': ObjectId(scenario_id)},
            {'$set': {f'scenario.{index}.status': 'loading'}}
        )

        # 액션 검증
        if index%2==1:
            try:
                action_cmd = scenario_seq[index]['action']
                # action_status = scenario_seq[i]['status']
                # 문제없이 액션 값을 받아오면 성공
                result = infer_viewid(before_hierarchy, action_cmd)

                scenario_list.update_one(
                    {'_id': ObjectId(scenario_id)},
                    {'$set': {f'scenario.{index}.status': 'success'}}
                )
            except:
                ui_compare_fail(index, scenario_id, scenario_list, scenario_seq)
                return error_response()

        # 화면 검증(여기서 부터 수정해야 함. abd function쪽 수정과 같이 하기)
        elif index%2==0:
            try:
                after_hierarchy = scenario_seq[index]['ui_data']

                # adb 함수 수행
                if len(result) == 2:
                    key, function_name = result

                    if function_name == 'back' or function_name == 'home' or 'swipe' in function_name:
                        execute_function(function_name)
                    else:
                        execute_function(function_name, key, serial_no)  # 문자열로 함수 실행

                # 새로운 화면에 대한 계층정보 추출 변환
                vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
                vc.dump(window='-1', sleep=1)  # 현재 화면을 강제로 새로 고침
                ui_list = vc.traverse_to_list(transform=vc.traverseShowClassIdTextAndUniqueId)


                ui = {}
                transform(ui_list, ui)
                before_hierarchy = after_hierarchy

                # 새로운 화면과 계층정보가 동일하면 성공
                # 시작화면과 현재 화면이 같은지 비교(홈화면 기준으로 시간이 조금만 달라도 계층정보가 다르다고 판단함)
                if (ui_compare(ui, after_hierarchy)):
                    scenario_list.update_one(
                        {'_id': ObjectId(scenario_id)},
                        {'$set': {f'scenario.{index}.status': 'success'}}
                    )

                else:
                    ui_compare_fail(index, scenario_id, scenario_list, scenario_seq)
                    return error_response()

            except:
                ui_compare_fail(index, scenario_id, scenario_list, scenario_seq)
                return error_response()

    scenario_list.update_one(
        {'_id': ObjectId(scenario_id)},
        {'$set': {'run_status': 'success'}}
    )
    return jsonify({'message': 'Success'})


# 화면 비교
def ui_compare(ui_data, hierarchy):
    for ui_key in ui_data.keys():
        screen = ui_data[ui_key].split(" ")[0]
        hierarchy_screen = hierarchy[ui_key].split(" ")[0]

        if screen != hierarchy_screen:
            return False
    return True


# 화면 비교시 실패한 경우 처리하는 로직 정의 함수
def ui_compare_fail(now_index, scenario_id, scenario_list, scenario_seq):
    bulk_fail(now_index, len(scenario_seq), scenario_id)
    run_result(scenario_list, scenario_id)


# 전체 시나리오 실행
def run_all_scenario():
    scenario_list = app.config['scenario']
    for scenario in scenario_list.find():
        scenario_id = str(scenario.get('_id'))
        response = run_scenario(scenario_id)
        print(response.status_code)

        adb_function.home()
        adb_function.home()


    return jsonify({'message': 'Success'})



# adb 함수 학습시켜서 응답으로 함수도 내보내게 해야하고, 응답 스키마도 설정해야함.
def infer_viewid(hierarchy, action):
    '''
    action을 입력받아서 view id를 추론하는 함수
    :param hierarchy: 계층 정보
    :param action: 수행하고자 하는 action
    :return: 추론된 view id, 실행할 함수
    '''
    # 계층정보를 문자열로 변환
    hierarchy_info = json.dumps(hierarchy, indent=4, ensure_ascii=False)  # 보기 좋게 포맷팅

    msg = "ui: \n" + hierarchy_info + "\naction: " + action

    # action을 GPT에 입력(gpt api는 이전 대회를 기억하지 못함)
    response = client.chat.completions.create( # 해당 요청과 model은 legacy 모델이므로 현재 최신 방법과 좀 다르다.
        model="gpt-3.5-turbo",
        # model="ft:davinci-002:personal::9J3zU2Lo",
        messages=[
            {"role": "system", "content": init_train_data},
            {"role": "user", "content": msg}
        ],
        max_tokens=50,
        temperature=0.5
    )
    # print(response)
    answer = response.choices[0].message.content
    print(answer)

    ans_lst = answer.split(",")

    # 응답 text가 없는 경우
    if len(ans_lst)==2:
        key = ans_lst[0].split("=")[-1]
        function_name = ans_lst[1].split("=")[-1]

        return key, function_name
    else:
        key = ans_lst[0].split("=")[-1]
        text = ans_lst[1].split("=")[-1]
        function_name = ans_lst[2].split("=")[-1]
        return key, text, function_name


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
    global device

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
        vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
        print(vc)
        return jsonify({'message': 'Device connected'})

# adb 서버 시작 함수
def start_adb_server():
    try:
        # adb start-server 명령어 실행
        subprocess.run(['adb', 'start-server'], check=True)
        print("ADB server started successfully.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
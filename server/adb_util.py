import subprocess
import time
from pathlib import Path
from urllib import request

from bson.objectid import ObjectId
import json
import openai
from openai import OpenAI
from ppadb.client import Client as AdbClient
from flask import request, jsonify, make_response
from com.dtmilano.android.viewclient import ViewClient



from server.fine_tuning import init_train_data
from server import app, adb_function

# client = openai.OpenAI(api_key=openai.api_key)
client = OpenAI()
# 시리얼 번호
serial_no = None
device = None

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
            return error_response()

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

# 실패시 상태 실패 처리
def run_result(scenario_list, scenario_id):
    scenario_list.update_one(
        {'_id': ObjectId(scenario_id)},
        {'$set': {'run_status': 'fail'}}
    )

def error_response():
    response = make_response(
        jsonify(
            {"message": "error"}
        ),
        404,
    )
    response.headers["Content-Type"] = "application/json"
    return response

def test_recommand_route():
    # action을 GPT에 입력(gpt api는 이전 대회를 기억하지 못함)
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "해당 이미지를 바탕으로 QA를 진행할거야. 내가 해볼 테스트를 추천해줘. 1. ~~, 2. ~~와 같이 리스트화 하고 키워드만 적어서 알려줘"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":"https://endtwoend.s3.ap-northeast-2.amazonaws.com/screenshot_12_48_07.png",
                            "detail": "high"
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    print(response.choices[0])

import os
from urllib import request
from pymongo import ReturnDocument
from flask import request, jsonify, make_response
from bson.objectid import ObjectId
from bson import errors
from com.dtmilano.android.viewclient import ViewClient



from server import adb_function
from server import app
from server.service import take_screenshot, s3_put_object, transform

from server.service import serial_no

# 템플릿 리스트 조회
def templates():
    if request.method == 'GET':
        template_list = app.config['template']
        cursor = template_list.find({}, {'template_name': 1, 'run_status': 1})

        # 쿼리 결과를 JSON 직렬화 가능한 형태로 변환
        templates = []
        for doc in cursor:
            # ObjectId를 문자열로 변환
            doc['_id'] = str(doc['_id']) if '_id' in doc else None
            templates.append(doc)

        return jsonify(list(templates))

# 템플릿 생성
def create_template():
    if request.method == 'POST':
        template_list = app.config['template']

        template_name = request.json['template_name']

        template_document = {'template_name': template_name,
                             'run_status': 'ready',
                             'template': [{'ui_data': "", 'screenshot_url': "", 'status': "ready"},
                                          {'action': "", 'status': "ready"},
                                          {'ui_data': "", 'screenshot_url': "", 'status': "ready"}]
                             }

        inserted_data = template_list.insert_one(template_document)
        return jsonify({'message': 'Success'})

# 템플릿 작업 추가
def add_task():
    if request.method == 'POST':
        template_list = app.config['template']
        object_id = request.json['object_id']

        try:
            # MongoDB에서 시나리오 문서를 조회
            template_doc = template_list.find_one({'_id': ObjectId(object_id)})
        except errors.InvalidId:
            return jsonify({'error': 'Invalid template ID format'}), 400

        if template_doc:
            # 시나리오 문서에 작업 추가
            new_tasks = [{'action': "", 'status': "ready"},{'ui_data': "", 'screenshot_url': "", 'status': "ready"}]
            updated_scenario = template_list.find_one_and_update(
                {'_id': ObjectId(object_id)},
                {'$push': {'template': {'$each': new_tasks}}},
                return_document=ReturnDocument.AFTER
            )

            if updated_scenario:
                return jsonify({'message': 'success'})
            else:
                return jsonify({'error': 'Update failed'}), 500
        else:
            return jsonify({'error': 'Template not found'}), 404

# 템플릿 상세 보기
def template(template_id):
    if request.method == 'GET':
        template_list = app.config['template']

        try:
            # MongoDB에서 시나리오 문서를 조회()
            template_doc = template_list.find_one({'_id': ObjectId(template_id)})

        # 잘못된 scenario_id를 전달받은 경우 예외처리가 안됨
        except errors.InvalidId:
            return jsonify({'error': 'Invalid scenario ID format'}), 400

        if template_doc:
            template_doc['_id'] = str(template_doc['_id'])
            return jsonify(template_doc)
        else:
            return jsonify({'error': 'Scenario not found'}), 404

# 현재 계층 정보 추출 및 DB에 저장
def extracted_hierarchy(template_id):


    template_list = app.config['template']

    if request.method == 'POST':
        print("extracted_hierarchy")

        object_id = template_id
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

        result = template_list.update_one(
            {'_id': ObjectId(object_id), f'template.{index}': {'$exists': True}},
            {'$set': {
                f'template.{index}': {
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
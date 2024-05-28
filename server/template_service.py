import os
from urllib import request
from pymongo import ReturnDocument
from flask import request, jsonify, make_response
from bson.objectid import ObjectId
from bson import errors
from com.dtmilano.android.viewclient import ViewClient



from server import adb_function
from server import app
from server.adb_util import ui_compare, ui_compare_fail, error_response, infer_viewid, execute_function
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
def save_action(template_id):
    template_list = app.config['template']

    if request.method == 'POST':
        object_id = template_id
        index = int(request.json['index'])
        action = request.json['action']

        # MongoDB에서 특정 시나리오의 특정 인덱스에 action 데이터를 업데이트
        result = template_list.update_one(
            {'_id': ObjectId(object_id), f'template.{index}': {'$exists': True}},
            {'$set': {
                f'template.{index}.action': action,
                f'template.{index}.status': 'ready'
            }}
        )

    return jsonify({"message": "success"})

# 템플릿 시나리오 실행
def run_template(template_id):
    template_list = app.config['template']
    template = template_list.find_one({'_id': ObjectId(template_id)})

    before_hierarchy = None
    now_index = 0
    template_seq = template['template']  # 시나리오 순서 추출(화면-액션-화면-액션...)

    # 전체 status 로딩으로 처리
    template_list.update_one(
        {'_id': ObjectId(template_id)},
        {'$set': {'run_status': 'loading'}}
    )

    # 모든 태스크를 준비상태로 처리
    for i in range(len(template_seq)):
        template_list.update_one(
            {'_id': ObjectId(template_id)},
            {'$set': {f'template.{i}.status': 'ready'}}
        )

    try:
        start = template_seq[0]
        start_hierarchy = start['ui_data']
        start_status = start['status']
        before_hierarchy = start_hierarchy

        # loading 처리
        template_list.update_one(
            {'_id': ObjectId(template_id)},
            {'$set': {'template.0.status': 'loading'}}
        )

        # 현재 화면 추출 및 변환
        vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
        ui_list = vc.traverse_to_list(transform=vc.traverseShowClassIdTextAndUniqueId)
        ui_data = {}
        transform(ui_list, ui_data)
        # 시작화면과 현재 화면이 같은지 비교(홈화면 기준으로 시간이 조금만 달라도 계층정보가 다르다고 판단함)
        if (ui_compare(ui_data, before_hierarchy)):
            # 시작은 성공
            template_list.update_one(
                {'_id': ObjectId(template_id)},
                {'$set': {'template.0.status': 'success'}}
            )

        else:  # 다른화면인 경우
            ui_compare_fail(now_index, template_id, template_list, template_seq)
            return error_response()
    except Exception as e:
        # 첫 화면에서 실패했다면 모든 태스크는 실패 처리
        ui_compare_fail(now_index, template_id, template_list, template_seq)
        return error_response()
    result = None
    # 이후 태스크 실행 및 검증
    for index in range(1, len(template_seq)):
        # loading 처리
        template_list.update_one(
            {'_id': ObjectId(template_id)},
            {'$set': {f'template.{index}.status': 'loading'}}
        )

        # 액션 검증
        if index % 2 == 1:
            try:
                action_cmd = template_seq[index]['action']
                # action_status = scenario_seq[i]['status']
                # 문제없이 액션 값을 받아오면 성공
                result = infer_viewid(before_hierarchy, action_cmd)

                template_list.update_one(
                    {'_id': ObjectId(template_id)},
                    {'$set': {f'template.{index}.status': 'success'}}
                )
            except:
                ui_compare_fail(index, template_id, template_list, template_seq)
                return error_response()

        # 화면 검증(여기서 부터 수정해야 함. abd function쪽 수정과 같이 하기)
        elif index % 2 == 0:
            try:
                after_hierarchy = template_seq[index]['ui_data']

                # adb 함수 수행
                if len(result) == 2:
                    key, function_name = result

                    if function_name == 'back' or function_name == 'home' or 'swipe' in function_name:
                        execute_function(function_name)
                    else:
                        execute_function(function_name, key)  # 문자열로 함수 실행

                # 새로운 화면에 대한 계층정보 추출 변환
                vc = ViewClient(*ViewClient.connectToDeviceOrExit())
                vc.dump(window='-1', sleep=1)  # 현재 화면을 강제로 새로 고침
                ui_list = vc.traverse_to_list(transform=vc.traverseShowClassIdTextAndUniqueId)

                ui = {}
                transform(ui_list, ui)
                before_hierarchy = after_hierarchy

                # 새로운 화면과 계층정보가 동일하면 성공
                # 시작화면과 현재 화면이 같은지 비교(홈화면 기준으로 시간이 조금만 달라도 계층정보가 다르다고 판단함)
                if (ui_compare(ui, after_hierarchy)):
                    template_list.update_one(
                        {'_id': ObjectId(template_id)},
                        {'$set': {f'template.{index}.status': 'success'}}
                    )

                else:
                    ui_compare_fail(index, template_id, template_list, template_seq)
                    return error_response()

            except:
                ui_compare_fail(index, template_id, template_list, template_seq)
                return error_response()

    template_list.update_one(
        {'_id': ObjectId(template_id)},
        {'$set': {'run_status': 'success'}}
    )
    return jsonify({'message': 'Success'})

def delete_template(template_id):
    template_list = app.config['template']
    template_list.delete_one({'_id': ObjectId(template_id)})

    return jsonify({'message': 'Success'})
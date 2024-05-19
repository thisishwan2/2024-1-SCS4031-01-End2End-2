from urllib import request
from pymongo import ReturnDocument
from flask import request, jsonify, make_response
from bson.objectid import ObjectId
from bson import errors



from server import adb_function
from server import app

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

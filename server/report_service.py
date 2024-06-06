from flask import request, jsonify, make_response
from server import app
from bson.objectid import ObjectId


def get_reports():
    if request.method == 'GET':
        report_list = app.config['report']
        cursor = report_list.find({}, {'report_name': 1, 'created_at': 1})

        reports = []
        for doc in cursor:
            # ObjectId를 문자열로 변환
            doc['_id'] = str(doc['_id']) if '_id' in doc else None
            reports.append(doc)

        return jsonify(list(reports))

def get_report(report_id):
    if request.method == 'GET':
        report_list = app.config['report']
        # MongoDB에서 시나리오 문서를 조회()
        report_doc = report_list.find_one({'_id': ObjectId(report_id)})

        if report_doc:
            report_doc['_id'] = str(report_doc['_id'])
            return jsonify(report_doc)
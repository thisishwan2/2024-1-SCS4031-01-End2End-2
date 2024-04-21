from server import service
from flask_restx import Api, Resource, reqparse, fields
from server import app


api = Api(app, version='1.0', title='E2E API 문서', description='Swagger 문서', doc="/api-docs")
E2E = api.namespace(name = "E2E", description='E2E API')
test_action = E2E.model('action', {
    'action': fields. String(description = '수행하고자 하는 action을 입력하세요', required = True, example = '1번 id를 찾아서 클릭해줘')
})

action_response_model = api.model('ActionResponse', {
'object_id': fields.String(description='action Id', required=True)
})

# 디바이스 연결 확인
@E2E.route('/device-connection')
class adb_connect(Resource):
    def get(self):
        '''
        디바이스 연결 확인
        :return: 디바이스 연결 상태
        '''
        return service.adb_connect()

# 현재 계층 정보 추출 및 DB에 저장
@E2E.route('/current-view')
class current_view(Resource):
    def post(self):
        '''
        현재 계층 정보 추출 및 DB에 저장
        :return: 현재 계층 정보
        '''
        return service.current_view()

# 액션 저장
@E2E.route('/save-action')
@api.doc(responses={200: 'Success', 400: 'Error'},
         description='이 API 엔드포인트는 사용자의 액션을 받아서 데이터베이스에 저장합니다.')
class save_action(Resource):
    @E2E.expect(test_action)
    @api.response(200, 'Success', action_response_model)  # 응답 모델 적용
    def post(self):
        '''
        액션 저장
        :return: 액션 아이디
        '''
        return service.save_action()

# DB에 저장되어 있는 시나리오 불러오기
@E2E.route('/load-scenario')
class load_scenario(Resource):
    def get(self):
        '''
        DB에 저장되어 있는 시나리오 불러오기
        :return: 시나리오
        '''
        return service.load_scenario()

# 클라이언트의 input을 전달받음
@E2E.route('/test_gpt')
class test_gpt(Resource):
    def post(self):
        '''
        클라이언트의 input을 전달받음
        :return: GPT-3 결과
        '''
        return service.test_gpt()
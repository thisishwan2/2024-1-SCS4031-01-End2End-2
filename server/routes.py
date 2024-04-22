from server import service
from flask_restx import Api, Resource, reqparse, fields
from server import app


api = Api(app, version='1.0', title='E2E API 문서', description='Swagger 문서', doc="/api-docs")
E2E = api.namespace(name = "E2E", description='E2E API')

current_view = E2E.model('current_view', {
    'scenario_num': fields. String(description = '시나리오 번호', required = True, example = '1'),
    'task_num': fields. String(description = '작업 번호', required = True, example = '1')
})
current_view_response_model = api.model('currentViewResponse', {
    'object_id': fields.String(description='object Id', required=True),
    'screenshot_url': fields.String(description='스크린샷 url', required=True),
    'scenario_num': fields.String(description='시나리오 번호', required=True),
    'task_num': fields.String(description='작업 번호', required=True),
})

test_action = E2E.model('action', {
    'action': fields. String(description = '수행하고자 하는 action을 입력하세요', required = True, example = '1번 id를 찾아서 클릭해줘'),
    'scenario_num': fields. String(description = '시나리오 번호', required = True, example = '1'),
    'action_num': fields. String(description = '액션 번호', required = True, example = '1')
})

action_response_model = api.model('ActionResponse', {
    'object_id': fields.String(description='action Id', required=True),
    'scenario_num': fields.String(description='시나리오 번호', required=True),
    'action_num': fields.String(description='액션 번호', required=True),
})


# Action의 상세 정보를 나타내는 모델
ActionDetail = api.model('ActionDetail', {
    'action': fields.String(description='수행할 액션 설명', required=True),
    'object_id': fields.String(description='액션의 MongoDB ObjectId', required=True)
})

# Hierarchy의 상세 정보를 나타내는 모델
HierarchyDetail = api.model('HierarchyDetail', {
    'object_id': fields.String(description='Hierarchy의 MongoDB ObjectId', required=True),
    'screenshot_url': fields.String(description='스크린샷의 URL', required=True),
    'task_num': fields.String(description='작업 번호', required=True)
})

# 시나리오 전체를 로드하는 모델
load_scenario = api.model('LoadScenario', {
    'action': fields.Nested(ActionDetail, as_list=True, description='액션들의 리스트'),
    'hierarchy': fields.Nested(HierarchyDetail, as_list=True, description='계층 구조의 리스트')
})


run_scenario = E2E.model('scenario', {
    'before_hierachy_id': fields.String(description = 'action 실행 전 계층 objectId', required = True, example = '1'),
    'action': fields.String(description = '수행하고자 하는 action', required = True, example = '1번 id를 찾아서 클릭해줘'),
    'after_hierachy_id': fields.String(description = 'action 실행 후 계층 objectId', required = True, example = '2')
})
run_scenario_response_model = api.model('RunScenarioResponse', {
    'result': fields.String(description='시나리오 실행 결과', required=True, example='success')
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
@api.doc(responses={200: 'Success', 400: 'Error'},
            description='이 API 엔드포인트는 현재 계층 정보를 추출하고 데이터베이스에 저장합니다.')
class current_view(Resource):
    @E2E.expect(current_view)
    @api.response(200, 'Success', current_view_response_model)  # 응답 모델 적용
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
    # @E2E.expect(run_scenario)
    @api.response(200, 'Success', load_scenario)  # 응답 모델 적용
    def get(self):
        '''
        DB에 저장되어 있는 시나리오 불러오기
        :return: 시나리오
        '''
        return service.load_scenario()

# 시나리오 실행(계층정보 - 액션 - 계층정보)
@E2E.route('/run-scenario')
class run_scenario(Resource):
    @E2E.expect(run_scenario)
    @api.response(200, 'Success', run_scenario_response_model)  # 응답 모델 적용
    def post(self):
        '''
        시나리오 실행(계층정보 - 액션 - 계층정보)
        :return: 시나리오 실행 결과
        '''
        return service.run_scenario()


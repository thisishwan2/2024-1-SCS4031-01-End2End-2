from server import service
from flask_restx import Api, Resource, reqparse, fields
from server import app


api = Api(app, version='1.0', title='e2e API 문서', description='Swagger 문서', doc="/api-docs")
e2e = api.namespace(name = "e2e", description='e2e API')

# 개별 시나리오 아이템 응답 모델
scenario_model = api.model('scenario', {
    'object_id': fields.String(description='Object ID', required=True, attribute=lambda x: str(x['_id'])),
    'scenario_name': fields.String(description='시나리오 이름', required=True),
    'run_status': fields.String(description='시나리오 실행 상태', required=True),
})

# 시나리오 리스트 응답 모델
scenario_list_model = api.model('scenario_list', {
    'scenarios': fields.List(fields.Nested(scenario_model), description='시나리오 리스트')
})

# 시나리오 상세 정보 응답 모델
scenario_detail_model = api.model('scenario_detail', {
    'object_id': fields.String(description='Object ID', required=True),
    'scenario_name': fields.String(description='시나리오 이름', required=True),
    'run_status': fields.String(description='시나리오 실행 상태', required=True),
})

# 시나리오 생성 요청 모델
create_scenario_model = e2e.model('CreateScenario', {
    'scenario_name': fields.String(description='시나리오 이름', required=True),
})

# 시나리오 생성 응답 모델
# create_scenario_model = api.model('CreateScenario', {
#     'object_id': fields.String(description='Object ID', required=True),
#     'scenario_name': fields.String(description='시나리오 이름', required=True),
# })

# 시나리오 작업 추가 요청 모델
add_task_model = e2e.model('AddTask', {
    'object_id': fields.String(description='Object ID', required=True),
})

# 계층 정보 추출 요청 모델
extracted_hierarchy_model = e2e.model('ExtractedHierarchy', {
    'index': fields.String(description='순서', required=True),
})

# 계층 정보 추출 응답 모델
extracted_hierarchy_response_model = api.model('ExtractedHierarchyResponse', {
    'screenshot_url': fields.String(description='스크린샷 url', required=True),
})

# 액션 추가 요청 모델
save_action = e2e.model('SaveAction', {
    'action': fields. String(description = '수행하고자 하는 action을 입력하세요', required = True, example = '1번 id를 찾아서 클릭해줘'),
    'index': fields.String(description = '순서', required = True, example = '1')
})

# 액션 추가 응답 모델
# save_action_response_model = api.model('SaveActionResponse', {
#     'object_id': fields.String(description='action Id', required=True),
#     'scenario_num': fields.String(description='시나리오 번호', required=True),
#     'action_num': fields.String(description='액션 번호', required=True),
# })


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

# run_scenario = e2e.model('scenario', {
#     'before_hierachy_id': fields.String(description = 'action 실행 전 계층 objectId', required = True, example = '1'),
#     'action': fields.String(description = '수행하고자 하는 action', required = True, example = '1번 id를 찾아서 클릭해줘'),
#     'after_hierachy_id': fields.String(description = 'action 실행 후 계층 objectId', required = True, example = '2')
# })
run_scenario_response_model = api.model('RunScenarioResponse', {
    'result': fields.String(description='시나리오 실행 결과', required=True, example='success')
})



# 디바이스 연결 확인
@e2e.route('/device-connection')
class adb_connect(Resource):
    def get(self):
        '''
        디바이스 연결 확인
        :return: 디바이스 연결 상태
        '''
        return service.adb_connect()

# 시나리오 리스트 불러오기
@e2e.route('/scenarios')
class scenarios(Resource):
    @api.response(200, 'Success', scenario_list_model)  # 응답 모델 적용
    def get(self):
        '''
        시나리오 리스트 불러오기
        :return: 시나리오 리스트
        '''
        scenarios = service.scenarios()  # 시나리오 데이터를 불러오는 서비스 함수
        return scenarios  # 모델에 맞게 데이터를 포맷

    # 시나리오 생성
    @e2e.expect(create_scenario_model)
    @api.response(200, 'Success')  # 응답 모델 적용
    def post(self):
        '''
        시나리오 생성
        '''
        return service.create_scenario()

# 시나리오 상세 조회
@e2e.route('/scenarios/<string:scenario_id>')
class scenario(Resource):
    @api.response(200, 'Success')  # 응답 모델 적용
    @api.response(400, 'Error')
    def get(self, scenario_id):
        '''
        시나리오 상세 조회
        :param scenario_id: 시나리오 아이디
        :return: 시나리오 상세 정보
        '''
        return service.scenario(str(scenario_id))


# 시나리오 작업 추가
@e2e.route('/scenarios/tasks')
class add_task(Resource):
    @e2e.expect(add_task_model)
    @api.response(200, 'Success')  # 응답 모델 적용
    def post(self):
        '''
        시나리오 작업 추가
        '''
        return service.add_task()

# 현재 계층 정보 추출 및 DB에 저장
@e2e.route('/scenarios/<string:scenario_id>/hierarchy')
class extracted_hierarchy(Resource):
    @e2e.expect(extracted_hierarchy_model)
    @api.response(200, 'Success', extracted_hierarchy_response_model)
    def post(self, scenario_id):
        '''
        현재 계층 정보 추출 및 DB에 저장
        :return: 현재 계층 정보
        '''
        return service.extracted_hierarchy(scenario_id)

# 액션 저장
@e2e.route('/scenarios/<string:scenario_id>/action')
class save_action(Resource):
    @e2e.expect(save_action)
    # @api.response(200, 'Success', save_action_response_model)  # 응답 모델 적용
    def post(self, scenario_id):
        '''
        액션 저장
        :return: 액션 아이디
        '''
        return service.save_action(scenario_id)

# 시나리오 실행
@e2e.route('/scenarios/<string:scenario_id>/run')
class run_scenario(Resource):
    @api.response(200, 'Success', run_scenario_response_model)  # 응답 모델 적용
    @api.response(400, 'Error')
    def post(self, scenario_id):
        '''
        시나리오 실행(계층정보 - 액션 - 계층정보)
        :return: 시나리오 실행 결과
        '''
        return service.run_scenario(scenario_id)

# 전체 시나리오 실행
@e2e.route('/scenarios/run-all')
class run_all_scenario(Resource):
    @api.response(200, 'Success')  # 응답 모델 적용
    def post(self):
        return service.run_all_scenario()

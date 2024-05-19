from flask import Flask
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 모든 도메인에서의 CORS 요청을 허용

from server import routes
from server import s3_upload

# db 연동
client = MongoClient(host='localhost', port=27017)
db = client['e2e_database']
scenario= db.scenario_collection
template = db.template_collection

app.config['scenario'] = db.scenario_collection
app.config['template'] = db.template_collection
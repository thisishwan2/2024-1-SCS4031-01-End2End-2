import xml.etree.ElementTree as elemTree
import openai
from openai import OpenAI

tree = elemTree.parse('keys.xml')
openai.api_key = tree.find('string[@name="OPEN_API_KEY"]').text

client = OpenAI(api_key=openai.api_key)


# 파일 업로드
with open("example_prepared.jsonl", "rb") as f:
    upload_response = client.files.create(
        file=f,
        purpose="fine-tune"
    )


# 모델 생성
client.fine_tuning.jobs.create(
    training_file=upload_response.id,
    model="davinci-002"
)
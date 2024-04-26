import xml.etree.ElementTree as elemTree
# from openai import OpenAI
import openai
import subprocess

tree = elemTree.parse('keys.xml')
openai.api_key = tree.find('string[@name="OPEN_API_KEY"]').text

# client = OpenAI(api_key=openai.api_key)

def fine_tunes():
    # 명령어 실행
    command = "openai tools fine_tunes.prepare_data -f example.jsonl"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 실행 결과 받기
    stdout, stderr = process.communicate()

    # 결과 출력
    print("표준 출력:", stdout.decode())
    print("표준 에러:", stderr.decode())

# fine_tunes()

# 파일 업로드
with open("example.jsonl", "rb") as f:
    upload_response = openai.File.create(
        file=f,
        purpose="fine-tune"
    )


# 모델 생성
openai.FineTuningJob.create(
    training_file=upload_response.id,
    model="gpt-3.5-turbo-0125",
)
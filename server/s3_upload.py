import boto3
import xml.etree.ElementTree as elemTree


#Parse XML
tree = elemTree.parse('keys.xml')

AWS_ACCESS_KEY = tree.find('string[@name="AWS_ACCESS_KEY"]').text
AWS_SECRET_KEY = tree.find('string[@name="AWS_SECRET_KEY"]').text
BUCKET_NAME = tree.find('string[@name="BUCKET_NAME"]').text
location = 'ap-northeast-2'

# S3 연결
def s3_connection():
    '''
    s3 bucket에 연결
    :return: 연결된 s3 객체
    '''
    try:
        s3 = boto3.client(
            service_name='s3',
            region_name=location,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3

s3 = s3_connection()

# s3에 파일 업로드
def s3_put_object(file_dir):
    '''
    s3 bucket에 지정 파일 업로드
    :param s3: 연결된 s3 객체(boto3 client)
    :param BUCKET_NAME: 버킷명
    :param AWS_ACCESS_KEY: 저장 파일명
    :return: 성공 시 True, 실패 시 False 반환
    '''
    try:
        upload_name = file_dir.split('/')[-1]
        s3.upload_file(
            Filename = file_dir,
            Bucket = BUCKET_NAME,
            Key = upload_name
        )

        image_url = f'https://{BUCKET_NAME}.s3.{location}.amazonaws.com/{upload_name}'
    except Exception as e:
        print(e)
        return False
    return image_url
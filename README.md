# 융합캡스톤 디자인
2024년 융합캡스톤 디자인 프로젝트 End2End팀 입니다.
<br>

## 🖥️ 시연 영상
[시연 영상](https://www.youtube.com/watch?v=T3jg4lkdJek)
<br>

## 🎲 프로젝트명(Project Name)

생성형 AI 기반 배포전 오류검출 서비스
<br>


## ⚒️ Tech Stack

<div align=center>
  <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=React&logoColor=black">
  <br>
  
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=flask&logoColor=white">
  <img src="https://img.shields.io/badge/mongodb-47A248?style=for-the-badge&logo=mongodb&logoColor=white">
  <br>

  <img src="https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/openai-412991?style=for-the-badge&logo=openai&logoColor=white">
  <img src="https://img.shields.io/badge/amazons3-569A31?style=for-the-badge&logo=amazons3&logoColor=white">
  <img src="https://img.shields.io/badge/android debug bridge-34A853?style=for-the-badge&logo=android&logoColor=white">
  <br>

  <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/slack-4A154B?style=for-the-badge&logo=slack&logoColor=white">
  <img src="https://img.shields.io/badge/notion-000000?style=for-the-badge&logo=notion&logoColor=white">
  <img src="https://img.shields.io/badge/figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white">


</div>

## 개발 환경(Development Environment)

|Language|Python 3.10|
|:---|:---|
|Framework|Flask|
|Database|MongoDB, AWS S3|
|ETC|Open AI, Android Debug Bridge(ADB)|

## ⚙️ System Architecture
<img width="841" alt="e2e 아키텍쳐" src="https://github.com/thisishwan2/2024-1-SCS4031-01-End2End-2/blob/main/server/image/E2E_Architecture.png">



## 📙 프로젝트 내용(Project Description)
### 프로젝트 배경 및 문제정의
- 인터넷 상에는 많은 이미지가 존재.
- 하지만, 다량의 이미지를 획득할 수 있는 방법은 부재.
- 저작권, 라이선스로부터 자유로운 많은양의 이미지를 구하기가 어려움

### 프로젝트 목표
- 사용자가 원하는 수량만큼 Input 이미지와 유사한 이미지를 생성해주는 플랫폼 구축.
- 사용자들간의 이미지 데이터를 거래할 수 있는 서비스 구현

### 담당 업무
- 팀장으로서 프로젝트 일정관리, 업무 분담, 발표, 프로세스 구성
- 백엔드 서비스 로직 개발
- 데이터베이스 구축 및 운용
- AI 모델의 결과를 서빙하여 사용자에게 제공
- Github actions를 활용한 CI/CD 파이프라인 구축
- 데이터 생성 메서드 비동기적 처리
- Server Sent Events 처리를 통한 사용성 증대

## 🔍 Appendix

### ERD
<img width="776" alt="GANerate_ERD" src="https://github.com/four-leaf-clover-haninum/GANerate_Backend/assets/112103038/5667f19b-29e3-46c4-8cc6-b929ea2acb7e">

### Rest Docs API 명세서
[GANerate REST API 문서-pdf.pdf](https://github.com/four-leaf-clover-haninum/GANerate_Backend/files/12798818/GANerate.REST.API.-pdf.pdf)

### 결과 상세 이미지
<img width="960" alt="스크린샷 2023-10-04 오전 11 36 25" src="https://github.com/four-leaf-clover-haninum/GANerate_Backend/assets/112103038/6cd5ed60-0bde-4f78-911c-14ab4776ae4f">

- JPA Specification을 이용하여 다중 조건 검색 구현

<div><br><br></div>

<img width="1687" alt="스크린샷 2023-09-25 오후 6 30 30" src="https://github.com/four-leaf-clover-haninum/GANerate_Backend/assets/112103038/cf1d842a-94fc-4557-9c97-2ecaa34ba71e">

- 데이터 생성 요청 폼에 수량, 이미지, 설명, 카테고리 등을 기입.

<div><br><br></div>

<img width="1560" alt="스크린샷 2023-09-25 오후 6 27 55" src="https://github.com/four-leaf-clover-haninum/GANerate_Backend/assets/112103038/ec484cc1-fc97-48e7-876e-43841617babf">

- 아임포트 API를 이용한 결제 및 검증

<div><br><br></div>

<img width="1709" alt="스크린샷 2023-09-25 오후 6 32 49" src="https://github.com/four-leaf-clover-haninum/GANerate_Backend/assets/112103038/1fdd0103-66f6-44b1-83c4-533c6b3a65b3">

- 데이터 생성 완료시 SSE를 통해 메세지 전송 및 이벤트 처리

<div><br><br></div>


<img width="1184" alt="스크린샷 2023-09-25 오후 6 45 36" src="https://github.com/four-leaf-clover-haninum/GANerate_Backend/assets/112103038/2d3191bb-0900-4bd6-aade-461680abf00f">

- 마이페이지를 통해 이미지 셋 다운로드 후 로컬에서 64*64의 Input과 유사한 생성이미지 확인.
  


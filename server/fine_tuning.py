import xml.etree.ElementTree as elemTree
import subprocess
from openai import OpenAI
import openai
import jsonlines

tree = elemTree.parse('keys.xml')
openai.api_key = tree.find('string[@name="OPEN_API_KEY"]').text

client = OpenAI(api_key=openai.api_key)

init_train_data = '''
user의 input은 ui와 action이 있어. 따라서 입력 예시를 보여주면 아래와 같아

ui:
{
  "1": "android.widget.FrameLayout",
  "2": "android.view.View",
  "3": "android.view.View",
  "4": "android.view.View",
  "5": "android.widget.Button",
  "6": "android.view.View",
  "7": "android.widget.TextView  리뷰",
  "8": "android.view.View",
  "9": "android.view.View",
  "10": "android.widget.Button",
  "11": "android.view.View",
  "12": "android.view.View",
  "13": "android.widget.Button",
  "14": "androidx.recyclerview.widget.RecyclerView com.sampleapp:id/contentRecyclerview",
  "15": "android.view.ViewGroup com.sampleapp:id/topRatingLayout",
  "16": "android.widget.TextView com.sampleapp:id/recentRatingTextView 4.9",
  "17": "android.widget.TextView com.sampleapp:id/rating5TitleTextView 5점",
  "18": "android.widget.ProgressBar com.sampleapp:id/rating5ProgressBar",
  "19": "android.widget.TextView com.sampleapp:id/rating5ReviewCountTextView 612",
  "20": "android.widget.TextView com.sampleapp:id/rating4TitleTextView 4점",
  "21": "android.widget.ProgressBar com.sampleapp:id/rating4ProgressBar",
  "22": "android.widget.TextView com.sampleapp:id/rating4ReviewCountTextView 12",
  "23": "android.widget.TextView com.sampleapp:id/rating3TitleTextView 3점",
  "24": "android.widget.ProgressBar com.sampleapp:id/rating3ProgressBar",
  "25": "android.widget.TextView com.sampleapp:id/rating3ReviewCountTextView 6",
  "26": "android.widget.TextView com.sampleapp:id/rating2TitleTextView 2점",
  "27": "android.widget.ProgressBar com.sampleapp:id/rating2ProgressBar",
  "28": "android.widget.TextView com.sampleapp:id/rating2ReviewCountTextView 1",
  "29": "android.widget.TextView com.sampleapp:id/rating1TitleTextView 1점",
  "30": "android.widget.ProgressBar com.sampleapp:id/rating1ProgressBar",
},
action: 3점을 찾아서 클릭해줘

위가 입력 예시야. 넌 이런 입력이 들어왔을때, 아래와 같은 응답을 해주면 돼.

"key = 1, action = find_by_id_touch" 와 같은 형태로 답변하거나,  "key = 1, text= 가나다,  action = find_by_id_touch" 와 같은 형태로 답변하거나, "key = None, action = swipe_up_to_down" 과 같이 답변할 수도 있어

key는 해당하는 id를 반환하고, text는 입력할 text를 반환하면 돼, 그리고 function은 알맞은 함수 이름을 반환하면 되는데 그 function을 선택하는 방법은 아래와 같아

클릭해줘 라는 action에는 find_by_id_touch 함수 혹은 find_by_text_touch를 반환하고, xx를 찾아서 xxx을 입력해줘 라는 action에는 find_by_id_touch_type를 반환하고, 뒤로가줘 라는 action에는 back를 반환하고,  홈으로 가줘 라는 action에는 home을 반환하고, 오른쪽으로 스와이프해줘 라는 action에는 swipe_left_to_right 를 반환하고, 왼쪽으로 스와이프해줘 라는 action에는 swipe_right_to_left를 반환하고, 아래로 스와이프해줘 라는 action에는 swipe_up_to_down를 반환하고, 위로 스와이프 해줘 라는 action에는 swipe_down_to_up을 반환해야 해. 

자 이제 이런 정보들을 학습하고, 다음 질문부터 알맞는 답변을 해주면 돼
'''

# gpt 초기 학습
def init_train_llm(init_train_data):
    response = client.chat.completions.create(  # 해당 요청과 model은 legacy 모델이므로 현재 최신 방법과 좀 다르다.
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": init_train_data}
        ],

        max_tokens=20,
        temperature=0.5
    )
    answer = response.choices[0].message.content
    print(answer)
init_train_llm(init_train_data)


def fine_tunes():
    # 명령어 실행
    command = "openai tools fine_tunes.prepare_data -f example.jsonl"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 파일 업로드
def upload_file():
    with open("example.jsonl", "rb") as f:
        upload_response = openai.File.create(
            file=f,
            purpose="fine-tune"
        )

    return upload_response


# 모델 생성
def create_model(upload_response):
    model = openai.FineTuningJob.create(
        training_file=upload_response.id,
        model="davinci-002",
    )

data1 = {
  "1": "android.widget.FrameLayout",
  "2": "com.android.launcher2.Workspace com.sec.android.app.launcher:id/workspace",
  "3": "android.view.ViewGroup",
  "4": "android.appwidget.AppWidgetHostView",
  "5": "android.widget.RelativeLayout com.sec.android.daemonapp:id/main_layout",
  "6": "android.widget.TextView com.sec.android.daemonapp:id/time_view 2:02",
  "7": "android.widget.TextView com.sec.android.daemonapp:id/am_pm_view 오전",
  "8": "android.widget.TextView com.sec.android.daemonapp:id/date_view 4월 27일 토요일",
  "9": "android.appwidget.AppWidgetHostView",
  "10": "android.widget.FrameLayout com.google.android.googlequicksearchbox:id/search_widget_google_logo",
  "11": "android.widget.FrameLayout com.google.android.googlequicksearchbox:id/search_edit_frame",
  "12": "android.widget.ImageButton com.google.android.googlequicksearchbox:id/search_widget_dynamic_left_icon",
  "13": "android.widget.ImageButton com.google.android.googlequicksearchbox:id/search_widget_dynamic_right_icon",
  "14": "android.widget.TextView  T전화",
  "15": "android.widget.TextView  카메라",
  "16": "android.widget.TextView  Play 스토어",
  "17": "android.widget.TextView  Google",
  "18": "android.widget.FrameLayout com.sec.android.app.launcher:id/hotseat",
  "19": "android.widget.TextView  전화",
  "20": "android.widget.TextView  연락처",
  "21": "android.widget.TextView  메시지",
  "22": "android.widget.TextView  인터넷",
  "23": "android.widget.TextView com.sec.android.app.launcher:id/home_allAppsIcon 앱스",
}

data2 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.View",
  "3": "android.view.View",
  "4": "android.view.View",
  "5": "android.view.View",
  "6": "android.view.View",
  "7": "android.widget.TextView  레전드 닥터 최태수, 그의 아들 '닥터 최대호'로 돌아오다",
  "8": "android.widget.TextView  업데이트 가능",
  "9": "android.view.View",
  "10": "android.view.View",
  "11": "android.view.View",
  "12": "android.widget.TextView  설치",
  "13": "android.widget.Button",
  "14": "android.widget.TextView  인앱 구매",
  "15": "android.view.View",
  "16": "android.widget.TextView  인기 앱",

}

data3 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.View",
  "3": "android.view.View",
  "4": "android.view.View",
  "5": "android.view.View",
  "6": "android.view.View",
  "7": "android.widget.TextView  Netflix(넷플릭스)",
  "8": "android.widget.TextView  Netflix, Inc.",
  "9": "android.view.View",
  "10": "android.view.View",
  "11": "android.view.View",
  "12": "android.view.View",
  "13": "android.widget.TextView  설치",
  "14": "android.widget.Button",
  "15": "android.view.View",
  "16": "android.view.View",
  "17": "android.view.View",
  "18": "android.view.View",
  "19": "android.view.View",
  "20": "android.view.View",
  "21": "android.view.View",
  "22": "android.widget.TextView  앱 정보",
  "23": "android.view.View",
  "24": "android.widget.TextView  다양한 TV 시리즈와 영화를 볼 수 있는 세계 최고의 구독 서비스",
  "25": "android.widget.HorizontalScrollView",
  "26": "android.view.View",
}

data4 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.ViewGroup com.android.vending:id/0_resource_name_obfuscated",
  "3": "android.widget.FrameLayout com.android.vending:id/0_resource_name_obfuscated",
  "4": "android.widget.ScrollView com.android.vending:id/0_resource_name_obfuscated",
  "5": "android.view.ViewGroup",
  "6": "android.widget.ImageButton",
  "7": "android.widget.TextView com.android.vending:id/0_resource_name_obfuscated 점핏 - 개발자 커리어 점프",
  "8": "android.widget.TextView com.android.vending:id/0_resource_name_obfuscated 세부정보",
  "9": "android.widget.ScrollView com.android.vending:id/0_resource_name_obfuscated",
  "10": "android.widget.TextView com.android.vending:id/0_resource_name_obfuscated 개발자 커리어 점프, 점핏(Jumpit)은 기술스택 기반 개발자 채용 서비스입니다.  점핏에서 기술스택으로 간편하게 입사지원하고 기업정보부터 최신 IT 트랜드까지 한번에 확인하세요!  # 프로필 = 당신의 이력서 - 더이상 글짓기로 골치썩지 마세요~    기술스택으로 쉽고 빠르게 이력서를 완성해보세요.  # IT 트렌드 콜렉션 - 요즘 개발자들이 즐겨보는 컨텐츠는 무엇이 있을까?   핫한 개발 유튜버, 개발도서 추천, 세미나 등 IT 트렌드를 간편하게 체크하세요  #당신이 묻지 못한 호기심 해결 - 이 기업은 어떻게 일하고 있을까?   기업의 대표 서비스, 기술 블로그, 개발환경 등 입사지원에 필요한 모든 정보를 알려드려요.  # 당신의 도움닫기, 점핏! - 당신의 커리어 점프를 축하해요.   점핏으로 입사지원하고 취업 성공하면 취업축하금 50만원에 점핏 론칭 기념으로 20만원을 더 드려요!   # 점핏에서 사용하는 접근권한 안내 선택적 접근 권한은 해당 기능을 사용할 때 허용이 필요하며, 비허용시에도 해당 기능 외 서비스 이용이 가능합니다.  [선택 접근 권한] - 저장 공간(사진, 미디어, 파일), 파일 및 미디어: 이력서 내 사진 및 첨부파일 등록 - 알림: 앱에서 제공하는 각종 알림 수신  _    점핏 고객센터 - 연락처 : 02-2025-2733 (평일 09:00 - 18:00, 주말·공휴일 휴무) - 이메일 : help@jumpit.co.kr ---- 개발자 연락처 : 02-2025-4733",
}

data5 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.View",
  "3": "android.view.View",
  "4": "android.view.View",
  "5": "android.widget.Button",
  "6": "android.view.View",
  "7": "android.widget.TextView  주문내역",
  "8": "android.view.View",
  "9": "android.view.View",
  "10": "android.widget.Button",
  "11": "android.view.View",
  "47": "android.view.View",
  "48": "android.widget.TextView  인기브랜드 위크 3천원 쿠폰을 드려요",
  "49": "android.view.View",
  "50": "android.widget.TextView  주문내역이 없어요.",
  "51": "android.widget.TextView  비회원 주문내역은 30일동안 확인 가능합니다. 배달의민족 앱을 삭제하시면 비회원 주문내역을 확인할 수 없습니다.",
  "52": "android.widget.ListView",
  "53": "android.view.View",
  "54": "android.view.View",
  "55": "android.view.View",
  "56": "android.widget.TextView  재주문 많은 가게 추천해요",
  "57": "android.widget.Button  광고",
  "58": "android.view.View",
  "59": "android.widget.TextView  광고상품 영역으로 브랜드명은 음식점 상호와 다를 수 있습니다.",
  "60": "android.widget.ListView",
  "61": "android.view.View",
  "62": "android.view.View",
  "63": "android.view.View",
  "64": "android.view.View",
  "65": "android.widget.Button  옥수동 묵은지 김치찜 성동점 5.0 배달49~64분 배달팁500원~",
  "66": "android.view.View",
  "67": "android.view.View",
  "68": "android.widget.Button  인생대패 4.3 배달31~46분 배달팁4,000원",
  "69": "android.view.View",
  "70": "android.view.View",
  "71": "android.widget.Button  곱도리탕전문점 본점 4.9 배달40~55분 배달팁1,000원~",
  "72": "android.view.View",
  "73": "android.view.View",
  "74": "android.widget.Button  매운녀석들 본점 4.8 배달50~65분 배달팁3,000원",
  "75": "android.view.View",
  "76": "android.view.View",
  "77": "android.widget.Button  열짱닭발 동대문본점 4.6 배달50~65분 배달팁2,500원",
}

data6 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.View",
  "3": "android.view.View",
  "4": "android.view.View",
  "5": "android.widget.Button",
  "6": "android.widget.Button",
  "7": "android.view.View",
  "8": "android.view.View",
  "9": "android.widget.Button",
  "10": "android.view.View",
  "11": "android.view.View",
  "12": "android.widget.Button",
  "13": "android.view.ViewGroup",
  "14": "android.view.View",
  "15": "android.widget.Button",
  "16": "android.view.View",
  "17": "androidx.recyclerview.widget.RecyclerView com.sampleapp:id/recyclerView",
  "18": "android.widget.RelativeLayout com.sampleapp:id/indicatorContainer",
  "19": "android.widget.TextView com.sampleapp:id/positionTextView 2 / 23",
  "20": "androidx.viewpager.widget.ViewPager com.sampleapp:id/viewPager",
  "21": "android.widget.FrameLayout",
  "22": "android.widget.FrameLayout com.sampleapp:id/bannerImageView",
  "23": "androidx.recyclerview.widget.RecyclerView com.sampleapp:id/categoryBannerRecyclerView",
  "24": "android.view.ViewGroup",
  "25": "android.view.ViewGroup",
  "26": "android.view.ViewGroup",
  "27": "android.view.ViewGroup",
  "28": "androidx.recyclerview.widget.RecyclerView com.sampleapp:id/mainCategoryRecyclerView",
  "29": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "30": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "31": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "32": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "33": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "34": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "35": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "36": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "37": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "38": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "39": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "40": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "41": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "42": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "43": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "44": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "45": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "46": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "47": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "48": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "49": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "50": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "51": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "52": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "53": "android.widget.ImageView com.sampleapp:id/iconImageView",
  "54": "android.view.ViewGroup",
  "55": "android.view.View",
  "56": "android.widget.TextView com.sampleapp:id/searchButton 검색",
  "57": "android.widget.TextView com.sampleapp:id/favoriteButton 찜",
  "58": "android.widget.ImageView com.sampleapp:id/homeButton",
  "59": "android.widget.TextView com.sampleapp:id/orderHistoryButton 주문내역",
  "60": "android.widget.TextView com.sampleapp:id/myBaeminButton my배민",
}

data7 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.View",
  "3": "android.view.View",
  "4": "android.view.View",
  "5": "android.widget.Button",
  "6": "android.view.View",
  "7": "android.widget.TextView  장바구니",
  "8": "android.view.View",
  "9": "android.view.View",
  "10": "android.widget.Button",
  "11": "android.widget.Button",
  "12": "android.widget.HorizontalScrollView com.sampleapp:id/cartBaeminTabLayout",
  "13": "android.widget.LinearLayout",
  "14": "android.widget.TextView  배달/포장",
  "15": "android.widget.LinearLayout",
  "16": "android.widget.TextView  B마트/스토어",
  "17": "android.widget.LinearLayout",
  "18": "android.widget.TextView  대용량특가",
  "19": "android.widget.LinearLayout",
  "20": "android.widget.TextView  전국별미",
  "21": "androidx.viewpager.widget.ViewPager com.sampleapp:id/cartViewPager",
  "22": "android.webkit.WebView com.sampleapp:id/webview",
}

data8 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.View",
  "3": "android.view.View",
  "4": "android.view.View",
  "5": "android.widget.Button",
  "6": "android.view.View",
  "7": "android.widget.TextView  리뷰",
  "8": "android.view.View",
  "9": "android.view.View",
  "10": "android.widget.Button",
  "11": "android.view.View",
  "12": "android.view.View",
  "13": "android.widget.Button",
  "14": "androidx.recyclerview.widget.RecyclerView com.sampleapp:id/contentRecyclerview",
  "15": "android.view.ViewGroup com.sampleapp:id/topRatingLayout",
  "16": "android.widget.TextView com.sampleapp:id/recentRatingTextView 4.9",
  "17": "android.widget.TextView com.sampleapp:id/rating5TitleTextView 5점",
  "18": "android.widget.ProgressBar com.sampleapp:id/rating5ProgressBar",
  "19": "android.widget.TextView com.sampleapp:id/rating5ReviewCountTextView 612",
  "20": "android.widget.TextView com.sampleapp:id/rating4TitleTextView 4점",
  "21": "android.widget.ProgressBar com.sampleapp:id/rating4ProgressBar",
  "22": "android.widget.TextView com.sampleapp:id/rating4ReviewCountTextView 12",
  "23": "android.widget.TextView com.sampleapp:id/rating3TitleTextView 3점",
  "24": "android.widget.ProgressBar com.sampleapp:id/rating3ProgressBar",
  "25": "android.widget.TextView com.sampleapp:id/rating3ReviewCountTextView 6",
  "26": "android.widget.TextView com.sampleapp:id/rating2TitleTextView 2점",
  "27": "android.widget.ProgressBar com.sampleapp:id/rating2ProgressBar",
  "28": "android.widget.TextView com.sampleapp:id/rating2ReviewCountTextView 1",
  "29": "android.widget.TextView com.sampleapp:id/rating1TitleTextView 1점",
  "30": "android.widget.ProgressBar com.sampleapp:id/rating1ProgressBar",
  "31": "android.widget.TextView com.sampleapp:id/rating1ReviewCountTextView 3",
  "32": "android.view.View com.sampleapp:id/chartView",
  "33": "android.widget.Button",
  "34": "android.widget.Button",
  "35": "android.widget.TextView com.sampleapp:id/latestReviewCountText 최근 리뷰 634개",
  "36": "android.widget.TextView com.sampleapp:id/ceoReplyTextView 사장님댓글 640개",
  "37": "android.widget.TextView com.sampleapp:id/reviewReportDescriptionTextView 모든 리뷰는 검토 후 보여드려요",
  "38": "android.widget.TextView com.sampleapp:id/reviewReportShowPopupButton 자세히",
  "39": "android.view.View",
  "40": "android.view.View",
  "41": "android.view.View",
  "42": "android.widget.TextView  최신순",
  "43": "android.view.View",
  "44": "android.widget.CheckBox",
  "45": "android.view.View",
  "46": "android.widget.TextView  사진 리뷰만 보기",
  "47": "android.widget.CheckBox",
}

data9 = {
  "1": "android.widget.FrameLayout",
  "2": "android.widget.FrameLayout",
  "3": "android.widget.ImageButton com.sec.android.app.sbrowser:id/customtab_close",
  "4": "android.widget.ImageButton com.sec.android.app.sbrowser:id/security_icon",
  "5": "android.widget.TextView com.sec.android.app.sbrowser:id/title_bar_text 네이버 : 로그인",
  "6": "android.widget.TextView com.sec.android.app.sbrowser:id/url_bar_text https://nid.naver.com/oauth2.0/authorize?network=wifi&inapp_view=custom_tab&client_id=gIarItKH0yF83oDoqFjQ&oauth_os=android&locale=ko_KR&version=android-5.6.0&state=cjn8i88segnrflipnd1pv7kvn6&response_type=code&redirect_uri=com.sampleapp",
  "7": "android.widget.Button com.sec.android.app.sbrowser:id/option_share 공유",
  "8": "android.widget.ImageButton com.sec.android.app.sbrowser:id/option_menu",
}

data10 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.View",
  "3": "android.view.View",
  "4": "android.widget.ScrollView",
  "5": "android.view.View",
  "6": "android.view.View",
  "7": "android.view.View",
  "8": "android.view.View",
  "9": "android.view.View",
  "10": "android.view.View",
  "11": "android.view.View",
  "12": "android.view.View",
  "13": "android.view.View",
  "14": "android.view.View",
  "15": "android.view.View",
  "16": "android.view.View",
  "17": "android.view.View",
  "18": "android.view.View",
  "19": "android.view.View",
  "20": "android.view.View",
  "21": "android.view.View",
  "22": "android.view.View",
  "23": "android.view.View",
  "24": "android.view.View",
  "25": "android.view.View",
  "26": "android.view.View",
  "27": "android.widget.Button",
}

data11 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.ViewGroup",
  "3": "android.widget.FrameLayout com.sampleapp:id/headerImageview",
  "4": "android.widget.FrameLayout com.sampleapp:id/createGroupOrderTooltipView",
  "5": "android.widget.TextView com.sampleapp:id/bodyTextView 같이 먹고 싶은 멤버와 함께 골라요",
  "6": "android.widget.ImageView com.sampleapp:id/closeButton",
}

data12 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.ViewGroup",
  "3": "android.view.View",
  "4": "android.view.View",
  "5": "android.view.View",
  "6": "android.widget.Button",
  "7": "android.widget.EditText",
  "8": "android.widget.TextView  검색어를 입력해주세요",
  "9": "android.view.View",
  "10": "android.view.View",
  "11": "android.widget.Button",
  "12": "androidx.recyclerview.widget.RecyclerView com.sampleapp:id/searchHomeRecyclerView",
  "13": "android.widget.TextView com.sampleapp:id/curationTitleTextView 요즘 우리동네 인기 맛집",
  "14": "android.widget.TextView com.sampleapp:id/curationTitleAdTextView 광고",
  "15": "android.widget.ImageView com.sampleapp:id/curationTitleQuestionButton",
  "16": "androidx.recyclerview.widget.RecyclerView com.sampleapp:id/shopListHorizontalRecyclerView",
  "17": "android.view.View",
  "18": "android.view.View",
  "19": "android.view.View",
  "20": "android.view.View",
  "21": "android.view.View",
  "22": "android.view.View",
  "23": "android.widget.TextView  4.9",
  "24": "android.view.ViewGroup",
  "25": "android.widget.TextView  배달 17~38분",
  "26": "android.view.ViewGroup",
  "27": "android.widget.TextView  배달팁 1,540원~1,640원",
  "28": "android.view.View",
  "29": "android.view.View",
  "30": "android.view.View",
  "31": "android.view.View",
  "32": "android.view.View",
  "33": "android.view.View",
  "34": "android.view.View",
  "35": "android.view.View",
  "36": "android.widget.TextView  4.9",
  "37": "android.view.ViewGroup",
  "38": "android.widget.TextView  배달 18~38분",
  "39": "android.view.ViewGroup",
  "40": "android.widget.TextView  배달팁 1,540원~2,440원",
  "41": "android.view.View",
  "42": "android.view.View",
  "43": "android.view.View",
  "44": "android.view.View",
  "45": "android.view.View",
  "46": "android.view.View",
  "47": "android.view.View",
  "48": "android.view.View",
  "49": "android.widget.TextView  5.0",
  "50": "android.view.ViewGroup",
  "51": "android.widget.TextView  배달 32~47분",
  "52": "android.view.ViewGroup",
  "53": "android.widget.TextView  배달팁 3,080원",
  "54": "android.view.View",
  "55": "androidx.viewpager.widget.ViewPager com.sampleapp:id/viewPager",
  "56": "android.widget.FrameLayout",
  "57": "android.widget.FrameLayout com.sampleapp:id/bannerImageView",
  "58": "android.widget.TextView com.sampleapp:id/titleTextView 가장 많이 검색하고 있어요",
  "59": "android.widget.TextView com.sampleapp:id/baseTimeTextView 04.27 23:00 기준",
  "60": "androidx.recyclerview.widget.RecyclerView com.sampleapp:id/upperRankKeywordRecyclerView",
  "61": "android.view.ViewGroup",
  "62": "android.widget.ImageView com.sampleapp:id/rankingImageView",
  "63": "android.widget.TextView com.sampleapp:id/keywordTextView 육회",
  "64": "androidx.recyclerview.widget.RecyclerView com.sampleapp:id/lowerRankKeywordRecyclerView",
  "65": "android.view.ViewGroup",
  "66": "android.widget.TextView com.sampleapp:id/rankingTextView 6",
  "67": "android.widget.TextView com.sampleapp:id/keywordTextView 햄버거",
}

data13 = {
  "1": "android.widget.FrameLayout",
  "2": "android.view.ViewGroup com.android.vending:id/0_resource_name_obfuscated",
  "3": "android.widget.FrameLayout com.android.vending:id/0_resource_name_obfuscated",
  "4": "android.widget.ScrollView com.android.vending:id/0_resource_name_obfuscated",
  "5": "android.view.ViewGroup",
  "6": "android.widget.ImageButton",
  "7": "android.widget.TextView com.android.vending:id/0_resource_name_obfuscated 점핏 - 개발자 커리어 점프",
  "8": "android.widget.TextView com.android.vending:id/0_resource_name_obfuscated 세부정보",
  "9": "android.widget.ScrollView com.android.vending:id/0_resource_name_obfuscated",
  "10": "android.widget.TextView com.android.vending:id/0_resource_name_obfuscated 개발자 커리어 점프, 점핏(Jumpit)은 기술스택 기반 개발자 채용 서비스입니다.  점핏에서 기술스택으로 간편하게 입사지원하고 기업정보부터 최신 IT 트랜드까지 한번에 확인하세요!  # 프로필 = 당신의 이력서 - 더이상 글짓기로 골치썩지 마세요~    기술스택으로 쉽고 빠르게 이력서를 완성해보세요.  # IT 트렌드 콜렉션 - 요즘 개발자들이 즐겨보는 컨텐츠는 무엇이 있을까?   핫한 개발 유튜버, 개발도서 추천, 세미나 등 IT 트렌드를 간편하게 체크하세요  #당신이 묻지 못한 호기심 해결 - 이 기업은 어떻게 일하고 있을까?   기업의 대표 서비스, 기술 블로그, 개발환경 등 입사지원에 필요한 모든 정보를 알려드려요.  # 당신의 도움닫기, 점핏! - 당신의 커리어 점프를 축하해요.   점핏으로 입사지원하고 취업 성공하면 취업축하금 50만원에 점핏 론칭 기념으로 20만원을 더 드려요!   # 점핏에서 사용하는 접근권한 안내 선택적 접근 권한은 해당 기능을 사용할 때 허용이 필요하며, 비허용시에도 해당 기능 외 서비스 이용이 가능합니다.  [선택 접근 권한] - 저장 공간(사진, 미디어, 파일), 파일 및 미디어: 이력서 내 사진 및 첨부파일 등록 - 알림: 앱에서 제공하는 각종 알림 수신  _    점핏 고객센터 - 연락처 : 02-2025-2733 (평일 09:00 - 18:00, 주말·공휴일 휴무) - 이메일 : help@jumpit.co.kr ---- 개발자 연락처 : 02-2025-4733",
}

action1 = "xx를 클릭해줘"
action2 = "xx를 찾아서 xxx을 입력해줘"
action4 = "뒤로가줘"
action5 = "홈으로 돌아가줘"
action6 = "오른쪽으로 스와이프해줘"
action7 = "왼쪽으로 스와이프해줘"
action8 = "아래로 스와이프해줘"
action9 = "위로 스와이프해줘"


completion1 = "key = 2, function = find_by_id_touch"
completion2 = "key = 10, function = find_by_id_touch"
completion3 = "key = 1, function = find_by_id_touch"
completion4 = "key = 53, function = find_by_id_touch"
completion5 = "key = 21, function = find_by_id_touch"
completion6 = "key = 카메라, function = find_by_text_touch"
completion7 = "key = 배달의 민족, function = find_by_text_touch"
completion8 = "key = 버튼, function = find_by_text_touch"
completion9 = "key = 검색, function = find_by_text_touch"
completion10 = "key = 세부정보, function = find_by_text_touch"
completion11 = "key = 육회, function = find_by_text_touch"
completion12 = "key = None, function = back"
completion13 = "key = None, function = home"
completion14 = "key = None, function = swipe_left_to_right"
completion15 = "key = None, function = swipe_right_to_left"
completion16 = "key = None, function = swipe_up_to_down"
completion17 = "key = None, function = swipe_down_to_up"
completion18 = "key = 4, text = 치킨 function = find_by_id_touch_type"
completion19 = "key = 3, text = 날씨 function = find_by_id_touch_type"
completion20 = "key = 61, text = 가나다라마 function = find_by_id_touch_type"
completion21 = "key = 12, text = 아디다스 function = find_by_id_touch_type"


data_list = [data1, data2, data3, data4, data5, data6, data7, data8, data9, data10, data11, data12, data13, data1, data2, data3, data4, data5, data6, data7, data8]
action_list = [action1, action1, action1, action1, action1, action1, action1, action1, action1, action1, action1, action4, action5, action6, action7, action8, action9, action2, action2, action2, action2]
completion_list = [completion1, completion2, completion3, completion4, completion5, completion6, completion7, completion8, completion9, completion10, completion11, completion12, completion13, completion14, completion15, completion16, completion17, completion18, completion19, completion20, completion21]


def make_fine_tunes_jsonl():
  with jsonlines.open('example.jsonl', mode='w') as writer:
    for data, action, completion in zip(data_list, action_list, completion_list):
      prompt = f"You must respond only once for each appropriate key, text, or function if present.\n ui hierarchy: {data}, action: {action}"
      writer.write({"prompt": prompt, "completion": completion})

# make_fine_tunes_jsonl()
# fine_tunes()
# upload_response = upload_file()
# create_model(upload_response)
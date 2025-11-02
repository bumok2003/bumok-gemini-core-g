import streamlit as st
from streamlit_oauth import OAuth2
import yaml
import requests
from google import genai

# --- [1] 환경 설정 및 키 로드 ---
# Streamlit Secrets에서 API 키 로드
try:
    GEMINI_API_KEY = st.secrets['GEMINI_API_KEY']
    GOOGLE_CLIENT_ID = st.secrets['GOOGLE_CLIENT_ID']
    GOOGLE_CLIENT_SECRET = st.secrets['GOOGLE_CLIENT_SECRET']
    KAKAO_CLIENT_ID = st.secrets['KAKAO_CLIENT_ID']
except KeyError:
    st.error("⚠️ API/Client 키가 Streamlit Secrets에 설정되지 않았습니다. Secrets을 확인해주세요.")
    st.stop()

# --- [2] Streamlit 페이지 설정 ---
st.set_page_config(
    page_title="AI친구, 코어G",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- [3] OAuth2 설정 (이 부분이 수정됨) ---

# OAuth 제공자 설정
oauth_providers = [
    {
        'provider': 'google',
        'icon': 'Google',
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'userinfo_url': 'https://www.googleapis.com/oauth2/v3/userinfo',
        'scopes': ['openid', 'email', 'profile'],
        'redirect_uri': st.secrets['STREAMLIT_URL'] # 배포된 앱 URL (자동으로 설정됨)
    },
    {
        'provider': 'kakao',
        'icon': 'Kakaotalk',
        'client_id': KAKAO_CLIENT_ID,
        'client_secret': '', # 카카오는 클라이언트 시크릿을 사용하지 않음
        'authorize_url': 'https://kauth.kakao.com/oauth/authorize',
        'token_url': 'https://kauth.kakao.com/oauth/token',
        'userinfo_url': 'https://kapi.kakao.com/v2/user/me',
        'scopes': ['profile_nickname', 'account_email'],
        'redirect_uri': st.secrets['STREAMLIT_URL'] # 배포된 앱 URL
    }
]

# OAuth2 객체 초기화
# ************ 오류가 발생한 Line 57 근처 수정 ************
# client_id 인자를 Secrets에서 가져온 실제 Google Client ID로 설정하여 라이브러리의 요구사항을 만족시킵니다.
oauth = OAuth2(
    client_id=GOOGLE_CLIENT_ID, # 이전 오류 발생 지점 수정
    client_secret=GOOGLE_CLIENT_SECRET,
    providers=oauth_providers
)
# ********************************************************


# --- [4] 사용자 인증 및 정보 로드 ---
if 'user_info' not in st.session_state:
    try:
        # 로그인 시도 (url에서 code 파라미터를 확인)
        user_info, provider = oauth.get_user_info()

        if user_info:
            st.session_state['user_info'] = user_info
            st.session_state['logged_in'] = True
        else:
            st.session_state['logged_in'] = False
    except Exception as e:
        # 로그인 실패 시 (예: 토큰 만료, 잘못된 설정 등)
        st.session_state['logged_in'] = False
        # st.warning(f"로그인 오류 발생: {e}") # 개발 시에만 주석 해제

# --- [5] UI 렌더링 ---

if st.session_state.get('logged_in'):
    # 사용자 정보와 함께 챗봇 메인 화면 표시
    st.sidebar.success(f"로그인: {st.session_state['user_info'].get('email', '사용자')}")

    # Gemini 클라이언트 초기화
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 챗봇 제목
    st.title("AI친구, 코어G")
    st.caption("AI 기반 교육용 챗봇입니다.")

    # 챗봇 로직 (기존 챗봇 코드)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("질문을 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Gemini API 호출
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            st.markdown(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})

else:
    # 로그인 버튼 표시
    st.title("AI친구, 코어G")
    st.markdown("### 서비스 이용을 위해 로그인해주세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        oauth.login(oauth_providers[0]['provider'], text='구글 로그인')
    with col2:
        oauth.login(oauth_providers[1]['provider'], text='카카오 로그인')
    
    st.info("로그인 후 교육용 AI 챗봇 서비스를 이용할 수 있습니다.")

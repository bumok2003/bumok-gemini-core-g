import streamlit as st
from google import genai
import yaml
import requests
# from streamlit_oauth import OAuth2 # 이 줄은 이제 필요 없으므로 삭제합니다.

# --- 1. 환경 설정 및 키 로드 ---
# Streamlit Secrets에서 API 키 로드
try:
    GEMINI_API_KEY = st.secrets['GEMINI_API_KEY']
except KeyError:
    st.error("⚠️ Gemini API 키가 Streamlit Secrets에 설정되지 않았습니다. Secrets을 확인해주세요.")
    st.stop()

# Gemini 클라이언트 초기화
client = genai.Client(api_key=GEMINI_API_KEY)

# --- 2. Streamlit 페이지 설정 ---
st.set_page_config(
    page_title="AI친구, 코어G (로그인 없이 바로 사용)",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 3. 챗봇 UI 렌더링 ---

st.title("AI친구, 코어G")
st.caption("✨ 로그인 없이 바로 사용 가능한 교육용 AI 챗봇입니다.")

# 챗 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Gemini API 호출
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Gemini API 호출 오류가 발생했습니다: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "죄송합니다. API 호출 중 오류가 발생했습니다."})

# --- 4. Sidebar 정보 ---
st.sidebar.markdown("### ⚙️ 설정 정보")
st.sidebar.markdown("현재 버전은 로그인 기능 없이 **GEMINI\_API\_KEY**만 사용하여 구동됩니다.")
st.sidebar.markdown("---")
# OAuth 관련 라이브러리 설정 정보는 삭제되었습니다.

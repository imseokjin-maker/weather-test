import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import random

# 1. 페이지 설정
st.set_page_config(page_title="날씨 안내 시범 서비스", page_icon="☀️")

# 2. 보안 정보 로드 및 AI 설정
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('models/gemini-flash-latest')
except Exception as e:
    st.error(f"설정 불러오기 실패: {e}")

# 3. 세션 상태 초기화 (그룹 할당 및 프레이밍 메시지 설정)
if 'group' not in st.session_state:
    # 랜덤하게 그룹 결정
    st.session_state.group = random.choice(["Positive", "Negative"])
    st.session_state.step = 'chat'
    st.session_state.completed_chat = False

# --- 1단계: AI 날씨 대화 화면 ---
if st.session_state.step == 'chat':
    st.title("☀️ 오늘의 날씨 안내 서비스")
    
    # [수정 포인트] 교수님이 요청하신 연구용 프레이밍 메시지 출력
    st.write("---")
    if st.session_state.group == "Positive":
        st.success("✨ **긍정메시지-AI에게 날씨를 물어보면 빠르게 필요한 정보를 얻을 수 있습니다.**")
    else:
        st.error("⚠️ **부정메시지-AI에게 날씨를 묻지 않으면 필요한 정보를 확인할 수 없습니다.**")
    st.write("---")

    question = st.text_input("위 내용을 확인하신 후, 날씨에 대해 물어보세요.", placeholder="예: 오늘 서울 날씨 어때?")
    
    if st.button("AI 답변 듣기"):
        if question:
            try:
                # 프롬프트 구성
                prompt = f"당신은 {st.session_state.group} 톤의 날씨 비서입니다. 실제 데이터는 없으니 서울 날씨가 맑다고 가정하고 한 문장으로 대답하세요."
                
                # 답변 생성 실행
                response = model.generate_content(prompt)
                
                st.info(f"🤖 AI 답변: {response.text}")
                st.session_state.completed_chat = True # 답변 확인 체크
                
            except Exception as e:
                st.error(f"AI 호출 오류가 발생했습니다: {e}")
        else:
            st.warning("질문을 먼저 입력해주세요.")

    # 답변을 한 번이라도 들었다면 설문 이동 버튼 표시
    if st.session_state.completed_chat:
        st.write("")
        if st.button("답변 확인 완료 (설문 이동) ➡️"):
            st.session_state.step = 'survey'
            st.rerun()

# --- 2단계: 설문 및 저장 화면 ---
elif st.session_state.step == 'survey':
    st.title("📋 서비스 만족도 조사")
    st.subheader("연구 데이터 수집을 위한 마지막 단계입니다.")
    
    st.write("방금 경험하신 날씨 안내 서비스에 대해 솔직한 의견을 남겨주세요.")
    
    # 구글 폼 링크 (교수님의 고유 번호 유지)
    # 알려주신 보안 안내창 방지를 위해 usp=pp_url& 부분은 제거한 최적화 링크입니다.
    base_url = "https://docs.google.com/forms/d/e/1FAIpQLSdCiF4lzxN5NRaOWIrgLsW9Tphs99FmtS6mLXAlCEKs75udXg/viewform?entry.41790104="
    
    # 자동으로 Positive/Negative를 붙여서 주소 완성
    final_form_url = base_url + st.session_state.group
    
    st.info(f"""
    **💡 중요 안내**
    - 현재 교수님은 **{st.session_state.group}** 그룹으로 할당되었습니다.
    - 아래 버튼을 누르면 설문지가 열리며, 이 그룹 정보는 자동으로 입력됩니다.
    - 첫 페이지에서 본인의 그룹을 확인하신 후 바로 **[다음]**을 눌러주세요.
    """)
    
    # 설문지 연결 버튼
    st.link_button("🚀 설문 참여하고 완료하기", final_form_url, use_container_width=True)
    
    st.divider()
    
    if st.button("처음으로 돌아가기 (데이터 초기화)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(page_title="날씨 안내 시범 서비스", page_icon="☀️")

# 2. 보안 정보 로드 및 AI 설정
try:
    # Secrets에서 값을 가져옴
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    SHEET_URL = st.secrets["SHEET_URL"]
    
    # AI 모델 설정 (가장 안정적인 모델명 사용)
    genai.configure(api_key=GEMINI_KEY)
    #model = genai.GenerativeModel('gemini-1.5-flash')
    model = genai.GenerativeModel('models/gemini-flash-latest')
except Exception as e:
    st.error(f"설정 불러오기 실패: {e}")
    st.info("Streamlit Cloud의 Settings > Secrets에 키가 정확히 입력되었는지 확인하세요.")

# 3. 세션 상태 초기화 (그룹 할당)
if 'group' not in st.session_state:
    import random
    st.session_state.group = random.choice(["Positive", "Negative"])
    st.session_state.step = 'chat'

# --- 1단계: AI 날씨 대화 화면 ---
if st.session_state.step == 'chat':
    st.title("☀️ 오늘의 날씨 안내 서비스")
    
    # 프레이밍 메시지
    if st.session_state.group == "Positive":
        st.success("✨ 안녕하세요! 당신의 기분 좋은 하루를 돕는 똑똑한 날씨 비서입니다.")
    else:
        st.error("⚠️ 주의: 이 시스템은 테스트용이며 날씨 정보가 정확하지 않을 수 있습니다.")

    question = st.text_input("날씨에 대해 물어보세요 (예: 오늘 서울 날씨 어때?)", placeholder="여기에 입력하세요...")
    
    if st.button("AI 답변 듣기"):
        if question:
            try:
                # 프롬프트 구성 (에러 방지를 위해 간단하게 작성)
                prompt = f"당신은 {st.session_state.group} 톤의 날씨 비서입니다. 실제 데이터는 없으니 서울 날씨가 맑다고 가정하고 한 문장으로 대답하세요."
                
                # 답변 생성 실행
                response = model.generate_content(prompt)
                
                st.write("---")
                st.info(response.text)
                st.session_state.completed_chat = True # 답변 확인 체크
                
            except Exception as e:
                st.error(f"AI 호출 오류가 발생했습니다. API 키가 유효한지 확인하세요. (오류 내용: {e})")
        else:
            st.warning("질문을 먼저 입력해주세요.")

    # 답변을 한 번이라도 들었다면 설문 이동 버튼 표시
    if st.session_state.get('completed_chat'):
        if st.button("답변 확인 완료 (설문 이동)"):
            st.session_state.step = 'survey'
            st.rerun()

# --- 2단계: 설문 및 저장 화면 ---

elif st.session_state.step == 'survey':
    st.title("📋 서비스 만족도 조사")
    st.subheader("연구 데이터 수집을 위한 마지막 단계입니다.")
    
    st.write("방금 경험하신 날씨 안내 서비스에 대해 솔직한 의견을 남겨주세요.")
    
    # [설정] 교수님이 복사한 구글 폼 링크의 'entry' 번호와 등호(=)까지만 넣으세요.
    # 예: "https://docs.google.com/forms/d/e/.../viewform?usp=pp_url&entry.123456789="
    # 복사하신 링크 주소가 아래 예시와 다르다면 따옴표 안의 주소만 교체하시면 됩니다.
    base_url = "https://docs.google.com/forms/d/e/1FAIpQLSd_example_url/viewform?usp=pp_url&entry.20456123="
    
    # [로직] 현재 세션의 그룹(Positive 또는 Negative)을 주소 뒤에 자동으로 붙입니다.
    # 주의: 구글 폼의 옵션명과 st.session_state.group의 값이 대소문자까지 일치해야 합니다.
    final_form_url = base_url + st.session_state.group
    
    st.info("""
    **💡 안내사항**
    1. 아래 버튼을 누르면 설문지 페이지가 새 창으로 열립니다.
    2. 첫 번째 페이지의 '할당 그룹' 정보는 시스템이 자동으로 입력했으니 바로 **[다음]** 버튼을 눌러주세요.
    3. 모든 문항에 답변 후 **[제출]**을 눌러야 연구 참여가 완료됩니다.
    """)
    
    # 설문지 연결 버튼
    st.link_button("🚀 설문 참여하고 완료하기", final_form_url, use_container_width=True)
    
    st.divider()
    
    # 초기화 버튼
    if st.button("처음으로 돌아가기 (새로운 대화 시작)"):
        # 세션 상태 초기화 후 처음으로 이동
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()





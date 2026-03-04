import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(page_title="날씨 안내 시범 서비스", page_icon="☀️")

# 2. 보안 정보 로드 (Streamlit Cloud 설정에서 입력할 값들)
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    SHEET_URL = st.secrets["SHEET_URL"]
    genai.configure(api_key=GEMINI_KEY)
except:
    st.warning("⚠️ API 키 또는 시트 URL이 설정되지 않았습니다. (Advanced settings 확인 필요)")

# 3. 실험 그룹 할당 (처음 접속 시 한 번만 실행)
if 'group' not in st.session_state:
    import random
    st.session_state.group = random.choice(["Positive", "Negative"])
    st.session_state.step = 'chat'

# --- 단계별 화면 구성 ---

# [1단계: AI와 대화하기]
if st.session_state.step == 'chat':
    st.title("☀️ 오늘의 날씨 안내 서비스")
    
    if st.session_state.group == "Positive":
        st.success("✨ 안녕하세요! 당신의 기분 좋은 하루를 돕는 똑똑한 날씨 비서입니다.")
    else:
        st.error("⚠️ 주의: 이 시스템은 테스트용이며 날씨 정보가 정확하지 않을 수 있습니다.")

    question = st.text_input("날씨에 대해 물어보세요 (예: 오늘 날씨 어때?)")
    
    if st.button("AI 답변 듣기"):
        if question:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            # 실험용 페르소나 주입
            prompt = f"당신은 {st.session_state.group} 톤을 가진 날씨 비서입니다. 실제 데이터는 없으니 서울 날씨가 맑다고 가정하고 한 문장으로 대답하세요."
            response = model.generate_content(prompt)
            st.info(response.text)
            
            if st.button("답변 확인 완료 (설문 이동)"):
                st.session_state.step = 'survey'
                st.rerun()

# [2단계: 설문 및 저장]
elif st.session_state.step == 'survey':
    st.title("📋 서비스 만족도 조사")
    st.write("방금 경험하신 날씨 안내 서비스는 어떠셨나요?")
    
    rating = st.radio("만족도를 선택해주세요:", ["좋았음", "나빴음"])
    
    if st.button("최종 결과 제출하기"):
        # 구글 시트 연결 및 데이터 추가
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            # 기존 데이터 읽기 (URL 기반)
            existing_data = conn.read(spreadsheet=SHEET_URL)
            
            # 새 데이터 생성
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Group": st.session_state.group,
                "Rating": rating
            }])
            
            # 데이터 합치기 및 업데이트
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            
            st.balloons()
            st.success("✅ 결과가 안전하게 저장되었습니다! 협조해주셔서 감사합니다.")
        except Exception as e:

            st.error(f"저장 중 오류가 발생했습니다: {e}")

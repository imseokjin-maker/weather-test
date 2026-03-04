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
    st.write("방금 경험하신 날씨 안내 서비스는 어떠셨나요?")
    
    rating = st.radio("만족도를 선택해주세요:", ["좋았음", "나빴음"])
    
    if st.button("최종 결과 제출하기"):
        try:
            # 구글 시트 연결
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # 기존 데이터 읽기
            existing_data = conn.read(spreadsheet=SHEET_URL, usecols=[0,1,2])
            
            # 새 데이터 한 줄 만들기
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Group": st.session_state.group,
                "Rating": rating
            }])
            
            # 데이터 합쳐서 업데이트
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            
            st.balloons()
            st.success("✅ 결과가 구글 시트에 안전하게 저장되었습니다! 협조해주셔서 감사합니다.")
            
            if st.button("처음으로 돌아가기"):
                del st.session_state['group']
                st.session_state.step = 'chat'
                st.rerun()
                
        except Exception as e:
            st.error(f"저장 중 오류가 발생했습니다: {e}")
            st.info("구글 시트의 공유 설정이 '편집자'로 되어 있는지 확인하세요.")



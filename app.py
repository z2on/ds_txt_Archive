import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. 프로그램 기본 설정
st.set_page_config(page_title="텍스트 아카이브", layout="wide")
st.title("📂 텍스트 아카이브 (Public Search)")

# 2. 구글 시트 연결 https://docs.google.com/spreadsheets/d/19I-TJMTVNS_otgXyrggEclKBcrSrlsVpLS8f_a1qjJQ/edit?usp=sharing
# 실제 배포 시에는 보안을 위해 'secrets' 기능을 써야 하지만, 지금은 연습용으로 직접 넣습니다.
SHEET_URL = "https://docs.google.com/spreadsheets/d/19I-TJMTVNS_otgXyrggEclKBcrSrlsVpLS8f_a1qjJQ/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("구글 시트 연결 설정이 필요합니다.")

# 3. 윈도우 메모장 파일 읽기 함수 (한글 깨짐 방지)
def decode_file(file):
    raw = file.read()
    for encoding in ['utf-8', 'cp949']: # 윈도우 메모장은 보통 이 두 가지입니다.
        try:
            return raw.decode(encoding)
        except:
            continue
    return raw.decode('utf-8', errors='ignore')

# 4. 관리자 업로드 기능 (비밀번호 잠금)
with st.sidebar:
    st.header("🔒 관리자 메뉴")
    pw = st.text_input("업로드 비밀번호", type="password")
    if pw == "1234": # 원하는 비밀번호로 바꾸세요
        files = st.file_uploader("메모장(.txt) 업로드", type='txt', accept_multiple_files=True)
        if st.button("시트에 저장하기"):
            if files:
                # 기존 데이터 가져오기
                df_old = conn.read(spreadsheet=SHEET_URL)
                new_entries = []
                for f in files:
                    content = decode_file(f)
                    new_entries.append({
                        "title": f.name,
                        "content": content,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                df_new = pd.concat([df_old, pd.DataFrame(new_entries)], ignore_index=True)
                # 시트 업데이트
                conn.update(spreadsheet=SHEET_URL, data=df_new)
                st.success("업로드 완료!")
                st.rerun()

# 5. 메인 화면: 검색 기능 (외부인용)
search = st.text_input("🔍 찾고 싶은 키워드를 입력하세요")

try:
    data = conn.read(spreadsheet=SHEET_URL)
    if not data.empty:
        # 검색 필터링
        if search:
            res = data[data['title'].str.contains(search, na=False) | data['content'].str.contains(search, na=False)]
        else:
            res = data.iloc[::-1].head(10) # 최신순 10개
        
        for _, row in res.iterrows():
            with st.expander(f"📄 {row['title']} ({row['date']})"):
                st.text_area("내용", value=row['content'], height=200, disabled=True)
    else:
        st.write("아직 저장된 내용이 없습니다.")
except:
    st.write("데이터를 불러오는 중입니다...")
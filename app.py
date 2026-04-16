import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# 1. 프로그램 설정
st.set_page_config(page_title="나스 텍스트 아카이브", layout="wide")
st.title("📂 NAS 텍스트 아카이브")

# 2. 데이터베이스 연결 (나스 안의 같은 폴더에 저장됨)
DB_PATH = 'archive.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS docs 
                 (title TEXT, content TEXT, date TEXT)''')
    conn.commit()
    return conn

def decode_file(file):
    raw = file.read()
    for encoding in ['utf-8', 'cp949']:
        try: return raw.decode(encoding)
        except: continue
    return raw.decode('utf-8', errors='ignore')

# 3. 관리자 메뉴 (사이드바)
with st.sidebar:
    st.header("🔒 관리자 메뉴")
    pw = st.text_input("업로드 비밀번호", type="password")
    if pw == "ds2233":
        files = st.file_uploader("메모장 업로드", type='txt', accept_multiple_files=True)
        if st.button("나스에 저장하기"):
            if files:
                conn = init_db()
                c = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                for f in files:
                    content = decode_file(f)
                    c.execute("INSERT INTO docs (title, content, date) VALUES (?, ?, ?)", 
                              (f.name, content, now))
                conn.commit()
                conn.close()
                st.success("나스 저장 완료!")
                st.rerun()

# 4. 검색 및 조회 (메인)
search = st.text_input("🔍 키워드 검색")
conn = init_db()

if search:
    query = f"%{search}%"
    df = pd.read_sql("SELECT * FROM docs WHERE title LIKE ? OR content LIKE ? ORDER BY date DESC", 
                     conn, params=(query, query))
else:
    df = pd.read_sql("SELECT * FROM docs ORDER BY date DESC LIMIT 20", conn)

if not df.empty:
    for _, row in df.iterrows():
        with st.expander(f"📄 {row['title']} ({row['date']})"):
            st.text_area("내용", value=row['content'], height=250, disabled=True)
else:
    st.info("데이터가 없습니다.")

conn.close()

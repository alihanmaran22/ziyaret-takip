import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Sayfa ayarları
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem;}
    h1, h2, h3 {margin-top: 0.1rem; margin-bottom: 0.1rem;}
    div.stButton > button {width: 100%; padding: 0.2rem 0.4rem; font-size: 13px; height: auto;}
    </style>
""", unsafe_allow_html=True)

# Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    # Session State
    if 'ziyaret_gecmisi' not in st.session_state:
        st.session_state.ziyaret_gecmisi = []

    # Menü
    menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?"])
    bugun_str = datetime.now().strftime("%d/%m/%Y")

    st.title("💊 Nextpharma Ziyaret Takip")

    if menu == "Ziyaret Girişi":
        hastane = st.selectbox("Hastane Seç:", ['Seçiniz...'] + sorted(df['KURUM'].unique().tolist()))
        
        if hastane != 'Seçiniz...':
            df_hastane = df[df['KURUM'] == hastane]
            for i, row in df_hastane.iterrows():
                if st.button(f"{row['DOKTOR']} - {row['İHTİSAS']}", key=f"z_{i}"):
                    st.session_state.ziyaret_gecmisi.append({
                        "Doktor": row['DOKTOR'], 
                        "Kurum": row['KURUM'], 
                        "Tarih": bugun_str,
                        "Saat": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()

    elif menu == "Bugün Ne Yaptım?":
        st.write("### 📋 Bugünün Kayıtları")
        bugun_kayitlari = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]
        
        if bugun_kayitlari:
            for z in bugun_kayitlari:
                st.write(f"⏰ {z['Saat']} | **{z['Doktor']}** ({z['Kurum']})")
        else:
            st.info("Henüz kayıt yok.")

except Exception as e:
    st.error(f"Bir hata oluştu: {e}")

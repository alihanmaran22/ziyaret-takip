import streamlit as st
import pandas as pd
from datetime import datetime

# Mobil ekran düzeni
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem;}
    </style>
""", unsafe_allow_html=True)

# Veri Yükleme (Public CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    # Sütun isimlerindeki boşlukları temizle
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    # Session State
    if 'ziyaret_gecmisi' not in st.session_state:
        st.session_state.ziyaret_gecmisi = []

    # Basit Menü
    menu = st.sidebar.radio("Menü:", ["Ziyaret Girişi", "Bugün Ne Yaptım?"])
    
    st.title("💊 Nextpharma Ziyaret Takip")

    if menu == "Ziyaret Girişi":
        # Hastane Listesi
        hastane_listesi = ['Seçiniz...'] + sorted(df['KURUM'].unique().astype(str).tolist())
        secilen_hastane = st.selectbox("Hastane Seç:", hastane_listesi)

        if secilen_hastane != 'Seçiniz...':
            df_filtre = df[df['KURUM'] == secilen_hastane]
            for i, row in df_filtre.iterrows():
                if st.button(f"Ekle: {row['DOKTOR']} ({row['İHTİSAS']})", key=f"z_{i}"):
                    st.session_state.ziyaret_gecmisi.append({
                        "Doktor": row['DOKTOR'],
                        "Kurum": row['KURUM'],
                        "Zaman": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()

    elif menu == "Bugün Ne Yaptım?":
        st.write("### 📋 Günlük Ziyaretler")
        if st.session_state.ziyaret_gecmisi:
            for z in reversed(st.session_state.ziyaret_gecmisi):
                st.write(f"⏰ {z['Zaman']} | **{z['Doktor']}** - {z['Kurum']}")
        else:
            st.info("Henüz ziyaret eklenmedi.")

except Exception as e:
    st.error("Veri yüklenirken bir hata oluştu. Lütfen bağlantını kontrol et.")
    st.write(e)

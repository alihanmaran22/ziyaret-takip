import streamlit as st
import pandas as pd
from datetime import datetime

# Sayfa ayarları
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")
st.markdown("<style>.block-container {padding: 1rem;} div.stButton > button {width: 100%;}</style>", unsafe_allow_html=True)

# Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

menu = st.sidebar.radio("Menü:", ["Ziyaret Girişi", "Bugün Ne Yaptım?"])
bugun_str = datetime.now().strftime("%d/%m/%Y")

st.title("💊 Nextpharma Ziyaret Takip")

if menu == "Ziyaret Girişi":
    # Hastane seçimi
    hastane_listesi = ['Seçiniz...'] + sorted(df['KURUM'].dropna().astype(str).str.strip().unique().tolist())
    secilen_hastane = st.selectbox("Hastane Seç:", hastane_listesi)

    if secilen_hastane != 'Seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        
        for i, row in df_filtre.iterrows():
            st.write(f"**{row['DOKTOR']}** - {row['İHTİSAS']}")
            # ZİYARET EKLE BUTONU BURADA
            if st.button(f"Ziyaret Ekle: {row['DOKTOR']}", key=f"z_{i}"):
                st.session_state.ziyaret_gecmisi.append({
                    "Doktor": row['DOKTOR'],
                    "Kurum": row['KURUM'],
                    "Zaman": datetime.now().strftime("%H:%M"),
                    "Tarih": bugun_str
                })
                st.success(f"{row['DOKTOR']} eklendi!")
                st.rerun()

elif menu == "Bugün Ne Yaptım?":
    st.write("### 📋 Bugünün Ziyaretleri")
    bugun_kayitlari = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]
    
    if bugun_kayitlari:
        for z in reversed(bugun_kayitlari):
            st.write(f"⏰ {z['Zaman']} | **{z['Doktor']}** ({z['Kurum']})")
    else:
        st.info("Henüz ziyaret kaydı yok.")

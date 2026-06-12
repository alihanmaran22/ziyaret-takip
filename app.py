import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Ayarlar ve Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Session State ile ziyaret geçmişini tutalım
if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

# Başlık ve İsim
st.title("💊 Nextpharma Ziyaret Takip")
st.subheader("Hoş geldin, Neutec İlaç - Alihan Maran")

# 2. Çoklu Filtreleme (Hastane -> Branş)
hastaneler = ['Tümü'] + df['KURUM'].unique().tolist()
secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

# Eğer hastane seçildiyse branşları getir
if secilen_hastane != 'Tümü':
    df_filtre = df[df['KURUM'] == secilen_hastane]
    branslar = ['Tümü'] + df_filtre['İHTİSAS'].unique().tolist()
    secilen_brans = st.selectbox("Branş Seç:", branslar)
    
    if secilen_brans != 'Tümü':
        df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
else:
    df_filtre = df

# 3. Doktor Listeleme ve Ziyaret İşlemleri
st.markdown("---")
for i, row in df_filtre.iterrows():
    cols = st.columns([3, 1, 1])
    cols[0].write(f"**{row['DOKTOR']}** ({row['İHTİSAS']}) - Kalan: {row['FREKANS']}")
    
    if cols[1].button("Ziyaret Et", key=f"ziyaret_{i}"):
        st.session_state.ziyaret_gecmisi.append({
            "Doktor": row['DOKTOR'], "Tarih": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        st.toast(f"{row['DOKTOR']} ziyaret edildi!")
    
    if cols[2].button("İptal Et", key=f"iptal_{i}"):
        st.session_state.ziyaret_gecmisi = [z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] != row['DOKTOR']]
        st.warning(f"{row['DOKTOR']} ziyareti listeden silindi.")

# 4. Ziyaret Geçmişi (Tarihsel Takip)
st.sidebar.title("📅 Ziyaret Geçmişi")
if st.sidebar.button("Geçmişi Temizle"):
    st.session_state.ziyaret_gecmisi = []
for z in st.session_state.ziyaret_gecmisi:
    st.sidebar.write(f"✅ {z['Doktor']} - {z['Tarih']}")
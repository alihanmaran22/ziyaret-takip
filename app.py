import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret")

# 1. Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=3600)
def load_data():
    return pd.read_csv(SHEET_URL)

df = load_data()

# 2. Hata İçermeyen Veri Yapısı
if 'ziyaretler' not in st.session_state:
    st.session_state.ziyaretler = []

# 3. Arayüz
st.title("💊 Nextpharma Ziyaret Takip")

# Ziyaret Ekleme Bölümü
hastane = st.selectbox("Hastane Seç:", ['Seçiniz...'] + sorted(df['KURUM'].unique().tolist()))
if hastane != 'Seçiniz...':
    df_f = df[df['KURUM'] == hastane]
    brans = st.selectbox("Branş Seç:", ['Tümü'] + sorted(df_f['İHTİSAS'].unique().tolist()))
    if brans != 'Tümü': df_f = df_f[df_f['İHTİSAS'] == brans]
    
    for i, row in df_f.iterrows():
        if st.button(f"➕ {row['DOKTOR']}", key=f"dr_{i}"):
            st.session_state.ziyaretler.append({
                "Doktor": row['DOKTOR'],
                "Kurum": row['KURUM'],
                "Brans": row['İHTİSAS']
            })
            st.success(f"{row['DOKTOR']} eklendi!")

# 4. Füzyon Aktarım (Hatasız Kopyalama)
st.divider()
st.subheader("🚀 Füzyon Hızlı Aktarım")
if st.session_state.ziyaretler:
    metin = ""
    df_temp = pd.DataFrame(st.session_state.ziyaretler)
    for kurum in df_temp['Kurum'].unique():
        metin += f"■ {kurum.upper()}\n"
        for brans in df_temp[df_temp['Kurum'] == kurum]['Brans'].unique():
            metin += f"  • {brans.upper()}\n"
            for dr in df_temp[(df_temp['Kurum'] == kurum) & (df_temp['Brans'] == brans)]['Doktor']:
                metin += f"    - {dr}\n"
    
    st.text_area("Bu metni kopyala:", value=metin, height=200)
else:
    st.info("Henüz ziyaret kaydı yok.")

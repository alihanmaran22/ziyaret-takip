import streamlit as st
import pandas as pd
from datetime import datetime

# Mobil ekranlar için padding (boşluk) ayarlarını sıfırlayan CSS
st.set_page_config(layout="centered", page_title="Ziyaret Takip")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem;}
    h1, h2, h3 {margin-top: 0.2rem; margin-bottom: 0.2rem;}
    div.stButton > button {width: 100%; padding: 0.2rem 0.5rem; font-size: 13px;}
    </style>
""", unsafe_allow_html=True)

# 1. Ayarlar ve Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Session State Başlatma
if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

# Sol Menü Seçimi
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"])

bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]

if menu == "Ziyaret Girişi":
    # Seçim alanları
    hastaneler = ['Lütfen hastane seçiniz...'] + df['KURUM'].unique().tolist()
    secilen_hastane = st.selectbox("Hastane:", hastaneler)

    if secilen_hastane != 'Lütfen hastane seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        branslar = ['Tümü'] + df_filtre['İHTİSAS'].unique().tolist()
        secilen_brans = st.selectbox("Branş:", branslar)
        
        if secilen_brans != 'Tümü':
            df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
        
        st.markdown("<div style='margin: 5px 0; border-bottom: 1px solid #444;'></div>", unsafe_allow_html=True)
        
        if df_filtre.empty:
            st.warning("Doktor bulunamadı.")
        else:
            # KOMPAKT DOKTOR LİSTESİ
            for i, row in df_filtre.iterrows():
                yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
                kalan = int(row['FREKANS']) - yapilan
                
                # Kritik Frekans Uyarısı
                uyari_etiketi = ""
                if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                    uyari_etiketi = " ⚠️"
                
                # Doktor İsmi - Küçültülmüş ve kalın formatta
                st.markdown(f"**{row['DOKTOR']}** <span style='font-size:12px; color:#888;'>({row['İHTİSAS']})</span>{uyari_etiketi}", unsafe_allow_html=True)
                
                # Mobilde her şeyi tek satıra sığdırmak için 4 sütunlu kompakt düzen
                cols = st.columns([2, 1.2, 1, 1])
                cols[0].markdown(f"<p style='font-size:13px; margin-top:5px;'>Kal

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

# Session State Başlatma
if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

# Sol Menü Seçimi
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"])

bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]

if menu == "Ziyaret Girişi":
    # Doktor Ara kısmı tamamen kaldırıldı, doğrudan seçimlerle başlıyor

    # Orijinal Temiz Açılır Liste (Selectbox) Düzeni
    hastaneler = ['Lütfen hastane seçiniz...'] + df['KURUM'].unique().tolist()
    secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

    if secilen_hastane != 'Lütfen hastane seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        branslar = ['Tümü'] + df_filtre['İHTİSAS'].unique().tolist()
        secilen_brans = st.selectbox("Branş Seç:", branslar)
        
        if secilen_brans != 'Tümü':
            df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
        
        st.markdown("---")
        
        if df_filtre.empty:
            st.warning("Bu kriterlere uygun doktor bulunamadı.")
        
        # Orijinal Hızlı Liste Düzeni: Doktor kartları ve yan yana butonlar
        for i, row in df_filtre.iterrows():
            yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
            kalan = int

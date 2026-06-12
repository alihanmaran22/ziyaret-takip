import streamlit as st
import pandas as pd
from datetime import datetime

# Mobil ekranlarda boşlukları sıfırlayan ve butonları küçülten CSS
st.set_page_config(layout="centered", page_title="Neutec Ziyaret Takip")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem;}
    h1, h2, h3 {margin-top: 0.1rem; margin-bottom: 0.1rem;}
    div.stButton > button {width: 100%; padding: 0.2rem 0.4rem; font-size: 13px; height: auto;}
    </style>
""", unsafe_allow_html=True)

# 1. Google Sheets Veri Yükleme ve Boşluk Temizliği
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    # Sütun isimlerindeki boşlukları temizle
    df.columns = df.columns.str.strip()
    # Hücrelerin içindeki gizli boşlukları temizle (Eşleşme hatasını önler)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    return df

df = load_data()

# Session State Başlatma
if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

# Sol Menü Yapısı
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"])

bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]

# Ana Başlık
st.title("💊 Nextpharma Ziyaret Takip")

if menu == "Ziyaret Girişi":
    # 1. Bugün Ziyaret Edilenler Paneli (Üst Kısım)
    with st.expander(f"📋 Bugün Ziyaret Edilenler ({len(bugun_ziyaretleri)} Doktor)"):
        if bugun_ziyaretleri:
            for z in reversed(bugun_ziyaretleri):
                st.markdown(f"⏰ **{z['Saat']}** | {z['Doktor']} - {z['Brans']} ({z['Kurum']})")
        else:
            st.caption("Henüz bugün ziyaret kaydı girilmedi.")

    st.markdown("### 🔍 Kurum ve Branş Seçimi")

    # Tam istediğin gibi: İlk başta temiz bir açılır liste geliyor
    hastaneler = ['Lütfen hastane seçiniz...'] + sorted(df['KURUM'].unique().tolist())
    secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

    if secilen_hastane != 'Lütfen hastane seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        
        branslar = ['Tümü'] + sorted(df_filtre['İHTİSAS'].unique().tolist())
        secilen_brans = st.selectbox("Branş Seç:", branslar)
        
        if secilen_brans != 'Tümü':
            df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
        
        st.markdown("<div style='margin: 5px 0; border-bottom: 1px solid #444;'></div>", unsafe_allow_html=True)
        
        if df_filtre.empty:
            st.warning("Bu kriterlere uygun doktor bulunamadı.")
        else:
            # Beğendiğin Kompakt Doktor Listesi Düzeni
            for i, row in df_filtre.iterrows():
                yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
                kalan = int(row['FREKANS']) - yapilan
                
                # Kritik Durum Uyarı Etiketi
                uyari_etiketi = ""
                if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                    uyari_etiketi = " <span style='color:#ffaa00; font-size:12px; font-weight:bold;'>[KRİTİK] ⚠️</span>"
                
                # Kompakt Doktor Bilgisi
                st.

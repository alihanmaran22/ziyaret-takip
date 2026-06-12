import streamlit as st
import pandas as pd
from datetime import datetime

# Mobil ekranlarda boşlukları sıfırlayan ve butonları küçülten CSS
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")
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
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    return df

df = load_data()

# Session State Başlatma
if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

# Sol Menü Yapısı
menu = st.sidebar.radio(
    "Menü Seç:", 
    ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"]
)

bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [
    z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str
]

st.title("💊 Nextpharma Ziyaret Takip")

if menu == "Ziyaret Girişi":
    panel_baslik = f"📋 Bugün Ziyaret Edilenler ({len(bugun_ziyaretleri)} Doktor)"
    with st.expander(panel_baslik):
        if bugun_ziyaretleri:
            for z in reversed(bugun_ziyaretleri):
                st.write(f"⏰ {z['Saat']} | {z['Doktor']} - {z['Brans']} ({z['Kurum']})")
        else:
            st.caption("Henüz bugün ziyaret kaydı girilmedi.")

    st.markdown("### 🔍 Kurum ve Branş Seçimi")

    hastane_listesi = sorted(df['KURUM'].unique().tolist())
    hastaneler = ['Lütfen hastane seçiniz...'] + hastane_listesi
    secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

    if secilen_hastane != 'Lütfen hastane seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        
        brans_listesi = sorted(df_filtre['İHTİSAS'].unique().tolist())
        branslar = ['Tümü'] + brans_listesi
        secilen_brans = st.selectbox("Branş Seç:", branslar)
        
        if secilen_brans != 'Tümü':
            df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
        
        st.markdown("---")
        
        if df_filtre.empty:
            st.warning("Bu kriterlere uygun doktor bulunamadı.")
        else:
            for i, row in df_filtre.iterrows():
                dr_adi = row['DOKTOR']
                dr_brans = row['İHTİSAS']
                dr_kurum = row['KURUM']
                dr_frekans = int(row['FREKANS'])
                
                yapilan = len([
                    z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == dr_adi
                ])
                kalan = dr_frekans - yapilan
                
                uyari_etiketi = ""
                if kalan > 0 and kalan >= (dr_frekans / 2):
                    uyari_etiketi = " ⚠️ [KRİTİK]"
                
                st.write(f"**{dr_adi}** - {dr_brans} {uyari_etiketi}")
                
                cols = st.columns([1.5, 1.1, 1.1, 0.8])
                cols[0].write(f"Kal: {kalan}/{dr_frekans}")
                
                if cols[1].button("Ziyaret", key=f"z_{i}"):
                    k_notu = st.session_state.get(f"temp_not_{i}", "").strip()
                    st.session_state.ziyaret_gecmisi.append({
                        "Doktor": dr_adi, 
                        "Tarih": bugun_

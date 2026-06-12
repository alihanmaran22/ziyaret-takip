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
    # Sütun isimlerindeki gizli boşlukları temizle
    df.columns = df.columns.str.strip()
    # Eşleşme hatası olmaması için hücrelerin içindeki gizli boşlukları da temizle kankam
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
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
    # Seçim alanları tamamen temiz açılır liste
    hastaneler = ['Lütfen hastane seçiniz...'] + sorted(df['KURUM'].unique().tolist())
    secilen_hastane = st.selectbox("Hastane:", hastaneler)

    if secilen_hastane != 'Lütfen hastane seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        branslar = ['Tümü'] + sorted(df_filtre['İHTİSAS'].unique().tolist())
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
                
                # Doktor İsmi - Tamamen küçültülmüş mobil uyumlu format
                st.markdown(f"**{row['DOKTOR']}** <span style='font-size:12px; color:#888;'>({row['İHTİSAS']})</span>{uyari_etiketi}", unsafe_allow_html=True)
                
                # Tüm butonlar ve yazılar tek satırda
                cols = st.columns([2, 1.2, 1, 1])
                
                kalan_metin = f"<p style='font-size:13px; margin-top:5px;'>Kal: <b>{kalan}</b>/{row['FREKANS']}</p>"
                cols[0].markdown(kalan_metin, unsafe_allow_html=True)
                
                # Ziyaret Et Butonu
                if cols[1].button("Ziyaret", key=f"z_{i}"):
                    aktif_not = st.session_state.get(f"temp_not_{i}", "").strip()
                    st.session_state.ziyaret_gecmisi.append({
                        "Doktor": row['DOKTOR'], 
                        "Tarih": bugun_str,
                        "Saat": datetime.now().strftime("%H:%M"),
                        "Kurum": row['KURUM'], 
                        "Brans": row['İHTİSAS'],
                        "Not": aktif_not if aktif_not else "Not eklenmedi."
                    })
                    if f"temp_not_{i}" in st.session_state:
                        del st.session_state[f"temp_not_{i}"]
                    st.rerun()
                
                # İptal Et Butonu
                if cols[2].button("İptal", key=f"i_{i}"):
                    for j, z in reversed(list(enumerate(st

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

st.title("💊 Nextpharma Ziyaret Takip")

# Sol Menü Seçimi (İstediğin gibi "Bugün Ne Yaptım?" sekmesi eklendi)
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"])

bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]

if menu == "Ziyaret Girişi":
    # Ekran tamamen eskiye döndü, o üstteki kalabalık kutuyu sildim!
    arama_sorgusu = st.text_input("🔍 Doktor İsmi ile Ara:", "").strip().lower()
    
    st.markdown("### 🏢 Hastaneler (Ziyaret Durum Analizi)")

    tum_hastaneler = df['KURUM'].unique().tolist()
    
    # Hastane Sekmeleri
    for i_kurum, kurum_adi in enumerate(tum_hastaneler):
        df_kurum = df[df['KURUM'] == kurum_adi]
        
        if arama_sorgusu:
            df_kurum = df_kurum[df_kurum['DOKTOR'].str.lower().str.contains(arama_sorgusu)]
            if df_kurum.empty:
                continue

        with st.expander(f"🏥 {kurum_adi}"):
            for i, row in df_kurum.iterrows():
                yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
                kalan = int(row['FREKANS']) - yapilan
                
                uyari_etiketi = ""
                if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                    uyari_etiketi = " ⚠️ <span style='color:#FF4B4B; font-weight:bold;'>[KRİTİK]</span>"
                
                # Doktor adı ve BRANŞ ADI
                st.markdown(f"### **{row['DOKTOR']}** (<span style='color:#00ffff;'>{row['İHTİSAS']}</span>){uyari_etiketi}", unsafe_allow_html=True)
                
                cols = st.columns([3, 1, 1])
                cols[0].write(f"**Kalan Ziyaret: {kalan}** / {row['FREKANS']}")
                
                # Ziyaret Et Butonu
                if cols[1].button("Ziyaret Et", key=f"z_{i}_{i_kurum}"):
                    aktif_not = st.session_state.get(f"temp_not_{i}_{i_kurum}", "").strip()
                    st.session_state.ziyaret_gecmisi.append({
                        "Doktor": row['DOKTOR'], 
                        "Tarih": bugun_str,
                        "Saat": datetime.now().strftime("%H:%M"),
                        "Kurum": row['KURUM'], 
                        "Brans": row['İHTİSAS'],
                        "Not": aktif_not if aktif_not else "Not eklenmedi."
                    })
                    if f"temp_not_{i}_{i_kurum}" in st.session_state:
                        del st.session_state[f"temp_not_{i}_{i_kurum}"]
                    st.rerun()
                
                # İpt

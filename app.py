import streamlit as st
import pandas as pd
from datetime import datetime

# Mobil ekranlar için padding ayarlarını sıfırlayan ve butonları küçülten CSS
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem;}
    h1, h2, h3 {margin-top: 0.1rem; margin-bottom: 0.1rem;}
    div.stButton > button {width: 100%; padding: 0.2rem 0.4rem; font-size: 12px; height: auto;}
    .stExpander {margin-bottom: 0.3rem;}
    </style>
""", unsafe_allow_html=True)

# 1. Veri Yükleme ve Temizleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    # Sütun isimlerindeki boşlukları temizle
    df.columns = df.columns.str.strip()
    # Eşleşme hatası olmaması için satırların içindeki gizli boşlukları temizle
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    return df

df = load_data()

# Session State Başlatma
if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

# Sol Menü
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"])

bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]

# Başlık
st.title("💊 Nextpharma Ziyaret Takip")

if menu == "Ziyaret Girişi":
    # Bugün Ziyaret Edilenler Expander'ı (Üst Kısım)
    with st.expander(f"📝 Bugün Ziyaret Edilenler ({len(bugun_ziyaretleri)} Doktor)"):
        if bugun_ziyaretleri:
            for z in reversed(bugun_ziyaretleri):
                st.markdown(f"<p style='font-size:13px; margin:2px 0;'>⏰ <b>{z['Saat']}</b> | {z['Doktor']} - {z['Brans']} ({z['Kurum']})</p>", unsafe_allow_html=True)
        else:
            st.caption("Henüz bugün ziyaret girilmedi.")

    # Doktor İsmi ile Ara (Arama Çubuğu)
    arama_terimi = st.text_input("🔍 Doktor İsmi ile Ara:", placeholder="Doktor adı yazın...").strip().lower()

    st.markdown("### 🏢 Hastaneler (Ziyaret Durum Analizi)")

    # Eğer arama yapılıyorsa hastaneleri filtrele, yapılmıyorsa hepsini getir
    if arama_terimi:
        df_goster = df[df['DOKTOR'].str.lower().str.contains(arama_terimi)]
    else:
        df_goster = df

    # Hastaneleri tek tek expander olarak listeleme (Orijinal Tasarımın)
    hastane_listesi = sorted(df_goster['KURUM'].unique().tolist())

    for hastane in hastane_listesi:
        df_hastane_doktorlari = df_goster[df_goster['KURUM'] == hastane]
        
        with st.expander(f"🏥 {hastane}"):
            for i, row in df_hastane_doktorlari.iterrows():
                yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
                kalan = int(row['FREKANS']) - yapilan
                
                # Kritik Frekans Uyarısı
                uyari_etiketi = ""
                if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                    uyari_etiketi = " <span style='color:#ffaa00; font-size:12px;'>[KRİTİK] ⚠️</span>"
                
                # Doktor İsmi ve Branşı (Küçültülmüş mobil düzen)
                st.markdown(f"<p style='margin-bottom:2px; margin-top:5px; font-size:14px;'><b>{row['DOKTOR']}</b> - {row['İHTİSAS']}{uyari_etiketi}</p>", unsafe_allow_html=True)
                
                # Sütunları yan yana alarak dikey boşluğu yok ediyoruz
                cols = st.columns([1.8, 1.1, 1.1, 1])
                
                # Kalan Ziyaret Bilgisi
                cols[0].markdown(f"<p style='font-size:12px; margin-top:6px;'>Kal: <b>{kalan}</b>/{row['FREKANS']}</p>", unsafe_allow_html=True)
                
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
                
                # İptal Et Butonu (Eksik parantez tamamen kapatıldı)
                if cols[2].button("İptal", key=f"i_{i}"):

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
    # İstediğin gibi: Büyük "Nextpharma Ziyaret Takip" başlığı kaldırıldı!
    
    # Hızlı Doktor Arama Kutusu
    arama_sorgusu = st.text_input("🔍 Doktor İsmi ile Ara:", "").strip().lower()

    # ESKİSİ GİBİ: Açılır Liste (Selectbox) Düzeni
    hastaneler = ['Lütfen hastane seçiniz...'] + df['KURUM'].unique().tolist()
    secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

    if secilen_hastane != 'Lütfen hastane seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        branslar = ['Tümü'] + df_filtre['İHTİSAS'].unique().tolist()
        secilen_brans = st.selectbox("Branş Seç:", branslar)
        
        if secilen_brans != 'Tümü':
            df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
        
        # Arama kutusu filtresi
        if arama_sorgusu:
            df_filtre = df_filtre[df_filtre['DOKTOR'].str.lower().str.contains(arama_sorgusu)]
        
        st.markdown("---")
        
        if df_filtre.empty:
            st.warning("Aranan kriterlere uygun doktor bulunamadı.")
        
        # ESKİ SADE LİSTE: Doktorlar orijinal kompakt yapısıyla listeleniyor
        for i, row in df_filtre.iterrows():
            yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
            kalan = int(row['FREKANS']) - yapilan
            
            # Kritik Frekans Uyarısı
            uyari_etiketi = ""
            if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                uyari_etiketi = " ⚠️ [KRİTİK]"
            
            # Doktor başlığı ve branşı (Hatasız düz string biçimi)
            st.markdown(f"### **{row['DOKTOR']}** ({row['İHTİSAS']}){uyari_etiketi}")
            
            cols = st.columns([3, 1, 1])
            cols[0].write(f"**Kalan Ziyaret: {kalan}** / {row['FREKANS']}")
            
            # Ziyaret Et Butonu
            if cols[1].button("Ziyaret Et", key=f"z_{i}"):
                aktif_not = st.session_state.get(f"temp_not_{i}", "").strip()
                st.session_state.ziyaret_gecmisi.append({
                    "Doktor": row['DOKTOR'], 
                    "Tarih": bugun_str,
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Kurum": row['KURUM'], 
                    "Brans": row['İHTİSAS'],
                    "Not": aktif_not if aktif_not else "Not eklenmedi."
                })
                if f"temp_not

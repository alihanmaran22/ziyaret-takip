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

# Sol Menü Seçimi
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Ziyaret Detay Raporu"])

if menu == "Ziyaret Girişi":
    # Özellik 3: Hızlı Doktor Arama Kutusu
    arama_sorgusu = st.text_input("🔍 Doktor İsmi ile Ara:", "").strip().lower()

    # Hastane Seçimi
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
        
        for i, row in df_filtre.iterrows():
            yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
            kalan = int(row['FREKANS']) - yapilan
            
            # Öneri 1: "Kırmızı Alarm" Sistemi (Kalan ziyaret frekansın yarısından fazlaysa ve kalan > 0 ise uyarı ver)
            uyari_etiketi = ""
            if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                uyari_etiketi = " ⚠️ <span style='color:#FF4B4B; font-weight:bold;'>[KRİTİK FREKANS]</span>"
            
            # HTML destekli Doktor Başlığı
            st.markdown(f"### **{row['DOKTOR']}** ({row['İHTİSAS']}){uyari_etiketi}", unsafe_allow_html=True)
            
            cols = st.columns([3, 1, 1])
            cols[0].write(f"**Kalan Ziyaret: {kalan}** / {row['FREKANS']}")
            
            # Ziyaret Et Butonu
            if cols[1].button("Ziyaret Et", key=f"z_{i}"):
                aktif_not = st.session_state.get(f"temp_not_{i}", "").strip()
                st.session_state.ziyaret_gecmisi.append({
                    "Doktor": row['DOKTOR'], 
                    "Tarih": datetime.now().strftime("%d/%m/%Y"),
                    # Öneri 3: Saat ve dakika damgası ekleme
                    "Saat": datetime.now().strftime("%H:%M"),
                    "Kurum": row['KURUM'], 
                    "Brans": row['İHTİSAS'],
                    "Not": aktif_not if aktif_not else "Not eklenmedi."
                })
                if f"temp_not_{i}" in st.session_state:
                    del st.session_state[f"temp_not_{i}"]
                st.rerun()
            
            # İptal Et Butonu
            if cols[2].button("İptal Et", key=f"i_{i}"):
                for j, z in reversed(list(enumerate(st.session_state.ziyaret_gecmisi))):
                    if z['Doktor'] == row['DOKTOR']:
                        del st.session_state.ziyaret_gecmisi[j]
                        break
                st.rerun()
            
            # Gizli Not Alanı (Expander)
            with st.expander("✍️ Ziyaret Notu Ekle / Düzenle"):
                st.text_input(
                    "Bu ziyaret için notunuzu yazın:", 
                    key=f"temp_not_{i}", 
                    placeholder="Örn: Levmont hakkında olumlu konuştu..."
                )
                
            st.markdown("---")

elif menu == "Ziyaret Detay Raporu":
    st.header("📋 Ziyaret Detay Raporu")
    
    # Tarih seçimi
    rapor_tarihi = st.date_input("Rapor Tarihi Seç:", datetime.now())
    tarih_str = rapor_tarihi.strftime("%d/%m/%Y")
    
    # Günlük kayıtlar
    gunluk_kayitlar = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == tarih_str]
    
    # Ziyaret İstatistikleri
    st.markdown("### 📊 Günlük Özet")
    st.metric(label=f"{tarih_str} Toplam Ziyaret Edilen Doktor", value=f"{len(gunluk_kayitlar)} Kişi")
    st.markdown("---")
    
    if gunluk_kayitlar:
        df_rapor = pd.DataFrame(gunluk_kayitlar)
        
        # Öneri 3: Raporu kronolojik olarak saat bazlı sırala
        if 'Saat' in df_rapor.columns:
            df_rapor = df_rapor.sort_values(by='Saat')
        
        for brans in df_rapor['Brans'].unique():
            with st.expander(f"🏥 {brans} Branşı"):
                brans_df = df_rapor[df_rapor['Brans'] == brans]
                for _, z in brans_df.iterrows():
                    # Öneri 3'ün Raporda Gösterilmesi: Saat bilgisi ismin başına eklendi
                    ziyaret_saati = f"⏰ {z['Saat']} | " if 'Saat' in z else ""
                    st.write(f"✅ {ziyaret_saati}**{z['Doktor']}** ({z['Kurum']})")
                    if z['Not'] != "Not eklenmedi.":
                        st.info(f"💬 **Ziyaret Notu:** {z['Not']}")
    else:
        st.warning("Bu tarihte henüz bir kayıt bulunamadı.")

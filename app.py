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
        
        # Eğer arama kutusuna bir şey yazıldıysa filtrele
        if arama_sorgusu:
            df_filtre = df_filtre[df_filtre['DOKTOR'].str.lower().str.contains(arama_sorgusu)]
        
        st.markdown("---")
        
        if df_filtre.empty:
            st.warning("Aranan kriterlere uygun doktor bulunamadı.")
        
        for i, row in df_filtre.iterrows():
            yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
            kalan = int(row['FREKANS']) - yapilan
            
            # Doktor başlığı ve kalan sayısı
            st.write(f"### **{row['DOKTOR']}** ({row['İHTİSAS']})")
            
            # Özellik 1: Not Alma Girişi (Her doktora özel benzersiz key ile)
            ziyaret_notu = st.text_input(f"✍️ Ziyaret Notu ({row['DOKTOR']} için):", key=f"not_input_{i}", placeholder="Örn: İlaç olumlu karşılandı, numune verildi...")
            
            cols = st.columns([3, 1, 1])
            cols[0].write(f"**Kalan Ziyaret: {kalan}** / {row['FREKANS']}")
            
            # Ziyaret Et Butonu
            if cols[1].button("Ziyaret Et", key=f"z_{i}"):
                st.session_state.ziyaret_gecmisi.append({
                    "Doktor": row['DOKTOR'], 
                    "Tarih": datetime.now().strftime("%d/%m/%Y"),
                    "Kurum": row['KURUM'], 
                    "Brans": row['İHTİSAS'],
                    "Not": ziyaret_notu if ziyaret_notu else "Not eklenmedi."
                })
                st.rerun()
            
            # İptal Et Butonu
            if cols[2].button("İptal Et", key=f"i_{i}"):
                for j, z in reversed(list(enumerate(st.session_state.ziyaret_gecmisi))):
                    if z['Doktor'] == row['DOKTOR']:
                        del st.session_state.ziyaret_gecmisi[j]
                        break
                st.rerun()
            st.markdown("---")

elif menu == "Ziyaret Detay Raporu":
    st.header("📋 Ziyaret Detay Raporu")
    
    # Tarih seçimi
    rapor_tarihi = st.date_input("Rapor Tarihi Seç:", datetime.now())
    tarih_str = rapor_tarihi.strftime("%d/%m/%Y")
    
    # Seçilen tarihe ait kayıtları filtrele
    gunluk_kayitlar = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == tarih_str]
    
    # Özellik 2: Ziyaret İstatistikleri (Büyük Metrik Sayacı)
    st.markdown("### 📊 Günlük Özet")
    st.metric(label=f"{tarih_str} Toplam Ziyaret Edilen Doktor", value=f"{len(gunluk_kayitlar)} Kişi")
    st.markdown("---")
    
    if gunluk_kayitlar:
        df_rapor = pd.DataFrame(gunluk_kayitlar)
        
        # Branş bazlı expander yapı ve detayların gösterilmesi
        for brans in df_rapor['Brans'].unique():
            with st.expander(f"🏥 {brans} Branşı"):
                brans_df = df_rapor[df_rapor['Brans'] == brans]
                for _, z in brans_df.iterrows():
                    st.write(f"✅ **{z['Doktor']}** ({z['Kurum']})")
                    # Özellik 1'in Raporda Gösterilmesi: Alınan notu burada listeliyoruz
                    st.info(f"💬 **Ziyaret Notu:** {z['Not']}")
    else:
        st.warning("Bu tarihte henüz bir kayıt bulunamadı.")

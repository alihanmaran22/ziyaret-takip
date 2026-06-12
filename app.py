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
    # Hızlı Doktor Arama Kutusu
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
            
            # Ana Satır: Doktor ismi ve Kalan Sayısı
            cols = st.columns([3, 1, 1])
            cols[0].write(f"### **{row['DOKTOR']}** ({row['İHTİSAS']})")
            
            # Ziyaret Et Butonu
            if cols[1].button("Ziyaret Et", key=f"z_{i}"):
                # Eğer alt menüdeki not yazılmadıysa session_state'den geçici notu al, yoksa boş bırak
                aktif_not = st.session_state.get(f"temp_not_{i}", "").strip()
                st.session_state.ziyaret_gecmisi.append({
                    "Doktor": row['DOKTOR'], 
                    "Tarih": datetime.now().strftime("%d/%m/%Y"),
                    "Kurum": row['KURUM'], 
                    "Brans": row['İHTİSAS'],
                    "Not": aktif_not if aktif_not else "Not eklenmedi."
                })
                # Ziyaret gerçekleştikten sonra geçici notu temizle
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
            
            # Alt Bilgi Satırı
            st.write(f"**Kalan Ziyaret: {kalan}** / {row['FREKANS']}")
            
            # İstediğin Şey: Doktorun içine girilecek gizli Not Alanı (Expander)
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
    gunluk_kayitlar = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] ==_str]
    gunluk_kayitlar = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == tarih_str]
    
    # Ziyaret İstatistikleri
    st.markdown("### 📊 Günlük Özet")
    st.metric(label=f"{tarih_str} Toplam Ziyaret Edilen Doktor", value=f"{len(gunluk_kayitlar)} Kişi")
    st.markdown("---")
    
    if gunluk_kayitlar:
        df_rapor = pd.DataFrame(gunluk_kayitlar)
        
        for brans in df_rapor['Brans'].unique():
            with st.expander(f"🏥 {brans} Branşı"):
                brans_df = df_rapor[df_rapor['Brans'] == brans]
                for _, z in brans_df.iterrows():
                    st.write(f"✅ **{z['Doktor']}** ({z['Kurum']})")
                    if z['Not'] != "Not eklenmedi.":
                        st.info(f"💬 **Ziyaret Notu:** {z['Not']}")
    else:
        st.warning("Bu tarihte henüz bir kayıt bulunamadı.")

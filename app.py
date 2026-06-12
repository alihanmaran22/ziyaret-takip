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
    # Büyük başlık ve arama kutusu yok, doğrudan seçimlerle başlıyor
    
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
        else:
            # Doktor listesi döngüsü
            for i, row in df_filtre.iterrows():
                yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
                kalan = int(row['FREKANS']) - yapilan
                
                # Kritik Frekans Uyarısı
                uyari_etiketi = ""
                if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                    uyari_etiketi = " ⚠️ [KRİTİK]"
                
                st.write(f"### **{row['DOKTOR']}** ({row['İHTİSAS']}){uyari_etiketi}")
                
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
                    if f"temp_not_{i}" in st.session_state:
                        del st.session_state[f"temp_not_{i}"]
                    st.rerun()
                
                # İptal Et Butonu (Hatalı kısım tamamen düzeltildi kankam)
                if cols[2].button("İptal Et", key=f"i_{i}"):
                    for j, z in reversed(list(enumerate(st.session_state.ziyaret_gecmisi))):
                        if z['Doktor'] == row['DOKTOR']:
                            del st.session_state.ziyaret_gecmisi[j]
                            break
                    st.rerun()
                
                # Ziyaret Notu Girişi
                with st.expander("✍️ Ziyaret Notu Ekle / Düzenle"):
                    st.text_input(
                        "Bu ziyaret için notunuzu yazın:", 
                        key=f"temp_not_{i}", 
                        placeholder="Örn: Ürün hakkında olumlu..."
                    )
                    
                st.markdown("---")

elif menu == "Bugün Ne Yaptım?":
    st.header(f"📋 Bugün Ne Yaptım? ({bugun_str})")
    st.markdown(f"### 🗓️ Bugün Toplam Girdiğin Ziyaret: **{len(bugun_ziyaretleri)} Doktor**")
    st.markdown("---")
    
    if bugun_ziyaretleri:
        for z in reversed(bugun_ziyaretleri):
            st.markdown(f"⏰ **{z['Saat']}** | **{z['Doktor']}** - **{z['Brans']}** ({z['Kurum']})")
            if z['Not'] != "Not eklenmedi.":
                st.info(f"💬 Not: {z['Not']}")
            st.markdown("---")
    else:
        st.info("Bugün henüz bir doktor ziyaret kaydı girmediniz.")

elif menu == "Ziyaret Detay Raporu":
    st.header("📋 Ziyaret Detay Raporu")
    
    rapor_tarihi = st.date_input("Rapor Tarihi Seç:", datetime.now())
    tarih_str = rapor_tarihi.strftime("%d/%m/%Y")
    
    gunluk_kayitlar = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == tarih_str]
    
    st.markdown("### 📊 Günlük Özet")
    st.metric(label="Toplam Ziyaret Edilen Doktor", value=f"{len(gunluk_kayitlar)} Kişi")
    st.markdown("---")
    
    if gunluk_kayitlar:
        df_rapor = pd.DataFrame(gunluk_kayitlar)
        df_rapor = df_rapor.sort_values(by='Saat')
        
        for brans in df_rapor['Brans'].unique():
            with st.expander(f"🏥 {brans} Branşı"):
                brans_df = df_rapor[df_rapor['Brans'] == brans]
                for _, z in brans_df.iterrows():
                    st.write(f"✅ ⏰ {z['Saat']} | **{z['Doktor']}** ({z['Kurum']})")
                    if z['Not'] != "Not eklenmedi.":
                        st.info(f"💬 **Ziyaret Notu:** {z['Not']}")
    else:
        st.warning("Bu tarihte henüz bir kayıt bulunamadı.")

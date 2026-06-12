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
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"])

bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]

if menu == "Ziyaret Girişi":
    # 🔍 Hızlı Doktor Arama Kutusu
    arama_sorgusu = st.text_input("🔍 Doktor İsmi ile Ara:", "").strip().lower()
    
    st.markdown("### 🏢 Hastaneler (Ziyaret Durum Analizi)")

    # Benzersiz hastane listesi
    tum_hastaneler = df['KURUM'].unique().tolist()
    
    # Her hastaneyi birer expander yapıyoruz
    for idx_kurum, kurum_adi in enumerate(tum_hastaneler):
        df_kurum = df[df['KURUM'] == kurum_adi]
        
        if arama_sorgusu:
            df_kurum = df_kurum[df_kurum['DOKTOR'].str.lower().str.contains(arama_sorgusu)]
            if df_kurum.empty:
                continue

        # Hastane Sekmesi
        with st.expander(f"🏥 {kurum_adi}"):
            for idx_doktor, row in df_kurum.reset_index().iterrows():
                yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
                kalan = int(row['FREKANS']) - yapilan
                
                # Kritik Frekans Uyarısı
                uyari_metni = ""
                if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                    uyari_metni = " ⚠️ [KRİTİK]"
                
                # Doktor Başlığı ve Branşı (Hata vermemesi için düz metin yapıldı)
                st.markdown(f"### **{row['DOKTOR']}** - {row['İHTİSAS']}{uyari_metni}")
                st.write(f"**Kalan Ziyaret: {kalan}** / {row['FREKANS']}")
                
                cols = st.columns([1, 1])
                
                # Ziyaret Et Butonu (Benzersiz Key Atandı)
                if cols[0].button("Ziyaret Et", key=f"btn_ziyaret_{idx_kurum}_{idx_doktor}"):
                    temp_key = f"not_giris_{idx_kurum}_{idx_doktor}"
                    aktif_not = st.session_state.get(temp_key, "").strip()
                    
                    st.session_state.ziyaret_gecmisi.append({
                        "Doktor": row['DOKTOR'], 
                        "Tarih": bugun_str,
                        "Saat": datetime.now().strftime("%H:%M"),
                        "Kurum": row['KURUM'], 
                        "Brans": row['İHTİSAS'],
                        "Not": aktif_not if aktif_not else "Not eklenmedi."
                    })
                    if temp_key in st.session_state:
                        del st.session_state[temp_key]
                    st.rerun()
                
                # İptal Et Butonu (Benzersiz Key Atandı)
                if cols[1].button("İptal Et", key=f"btn_iptal_{idx_kurum}_{idx_doktor}"):
                    for j, z in reversed(list(enumerate(st.session_state.ziyaret_gecmisi))):
                        if z['Doktor'] == row['DOKTOR']:
                            del st.session_state.ziyaret_gecmisi[j]
                            break
                    st.rerun()
                
                # Doktorun İçindeki Gizli Not Alanı (Expander)
                with st.expander("✍️ Ziyaret Notu Ekle"):
                    st.text_input(
                        "Notunuzu yazın:", 
                        key=f"not_giris_{idx_kurum}_{idx_doktor}", 
                        placeholder="Örn: Levmont numunesi istendi..."
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
        st.info("Bugün henüz bir doktor ziyareti kaydetmediniz.")

elif menu == "Ziyaret Detay Raporu":
    st.header("📋 Ziyaret Detay Raporu")
    
    rapor_tarihi = st.date_input("Rapor Tarihi Seç:", datetime.now())
    tarih_str = rapor_tarihi.strftime("%d/%m/%Y")
    
    gunluk_kayitlar = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == tarih_str]
    
    st.markdown("### 📊 Günlük Özet")
    st.metric(label=f"{tarih_str} Toplam Ziyaret Edilen Doktor", value=f"{len(gunluk_kayitlar)} Kişi")
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

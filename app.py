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
    bugun_str = datetime.now().strftime("%d/%m/%Y")
    # Bugün girilen tüm ziyaretleri filtrele
    bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]
    
    # 1. Canlı Takip Kutusu (image_7a67a0.png yapısı)
    with st.expander(f"📋 Bugün Ziyaret Edilenler ({len(bugun_ziyaretleri)} Doktor)"):
        if bugun_ziyaretleri:
            for z in reversed(bugun_ziyaretleri):
                st.write(f"⏰ {z['Saat']} | **{z['Doktor']}** - {z['Brans']} ({z['Kurum']})")
        else:
            st.info("Bugün henüz bir doktor ziyareti girmediniz.")

    st.markdown("---")

    # Hızlı Doktor Arama Kutusu
    arama_sorgusu = st.text_input("🔍 Doktor İsmi ile Ara:", "").strip().lower()
    
    st.markdown("### 🏢 Hastaneler (Ziyaret Durum Analizi)")

    # Benzersiz hastane listesini alıyoruz
    tum_hastaneler = df['KURUM'].unique().tolist()
    
    # İstediğin Şey: Her hastaneyi birer sekme (expander) yapıyoruz
    for kurum_adi in tum_hastaneler:
        df_kurum = df[df['KURUM'] == kurum_adi]
        
        # Eğer arama kutusuna isim yazıldıysa hastane içindeki doktorları filtrele
        if arama_sorgusu:
            df_kurum = df_kurum[df_kurum['DOKTOR'].str.lower().str.contains(arama_sorgusu)]
            # Eğer bu hastanede aranan doktor yoksa sekmeyi hiç gösterme, temiz kalsın
            if df_kurum.empty:
                continue

        # Hastane Sekmesi Başlığı (image_84d80b.png tarzı şık buton hissi)
        with st.expander(f"🏥 {kurum_adi}"):
            for i, row in df_kurum.iterrows():
                yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
                kalan = int(row['FREKANS']) - yapilan
                
                # Kritik Frekans Uyarısı
                uyari_etiketi = ""
                if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                    uyari_etiketi = " ⚠️ <span style='color:#FF4B4B; font-weight:bold;'>[KRİTİK]</span>"
                
                # Doktor adı ve parantez içinde BRANŞ ADI (İHTİSAS) yazıyor
                st.markdown(f"### **{row['DOKTOR']}** (<span style='color:#00ffff;'>{row['İHTİSAS']}</span>){uyari_etiketi}", unsafe_allow_html=True)
                
                cols = st.columns([3, 1, 1])
                cols[0].write(f"**Kalan Ziyaret: {kalan}** / {row['FREKANS']}")
                
                # Ziyaret Et Butonu
                if cols[1].button("Ziyaret Et", key=f"z_{i}_{kurum_adi[:3]}"):
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
                if cols[2].button("İptal Et", key=f"i_{i}_{kurum_adi[:3]}"):
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
                        placeholder="Örn: Ürün olumlu karşılandı..."
                    )
                st.markdown("---")

elif menu == "Ziyaret Detay Raporu":
    st.header("📋 Ziyaret Detay Raporu")
    
    # Tarih seçimi
    rapor_tarihi = st.date_input("Rapor Tarihi Seç:", datetime.now())
    tarih_str = rapor_tarihi.strftime("%d/%m/%Y")
    
    # Günlük kayıtlar
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
                    ziyaret_saati = f"⏰ {z['Saat']} | "
                    st.write(f"✅ {ziyaret_saati}**{z['Doktor']}** ({z['Kurum']})")
                    if z['Not'] != "Not eklenmedi.":
                        st.info(f"💬 **Ziyaret Notu:** {z['Not']}")
    else:
        st.warning("Bu tarihte henüz bir kayıt bulunamadı.")

import streamlit as st
import pandas as pd
from datetime import datetime

# Mobil ekranlarda boşlukları sıfırlayan ve butonları küçülten CSS
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem;}
    h1, h2, h3 {margin-top: 0.1rem; margin-bottom: 0.1rem;}
    div.stButton > button {width: 100%; padding: 0.2rem 0.4rem; font-size: 13px; height: auto;}
    .stExpander {margin-bottom: 0.3rem;}
    </style>
""", unsafe_allow_html=True)

# 1. Google Sheets Veri Yükleme ve Boşluk Temizliği
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    # Sütun isimlerindeki görünmez boşlukları temizle
    df.columns = df.columns.str.strip()
    # Hücrelerin içindeki gizli boşlukları temizle (Eşleşme hatasını önler)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    return df

df = load_data()

# Session State (Veri Depolama) Başlatma
if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

# Sol Menü Yapısı
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"])

bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]

# Ana Başlık
st.title("💊 Nextpharma Ziyaret Takip")

if menu == "Ziyaret Girişi":
    # 1. Bugün Ziyaret Edilenler Paneli (Üst Kısım)
    with st.expander(f"📋 Bugün Ziyaret Edilenler ({len(bugun_ziyaretleri)} Doktor)"):
        if bugun_ziyaretleri:
            for z in reversed(bugun_ziyaretleri):
                st.markdown(f"⏰ **{z['Saat']}** | {z['Doktor']} - {z['Brans']} ({z['Kurum']})")
        else:
            st.caption("Henüz bugün ziyaret kaydı girilmedi.")

    # 2. Doktor Arama Çubuğu
    arama_terimi = st.text_input("🔍 Doktor İsmi ile Ara:", placeholder="Doktor adı yazın...").strip().lower()

    st.markdown("### 🏢 Hastaneler (Ziyaret Durum Analizi)")

    # Filtreleme Mantığı
    if arama_terimi:
        df_goster = df[df['DOKTOR'].str.lower().str.contains(arama_terimi)]
    else:
        df_goster = df

    # Hastaneleri Alfabetik Olarak Expander Düzeninde Listeleme
    hastane_listesi = sorted(df_goster['KURUM'].unique().tolist())

    for hastane in hastane_listesi:
        df_hastane_doktorlari = df_goster[df_goster['KURUM'] == hastane]
        
        with st.expander(f"🏥 {hastane}"):
            for i, row in df_hastane_doktorlari.iterrows():
                # Mevcut doktorun bugün yapılan ziyaret sayısını bul
                yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
                kalan = int(row['FREKANS']) - yapilan
                
                # Kritik Durum Uyarı Etiketi
                uyari_etiketi = ""
                if kalan > 0 and kalan >= (int(row['FREKANS']) / 2):
                    uyari_etiketi = " <span style='color:#ffaa00; font-size:12px; font-weight:bold;'>[KRİTİK] ⚠️</span>"
                
                # Doktor Bilgisi Satırı
                st.markdown(f"<p style='margin-bottom:2px; margin-top:6px; font-size:14px;'><b>{row['DOKTOR']}</b> - {row['İHTİSAS']}{uyari_etiketi}</p>", unsafe_allow_html=True)
                
                # Butonları ve Kalan Bilgisini Yan Yana Hizalama
                cols = st.columns([1.5, 1.1, 1.1, 0.8])
                
                # Kalan Sayısı
                cols[0].markdown(f"<p style='font-size:13px; margin-top:5px;'>Kal: <b>{kalan}</b>/{row['FREKANS']}</p>", unsafe_allow_html=True)
                
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
                
                # İptal Et Butonu (Hatalı döngü ve parantez tamamen düzeltildi)
                if cols[2].button("İptal", key=f"i_{i}"):
                    gecmis = st.session_state.ziyaret_gecmisi
                    for j in range(len(gecmis) - 1, -1, -1):
                        if gecmis[j]['Doktor'] == row['DOKTOR']:
                            del st.session_state.ziyaret_gecmisi[j]
                            break
                    st.rerun()
                
                # Küçük Not Girişi İkonu
                with cols[3].expander("✍️"):
                    st.text_input(
                        "Not Ekle:", 
                        key=f"temp_not_{i}", 
                        placeholder="Not...",
                        label_visibility="collapsed"
                    )
                
                st.markdown("<div style='margin: 1px 0; border-bottom: 1px dashed #333;'></div>", unsafe_allow_html=True)

elif menu == "Bugün Ne Yaptım?":
    st.markdown(f"### 📋 Bugün Ne Yaptım? ({bugun_str})")
    st.markdown(f"Toplam Ziyaret: **{len(bugun_ziyaretleri)} Doktor**")
    st.markdown("---")
    
    if bugun_ziyaretleri:
        for z in reversed(bugun_ziyaretleri):
            st.markdown(f"⏰ **{z['Saat']}** | **{z['Doktor']}** ({z['Kurum']})")
            if z['Not'] != "Not eklenmedi.":
                st.info(f"💬 {z['Not']}")
            st.markdown("<div style='margin: 2px 0; border-bottom: 1px dashed #333;'></div>", unsafe_allow_html=True)
    else:
        st.info("Henüz ziyaret kaydı yok.")

elif menu == "Ziyaret Detay Raporu":
    st.markdown("### 📋 Ziyaret Raporu")
    rapor_tarihi = st.date_input("Tarih Seçin:", datetime.now())
    tarih_str = rapor_tarihi.strftime("%d/%m/%Y")
    
    gunluk_kayitlar = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == tarih_str]
    st.metric(label="Toplam Ziyaret", value=f"{len(gunluk_kayitlar)} Kişi")
    
    if gunluk_kayitlar:
        df_rapor = pd.DataFrame(gunluk_kayitlar).sort_values(by='Saat')
        for brans in df_rapor['Brans'].unique():
            with st.expander(f"🏥 {brans}"):
                brans_df = df_rapor[df_rapor['Brans'] == brans]
                for _, z in brans_df.iterrows():
                    st.write(f"✅ {z['Saat']} | **{z['Doktor']}** ({z['Kurum']})")
                    if z['Not'] != "Not eklenmedi.":
                        st.caption(f"💬 Not: {z['Not']}")
    else:
        st.warning("Seçilen tarihe ait kayıt bulunamadı.")

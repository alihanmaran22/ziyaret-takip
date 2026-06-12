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
    </style>
""", unsafe_allow_html=True)

# 1. Google Sheets Veri Yükleme ve Boşluk Temizliği
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    # Sütun isimlerindeki görünmez boşlukları temizle
    df.columns = df.columns.str.strip()
    # Hücrelerin içindeki gizli boşlukları temizle
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    return df

df = load_data()

# Session State Başlatma
if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

# Sol Menü Yapısı
menu = st.sidebar.radio(
    "Menü Seç:", 
    ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"]
)

bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [
    z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str
]

# Ana Başlık
st.title("💊 Nextpharma Ziyaret Takip")

if menu == "Ziyaret Girişi":
    # 1. Bugün Ziyaret Edilenler Paneli (Üst Kısım)
    panel_baslik = f"📋 Bugün Ziyaret Edilenler ({len(bugun_ziyaretleri)} Doktor)"
    with st.expander(panel_baslik):
        if bugun_ziyaretleri:
            for z in reversed(bugun_ziyaretleri):
                st.write(f"⏰ {z['Saat']} | {z['Doktor']} - {z['Brans']} ({z['Kurum']})")
        else:
            st.caption("Henüz bugün ziyaret kaydı girilmedi.")

    st.markdown("### 🔍 Kurum ve Branş Seçimi")

    hastane_listesi = sorted(df['KURUM'].unique().tolist())
    hastaneler = ['Lütfen hastane seçiniz...'] + hastane_listesi
    secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

    if secilen_hastane != 'Lütfen hastane seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        
        brans_listesi = sorted(df_filtre['İHTİSAS'].unique().tolist())
        branslar = ['Tümü'] + brans_listesi
        secilen_brans = st.selectbox("Branş Seç:", branslar)
        
        if secilen_brans != 'Tümü':
            df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
        
        st.markdown("---")
        
        if df_filtre.empty:
            st.warning("Bu kriterlere uygun doktor bulunamadı.")
        else:
            for i, row in df_filtre.iterrows():
                dr_adi = row['DOKTOR']
                dr_brans = row['İHTİSAS']
                dr_kurum = row['KURUM']
                dr_frekans = int(row['FREKANS'])
                
                yapilan = len([
                    z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == dr_adi
                ])
                kalan = dr_frekans - yapilan
                
                uyari_etiketi = ""
                if kalan > 0 and kalan >= (dr_frekans / 2):
                    uyari_etiketi = " ⚠️ [KRİTİK]"
                
                st.write(f"**{dr_adi}** - {dr_brans} {uyari_etiketi}")
                
                cols = st.columns([1.5, 1.1, 1.1, 0.8])
                cols[0].write(f"Kal: {kalan}/{dr_frekans}")
                
                if cols[1].button("Ziyaret", key=f"z_{i}"):
                    k_notu = st.session_state.get(f"temp_not_{i}", "").strip()
                    st.session_state.ziyaret_gecmisi.append({
                        "Doktor": dr_adi, 
                        "Tarih": bugun_str,
                        "Saat": datetime.now().strftime("%H:%M"),
                        "Kurum": dr_kurum, 
                        "Brans": dr_brans,
                        "Not": k_notu if k_notu else "Not eklenmedi."
                    })
                    if f"temp_not_{i}" in st.session_state:
                        del st.session_state[f"temp_not_{i}"]
                    st.rerun()
                
                if cols[2].button("İptal", key=f"i_{i}"):
                    gecmis = st.session_state.ziyaret_gecmisi
                    for j in range(len(gecmis) - 1, -1, -1):
                        if gecmis[j]['Doktor'] == dr_adi:
                            del st.session_state.ziyaret_gecmisi[j]
                            break
                    st.rerun()
                
                with cols[3].expander("✍️"):
                    st.text_input(
                        "Not:", 
                        key=f"temp_not_{i}", 
                        placeholder="Not...",
                        label_visibility="collapsed"
                    )
                
                st.markdown("<div style='margin: 1px 0; border-bottom: 1px dashed #333;'></div>", unsafe_allow_html=True)

elif menu == "Bugün Ne Yaptım?":
    st.markdown(f"### 📋 Bugün Ne Yaptım? ({bugun_str})")
    st.write(f"Toplam Ziyaret: **{len(bugun_ziyaretleri)} Doktor**")
    st.markdown("---")
    
    metin_parcalari = []
    
    if bugun_ziyaretleri:
        for z in reversed(bugun_ziyaretleri):
            st.write(f"⏰ {z['Saat']} | **{z['Doktor']}** ({z['Kurum']})")
            if z['Not'] != "Not eklenmedi.":
                st.info(f"💬 {z['Not']}")
                metin_parcalari.append(f"{z['Saat']} | {z['Doktor']} ({z['Kurum']}) -> Not: {z['Not']}")
            else:
                metin_parcalari.append(f"{z['Saat']} | {z['Doktor']} ({z['Kurum']})")
            st.markdown("---")
        
        tum_ziyaretler_metni = "\n".join(metin_parcalari)
        
        st.markdown("### 🚀 Füzyon Hızlı Aktarım Paneli")
        st.caption("Aşağıdaki kutunun sağ üst köşesindeki kopyalama butonuna basarak listeyi direkt alabilirsin kankam:")
        # Hatayı kökten çözen, eski-yeni tüm sürümlerde sorunsuz çalışan kopyalama alanı
        st.code(tum_ziyaretler_metni, language="text")
        
    else:
        st.info("Henüz ziyaret kaydı yok.")

elif menu == "Ziyaret Detay Raporu":
    st.markdown("### 📋 Ziyaret Raporu")
    rapor_tarihi = st.date_input("Tarih Seçin:", datetime.now())
    tarih_str = rapor_tarihi.strftime("%d/%m/%Y")
    
    gunluk_kayitlar = [
        z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == tarih_str
    ]
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

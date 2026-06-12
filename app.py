import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret")

# 2. Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=3600)
def load_data():
    return pd.read_csv(SHEET_URL)

df = load_data()

# 3. Ziyaret Geçmişini Başlat
if 'ziyaretler' not in st.session_state:
    st.session_state.ziyaretler = []

st.title("💊 Nextpharma Ziyaret Takip")

# 4. ARAMA VE EKLEME PANELİ
st.subheader("🔍 Doktor Ekle")
hastane = st.selectbox("Hastane Seç:", ['Seçiniz...'] + sorted(df['KURUM'].unique().tolist()))

if hastane != 'Seçiniz...':
    df_f = df[df['KURUM'] == hastane]
    brans = st.selectbox("Branş Seç:", ['Tümü'] + sorted(df_f['İHTİSAS'].unique().tolist()))
    if brans != 'Tümü':
        df_f = df_f[df_f['İHTİSAS'] == brans]
    
    # Doktorları listele ve ekle butonları
    for i, row in df_f.iterrows():
        if st.button(f"➕ {row['DOKTOR']}", key=f"dr_{i}"):
            st.session_state.ziyaretler.append({
                "Doktor": row['DOKTOR'],
                "Kurum": row['KURUM'],
                "Brans": row['İHTİSAS']
            })
            st.success(f"{row['DOKTOR']} eklendi!")

# 5. BUGÜN ZİYARET EDİLENLER VE SİLME (Burası senin istediğin liste)
st.divider()
st.subheader("📋 Bugün Ziyaret Edilenler")
for idx, z in enumerate(st.session_state.ziyaretler):
    c1, c2 = st.columns([4, 1])
    c1.write(f"✅ {z['Doktor']} ({z['Kurum']})")
    if c2.button("❌", key=f"del_{idx}"):
        del st.session_state.ziyaretler[idx]
        st.rerun()

# 6. FÜZYON AKTARIM PANELİ
st.divider()
st.subheader("🚀 Füzyon Hızlı Aktarım")
if st.session_state.ziyaretler:
    metin = ""
    df_temp = pd.DataFrame(st.session_state.ziyaretler)
    # Gruplandırılmış format
    for kurum in df_temp['Kurum'].unique():
        metin += f"■ {kurum.upper()}\n"
        for brans in df_temp[df_temp['Kurum'] == kurum]['Brans'].unique():
            metin += f"  • {brans.upper()}\n"
            for dr in df_temp[(df_temp['Kurum'] == kurum) & (df_temp['Brans'] == brans)]['Doktor']:
                metin += f"    - {dr}\n"
    
    st.text_area("Bu metni kopyala:", value=metin, height=250)
else:
    st.info("Henüz ziyaret kaydı yok.")

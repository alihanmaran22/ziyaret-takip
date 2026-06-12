import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_browser_storage import local_storage

st.set_page_config(layout="centered", page_title="Nextpharma Kalıcı Ziyaret")

# 1. Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# 2. Kalıcı Hafıza (Local Storage) Yönetimi
ziyaretler = local_storage.getItem(key="ziyaret_gecmisi")
if ziyaretler is None:
    ziyaretler = []

def save_to_storage(data):
    local_storage.setItem(key="ziyaret_gecmisi", value=data)

# Sol Menü
menu = st.sidebar.radio("Menü:", ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Geçmiş Rapor"])

st.title("💊 Nextpharma Kalıcı")

if menu == "Ziyaret Girişi":
    # Ziyaret Edilenler
    with st.expander(f"📋 Bugün Ziyaret Edilenler ({len([z for z in ziyaretler if z['Tarih'] == datetime.now().strftime('%d/%m/%Y')])})"):
        for z in reversed(ziyaretler):
            if z['Tarih'] == datetime.now().strftime('%d/%m/%Y'):
                col1, col2 = st.columns([4, 1])
                col1.write(f"{z['Doktor']} ({z['Kurum']})")
                if col2.button("❌", key=f"del_{z['id']}"):
                    ziyaretler = [item for item in ziyaretler if item['id'] != z['id']]
                    save_to_storage(ziyaretler)
                    st.rerun()

    # Seçim
    hastane = st.selectbox("Hastane:", ['Seçiniz...'] + sorted(df['KURUM'].unique().tolist()))
    if hastane != 'Seçiniz...':
        df_f = df[df['KURUM'] == hastane]
        brans = st.selectbox("Branş:", ['Tümü'] + sorted(df_f['İHTİSAS'].unique().tolist()))
        if brans != 'Tümü': df_f = df_f[df_f['İHTİSAS'] == brans]
        
        for i, row in df_f.iterrows():
            if st.button(f"Ziyaret Ekle: {row['DOKTOR']}", key=f"z_{i}"):
                ziyaretler.append({
                    "id": f"{time.time()}", "Doktor": row['DOKTOR'], 
                    "Tarih": datetime.now().strftime('%d/%m/%Y'),
                    "Kurum": row['KURUM'], "Brans": row['İHTİSAS']
                })
                save_to_storage(ziyaretler)
                st.rerun()

elif menu == "Bugün Ne Yaptım?":
    st.markdown("### 🚀 Füzyon Hızlı Aktarım")
    df_bugun = pd.DataFrame([z for z in ziyaretler if z['Tarih'] == datetime.now().strftime('%d/%m/%Y')])
    if not df_bugun.empty:
        metin = ""
        for hastane in df_bugun['Kurum'].unique():
            metin += f"■ {hastane.upper()}\n"
            for brans in df_bugun[df_bugun['Kurum'] == hastane]['Brans'].unique():
                metin += f"  • {brans.upper()}\n"
                for dr in df_bugun[(df_bugun['Kurum'] == hastane) & (df_bugun['Brans'] == brans)]['Doktor']:
                    metin += f"    - {dr}\n"
            metin += "\n"
        st.code(metin, language="text")

elif menu == "Geçmiş Rapor":
    st.markdown("### 📅 Tüm Ziyaret Geçmişin")
    for z in reversed(ziyaretler):
        st.write(f"✅ {z['Tarih']} | {z['Doktor']} ({z['Kurum']})")

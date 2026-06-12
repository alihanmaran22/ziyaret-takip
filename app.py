import streamlit as st
import pandas as pd
from datetime import datetime
import time
from streamlit_browser_storage import Storage

# Kalıcı hafıza için Storage nesnesini başlatıyoruz
storage = Storage()

st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")

# Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Hafızadan veriyi çekme
ziyaretler = storage.getItem(key="ziyaret_gecmisi")
if ziyaretler is None:
    ziyaretler = []

def save_storage(data):
    storage.setItem(key="ziyaret_gecmisi", value=data)

# Sol Menü
menu = st.sidebar.radio("Menü:", ["Ziyaret Girişi", "Bugün Ne Yaptım?"])

st.title("💊 Nextpharma Ziyaret")

if menu == "Ziyaret Girişi":
    # Bugünün listesi
    bugun = datetime.now().strftime('%d/%m/%Y')
    
    with st.expander(f"📋 Bugün Ziyaret Edilenler"):
        for z in ziyaretler:
            if z.get('Tarih') == bugun:
                st.write(f"{z['Doktor']} ({z['Kurum']})")
    
    # Seçim
    hastane = st.selectbox("Hastane:", ['Seçiniz...'] + sorted(df['KURUM'].unique().tolist()))
    if hastane != 'Seçiniz...':
        df_f = df[df['KURUM'] == hastane]
        brans = st.selectbox("Branş:", ['Tümü'] + sorted(df_f['İHTİSAS'].unique().tolist()))
        if brans != 'Tümü': df_f = df_f[df_f['İHTİSAS'] == brans]
        
        for i, row in df_f.iterrows():
            if st.button(f"Ziyaret Ekle: {row['DOKTOR']}", key=f"z_{i}"):
                yeni_kayit = {
                    "id": str(time.time()), 
                    "Doktor": row['DOKTOR'], 
                    "Tarih": bugun,
                    "Kurum": row['KURUM'], 
                    "Brans": row['İHTİSAS']
                }
                ziyaretler.append(yeni_kayit)
                save_storage(ziyaretler)
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
    else:
        st.info("Henüz ziyaret kaydı yok.")

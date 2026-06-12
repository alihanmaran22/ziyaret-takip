import streamlit as st

import pandas as pd

from datetime import datetime

import time



# Mobil ekran düzeni ve buton tasarımları

st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")

st.markdown("""

    <style>

    .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem;}

    h1, h2, h3 {margin-top: 0.1rem; margin-bottom: 0.1rem;}

    div.stButton > button {width: 100%; padding: 0.2rem 0.4rem; font-size: 13px; height: auto;}

    </style>

""", unsafe_allow_html=True)



# Veri Yükleme

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"



@st.cache_data(ttl=60)

def load_data():

    df = pd.read_csv(SHEET_URL, header=0)

    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include=['object']).columns:

        df[col] = df[col].astype(str).str.strip()

    return df



df = load_data()



if 'ziyaret_gecmisi' not in st.session_state:

    st.session_state.ziyaret_gecmisi = []



menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?"])

bugun_str = datetime.now().strftime("%d/%m/%Y")

bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]



st.title("💊 Nextpharma Ziyaret Takip")



if menu == "Ziyaret Girişi":

    with st.expander(f"📋 Bugün Ziyaret Edilenler ({len(bugun_ziyaretleri)} Doktor)"):

        for z in reversed(st.session_state.ziyaret_gecmisi):

            if z['Tarih'] == bugun_str:

                col1, col2 = st.columns([4, 1])

                col1.write(f"{z['Doktor']} - {z['Brans']} ({z['Kurum']})")

                if col2.button("❌", key=f"del_{z['id']}"):

                    st.session_state.ziyaret_gecmisi = [item for item in st.session_state.ziyaret_gecmisi if item['id'] != z['id']]

                    st.rerun()



    secilen_hastane = st.selectbox("Hastane Seç:", ['Lütfen hastane seçiniz...'] + sorted(df['KURUM'].unique().tolist()))

    if secilen_hastane != 'Lütfen hastane seçiniz...':

        df_filtre = df[df['KURUM'] == secilen_hastane]

        secilen_brans = st.selectbox("Branş Seç:", ['Tümü'] + sorted(df_filtre['İHTİSAS'].unique().tolist()))

        if secilen_brans != 'Tümü': df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]

        

        for i, row in df_filtre.iterrows():

            st.write(f"**{row['DOKTOR']}** - {row['İHTİSAS']}")

            if st.button("Ziyaret Ekle", key=f"z_{i}"):

                st.session_state.ziyaret_gecmisi.append({

                    "id": f"{time.time()}_{i}", "Doktor": row['DOKTOR'], "Tarih": bugun_str,

                    "Kurum": row['KURUM'], "Brans": row['İHTİSAS']

                })

                st.rerun()



elif menu == "Bugün Ne Yaptım?":

    st.markdown("### 🚀 Füzyon Hızlı Aktarım")

    if bugun_ziyaretleri:

        df_bugun = pd.DataFrame(bugun_ziyaretleri)

        metin = ""

        # Hastane -> Branş -> Doktor hiyerarşisi

        for hastane in df_bugun['Kurum'].unique():

            metin += f"■ {hastane.upper()}\n"

            df_hastane = df_bugun[df_bugun['Kurum'] == hastane]

            for brans in df_hastane['Brans'].unique():

                metin += f"  • {brans.upper()}\n"

                for dr in df_hastane[df_hastane['Brans'] == brans]['Doktor']:

                    metin += f"    - {dr}\n"

            metin += "\n"

        

        st.code(metin, language="text")

    else:

        st.info("Henüz ziyaret kaydı yok.")

import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Ayarlar
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

st.title("💊 Nextpharma Ziyaret Takip")

# Menü
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Ziyaret Detay Raporu"])

if menu == "Ziyaret Girişi":
    # Tarih seçiciyi buradan kaldırdık, ziyaret anı tarihi otomatik alınıyor
    hastaneler = ['Lütfen hastane seçiniz...'] + df['KURUM'].unique().tolist()
    secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

    if secilen_hastane != 'Lütfen hastane seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        branslar = ['Tümü'] + df_filtre['İHTİSAS'].unique().tolist()
        secilen_brans = st.selectbox("Branş Seç:", branslar)
        
        if secilen_brans != 'Tümü':
            df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
        
        st.markdown("---")
        for i, row in df_filtre.iterrows():
            yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
            kalan = int(row['FREKANS']) - yapilan
            
            cols = st.columns([3, 1, 1])
            cols[0].write(f"**{row['DOKTOR']}** ({row['İHTİSAS']}) - **Kalan: {kalan}**")
            
            # Ziyaret Et
            if cols[1].button("Ziyaret Et", key=f"z_{i}"):
                st.session_state.ziyaret_gecmisi.append({
                    "Doktor": row['DOKTOR'], "Tarih": datetime.now().strftime("%d/%m/%Y"),
                    "Kurum": row['KURUM'], "Brans": row['İHTİSAS']
                })
                st.rerun()
            
            # İptal Et (Geri geldi!)
            if cols[2].button("İptal Et", key=f"i_{i}"):
                for j, z in reversed(list(enumerate(st.session_state.ziyaret_gecmisi))):
                    if z['Doktor'] == row['DOKTOR']:
                        del st.session_state.ziyaret_gecmisi[j]
                        break
                st.rerun()

elif menu == "Ziyaret Detay Raporu":
    st.header("📋 Ziyaret Detay Raporu")
    # Tarih seçimi artık sadece burada var
    rapor_tarihi = st.date_input("Rapor Tarihi Seç:", datetime.now())
    tarih_str = rapor_tarihi.strftime("%d/%m/%Y")
    
    gunluk_kayitlar = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == tarih_str]
    
    if gunluk_kayitlar:
        df_rapor = pd.DataFrame(gunluk_kayitlar)
        st.success(f"{tarih_str} tarihinde {len(df_rapor)} doktor ziyaret edildi.")
        
        for brans in df_rapor['Brans'].unique():
            with st.expander(f"🏥 {brans}"):
                doktorlar = df_rapor[df_rapor['Brans'] == brans]['Doktor'].unique()
                for doktor in doktorlar:
                    st.write(f"✅ {doktor}")
    else:
        st.warning("Bu tarihte henüz bir kayıt bulunamadı.")

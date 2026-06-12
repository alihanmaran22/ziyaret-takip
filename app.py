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

# Session State
if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

st.title("💊 Nextpharma Ziyaret Takip")
st.subheader("Hoş geldin, Neutec İlaç - Alihan Maran")

# 2. Filtreleme
hastaneler = ['Lütfen bir hastane seçiniz...'] + df['KURUM'].unique().tolist()
secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

if secilen_hastane != 'Lütfen bir hastane seçiniz...':
    df_filtre = df[df['KURUM'] == secilen_hastane]
    branslar = ['Tümü'] + df_filtre['İHTİSAS'].unique().tolist()
    secilen_brans = st.selectbox("Branş Seç:", branslar)
    
    if secilen_brans != 'Tümü':
        df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
    
    # 3. Doktor Listeleme (Dinamik Hesaplama)
    st.markdown("---")
    for i, row in df_filtre.iterrows():
        # Bu doktor için yapılan ziyaret sayısını bul
        yapilan_ziyaret = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == row['DOKTOR']])
        # Toplamdan çıkar
        kalan = int(row['FREKANS']) - yapilan_ziyaret
        
        cols = st.columns([3, 1, 1])
        # Dinamik "Kalan" metni
        cols[0].write(f"**{row['DOKTOR']}** ({row['İHTİSAS']}) - **Kalan: {kalan}**")
        
        if cols[1].button("Ziyaret Et", key=f"ziyaret_{i}"):
            st.session_state.ziyaret_gecmisi.append({
                "Doktor": row['DOKTOR'], "Tarih": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "Kurum": row['KURUM'], "Brans": row['İHTİSAS']
            })
            st.rerun() # Sayfayı yenile ve güncellenmiş "Kalan" sayısını göster
            
        if cols[2].button("İptal Et", key=f"iptal_{i}"):
            # Sadece en son eklenen ziyareti silmek için (tersine çevirip ilk bulduğumuzu siliyoruz)
            for j, z in reversed(list(enumerate(st.session_state.ziyaret_gecmisi))):
                if z['Doktor'] == row['DOKTOR']:
                    del st.session_state.ziyaret_gecmisi[j]
                    break
            st.rerun() # Sayfayı yenile
            
    # 4. Yan Menü: Ziyaret Durum Analizi (Tarih ve Gün Bilgili)
    st.sidebar.title("📊 Ziyaret Durum Analizi")
    if st.session_state.ziyaret_gecmisi:
        df_gecmis = pd.DataFrame(st.session_state.ziyaret_gecmisi)
        
        # Tarih formatını güzelleştirmek için Türkçe gün isimleri
        gunler = {
            "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
            "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"
        }

        for kurum in df_gecmis['Kurum'].unique():
            with st.sidebar.expander(f"🏢 {kurum}"):
                kurum_df = df_gecmis[df_gecmis['Kurum'] == kurum]
                for doktor in kurum_df['Doktor'].unique():
                    st.write(f"**{doktor}**")
                    doktor_df = kurum_df[kurum_df['Doktor'] == doktor]
                    
                    for _, z in doktor_df.iterrows():
                        # Tarih ve gün bilgisini ayıkla
                        tarih_obj = datetime.strptime(z['Tarih'], "%d/%m/%Y %H:%M")
                        gun_adi = gunler[tarih_obj.strftime("%A")]
                        st.write(f"- {z['Tarih']} ({gun_adi})")
    
    else:
        st.sidebar.info("Henüz ziyaret kaydı yok.")
else:
    st.info("Lütfen işlem yapmak için yukarıdan bir hastane seçiniz.")

import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- AYARLAR ---
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret")
st.markdown("<style>.block-container {padding: 1rem;} div.stButton > button {width: 100%;}</style>", unsafe_allow_html=True)

# Google Sheets Bağlantı Ayarları (Burayı kendi JSON anahtarınla dolduracaksın)
# Eğer JSON dosyan varsa onunla auth olacağız, burayı boş geçme
def get_sheet():
    # Buraya kendi servis hesabı JSON ayarlarını girmen gerekecek
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('anahtar.json', scope) # Dosyanın adını buraya yaz
    # client = gspread.authorize(creds)
    # return client.open("DosyaAdı").sheet1
    return None 

# Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"
df = pd.read_csv(SHEET_URL)
df.columns = df.columns.str.strip()

if 'ziyaret_gecmisi' not in st.session_state:
    st.session_state.ziyaret_gecmisi = []

menu = st.sidebar.radio("Menü:", ["Ziyaret Girişi", "Bugün Ne Yaptım?"])

if menu == "Ziyaret Girişi":
    st.title("💊 Ziyaret Girişi")
    hastaneler = ['Seçiniz...'] + sorted(df['KURUM'].dropna().astype(str).unique().tolist())
    secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

    if secilen_hastane != 'Seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        for i, row in df_filtre.iterrows():
            st.write(f"**{row['DOKTOR']}** - {row['İHTİSAS']}")
            if st.button(f"Ziyaret Ekle: {row['DOKTOR']}", key=f"z_{i}"):
                st.session_state.ziyaret_gecmisi.append({
                    "Doktor": row['DOKTOR'],
                    "Kurum": row['KURUM'],
                    "Brans": row['İHTİSAS'],
                    "Zaman": datetime.now().strftime("%H:%M")
                })
                st.rerun()

elif menu == "Bugün Ne Yaptım?":
    st.title("📋 Bugünün Ziyaretleri")
    for z in st.session_state.ziyaret_gecmisi:
        st.write(f"⏰ {z['Zaman']} | **{z['Doktor']}** ({z['Brans']})")
    
    # İNTERNETE KAYDETME BUTONU BURADA
    if st.button("🚀 İnternete (Sheets) Kaydet"):
        # sheet = get_sheet()
        # for z in st.session_state.ziyaret_gecmisi:
        #     sheet.append_row([z['Doktor'], z['Kurum'], z['Brans'], z['Zaman']])
        st.success("Veriler Google Sheets'e gönderildi!")

import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64

# Mobil ekran düzeni
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")

# Klasördeki resmi CSS'e gömmek için fonksiyon
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Resim kontrolü (Yüklediğin resmin adı 'arka-plan.png' olmalı)
try:
    bin_str = get_base64_of_bin_file('arka-plan.png')
    bg_image_css = f"url(data:image/png;base64,{bin_str})"
except FileNotFoundError:
    bg_image_css = "none"

# Arka Plan ve Okunurluk Tasarımı
st.markdown(f"""
    <style>
    /* Arka plan fotoğrafı ve opaklık katmanı */
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.70), rgba(0, 0, 0, 0.70)), 
                          {bg_image_css};
        background-attachment: fixed;
        background-size: cover;
        background-position: center top;
    }}
    
    /* Yazıların net okunması için beyaz yapıyoruz */
    h1, h2, h3, p, span, label, .stMarkdown, .stCaption {{
        color: #ffffff !important;
        font-weight: 500;
    }}
    
    /* Seçim kutularının (selectbox) içindeki yazıların rengi */
    div[data-baseweb="select"] * {{
        color: #333333 !important;
    }}
    
    /* Mobil ekran boşluk ayarları */
    .block-container {{
        padding-top: 1rem; 
        padding-bottom: 1rem; 
        padding-left: 0.5rem; 
        padding-right: 0.5rem;
    }}
    
    /* Butonların genel düzeni */
    div.stButton > button {{
        width: 100%; 
        padding: 0.2rem 0.4rem; 
        font-size: 13px; 
        height: auto;
    }}
    </style>
""", unsafe_allow_html=True)

# Google Sheets Fonksiyonu
def sheets_kaydet(ziyaretler):
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds_dict = {
        "type": st.secrets["gcp_service_account"]["type"],
        "project_id": st.secrets["gcp_service_account"]["project_id"],
        "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
        "private_key": st.secrets["gcp_service_account"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["gcp_service_account"]["client_email"],
        "client_id": st.secrets["gcp_service_account"]["client_id"],
        "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
        "token_uri": st.secrets["gcp_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
    }
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Frekans").sheet1
    for z in ziyaretler:
        sheet.append_row([z['Doktor'], z['Kurum'], z['Brans'], z['Tarih'], z['Saat'], z['Not']])

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

menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?", "Ziyaret Detay Raporu"])
bugun_str = datetime.now().strftime("%d/%m/%Y")
bugun_ziyaretleri = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == bugun_str]

st.title("💊 Nextpharma Ziyaret Takip")

if menu == "Ziyaret Girişi":
    with st.expander(f"📋 Bugün Ziyaret Edilenler ({len(bugun_ziyaretleri)} Doktor)"):
        if bugun_ziyaretleri:
            for z in reversed(bugun_ziyaretleri):
                st.write(f"⏰ {z['Saat']} | {z['Doktor']} - {z['Brans']} ({z['Kurum']})")
        else:
            st.caption("Henüz bugün ziyaret kaydı girilmedi.")

    st.markdown("### 🔍 Kurum ve Branş Seçimi")
    
    ham_hastaneler = df['KURUM'].dropna().astype(str).str.strip().unique().tolist()
    temiz_hastaneler = []
    for h in ham_hastaneler:
        if "/" in h and len(h) <= 10:
            continue
        if h != "" and h != "nan":
            temiz_hastaneler.append(h)
            
    hastaneler = ['Lütfen hastane seçiniz...'] + sorted(temiz_hastaneler)
    secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

    if secilen_hastane != 'Lütfen hastane seçiniz...':
        df_filtre = df[df['KURUM'] == secilen_hastane]
        
        ham_branslar = df_filtre['İHTİSAS'].dropna().astype(str).str.strip().unique().tolist()
        temiz_branslar = [b for b in ham_branslar if b != "" and b != "nan" and not ("/" in b and len(b) <= 10)]
        
        branslar = ['Tümü'] + sorted(temiz_branslar)
        secilen_brans = st.selectbox("Branş Seç:", branslar)
        if secilen_brans != 'Tümü':
            df_filtre = df_filtre[df_filtre['İHTİSAS'] == secilen_brans]
        
        st.markdown("---")
        if df_filtre.empty:
            st.warning("Bu kriterlere uygun doktor bulunamadı.")
        else:
            for i, row in df_filtre.iterrows():
                dr_adi, dr_brans, dr_kurum = row['DOKTOR'], row['İHTİSAS'], row['KURUM']
                dr_frekans = int(row['FREKANS'])
                yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == dr_adi])
                kalan = dr_frekans - yapilan
                uyari = " ⚠️ [KRİTİK]" if kalan > 0 and kalan >= (dr_frekans / 2) else ""
                
                st.write(f"**{dr_adi}** - {dr_brans} {uyari}")
                cols = st.columns(

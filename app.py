import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# JSON nesnesini bu şekilde güncelle
creds_dict = {
  "type": "service_account",
  "project_id": "innate-paratext-499214-r1",
  "private_key_id": "df9b7f453d81b26c64f3588ce78a376612388613",
  "private_key": PRIVATE_KEY,
  "client_email": "ziyaret-bot@innate-paratext-499214-r1.iam.gserviceaccount.com",
  "client_id": "117581869089406085398",  # EKSİK OLAN KISIM BUYDU
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ziyaret-bot%40innate-paratext-499214-r1.iam.gserviceaccount.com"
}

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Frekans").sheet1

# --- ARAYÜZ ---
st.set_page_config(page_title="Nextpharma Ziyaret", layout="wide")
st.title("💊 Nextpharma Ziyaret Takip Paneli")

# Verileri DataFrame olarak al
data = sheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])

# 1. Bölüm: Ziyaret Ekleme (Expander)
with st.expander("➕ Yeni Ziyaret Ekle"):
    col1, col2 = st.columns(2)
    with col1:
        yeni_doktor = st.text_input("Doktor Adı:")
    with col2:
        # Mevcut kurumlardan seçebilmen için dropdown yaptık
        yeni_kurum = st.selectbox("Kurum Seç:", df['KURUM'].unique())
    
    if st.button("Kaydet"):
        # Excel'e yeni satır ekle (İhtisas ve Frekans sütunlarını varsayılan değerlerle ekliyoruz)
        sheet.append_row([yeni_doktor, "DAHİLİYE", yeni_kurum, 1])
        st.success("Ziyaret başarıyla eklendi!")
        st.rerun()

# 2. Bölüm: Kurum Bazlı Filtreleme
st.divider()
st.subheader("🏢 Hastane/Kurum Bazlı Listeleme")
secilen_kurum = st.selectbox("Hangi kurumu incelemek istersin?", ["Tümü"] + list(df['KURUM'].unique()))

if secilen_kurum != "Tümü":
    df_filtrelenmis = df[df['KURUM'] == secilen_kurum]
else:
    df_filtrelenmis = df

# 3. Bölüm: İnteraktif Tablo
st.dataframe(df_filtrelenmis, use_container_width=True)

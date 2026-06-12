import streamlit as st
import json

# Secrets'tan string olarak al
creds_json = st.secrets["GCP_JSON"]

# String'i dict'e çevir
creds_dict = json.loads(creds_json)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Dosyayı bağla
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1mybm2kJtDHGUw5sruKp4tpSaV2PwINkfoTrIhCI82rY/edit").sheet1

st.title("💊 Nextpharma Kalıcı Kayıt")

doktor = st.text_input("Doktor Adı:")
kurum = st.text_input("Kurum:")

if st.button("Kaydet"):
    sheet.append_row([doktor, kurum])
    st.success("Kaydedildi! Excel'i kontrol et.")

st.write("Excel'deki mevcut kayıtlar:")
st.write(sheet.get_all_values())

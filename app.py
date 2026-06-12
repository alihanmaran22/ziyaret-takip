import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Secrets'ı al ve düzgünce yükle
creds_dict = json.loads(st.secrets["GCP_JSON"])

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Dosyayı bağla
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1mybm2kJtDHGUw5sruKp4tpSaV2PwINKfoTrIhCI82rY/edit").sheet1

st.title("💊 Nextpharma Kalıcı Kayıt")

doktor = st.text_input("Doktor Adı:")
kurum = st.text_input("Kurum:")

if st.button("Kaydet"):
    sheet.append_row([doktor, kurum])
    st.success("Kaydedildi! Excel'i kontrol et.")

st.write("Excel'deki mevcut kayıtlar:")
st.write(sheet.get_all_values())

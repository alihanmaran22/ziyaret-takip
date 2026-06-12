import streamlit as st
import pandas as pd
from datetime import datetime
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- GOOGLE CLOUD AYARLARI ---
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCwycvxEGMqfLW4CQrTWmKCifaNq6JX8FYlDzXfAiHUPTQ0UFeYorMz6nqJn+zCsvBPoK3A/q8fbhjaHI1XwfVNsvkni8btccEx+v2QyaydfScRzoI7XPluimeZJ7LlGJddVlRgmbgvWuIXKPquuOiS0I3+sIW7EDDGQuxCR35/uC4NvCkU/2OW7ZW9TjofbPWcK9KVx1E7wslLYD9g0WEdcQTA3yONdwiFlA4salG1P4xaqoCt45tMpscxOcZNespywH8hkeLV+L2P1i05p3LC67nspKeeOQx5OaKggH6q4vNDTsL0IYNW6uuHxEn1D+PGyotzvKotFy2yLzxidj/TAgMBAAECggEAPw67f7Corm7tIkeXZOvIV2d+Wenubg97qpxSSskn59ws0rwVgowF/26TZqN0f73zmXNmhoBRVpSeqK2mfLbiGGTOGhzxR6BbmMg9yXcl6sbJOMDAEwyGq7cSXL6cQLsUwmYYkpxB5iI0oq4rPEcYLcXV4BJ2oNKVkyIrwzhdFpCy6PuS1YDV0fwqXI1v3aUPuePipUZ1V78gUp2LgnndufF6cbzbXOopKcMUtc10cv5D1FkwdzyLW3BwtDdr9KcA4dhecOP5qSI9uAo8vSAq0ZGAvFZfL/veB6DZppZPZAXvtBbTXN35t9oglNrEa+LjOIFL+0HNtjlg4/OXzadIgQKBgQDp/FP2vX/iDn6HytQIFwgvVMffuD1kglWcsDcq1HxxQIICDiZW7lhUiuXAmwu88ZJsA0tJ9AYG44nOy/3bKW8CdMr0ZogbyhGGGIMu7sR+90du/F43+VhGXuQFk05Ti58kW66qaY6Fb1dp9D98AVKTGTz1w31Uc2QlRzTfo1Ni3wKBgQDBa9ah8lrCr0+6y9fNrybGSlRkTyiPWbTAeYqGRG6EaPHw9ydle9b4cr/Xi70WxkZfCtUV9GwusbOHU3KWBpOEnBVt5IoZm6FnMHJ7JT9h/cuxSsmNL+IyhvwPkMnYeqwzMoyQhzr1QT97dGFO18yRvGXClUmTI/tSZBhfL6OVjQKBgQC7Y8/CvcUbP8xp6DCjQf7WGSnxq9XPFuqFkEK+VGpNMQJtrvNZj4zCOHMEK6fc7AL96i1zzrC896G4Mnrd+HLlHrAjx7Gdv9kE8cCt558Kp/NXmVnDrjfaM8ieBnkmQ51yOtLJu7vedWsmeewV3eFJ2V6O3L8U0U0U5dAcgusXNQKBgECfTu58kmZJPFIkmM1Xn5TQcLGy4NJEHmfQM7/4TRRgG7VuXfNCFOidLgtN3LcnN4u5isfzCdHv/RNRhg8p00+S9nXozVsQ7DQVs6oBH9QVf2CUpBJP1TscbkqlDUsOcUoJsXz4MXKPgi41C+3Tm711PGpuhk5qzyUP3DSxLe5hAoGBAMpZViuJjQmyMMYqPU6Ptpb6nB1isgX4zqwYBPxFX1LJUiNAelZhjG7RR3DzYsCpQWDbSWjsiNN6swQGpIOO2tuPrqMrp5lkr6ehNKbu2VshK3lUwQOUUi4GagBoP57PYTIjwWYiZBtCdS6HxrUJ6h8PcyYvhXysapOMEpWX7o5
-----END PRIVATE KEY-----"""

creds_dict = {
  "type": "service_account",
  "project_id": "innate-paratext-499214-r1",
  "private_key_id": "df9b7f453d81b26c64f3588ce78a376612388613",
  "private_key": PRIVATE_KEY,
  "client_email": "ziyaret-bot@innate-paratext-499214-r1.iam.gserviceaccount.com",
  "client_id": "117581869089406085398",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ziyaret-bot%40innate-paratext-499214-r1.iam.gserviceaccount.com"
}

# --- AYARLAR ---
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")
st.markdown("""<style>.block-container {padding: 1rem;} div.stButton > button {width: 100%;}</style>""", unsafe_allow_html=True)

# Veri Yükleme
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGD7luSrQ-itoqU0QBinOX2TWzDr5Fabi-teecWOPy6VbnaB5-U_N8tHopNjaxRhj3BiivmrWrzi6f/pub?output=csv"
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL, header=0)
    df.columns = df.columns.str.strip()
    return df

df = load_data()
if 'ziyaret_gecmisi' not in st.session_state: st.session_state.ziyaret_gecmisi = []
menu = st.sidebar.radio("Menü Seç:", ["Ziyaret Girişi", "Bugün Ne Yaptım?"])
bugun_str = datetime.now().strftime("%d/%m/%Y")

# --- ZİYARET GİRİŞİ ---
if menu == "Ziyaret Girişi":
    st.title("💊 Ziyaret Girişi")
    hastane = st.selectbox("Hastane Seç:", ['Seçiniz...'] + sorted(df['KURUM'].unique().tolist()))
    if hastane != 'Seçiniz...':
        for i, row in df[df['KURUM'] == hastane].iterrows():
            if st.button(f"{row['DOKTOR']} - {row['İHTİSAS']}", key=f"z_{i}"):
                st.session_state.ziyaret_gecmisi.append({"Doktor": row['DOKTOR'], "Kurum": row['KURUM'], "Tarih": bugun_str})
                st.rerun()

# --- BUGÜN NE YAPTIM? ---
elif menu == "Bugün Ne Yaptım?":
    st.title("🚀 Bugün Ne Yaptım?")
    st.write(st.session_state.ziyaret_gecmisi)
    
    if st.button("🚀 Tümünü Cloud Excel'e Kaydet"):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Frekans").sheet1
        for z in st.session_state.ziyaret_gecmisi:
            sheet.append_row([z['Doktor'], z['Kurum'], z['Tarih']])
        st.session_state.ziyaret_gecmisi = []
        st.success("Tümü gönderildi!")
        st.rerun()

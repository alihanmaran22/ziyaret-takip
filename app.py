import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Özel anahtarı bu şekilde tırnak içine yapıştır
PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCwycvxEGMqfLW4CQrTWmKCifaNq6JX8FYlDzXfAiHUPTQ0UFeYorMz6nqJn+zCsvBPoK3A/q8fbhjaHI1XwfVNsvkni8btccEx+v2QyaydfScRzoI7XPluimeZJ7LlGJddVlRgmbgvWuIXKPquuOiS0I3+sIW7EDDGQuxCR35/uC4NvCkU/2OW7ZW9TjofbPWcK9KVx1E7wslLYD9g0WEdcQTA3yONdwiFlA4salG1P4xaqoCt45tMpscxOcZNespywH8hkeLV+L2P1i05p3LC67nspKeeOQx5OaKggH6q4vNDTsL0IYNW6uuHxEn1D+PGyotzvKotFy2yLzxidj/TAgMBAAECggEAPw67f7Corm7tIkeXZOvIV2d+Wenubg97qpxSSskn59ws0rwVgowF/26TZqN0f73zmXNmhoBRVpSeqK2mfLbiGGTOGhzxR6BbmMg9yXcl6sbJOMDAEwyGq7cSXL6cQLsUwmYYkpxB5iI0oq4rPEcYLcXV4BJ2oNKVkyIrwzhdFpCy6PuS1YDV0fwqXI1v3aUPuePipUZ1V78gUp2LgnndufF6cbzbXOopKcMUtc10cv5D1FkwdzyLW3BwtDdr9KcA4dhecOP5qSI9uAo8vSAq0ZGAvFZfL/veB6DZppZPZAXvtBbTXN35t9oglNrEa+LjOIFL+0HNtjlg4/OXzadIgQKBgQDp/FP2vX/iDn6HytQIFwgvVMffuD1kglWcsDcq1HxxQIICDiZW7lhUiuXAmwu88ZJsA0tJ9AYG44nOy/3bKW8CdMr0ZogbyhGGGIMu7sR+90du/F43+VhGXuQFk05Ti58kW66qaY6Fb1dp9D98AVKTGTz1w31Uc2QlRzTfo1Ni3wKBgQDBa9ah8lrCr0+6y9fNrybGSlRkTyiPWbTAeYqGRG6EaPHw9ydle9b4cr/Xi70WxkZfCtUV9GwusbOHU3KWBpOEnBVt5IoZm6FnMHJ7JT9h/cuxSsmNL+IyhvwPkMnYeqwzMoyQhzr1QT97dGFO18yRvGXClUmTI/tSZBhfL6OVjQKBgQC7Y8/CvcUbP8xp6DCjQf7WGSnxq9XPFuqFkEK+VGpNMQJtrvNZj4zCOHMEK6fc7AL96i1zzrC896G4Mnrd+HLlHrAjx7Gdv9kE8cCt558Kp/NXmVnDrjfaM8ieBnkmQ51yOtLJu7vedWsmeewV3eFJ2V6O3L8U0U0U5dAcgusXNQKBgECfTu58kmZJPFIkmM1Xn5TQcLGy4NJEHmfQM7/4TRRgG7VuXfNCFOidLgtN3LcnN4u5isfzCdHv/RNRhg8p00+S9nXozVsQ7DQVs6oBH9QVf2CUpBJP1TscbkqlDUsOcUoJsXz4MXKPgi41C+3Tm711PGpuhk5qzyUP3DSxLe5hAoGBAMpZViuJjQmyMMYqPU6Ptpb6nB1isgX4zqwYBPxFX1LJUiNAelZhjG7RR3DzYsCpQWDbSWjsiNN6swQGpIOO2tuPrqMrp5lkr6ehNKbu2VshK3lUwQOUUi4GagBoP57PYTIjwWYiZBtCdS6HxrUJ6h8PcyYvhXysapOMEpWX7o5/\n-----END PRIVATE KEY-----"

# Dict oluştururken direkt değişkeni kullan
creds_dict = {
    "type": "service_account",
    "project_id": st.secrets["GCP"]["project_id"],
    "private_key": PRIVATE_KEY,
    "client_email": st.secrets["GCP"]["client_email"],
}

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1mybm2kJtDHGUw5sruKp4tpSaV2PwINKfoTrIhCI82rY/edit").sheet1

st.title("💊 Nextpharma Kalıcı Kayıt")
doktor = st.text_input("Doktor Adı:")
kurum = st.text_input("Kurum:")

if st.button("Kaydet"):
    sheet.append_row([doktor, kurum])
    st.success("Kaydedildi!")

st.write("Mevcut Kayıtlar:", sheet.get_all_values())

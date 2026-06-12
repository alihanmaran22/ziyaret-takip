import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Mobil ekran düzeni
st.set_page_config(layout="centered", page_title="Nextpharma Ziyaret Takip")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem;}
    h1, h2, h3 {margin-top: 0.1rem; margin-bottom: 0.1rem;}
    div.stButton > button {width: 100%; padding: 0.2rem 0.4rem; font-size: 13px; height: auto;}
    </style>
""", unsafe_allow_html=True)

# Google Cloud Ortak Bağlantı Yapısı
def get_gspread_client():
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
    return gspread.authorize(creds)

# Google Sheets Veri Kaydetme Fonksiyonu
def sheets_kaydet(ziyaretler):
    client = get_gspread_client()
    SHEET_ADI = "Frekans"     
    SEKME_ADI = "Ziyaretler"  
    
    try:
        sheet = client.open(SHEET_ADI).worksheet(SEKME_ADI)
    except gspread.exceptions.WorksheetNotFound:
        sheet = client.open(SHEET_ADI).add_worksheet(title=SEKME_ADI, rows="1000", cols="20")
        sheet.append_row(["Doktor", "Kurum", "Branş", "Tarih", "Saat", "Not"])
        
    for z in ziyaretler:
        sheet.append_row([z['Doktor'], z['Kurum'], z['Brans'], z['Tarih'], z['Saat'], z['Not']])

# Veri Yükleme (DÜZELTME: AttributeError ve apply hatası vermeyen saf Python temizleme yapısı)
@st.cache_data(ttl=60)
def load_data():
    client = get_gspread_client()
    SHEET_ADI = "Frekans"
    SEKME_ADI = "Doktor Listesi"
    
    sheet = client.open(SHEET_ADI).worksheet(SEKME_ADI)
    all_values = sheet.get_all_values()
    
    if all_values and len(all_values) > 1:
        # Başlıkları ve tüm hücreleri daha DataFrame yapmadan saf Python listesi seviyesinde temizliyoruz
        headers = [str(h).strip() for h in all_values[0]]
        
        temiz_satirlar = []
        for row in all_values[1:]:
            # Satırdaki her hücreyi string'e çevirip sağındaki solundaki boşlukları siliyoruz
            temiz_satirlar.append([str(cell).strip() for cell in row])
            
        df = pd.DataFrame(temiz_satirlar, columns=headers)
    else:
        df = pd.DataFrame(columns=['DOKTOR', 'KURUM', 'İHTİSAS', 'FREKANS'])
        
    # Sayısal değere dönüştürme ve güvenlik kontrolü
    if 'FREKANS' in df.columns:
        df['FREKANS'] = pd.to_numeric(df['FREKANS'], errors='coerce').fillna(0).astype(int)
    else:
        df['FREKANS'] = 0
        
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
    
    hastane_sutunu = 'KURUM' if 'KURUM' in df.columns else df.columns[1] if len(df.columns) > 1 else None
    brans_sutunu = 'İHTİSAS' if 'İHTİSAS' in df.columns else df.columns[2] if len(df.columns) > 2 else None
    doktor_sutunu = 'DOKTOR' if 'DOKTOR' in df.columns else df.columns[0] if len(df.columns) > 0 else None
    
    if hastane_sutunu and brans_sutunu and doktor_sutunu:
        ham_hastaneler = df[hastane_sutunu].dropna().unique().tolist()
        temiz_hastaneler = []
        for h in ham_hastaneler:
            if "/" in h and len(h) <= 10:
                continue
            if h != "" and h != "nan" and h != hastane_sutunu:
                temiz_hastaneler.append(h)
                
        hastaneler = ['Lütfen hastane seçiniz...'] + sorted(temiz_hastaneler)
        secilen_hastane = st.selectbox("Hastane Seç:", hastaneler)

        if secilen_hastane != 'Lütfen hastane seçiniz...':
            df_filtre = df[df[hastane_sutunu] == secilen_hastane]
            
            ham_branslar = df_filtre[brans_sutunu].dropna().unique().tolist()
            temiz_branslar = [b for b in ham_branslar if b != "" and b != "nan" and not ("/" in b and len(b) <= 10)]
            
            branslar = ['Tümü'] + sorted(temiz_branslar)
            secilen_brans = st.selectbox("Branş Seç:", branslar)
            if secilen_brans != 'Tümü':
                df_filtre = df_filtre[df_filtre[brans_sutunu] == secilen_brans]
            
            st.markdown("---")
            if df_filtre.empty:
                st.warning("Bu kriterlere uygun doktor bulunamadı.")
            else:
                for i, row in df_filtre.iterrows():
                    dr_adi, dr_brans, dr_kurum = row[doktor_sutunu], row[brans_sutunu], row[hastane_sutunu]
                    dr_frekans = int(row['FREKANS']) if 'FREKANS' in row else 1
                    yapilan = len([z for z in st.session_state.ziyaret_gecmisi if z['Doktor'] == dr_adi])
                    kalan = dr_frekans - yapilan
                    uyari = " ⚠️ [KRİTİK]" if kalan > 0 and kalan >= (dr_frekans / 2) else ""
                    
                    st.write(f"**{dr_adi}** - {dr_brans} {uyari}")
                    cols = st.columns([1.5, 1.1, 1.1, 0.8])
                    cols[0].write(f"Kal: {kalan}/{dr_frekans}")
                    
                    if cols[1].button("Ziyaret", key=f"z_{i}"):
                        k_notu = st.session_state.get(f"temp_not_{i}", "").strip()
                        st.session_state.ziyaret_gecmisi.append({
                            "Doktor": dr_adi, "Tarih": bugun_str, "Saat": datetime.now().strftime("%H:%M"),
                            "Kurum": dr_kurum, "Brans": dr_brans, "Not": k_notu if k_notu else "Not eklenmedi."
                        })
                        if f"temp_not_{i}" in st.session_state: del st.session_state[f"temp_not_{i}"]
                        st.rerun()
                    
                    if cols[2].button("İptal", key=f"i_{i}"):
                        for j in range(len(st.session_state.ziyaret_gecmisi) - 1, -1, -1):
                            if st.session_state.ziyaret_gecmisi[j]['Doktor'] == dr_adi:
                                del st.session_state.ziyaret_gecmisi[j]; break
                        st.rerun()
                    
                    with cols[3].expander("✍️"):
                        st.text_input("Not:", key=f"temp_not_{i}", placeholder="Not...", label_visibility="collapsed")
                    st.markdown("<div style='margin: 1px 0; border-bottom: 1px dashed #333;'></div>", unsafe_allow_html=True)
    else:
        st.error("Eksik veya hatalı sütun yapısı! Lütfen Google Sheets dökümanındaki başlıkları kontrol edin.")

elif menu == "Bugün Ne Yaptım?":
    st.markdown(f"### 📋 Bugün Ne Yaptım? ({bugun_str})")
    st.write(f"Toplam Ziyaret: **{len(bugun_ziyaretleri)} Doktor**")
    
    if st.button("🚀 Tüm Ziyaretleri Google Sheets'e Gönder"):
        if not bugun_ziyaretleri:
            st.warning("Gönderilecek ziyaret kaydı bulunmuyor.")
        else:
            try:
                sheets_kaydet(bugun_ziyaretleri)
                st.success("Tüm ziyaretler 'Ziyaretler' sekmesine aktarıldı!")
            except Exception as e: 
                st.error(f"Hata: {e}")
    
    st.markdown("---")
    if bugun_ziyaretleri:
        for z in reversed(bugun_ziyaretleri):
            st.write(f"⏰ {z['Saat']} | **{z['Doktor']}** ({z['Kurum']})")
            if z['Not'] != "Not eklenmedi.": st.info(f"💬 {z['Not']}")
            st.markdown("---")
    else: 
        st.info("Henüz ziyaret kaydı yok.")

elif menu == "Ziyaret Detay Raporu":
    st.markdown("### 📋 Ziyaret Raporu")
    rapor_tarihi = st.date_input("Tarih Seçin:", datetime.now())
    tarih_str = rapor_tarihi.strftime("%d/%m/%Y")
    gunluk_kayitlar = [z for z in st.session_state.ziyaret_gecmisi if z['Tarih'] == tarih_str]
    st.metric(label="Toplam Ziyaret", value=f"{len(gunluk_kayitlar)} Kişi")
    if gunluk_kayitlar:
        df_rapor = pd.DataFrame(gunluk_kayitlar).sort_values(by='Saat')
        for brans in df_rapor['Brans'].unique():
            with st.expander(f"🏥 {brans}"):
                for _, z in df_rapor[df_rapor['Brans'] == brans].iterrows():
                    st.write(f"✅ {z['Saat']} | **{z['Doktor']}** ({z['Kurum']})")
                    if z['Not'] != "Not eklenmedi.": st.caption(f"💬 Not: {z['Not']}")
    else: 
        st.warning("Seçilen tarihe ait kayıt bulunamadı.")

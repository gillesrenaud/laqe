import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

# Authentification
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
SERVICE_ACCOUNT_FILE = 'credentials.json'
FOLDER_ID = '1IQULRgxwdgHQ0Nzp-D76zqLBocqg_zUI'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
docs_service = build('docs', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

# Interface
st.image("logo.png", width=400)
st.title("Formulaire d'analyse de l'eau - DLAQE")

st.subheader("Informations générales")
col1, col2 = st.columns(2)
with col1:
    code = st.text_input("Code échantillon")
    commanditaire = st.text_input("Commanditaire")
    motif = st.text_input("Motif de l’analyse")
    region = st.text_input("Région")
    province = st.text_input("Province")
    commune = st.text_input("Commune")
with col2:
    date_prel = st.date_input("Date de prélèvement", datetime.date.today())
    date_recep = st.date_input("Date de réception", datetime.date.today())
    secteur = st.text_input("Secteur / Village")
    point = st.text_input("Point de prélèvement")

st.markdown("---")
st.subheader("Paramètres physico-chimiques")
physico = {
    "pH": {"unit": "-", "oms": "6,5 – 8,5", "value": st.number_input("pH", 0.0)},
    "Conductivité": {"unit": "µS/cm", "oms": "-", "value": st.number_input("Conductivité (µS/cm)", 0.0)},
    "Dureté": {"unit": "°F", "oms": "-", "value": st.number_input("Dureté (°F)", 0.0)},
    "Nitrates": {"unit": "mg/L", "oms": "50", "value": st.number_input("Nitrates (mg/L)", 0.0)},
    "Fluorures": {"unit": "mg/L", "oms": "1,5", "value": st.number_input("Fluorures (mg/L)", 0.0)},
    "Fer total": {"unit": "mg/L", "oms": "0,3", "value": st.number_input("Fer total (mg/L)", 0.0)},
}

st.markdown("---")
st.subheader("Paramètres microbiologiques")
microbio = {
    "Coliformes fécaux": {"unit": "UFC/100ml", "oms": "0", "value": st.number_input("Coliformes fécaux", 0)},
    "Escherichia coli": {"unit": "UFC/100ml", "oms": "0", "value": st.number_input("E. coli", 0)},
    "Streptocoques fécaux": {"unit": "UFC/100ml", "oms": "0", "value": st.number_input("Streptocoques fécaux", 0)},
}

st.markdown("---")
conclusion_physico = st.text_area("Conclusion physico-chimique")
conclusion_micro = st.text_area("Conclusion microbiologique")

if st.button("Générer le rapport"):
    titre = f"Rapport_Analyse_{code}"
    file_metadata = {
        "name": titre,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [FOLDER_ID]
    }
    file = drive_service.files().create(body=file_metadata).execute()
    doc_id = file["id"]

    entete = [
        "MINISTERE DE L’ENVIRONNEMENT, DE L’EAU ET DE L’ASSAINISSEMENT\n",
        "SECRETARIAT GENERAL\n",
        "DIRECTION GENERALE DE LA PRESERVATION DE L’ENVIRONNEMENT\n",
        "BURKINA FASO – La Patrie ou la Mort, nous vaincrons\n\n",
        f"Commanditaire : {commanditaire}\nMotif : {motif}\n\n",
        f"Date prélèvement : {date_prel} - Date réception : {date_recep}\n",
        f"Région : {region} | Province : {province} | Commune : {commune}\n",
        f"Secteur/Village : {secteur} | Point de prélèvement : {point}\n\n",
        "RESULTATS PHYSICO-CHIMIQUES\n"
    ]

    requests = [{"insertText": {"location": {"index": 1}, "text": conclusion_micro + "\n\n"}}]
    requests.insert(0, {"insertText": {"location": {"index": 1}, "text": "CONCLUSION MICROBIOLOGIQUE\n"}})

    for param, d in reversed(microbio.items()):
        text = f"{param}\t{d['unit']}\t{d['value']}\t{d['oms']}\n"
        requests.insert(0, {"insertText": {"location": {"index": 1}, "text": text}})
    requests.insert(0, {"insertText": {"location": {"index": 1}, "text": "Paramètre\tUnité\tRésultat\tValeur OMS\n"}})
    requests.insert(0, {"insertText": {"location": {"index": 1}, "text": "RESULTATS MICROBIOLOGIQUES\n"}})

    requests.insert(0, {"insertText": {"location": {"index": 1}, "text": conclusion_physico + "\n\n"}})
    requests.insert(0, {"insertText": {"location": {"index": 1}, "text": "CONCLUSION PHYSICO-CHIMIQUE\n"}})

    for param, d in reversed(physico.items()):
        text = f"{param}\t{d['unit']}\t{d['value']}\t{d['oms']}\n"
        requests.insert(0, {"insertText": {"location": {"index": 1}, "text": text}})
    requests.insert(0, {"insertText": {"location": {"index": 1}, "text": "Paramètre\tUnité\tRésultat\tValeur OMS\n"}})

    for line in reversed(entete):
        requests.insert(0, {"insertText": {"location": {"index": 1}, "text": line}})

    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    st.success(f"✅ Rapport généré avec succès ! [Voir le rapport]({doc_url})")
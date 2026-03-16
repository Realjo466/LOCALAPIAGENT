import streamlit as st
import requests
from streamlit_mic_recorder import mic_recorder


API_URL = "http://localhost:8000/stt"


st.set_page_config(page_title="VocalAssistant STT", layout="centered")

st.title("VocalAssistant – Test STT")
st.write("Charge un fichier audio ou enregistre avec le micro, puis envoie à l'API FastAPI pour obtenir la transcription.")


st.header("1. Transcription depuis un fichier")
uploaded_file = st.file_uploader(
    "Choisis un fichier audio",
    type=["wav", "mp3", "ogg", "webm"],
)

if uploaded_file is not None:
    if st.button("Transcrire le fichier"):
        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            with st.spinner("Transcription en cours..."):
                resp = requests.post(API_URL, files=files)

            if resp.status_code == 200:
                data = resp.json()
                st.subheader("Texte transcrit (fichier)")
                st.write(data.get("text", ""))
            else:
                st.error(f"Erreur API ({resp.status_code}) : {resp.text}")
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")


st.markdown("---")
st.header("2. Transcription depuis le micro")
st.write("Clique sur le bouton pour enregistrer ta voix, puis envoie l'audio à l'API.")

audio = mic_recorder(
    start_prompt="🎙️ Démarrer l'enregistrement",
    stop_prompt="⏹️ Arrêter",
    just_once=True,
    use_container_width=True,
    key="mic_recorder",
)

if audio is not None:
    st.audio(audio["bytes"], format="audio/wav")

    if st.button("Transcrire l'enregistrement"):
        try:
            # mic_recorder renvoie des bytes WAV mono -> on les envoie comme fichier
            files = {
                "file": ("mic_recording.wav", audio["bytes"], "audio/wav"),
            }
            with st.spinner("Transcription en cours..."):
                resp = requests.post(API_URL, files=files)

            if resp.status_code == 200:
                data = resp.json()
                st.subheader("Texte transcrit (micro)")
                st.write(data.get("text", ""))
            else:
                st.error(f"Erreur API ({resp.status_code}) : {resp.text}")
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API : {e}")


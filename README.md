# VocalAssistant STT API

This project exposes a simple Speech-to-Text (STT) API using FastAPI and a local Hugging Face model stored at `D:\crunch_modele_ewe`.

## 1. Install dependencies

From the `d:\VocalAssitant_API` folder:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> Make sure you are using a Python 3.9+ environment.

## 2. Start the API server

In the same folder:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

- Swagger docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## 3. Use the `/stt` endpoint

Open the Swagger UI at `http://localhost:8000/docs`, select the `POST /stt` endpoint, and upload an audio file (e.g. WAV/MP3/OGG/WEBM).  
You will receive a JSON response like:

```json
{
  "text": "transcribed text here"
}
```

If your model directory is not exactly `D:\crunch_modele_ewe`, update the `MODEL_PATH` constant in `main.py` accordingly.


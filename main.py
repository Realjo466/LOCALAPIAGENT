from fastapi import FastAPI, UploadFile, File, HTTPException
from transformers import pipeline
import os
from typing import Optional

import io
import numpy as np
import soundfile as sf


MODEL_PATH = r"D:\crunch_modele_ewe"
APP_VERSION = "stt-no-ffmpeg-bytes-v1"


app = FastAPI(
    title="VocalAssistant STT API",
    description="Speech-to-text API powered by a local Hugging Face model.",
)

asr_pipeline: Optional[object] = None

def get_asr_pipeline():
    """
    Lazily load the ASR pipeline the first time it's needed.
    """
    global asr_pipeline

    if asr_pipeline is None:
        if not os.path.isdir(MODEL_PATH):
            raise RuntimeError(f"Model directory not found: {MODEL_PATH}")

        asr_pipeline = pipeline(
            task="automatic-speech-recognition",
            model=MODEL_PATH,
            generate_kwargs={
                "repetition_penalty": 1.2,
                "no_repeat_ngram_size": 3,
                "max_new_tokens": 128,
            },
        )

    return asr_pipeline

@app.get("/health")
def health_check():
    return {"status": "ok", "version": APP_VERSION}

@app.post("/stt")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Accept an audio file and return the transcription text.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    # Basic content-type guard; you can extend this as needed.
    allowed_types = {
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/ogg",
        "audio/webm",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type '{file.content_type}'. "
            f"Supported types: {', '.join(sorted(allowed_types))}.",
        )

    try:
        audio_bytes = await file.read()

        # Read audio directly from uploaded bytes (no ffmpeg needed).
        audio_array, sampling_rate = sf.read(io.BytesIO(audio_bytes))

        # Convert stereo -> mono if needed
        if isinstance(audio_array, np.ndarray) and audio_array.ndim > 1:
            audio_array = np.mean(audio_array, axis=1)

        asr = get_asr_pipeline()
        result = asr({"array": audio_array, "sampling_rate": sampling_rate})

        # Hugging Face ASR pipeline usually returns a dict with a "text" field.
        if isinstance(result, dict) and "text" in result:
            text = result["text"]
        else:
            text = str(result)

        return {"text": text}

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}")
    finally:
        try:
            await file.close()
        except Exception:
            pass

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


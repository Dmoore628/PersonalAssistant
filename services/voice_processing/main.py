from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import vosk
import sounddevice as sd
import queue
import json
import numpy as np
import threading

app = FastAPI(title="Voice Processing Engine")

class WakeWordDetection(BaseModel):
    wake_word: str
    sensitivity: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/detect_wake_word")
async def detect_wake_word(config: WakeWordDetection):
    return {"message": "Wake word detection is not available in this version."}

def always_on_listening():
    model = vosk.Model("models/vosk-model/vosk-model-small-en-us-0.15")  # Updated path to the Vosk model
    recognizer = vosk.KaldiRecognizer(model, 16000)
    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        if status:
            print(status)
        audio_queue.put(indata)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        print("Listening...")
        while True:
            try:
                data = audio_queue.get()
                data_bytes = np.frombuffer(data, dtype=np.int16).tobytes()
                if recognizer.AcceptWaveform(data_bytes):
                    result = json.loads(recognizer.Result())
                    print("Recognized:", result.get("text", ""))
                    # Add contextual understanding logic here
            except Exception as e:
                print(f"Error processing audio frame: {e}")

if __name__ == "__main__":
    listening_thread = threading.Thread(target=always_on_listening, daemon=True)
    listening_thread.start()
    listening_thread.join()
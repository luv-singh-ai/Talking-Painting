from dotenv import load_dotenv
from core.voice import text_to_speech
import base64
import tempfile
import requests
import time
import os

load_dotenv(dotenv_path="ops/.env")

LLAVA_URL = os.getenv("LLAVA_URL")

with open("prompts/main.txt", "r") as f:
    prompt = f.read()


def compose_body(encoded_img, prompt=prompt, model="llava"):
    return {
        "model": model,
        "prompt": prompt,
        "images": [encoded_img],
        "stream": False
    }


def respond(encoded_img):
    body = compose_body(encoded_img)
    start = time.time()
    response = requests.post(LLAVA_URL, json=body)
    end = time.time()
    print(end - start)
    print(response.json())
    return response.json().get("response", "").replace("</s>", "").strip()

def respond_voice(encoded_img):
    response_text = respond(encoded_img)
    if response_text:
        audio_response = text_to_speech(response_text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            audio_response.stream_to_file(f.name)
            audio_response = f.read()
            encoded_audio = base64.b64encode(audio_response).decode("utf-8")
        return {"response": response_text, "audio": encoded_audio}
    else:
        return {}
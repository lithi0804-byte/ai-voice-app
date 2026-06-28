from flask import Flask, request, jsonify
from transcribe import transcribe_audio
from groq import Groq

app = Flask(__name__)

import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- TRANSCRIBE ----------------
import requests

def send_to_make(transcript):
    url = "https://hook.eu1.make.com/dwdheysr0oo88depeund0ldrk663ou2i"  # 🔥 paste your webhook
    data = {"text": transcript}
    response = requests.post(url, json=data)
    print("Sent to Make:", response.status_code)

# ---------------- SUMMARIZE ----------------
def summarize_text(text):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": f"Summarize this:\n{text}"}
        ]
    )
    return response.choices[0].message.content


@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        text = request.json["text"]
        summary = summarize_text(text)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- CHAT ----------------
def chat_with_text(text, question):
    text = text[:2000]  # optional limit

    prompt = f"""
You are an AI assistant.

Answer the question based ONLY on the transcript below.
If the question is general (not related to transcript), answer normally.

Transcript:
{text}

Question:
{question}

Answer clearly:
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json

        text = data.get("text", "")
        question = data.get("question", "")

        answer = chat_with_text(text, question)
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)})
    
from flask import send_file

latest_transcript = ""   # 👈 MUST ADD THIS (top la)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    global latest_transcript

    file = request.files["audio"]
    file_path = "temp.wav"
    file.save(file_path)

    text = transcribe_audio(file_path)

    latest_transcript = text

    send_to_make(text)   # 🔥 ADD THIS LINE

    return jsonify({"transcript": text})

@app.route("/download", methods=["GET"])
def download_file():
    with open("transcript.txt", "w") as f:
        f.write(latest_transcript)

    return send_file("transcript.txt", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
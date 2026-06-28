import gradio as gr
import requests

def transcribe(audio):
    files = {"audio": open(audio, "rb")}

    try:
        res = requests.post("http://127.0.0.1:5000/transcribe", files=files)

        print("STATUS:", res.status_code)
        print("TEXT:", res.text)

        return res.json().get("transcript", res.text)

    except Exception as e:
        return str(e)
    
def summarize(text):
    res = requests.post("http://127.0.0.1:5000/summarize", json={"text": text})
    return res.json().get("summary", res.text)

def chat(text, question):
    try:
        res = requests.post(
            "http://127.0.0.1:5000/chat",
            json={"text": text, "question": question},
            timeout=30
        )

        print("STATUS:", res.status_code)
        print("TEXT:", res.text)

        return res.json().get("answer", res.text)

    except Exception as e:
        return f"Error: {str(e)}"

with gr.Blocks() as app:
    audio = gr.Audio(type="filepath")
    transcript = gr.Textbox(label="Transcript")
    summary = gr.Textbox(label="Summary")
    question = gr.Textbox(label="Ask Question")
    answer = gr.Textbox(label="Answer")

    gr.Button("Transcribe").click(transcribe, inputs=audio, outputs=transcript)
    gr.Button("Summarize").click(summarize, inputs=transcript, outputs=summary)
    gr.Button("Ask").click(chat, inputs=[transcript, question], outputs=answer)

app.launch()



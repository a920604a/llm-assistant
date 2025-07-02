import whisper

model = whisper.load_model("base")  # base, small, medium, large

def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path)
    return result.get("text", "")

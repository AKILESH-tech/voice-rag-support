def transcribe(audio_bytes: bytes, language: str = "en") -> dict:
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        import io
        segments, info = model.transcribe(io.BytesIO(audio_bytes))
        text = " ".join(s.text for s in segments).strip()
        return {"transcript": text, "available": True}
    except Exception as exc:
        return {"transcript": "", "available": False, "error": str(exc)}

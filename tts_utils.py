"""
Conversie text-in-vorbire (Text-to-Speech) folosind gTTS (Google Text-to-Speech).
Nu necesita cheie API - foloseste serviciul public gratuit al Google Translate.
"""
import io
from gtts import gTTS


def text_to_speech(text, lang="ro"):
    """
    Primeste un text si returneaza un buffer audio (MP3) in memorie,
    gata de redat cu st.audio().
    """
    # gTTS nu suporta texte foarte lungi foarte bine si dureaza mai mult;
    # taiem la un numar rezonabil de caractere pentru un raspuns de chat.
    MAX_CHARS = 800
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS].rsplit(".", 1)[0] + "."

    tts = gTTS(text=text, lang=lang, slow=False)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

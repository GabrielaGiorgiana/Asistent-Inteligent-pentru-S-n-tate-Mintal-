"""
Incarca modelul de clasificare a starii emotionale antrenat si ofera:
- clasificarea unui mesaj (negativ / pozitiv) folosind modelul ML
- o plasa de siguranta separata, bazata pe cuvinte-cheie, pentru
  semnale de criza (independenta de modelul ML, intentionat)
"""
import os
import joblib

_MODEL_PATH = "emotion_model.joblib"
_VECTORIZER_PATH = "emotion_vectorizer.joblib"

_model = None
_vectorizer = None

if os.path.exists(_MODEL_PATH) and os.path.exists(_VECTORIZER_PATH):
    _model = joblib.load(_MODEL_PATH)
    _vectorizer = joblib.load(_VECTORIZER_PATH)


def classify_message(text):
    """
    Returneaza (eticheta, incredere) pentru un mesaj.
    eticheta e "negativ" sau "pozitiv"; incredere e intre 0 si 1.
    Daca modelul nu a fost antrenat inca (fisierele .joblib lipsesc),
    returneaza ("necunoscut", 0.0) fara sa arunce eroare.
    """
    if _model is None or _vectorizer is None:
        return "necunoscut", 0.0

    X = _vectorizer.transform([text])
    prediction = _model.predict(X)[0]
    probability = _model.predict_proba(X)[0].max()

    label = "negativ" if prediction == 0 else "pozitiv"
    return label, float(probability)


# Cuvinte si expresii asociate cu risc de criza. Aceasta verificare este
# INDEPENDENTA de modelul ML de mai sus, in mod intentionat: un model ML
# antrenat pe recenzii de produse NU este suficient de fiabil pentru a
# decide singur intr-o situatie de risc real. Preferam sa afisam resursele
# de ajutor in plus (fals pozitiv) decat sa le ratam (fals negativ).
_CRISIS_KEYWORDS = [
    "sa mor", "să mor", "nu mai vreau sa traiesc", "nu mai vreau să trăiesc",
    "sinucid", "sa-mi fac rau", "să-mi fac rău", "nu mai am rost",
    "mai bine as muri", "mai bine aș muri", "vreau sa dispar", "vreau să dispar",
    "nu mai pot continua", "nu mai vad rost", "nu mai văd rost",
]


def check_crisis_signal(text):
    """Returneaza True daca mesajul contine limbaj asociat cu risc de criza."""
    normalized = text.lower()
    return any(keyword in normalized for keyword in _CRISIS_KEYWORDS)

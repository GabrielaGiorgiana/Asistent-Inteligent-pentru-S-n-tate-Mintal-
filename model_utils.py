from google import genai
import streamlit as st
from rag_utils import retrieve_context
from emotion_utils import classify_message, check_crisis_signal

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

SYSTEM_PROMPT = """Ești MindCare, un asistent conversațional empatic, cald și prietenos,
specializat în informații generale despre sănătate mintală (stres, anxietate, tehnici de
relaxare). Vorbești în română, cu un ton natural, cald și fără judecată.

Reguli importante:
- NU oferi niciodată diagnostice medicale.
- Dacă utilizatorul pare într-o situație de criză sau menționează gânduri de
  autovătămare, recomandă-i cu blândețe, dar clar, să contacteze un specialist
  sau o linie de urgență.
- Folosește contextul de mai jos DOAR dacă este relevant pentru întrebare;
  altfel, răspunde din empatie și cunoștințele tale generale, fără să forțezi
  informația din context.
- Nu menționa explicit că folosești un "context" sau o "bază de date" — vorbește
  natural, ca un asistent care pur și simplu știe aceste lucruri.
- Ai mai jos istoricul recent al conversației — ține cont de el, nu răspunde ca
  și cum ar fi prima replică dacă utilizatorul continuă un subiect deja discutat."""

# Mesaj afișat direct, INDIFERENT de răspunsul modelului AI, atunci când
# plasa de siguranță bazată pe cuvinte-cheie detectează risc de criză.
CRISIS_MESSAGE = """Îmi pare foarte rău că treci prin asta. Ce simți contează, și nu ești singur/ă.

Te rog să contactezi acum una dintre aceste resurse gratuite din România:
- 112 — Numărul unic de urgență (pericol iminent)
- 0800 801 200 — Telefonul Verde Antisuicid (vineri-sâmbătă-duminică, 19:00-07:00)
- 0374 456 420 — DepreHUB, linie de sprijin psihologic, gratuită, non-stop, 24/7

Sunt aici să te ascult în continuare, dar te rog, vorbește și cu o persoană reală cât mai curând posibil."""

# Câte mesaje anterioare (user + asistent) să trimitem ca istoric, pe lângă
# mesajul curent. Ținem un număr limitat ca să nu umflăm prompt-ul la infinit
# pe măsură ce conversația crește.
MAX_HISTORY_MESSAGES = 10


def _format_history(messages):
    """Transformă ultimele mesaje din conversație (fără ultimul, care e
    mesajul curent) într-un text simplu 'Utilizator: ... / Asistent: ...',
    ca modelul să aibă context real despre ce s-a discutat deja."""
    previous_messages = messages[:-1][-MAX_HISTORY_MESSAGES:]
    if not previous_messages:
        return "(Nu există mesaje anterioare — aceasta este prima replică.)"

    lines = []
    for msg in previous_messages:
        speaker = "Utilizator" if msg["role"] == "user" else "Asistent"
        lines.append(f"{speaker}: {msg['content']}")
    return "\n".join(lines)


def _format_memory(memory_summaries):
    """Formatează rezumatele conversațiilor anterioare (memorie pe termen lung),
    ca modelul să știe ce discuții au mai avut loc în trecut cu acest utilizator."""
    if not memory_summaries:
        return "(Nu există încă rezumate din conversații anterioare.)"
    lines = [f"- {s}" for s in memory_summaries]
    return "\n".join(lines)


def generate_response(model_name, messages, memory_summaries=None):
    """Returnează un tuplu (text_raspuns, emotion_label, emotion_confidence).
    Pentru mesajul de criza, emotion_label este 'criza' si confidence e 1.0,
    ca sa fie vizibil si el in statistici, fara sa mai treaca prin LLM."""
    user_input = messages[-1]["content"]
    try:
        # 1. Plasă de siguranță — verificare directă, independentă de ML.
        if check_crisis_signal(user_input):
            return CRISIS_MESSAGE, "criza", 1.0

        # 2. Clasificare a stării emoționale cu modelul ML antrenat separat.
        emotion_label, confidence = classify_message(user_input)

        # 3. Recuperare context relevant din baza de cunoștințe (RAG).
        context = retrieve_context(client, user_input)

        # 4. Istoricul conversației curente, ca modelul să înțeleagă continuitatea.
        conversation_history = _format_history(messages)

        # 5. Memorie pe termen lung — rezumate din conversații anterioare.
        long_term_memory = _format_memory(memory_summaries)

        tone_hint = ""
        if emotion_label == "negativ" and confidence > 0.6:
            tone_hint = ("\n(Analiza mesajului sugerează o stare emoțională dificilă — "
                          "fii extra empatic, blând, și oferă-i timp și spațiu utilizatorului.)")

        prompt = f"""{SYSTEM_PROMPT}{tone_hint}

Ce știi deja despre acest utilizator din conversații anterioare:
{long_term_memory}

Context relevant din baza de cunoștințe (folosește-l doar dacă ajută la răspuns):
{context}

Istoricul recent al conversației curente:
{conversation_history}

Mesajul curent al utilizatorului: {user_input}

Răspunde în română, cald, empatic, natural, ținând cont de tot ce s-a discutat deja."""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text, emotion_label, confidence
    except Exception as e:
        return f"Eroare: {str(e)}", None, None


def summarize_conversation(messages, model_name="gemini-flash-latest"):
    """Generează un rezumat scurt (2-3 propoziții) al unei conversații încheiate,
    folosit ca memorie pe termen lung în conversațiile viitoare. Se apelează o
    singură dată, când utilizatorul pornește o conversație nouă și cea veche
    avea deja mesaje."""
    if not messages:
        return None
    try:
        transcript = "\n".join(
            f"{'Utilizator' if m['role'] == 'user' else 'Asistent'}: {m['content']}"
            for m in messages
        )
        prompt = f"""Rezumă în 2-3 propoziții, la persoana a treia, conversația de mai jos
dintre un utilizator și un asistent de sănătate mintală. Reține doar informații
utile pentru continuitate (ex: ce probleme a menționat, ce stare avea, ce i s-a
recomandat) — nu detalii nesemnificative. Nu inventa informații care nu apar
în conversație.

{transcript}

Rezumat:"""
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[summarize_conversation] Eroare la generarea rezumatului: {e}")
        return None
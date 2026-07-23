import time
import streamlit as st
from model_utils import generate_response, summarize_conversation
from tts_utils import text_to_speech
import history_utils as history

st.set_page_config(page_title="MindCare AI", page_icon="🧠")
from mindcare_theme import apply_theme, render_header
apply_theme()
history.init_db()

render_header()

# Avatare tematice pentru mesajele din chat
AVATARS = {"user": "🫂", "assistant": "🧠"}

# --- Inițializare conversație curentă ---
# Dacă e prima rulare a sesiunii, încarcă ultima conversație salvată
# (dacă există) — astfel conversația nu se pierde la închiderea aplicației.
if "current_conversation_id" not in st.session_state:
    latest_id = history.get_latest_conversation_id()
    if latest_id is not None:
        st.session_state.current_conversation_id = latest_id
        st.session_state.messages = history.get_messages(latest_id)
    else:
        new_id = history.create_conversation()
        st.session_state.current_conversation_id = new_id
        st.session_state.messages = []


# --- Sidebar ---
with st.sidebar:
    st.header("Setări")
    tts_enabled = st.checkbox("🔊 Citește răspunsurile cu voce tare", value=False)

    st.divider()

    if st.button("🔄 Conversație nouă", use_container_width=True):
        if st.session_state.messages:
            new_id = history.create_conversation()
            st.session_state.current_conversation_id = new_id
            st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("Istoric conversații")

    conversations = history.get_all_conversations()
    if not conversations:
        st.caption("Nicio conversație salvată încă.")
    for conv in conversations:
        label = conv["title"] or "Conversație fără titlu"
        is_current = conv["id"] == st.session_state.current_conversation_id
        button_label = f"{'🟢 ' if is_current else '💬 '}{label}"
        if st.button(button_label, key=f"conv_{conv['id']}", use_container_width=True):
            st.session_state.current_conversation_id = conv["id"]
            st.session_state.messages = history.get_messages(conv["id"])
            st.rerun()

    st.divider()
    st.caption("Dashboard și Jurnal zilnic sunt disponibile în meniul de sus al sidebar-ului.")


def _render_feedback_buttons(message):
    """Afișează 👍/👎 sub un mesaj al asistentului deja salvat (are 'id')."""
    message_id = message.get("id")
    if message_id is None:
        return

    current_feedback = message.get("feedback")
    col_up, col_down, _ = st.columns([1, 1, 8])

    up_label = "👍" if current_feedback != "up" else "✅👍"
    down_label = "👎" if current_feedback != "down" else "✅👎"

    if col_up.button(up_label, key=f"fb_up_{message_id}"):
        new_value = None if current_feedback == "up" else "up"
        history.save_feedback(message_id, new_value)
        message["feedback"] = new_value
        st.rerun()

    if col_down.button(down_label, key=f"fb_down_{message_id}"):
        new_value = None if current_feedback == "down" else "down"
        history.save_feedback(message_id, new_value)
        message["feedback"] = new_value
        st.rerun()


# --- Afișarea mesajelor din conversația curentă ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=AVATARS[message["role"]]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if message.get("response_time"):
                st.caption(f"⏱️ Răspuns generat în {message['response_time']:.1f} secunde")
            _render_feedback_buttons(message)

# --- Input de la utilizator ---
if user_input := st.chat_input("Cum te simți azi?"):
    conversation_id = st.session_state.current_conversation_id

    user_message_id = history.save_message(conversation_id, "user", user_input)
    st.session_state.messages.append({"id": user_message_id, "role": "user", "content": user_input})

    # Primul mesaj din conversație devine automat titlul ei (pentru lista din sidebar)
    if len(st.session_state.messages) == 1:
        title = user_input[:40] + ("..." if len(user_input) > 40 else "")
        history.update_conversation_title(conversation_id, title)

    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("MindCare analizează..."):
            start_time = time.time()
            memory_summaries = history.get_recent_summaries(conversation_id)
            response_text, emotion_label, confidence = generate_response(
                "gemini-flash-latest", st.session_state.messages, memory_summaries
            )
            elapsed_time = time.time() - start_time

        st.markdown(response_text)
        st.caption(f"⏱️ Răspuns generat în {elapsed_time:.1f} secunde")

        if tts_enabled:
            with st.spinner("Generez audio..."):
                audio_buffer = text_to_speech(response_text)
            st.audio(audio_buffer, format="audio/mp3")

    assistant_message_id = history.save_message(
        conversation_id, "assistant", response_text, elapsed_time
    )
    if emotion_label is not None:
        history.save_emotion_for_message(user_message_id, emotion_label, confidence)

    st.session_state.messages.append({
        "id": assistant_message_id,
        "role": "assistant",
        "content": response_text,
        "response_time": elapsed_time,
        "feedback": None,
    })

    # Rezumăm conversația curentă DUPĂ FIECARE tură — nu doar la schimbarea
    # conversației. Așa, memoria pe termen lung e mereu la zi, indiferent
    # cum navighează utilizatorul (buton "Conversație nouă", click pe alta
    # din istoric, sau chiar închiderea directă a aplicației).
    with st.spinner("Actualizez memoria conversației..."):
        summary = summarize_conversation(st.session_state.messages)
    if summary:
        history.update_conversation_summary(conversation_id, summary)

    st.rerun()
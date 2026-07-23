"""
Mood Journal — jurnal zilnic simplu: notă de dispoziție (1-10) + text liber,
salvate separat de conversațiile de chat, cu un grafic al evoluției în timp.
"""
import pandas as pd
import streamlit as st
import history_utils as history
from mindcare_theme import apply_theme

st.set_page_config(page_title="Jurnal zilnic — MindCare AI", page_icon="📔")
apply_theme()

st.title("📔 Jurnal zilnic")
st.caption("Notează-ți starea de azi, în câteva secunde.")

if history.has_mood_entry_today():
    st.success("Ai completat deja jurnalul de azi. Poți adăuga o notă în plus mai jos, dacă vrei.")

with st.form("mood_form", clear_on_submit=True):
    mood_score = st.slider("Cum te simți azi? (1 = foarte greu, 10 = foarte bine)", 1, 10, 5)
    note = st.text_area("Vrei să adaugi câteva cuvinte despre ziua ta? (opțional)", "")
    submitted = st.form_submit_button("Salvează")

    if submitted:
        history.save_mood_entry(mood_score, note.strip() or None)
        st.success("Notat! Mulțumim că ai avut grijă să-ți urmărești starea azi.")
        st.rerun()

st.divider()

entries = history.get_mood_entries()

if not entries:
    st.info("Nu ai nicio notă salvată încă. Completează formularul de mai sus pentru a începe.")
else:
    st.subheader("Evoluția stării tale în timp")
    df = pd.DataFrame(entries)
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    daily_avg = df.groupby("entry_date")["mood_score"].mean()
    st.line_chart(daily_avg)

    st.subheader("Notele tale")
    for entry in reversed(entries):
        with st.container():
            st.markdown(f"**{entry['entry_date']}** — dispoziție: {entry['mood_score']}/10")
            if entry["note"]:
                st.caption(entry["note"])
            st.divider()

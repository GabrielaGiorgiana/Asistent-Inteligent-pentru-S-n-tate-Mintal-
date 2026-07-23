"""
Dashboard cu statistici — demonstrează concret Cerința 4 (analiza mesajelor
cu ML): distribuția stărilor emoționale detectate în mesajele utilizatorului,
de-a lungul timpului, plus statistici de feedback pentru răspunsurile AI.
"""
import pandas as pd
import streamlit as st
import history_utils as history
from mindcare_theme import apply_theme

st.set_page_config(page_title="Dashboard — MindCare AI", page_icon="📊")
apply_theme()

st.title("📊 Dashboard")
st.caption("Statistici generate din conversațiile salvate.")

emotion_rows = history.get_emotion_stats()
feedback = history.get_feedback_stats()

col1, col2, col3 = st.columns(3)
col1.metric("Mesaje analizate (ML)", len(emotion_rows))
col2.metric("👍 Feedback pozitiv", feedback["up"])
col3.metric("👎 Feedback negativ", feedback["down"])

st.divider()

if not emotion_rows:
    st.info("Încă nu există mesaje analizate emoțional. Poartă o conversație în chat, apoi revino aici.")
else:
    df = pd.DataFrame(emotion_rows)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["data"] = df["created_at"].dt.date

    st.subheader("Distribuția stărilor emoționale, în timp")
    counts_by_day = (
        df.groupby(["data", "emotion_label"])
        .size()
        .unstack(fill_value=0)
    )
    st.bar_chart(counts_by_day)

    st.subheader("Distribuția generală pe etichete")
    total_counts = df["emotion_label"].value_counts()
    st.bar_chart(total_counts)

    with st.expander("Vezi datele brute"):
        st.dataframe(df[["created_at", "emotion_label", "emotion_confidence"]], use_container_width=True)

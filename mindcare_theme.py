"""
MindCare AI — tema vizuală "Amurg către zori" v2
Adaugă: fonturi personalizate (Poppins + Nunito), gradient mai viu pe elementele
active, tranziții/fade-in la mesaje, scrollbar tematic.

Folosire — neschimbată:
    from mindcare_theme import apply_theme, render_header
    apply_theme()
    ...
    render_header()
"""

import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        /* ---------- Fonturi ---------- */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Nunito:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Nunito', sans-serif;
        }
        .mindcare-title, [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            font-family: 'Poppins', sans-serif !important;
        }

        /* ---------- Paleta ---------- */
        :root {
            --bg-deep:      #14152A;
            --bg-panel:     #1E2039;
            --bg-panel-alt: #262845;
            --accent-sage:  #8FBC9A;
            --accent-sage-dim: #6E9A7C;
            --accent-dusk:  #D9A0A4;
            --accent-violet: #B7A9E8;
            --text-soft:    #E8E6F0;
            --text-muted:   #9A97B5;
            --glow:         #B7A9E8;
        }

        /* ---------- Fundal general ---------- */
        [data-testid="stAppViewContainer"], .main {
            background: radial-gradient(ellipse 900px 500px at 15% -10%, rgba(183,169,232,0.18), transparent 60%),
                        radial-gradient(ellipse 900px 600px at 100% 100%, rgba(143,188,154,0.12), transparent 60%),
                        var(--bg-deep);
            color: var(--text-soft);
        }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background-color: var(--bg-panel);
            border-right: 1px solid rgba(183, 169, 232, 0.15);
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: var(--text-soft);
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        /* ---------- Butoane — gradient viu ---------- */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-sage-dim), var(--accent-violet));
            color: #0F1020;
            font-weight: 600;
            border: none;
            border-radius: 14px;
            padding: 0.55rem 0.9rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
            box-shadow: 0 2px 12px rgba(183, 169, 232, 0.25);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            filter: brightness(1.08);
            box-shadow: 0 4px 18px rgba(183, 169, 232, 0.4);
        }

        /* ---------- Butoane din istoric — mai discrete, gradient doar la hover ---------- */
        [data-testid="stSidebar"] .stButton > button {
            background: var(--bg-panel-alt);
            color: var(--text-soft);
            font-weight: 500;
            text-align: left;
            border: 1px solid rgba(183, 169, 232, 0.15);
            box-shadow: none;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: linear-gradient(135deg, rgba(143,188,154,0.25), rgba(183,169,232,0.25));
            border-color: var(--accent-sage);
            transform: translateX(2px);
            color: var(--text-soft);
        }

        /* ---------- Input mesaj ---------- */
        [data-testid="stChatInput"] textarea,
        input[type="text"] {
            background-color: var(--bg-panel-alt) !important;
            color: var(--text-soft) !important;
            border: 1px solid rgba(183, 169, 232, 0.25) !important;
            border-radius: 18px !important;
            transition: box-shadow 0.25s ease, border-color 0.25s ease;
        }
        [data-testid="stChatInput"] textarea:focus {
            border-color: var(--accent-sage) !important;
            box-shadow: 0 0 0 3px rgba(143, 188, 154, 0.25) !important;
        }

        /* ---------- Bule de chat + fade-in la apariție ---------- */
        [data-testid="stChatMessage"] {
            border-radius: 16px;
            padding: 0.6rem 1rem;
            margin-bottom: 0.5rem;
            animation: fadeInUp 0.35s ease both;
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            background-color: rgba(217, 160, 164, 0.12);
            border: 1px solid rgba(217, 160, 164, 0.25);
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
            background-color: rgba(143, 188, 154, 0.10);
            border: 1px solid rgba(143, 188, 154, 0.2);
        }

        /* ---------- Scrollbar tematic ---------- */
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: var(--bg-deep); }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(var(--accent-sage-dim), var(--accent-violet));
            border-radius: 8px;
        }

        /* ---------- Container de jos (chat input) — elimină negrul & chenarul default ---------- */
        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"] {
            background: var(--bg-deep) !important;
            border: none !important;
            box-shadow: none !important;
        }
        [data-testid="stChatInput"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        [data-testid="stChatInput"] > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* ---------- Avatare de mesaje — cercuri tematice, nu emoji default ---------- */
        [data-testid="stChatMessageAvatarUser"] {
            background: linear-gradient(135deg, var(--accent-dusk), #B87D82) !important;
        }
        [data-testid="stChatMessageAvatarAssistant"] {
            background: radial-gradient(circle at 35% 35%, var(--glow), var(--accent-sage) 70%) !important;
        }
        [data-testid="stChatMessageAvatarUser"] svg,
        [data-testid="stChatMessageAvatarAssistant"] svg {
            display: none;
        }

        /* ---------- Bara de sus (Deploy / meniu) — integrată în temă ---------- */
        [data-testid="stHeader"] {
            background: var(--bg-deep) !important;
            box-shadow: none !important;
            border-bottom: 1px solid rgba(183, 169, 232, 0.12) !important;
        }
        [data-testid="stToolbar"], [data-testid="stToolbarActions"] {
            background: transparent !important;
        }
        [data-testid="stToolbarActions"] button svg,
        [data-testid="stHeader"] svg {
            color: var(--text-muted) !important;
            fill: var(--text-muted) !important;
        }
        [data-testid="stHeader"] button:hover svg {
            fill: var(--accent-sage) !important;
        }
        /* linia subțire de accent, în loc de dunga default multicoloră */
        [data-testid="stDecoration"] {
            background: linear-gradient(90deg, var(--accent-sage), var(--accent-violet), var(--accent-dusk)) !important;
            height: 3px !important;
        }

        /* puțin mai mult spațiu sub bara de sus, ca titlul să respire */
        .block-container {
            padding-top: 2.2rem !important;
        }

        /* ---------- Titlu + orb care respiră ---------- */
        .mindcare-header {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            margin-bottom: 0.2rem;
        }
        .mindcare-orb {
            width: 46px;
            height: 46px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, var(--glow), var(--accent-sage) 70%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            animation: breathe 4s ease-in-out infinite;
            box-shadow: 0 0 24px rgba(183, 169, 232, 0.35);
        }
        @keyframes breathe {
            0%, 100% { transform: scale(1);   box-shadow: 0 0 18px rgba(183, 169, 232, 0.25); }
            50%      { transform: scale(1.08); box-shadow: 0 0 32px rgba(183, 169, 232, 0.45); }
        }
        .mindcare-title {
            font-size: 1.9rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            background: linear-gradient(90deg, var(--text-soft), var(--accent-violet));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .mindcare-subtitle {
            color: var(--text-muted);
            font-size: 1.05rem;
            margin-top: 0.3rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str = "MINDCARE AI", subtitle: str = "Sunt aici să te ascult"):
    st.markdown(
        f"""
        <div class="mindcare-header">
            <div class="mindcare-orb">🧠</div>
            <div class="mindcare-title">{title}</div>
        </div>
        <div class="mindcare-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )

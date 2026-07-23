"""
Persistenta istoricului de conversatii, folosind SQLite (inclus in Python,
nu necesita nicio dependinta noua). Fiecare conversatie e un rand in
tabelul `conversations`, iar mesajele ei sunt in tabelul `messages`.

Extensii adaugate:
- messages: coloane pentru feedback (👍/👎) si eticheta emotionala per mesaj
- conversations: coloana `summary` pentru memoria conversationala extinsa
- tabel nou `mood_entries` pentru Mood Journal
"""
import sqlite3
from datetime import datetime, date

DB_PATH = "mindcare_history.db"


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _add_column_if_missing(conn, table, column, coltype):
    """Adauga o coloana noua daca nu exista deja — sigur de rulat de mai multe ori."""
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # coloana exista deja


def init_db():
    """Creeaza tabelele daca nu exista deja. Se apeleaza o data, la pornirea aplicatiei."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            response_time REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            mood_score INTEGER NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()

    # Migratii aditive — sigure pe o baza deja existenta, cu date reale
    _add_column_if_missing(conn, "messages", "feedback", "TEXT")
    _add_column_if_missing(conn, "messages", "emotion_label", "TEXT")
    _add_column_if_missing(conn, "messages", "emotion_confidence", "REAL")
    _add_column_if_missing(conn, "conversations", "summary", "TEXT")

    conn.close()


def create_conversation(title="Conversație nouă"):
    conn = _get_connection()
    cursor = conn.execute(
        "INSERT INTO conversations (title, created_at) VALUES (?, ?)",
        (title, datetime.now().isoformat())
    )
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()
    return conversation_id


def update_conversation_title(conversation_id, title):
    conn = _get_connection()
    conn.execute("UPDATE conversations SET title = ? WHERE id = ?", (title, conversation_id))
    conn.commit()
    conn.close()


def update_conversation_summary(conversation_id, summary):
    conn = _get_connection()
    conn.execute("UPDATE conversations SET summary = ? WHERE id = ?", (summary, conversation_id))
    conn.commit()
    conn.close()


def get_recent_summaries(exclude_conversation_id, limit=3):
    """Returneaza rezumatele celor mai recente `limit` conversatii (altele decat
    cea curenta) care au deja un rezumat salvat — folosit pentru memoria extinsa."""
    conn = _get_connection()
    rows = conn.execute("""
        SELECT summary FROM conversations
        WHERE id != ? AND summary IS NOT NULL AND summary != ''
        ORDER BY created_at DESC
        LIMIT ?
    """, (exclude_conversation_id, limit)).fetchall()
    conn.close()
    return [row["summary"] for row in rows]


def save_message(conversation_id, role, content, response_time=None,
                  emotion_label=None, emotion_confidence=None):
    """Salveaza un mesaj si returneaza id-ul lui (necesar pentru feedback)."""
    conn = _get_connection()
    cursor = conn.execute(
        "INSERT INTO messages (conversation_id, role, content, response_time, "
        "created_at, emotion_label, emotion_confidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (conversation_id, role, content, response_time, datetime.now().isoformat(),
         emotion_label, emotion_confidence)
    )
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id


def save_emotion_for_message(message_id, emotion_label, emotion_confidence):
    """Actualizează eticheta emoțională a unui mesaj deja salvat (folosit pentru
    mesajul utilizatorului, după ce clasificarea ML rulează)."""
    conn = _get_connection()
    conn.execute(
        "UPDATE messages SET emotion_label = ?, emotion_confidence = ? WHERE id = ?",
        (emotion_label, emotion_confidence, message_id)
    )
    conn.commit()
    conn.close()


def save_feedback(message_id, feedback):
    """feedback trebuie sa fie 'up', 'down', sau None (pentru a-l sterge)."""
    conn = _get_connection()
    conn.execute("UPDATE messages SET feedback = ? WHERE id = ?", (feedback, message_id))
    conn.commit()
    conn.close()


def get_all_conversations():
    """Returneaza doar conversatiile care au cel putin un mesaj, cele mai recente primele."""
    conn = _get_connection()
    rows = conn.execute("""
        SELECT c.id, c.title, c.created_at
        FROM conversations c
        WHERE EXISTS (SELECT 1 FROM messages m WHERE m.conversation_id = c.id)
        ORDER BY c.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def has_messages(conversation_id):
    conn = _get_connection()
    row = conn.execute(
        "SELECT 1 FROM messages WHERE conversation_id = ? LIMIT 1", (conversation_id,)
    ).fetchone()
    conn.close()
    return row is not None


def get_messages(conversation_id):
    """Returneaza mesajele unei conversatii, in ordine cronologica."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT id, role, content, response_time, feedback, emotion_label, emotion_confidence "
        "FROM messages WHERE conversation_id = ? ORDER BY id ASC",
        (conversation_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_conversation_id():
    conn = _get_connection()
    row = conn.execute(
        "SELECT id FROM conversations ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return row["id"] if row else None


# ---------------- Dashboard: statistici emotionale ----------------

def get_emotion_stats():
    """Returneaza toate mesajele utilizatorului cu eticheta emotionala si data,
    pentru a fi agregate/afisate in dashboard (un rand per mesaj)."""
    conn = _get_connection()
    rows = conn.execute("""
        SELECT created_at, emotion_label, emotion_confidence
        FROM messages
        WHERE role = 'user' AND emotion_label IS NOT NULL
        ORDER BY created_at ASC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_feedback_stats():
    """Numarul de 👍 si 👎 primite de raspunsurile asistentului."""
    conn = _get_connection()
    row = conn.execute("""
        SELECT
            SUM(CASE WHEN feedback = 'up' THEN 1 ELSE 0 END) AS up_count,
            SUM(CASE WHEN feedback = 'down' THEN 1 ELSE 0 END) AS down_count
        FROM messages WHERE role = 'assistant'
    """).fetchone()
    conn.close()
    return {"up": row["up_count"] or 0, "down": row["down_count"] or 0}


# ---------------- Mood Journal ----------------

def save_mood_entry(mood_score, note, entry_date=None):
    conn = _get_connection()
    entry_date = entry_date or date.today().isoformat()
    conn.execute(
        "INSERT INTO mood_entries (entry_date, mood_score, note, created_at) VALUES (?, ?, ?, ?)",
        (entry_date, mood_score, note, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_mood_entries():
    conn = _get_connection()
    rows = conn.execute(
        "SELECT entry_date, mood_score, note, created_at FROM mood_entries ORDER BY entry_date ASC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def has_mood_entry_today():
    conn = _get_connection()
    row = conn.execute(
        "SELECT 1 FROM mood_entries WHERE entry_date = ? LIMIT 1", (date.today().isoformat(),)
    ).fetchone()
    conn.close()
    return row is not None

import sqlite3
from datetime import datetime

def insert_message(conn, msg):
    try:
        conn.execute(
            "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)",
            (
                msg["message_id"],
                msg["from"],
                msg["to"],
                msg["ts"],
                msg.get("text"),
                datetime.utcnow().isoformat() + "Z"
            )
        )
        conn.commit()
        return "created"
    except sqlite3.IntegrityError:
        return "duplicate"

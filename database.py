import sqlite3
import json
from datetime import datetime

DB_PATH = "super_student_ai.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_projet TEXT NOT NULL,
            description TEXT NOT NULL,
            duree TEXT,
            contraintes TEXT,
            resultat_json TEXT NOT NULL,
            date_creation TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def save_projet(nom_projet, description, duree, contraintes, resultat):
    conn = get_db()

    cur = conn.execute(
        """
        INSERT INTO projets 
        (nom_projet, description, duree, contraintes, resultat_json, date_creation)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            nom_projet,
            description,
            duree,
            contraintes,
            json.dumps(resultat, ensure_ascii=False),
            datetime.now().strftime("%d/%m/%Y %H:%M"),
        ),
    )

    conn.commit()
    projet_id = cur.lastrowid
    conn.close()

    return projet_id


def get_projet(projet_id):
    conn = get_db()

    projet = conn.execute(
        "SELECT * FROM projets WHERE id = ?",
        (projet_id,)
    ).fetchone()

    conn.close()

    return projet


def get_all_projets():
    conn = get_db()

    projets = conn.execute(
        "SELECT * FROM projets ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return projets


def delete_projet(projet_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM projets WHERE id = ?",
        (projet_id,)
    )

    conn.commit()
    conn.close()
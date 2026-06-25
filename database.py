import sqlite3
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "super_student_ai.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            date_creation TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS projets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nom_projet TEXT NOT NULL,
            description TEXT NOT NULL,
            duree TEXT,
            contraintes TEXT,
            resultat_json TEXT NOT NULL,
            date_creation TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def create_user(nom, email, password):
    conn = get_db()

    password_hash = generate_password_hash(password)

    cur = conn.execute("""
        INSERT INTO users (nom, email, password_hash, date_creation)
        VALUES (?, ?, ?, ?)
    """, (
        nom,
        email,
        password_hash,
        datetime.now().strftime("%d/%m/%Y %H:%M"),
    ))

    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    return user_id


def get_user_by_email(email):
    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.close()
    return user


def check_user_password(user, password):
    return check_password_hash(user["password_hash"], password)


def save_projet(user_id, nom_projet, description, duree, contraintes, resultat):
    conn = get_db()

    cur = conn.execute("""
        INSERT INTO projets 
        (user_id, nom_projet, description, duree, contraintes, resultat_json, date_creation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        nom_projet,
        description,
        duree,
        contraintes,
        json.dumps(resultat, ensure_ascii=False),
        datetime.now().strftime("%d/%m/%Y %H:%M"),
    ))

    conn.commit()
    projet_id = cur.lastrowid
    conn.close()

    return projet_id


def get_projet(projet_id, user_id):
    conn = get_db()

    projet = conn.execute(
        "SELECT * FROM projets WHERE id = ? AND user_id = ?",
        (projet_id, user_id)
    ).fetchone()

    conn.close()
    return projet


def get_all_projets(user_id):
    conn = get_db()

    projets = conn.execute(
        "SELECT * FROM projets WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()

    conn.close()
    return projets


def delete_projet(projet_id, user_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM projets WHERE id = ? AND user_id = ?",
        (projet_id, user_id)
    )

    conn.commit()
    conn.close()
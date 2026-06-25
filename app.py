import os
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

from database import (
    init_db,
    save_projet,
    get_projet,
    get_all_projets,
    delete_projet,
    create_user,
    get_user_by_email,
    check_user_password
)
from gemini_service import analyser_projet

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "superstudentai")

init_db()


def login_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Vous devez vous connecter pour accéder à cette page.", "warning")
            return redirect(url_for("login"))
        return route(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/inscription", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not nom or not email or not password or not confirm_password:
            flash("Tous les champs sont obligatoires.", "danger")
            return render_template("register.html", nom=nom, email=email)

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template("register.html", nom=nom, email=email)

        if len(password) < 6:
            flash("Le mot de passe doit contenir au moins 6 caractères.", "danger")
            return render_template("register.html", nom=nom, email=email)

        if get_user_by_email(email):
            flash("Un compte existe déjà avec cet email.", "danger")
            return render_template("register.html", nom=nom, email=email)

        create_user(nom, email, password)

        flash("Inscription réussie. Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/connexion", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user = get_user_by_email(email)

        if not user or not check_user_password(user, password):
            flash("Email ou mot de passe incorrect.", "danger")
            return render_template("login.html", email=email)

        session["user_id"] = user["id"]
        session["user_nom"] = user["nom"]

        flash("Connexion réussie.", "success")
        return redirect(url_for("formulaire"))

    return render_template("login.html")


@app.route("/deconnexion")
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("index"))


@app.route("/formulaire", methods=["GET", "POST"])
@login_required
def formulaire():
    if request.method == "POST":
        nom_projet = request.form.get("nom_projet", "").strip()
        description = request.form.get("description", "").strip()
        duree = request.form.get("duree", "").strip()
        contraintes = request.form.get("contraintes", "").strip()

        if not nom_projet or not description:
            flash("Le nom du projet et la description sont obligatoires.", "danger")
            return render_template(
                "formulaire.html",
                nom_projet=nom_projet,
                description=description,
                duree=duree,
                contraintes=contraintes
            )

        if not os.environ.get("GEMINI_API_KEY"):
            flash("Aucune clé API n'est configurée. Ajoute-la dans le fichier .env.", "danger")
            return render_template(
                "formulaire.html",
                nom_projet=nom_projet,
                description=description,
                duree=duree,
                contraintes=contraintes
            )

        try:
            resultat = analyser_projet(nom_projet, description, duree, contraintes)

        except Exception as exc:
            flash(f"Erreur lors de l'analyse : {exc}", "danger")
            return render_template(
                "formulaire.html",
                nom_projet=nom_projet,
                description=description,
                duree=duree,
                contraintes=contraintes
            )

        projet_id = save_projet(
            session["user_id"],
            nom_projet,
            description,
            duree,
            contraintes,
            resultat
        )

        flash("Analyse générée avec succès !", "success")
        return redirect(url_for("resultats", projet_id=projet_id))

    return render_template("formulaire.html")


@app.route("/resultats/<int:projet_id>")
@login_required
def resultats(projet_id):
    projet = get_projet(projet_id, session["user_id"])

    if not projet:
        flash("Projet introuvable.", "warning")
        return redirect(url_for("historique"))

    resultat = json.loads(projet["resultat_json"])

    return render_template(
        "resultats.html",
        projet=projet,
        resultat=resultat
    )


@app.route("/historique")
@login_required
def historique():
    projets = get_all_projets(session["user_id"])
    return render_template("historique.html", projets=projets)


@app.route("/historique/<int:projet_id>/supprimer", methods=["POST"])
@login_required
def supprimer_projet(projet_id):
    delete_projet(projet_id, session["user_id"])
    flash("Projet supprimé de l'historique.", "info")
    return redirect(url_for("historique"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

from database import init_db, save_projet, get_projet, get_all_projets, delete_projet
from gemini_service import analyser_projet

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "superstudentai")

init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/formulaire", methods=["GET", "POST"])
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
                contraintes=contraintes,
            )

        if not os.environ.get("GEMINI_API_KEY"):
            flash(
                "Aucune clé API n'est configurée. Ajoute-la dans le fichier .env.",
                "danger",
            )

            return render_template(
                "formulaire.html",
                nom_projet=nom_projet,
                description=description,
                duree=duree,
                contraintes=contraintes,
            )

        try:
            resultat = analyser_projet(
                nom_projet,
                description,
                duree,
                contraintes
            )

        except Exception as exc:
            flash(f"Erreur lors de l'analyse : {exc}", "danger")

            return render_template(
                "formulaire.html",
                nom_projet=nom_projet,
                description=description,
                duree=duree,
                contraintes=contraintes,
            )

        projet_id = save_projet(
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
def resultats(projet_id):
    projet = get_projet(projet_id)

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
def historique():
    projets = get_all_projets()
    return render_template("historique.html", projets=projets)


@app.route("/historique/<int:projet_id>/supprimer", methods=["POST"])
def supprimer_projet(projet_id):
    delete_projet(projet_id)
    flash("Projet supprimé de l'historique.", "info")

    return redirect(url_for("historique"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
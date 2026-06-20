import os
from dotenv import load_dotenv

load_dotenv()

cle = os.environ.get("GEMINI_API_KEY")

if cle:
    print("Clé API chargée avec succès.")
else:
    print("Aucune clé API trouvée.")
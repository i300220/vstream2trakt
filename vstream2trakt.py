import sqlite3
import requests
import time
import json
from tqdm import tqdm
from datetime import datetime

# ================== CONFIGURATION ==================

# Chemin vers ta base de données vStream
DB_PATH = r"/home/shizuma/.kodi/userdata/addon_data/plugin.video.vstream/video_cache.db"  # ← À MODIFIER

# Tes identifiants Trakt (OAuth)
CLIENT_ID = "ton_client_id_ici"
CLIENT_SECRET = "ton_client_secret_ici"

# Date de visionnage par défaut (si tu ne sais plus la date exacte)
# Utilise None pour que Trakt mette la date actuelle
WATCHED_DATE = "2023-01-01T12:00:00.000Z"   # ou None
BATCH_SIZE = 150
SLEEP_BETWEEN_BATCHES = 3.5   # secondes (augmente si tu as encore des 504)

# =================================================

# Authentification OAuth Trakt
def get_access_token():
    print("=== Authentification Trakt ===")
    auth_url = "https://trakt.tv/oauth/authorize"
    token_url = "https://api.trakt.tv/oauth/token"

    # Étape 1 : Obtenir le code de vérification
    print(f"Ouvre ce lien dans ton navigateur :\n")
    print(f"https://trakt.tv/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri=urn:ietf:wg:oauth:2.0:oob")
    code = input("\nColle ici le code que Trakt t'a donné : ").strip()

    # Étape 2 : Échanger le code contre un token
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, json=data)
    if response.status_code != 200:
        print("Erreur lors de l'obtention du token :", response.text)
        exit(1)

    token_info = response.json()
    access_token = token_info["access_token"]
    print("✅ Authentification réussie !\n")
    return access_token


# Connexion à la base vStream et récupération des IDs
def get_movies_from_vstream():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # vStream stocke souvent les films dans la table "movie"
    # On cherche les colonnes tmdb_id et imdb_id
    query = """
        SELECT DISTINCT 
            title,
            COALESCE(tmdb_id, '') as tmdb_id,
            COALESCE(imdb_id, '') as imdb_id,
            year
        FROM movie 
        WHERE (tmdb_id IS NOT NULL OR imdb_id IS NOT NULL)
        AND tmdb_id != '' OR imdb_id != ''
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    print(f"{len(rows)} films trouvés dans la base vStream.")
    return rows


# Construction du payload pour Trakt (par lots de 1000 max)
def build_history_payload(movies):
    items = []
    for movie in movies:
        movie_obj = {"ids": {}}

        if movie["tmdb_id"] and movie["tmdb_id"].strip():
            movie_obj["ids"]["tmdb"] = int(movie["tmdb_id"])
        if movie["imdb_id"] and movie["imdb_id"].strip():
            movie_obj["ids"]["imdb"] = movie["imdb_id"].strip()

        # On ajoute le film même si un seul ID est présent
        if movie_obj["ids"]:
            if WATCHED_DATE:
                movie_obj["watched_at"] = WATCHED_DATE
            items.append(movie_obj)

    return {"movies": items}


# Envoi vers Trakt
def send_to_trakt(access_token, payload):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "trakt-api-version": "2",
        "trakt-api-key": CLIENT_ID
    }

    url = "https://api.trakt.tv/sync/history"

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in (200, 201):
        result = response.json()
        print(f"✅ Succès ! {result.get('added', {}).get('movies', 0)} films ajoutés.")
        if result.get('not_found'):
            print(f"   {len(result['not_found'].get('movies', []))} films non trouvés.")
        return True
    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        return False

# ================== MAIN ==================

def main():
    access_token = get_access_token()

    movies = get_movies_from_vstream()

    if not movies:
        print("Aucun film trouvé avec un ID TMDB ou IMDB.")
        return

    # On envoie par lots de 100-150 pour éviter les timeouts/limites
    total_added = 0

    for i in tqdm(range(0, len(movies), BATCH_SIZE), desc="Envoi des batches"):
        batch = movies[i:i + BATCH_SIZE]
        payload = build_history_payload(batch)

        if not payload["movies"]:
            continue

        success = send_to_trakt(access_token, payload)
        if success:
            total_added += len(payload["movies"])

        # Petite pause pour ne pas se faire ban (rate limit Trakt)
        time.sleep(1.2)

    print(f"\n=== FIN ===")
    print(f"Total de films envoyés : {total_added} / {len(movies)}")


if __name__ == "__main__":
    main()
  

# vstream2trakt
Synchroniser les films que vous avez regardes avec vStream dans trakt.tv

## Resume
J'ai cree ce script parce que j'ai regarde plusieurs script avec l'addon [vStream](https://github.com/Kodi-vStream/venom-xbmc-addons) pour Kodi mais le suivi dans [trakt](https://trakt.tv/dashboard) n'etait pas active.  Resultat,  [couchmoney](https://couchmoney.tv/mylists) me proposait en majorite, des films que j'avais deja vus.

## Installation
Alors ce script va pallier a cette difference en synchronisant les films vus a l'aide de vStream, qui conserve une base de donnees locale, avec trakt.  La majorite des services savent importer les donnees de trakt, alors la synchronisation sera valide avec tous vos addons qui utilisent trakt.

Je l'ai teste sur une machine Fedora 42 et tout ce que j'ai eu a installer fut 
```bash
sudo dnf install python3-tqdm
```
Quoi qu'il en soit, votre machine doit avoir python installe et necessite requests, sqlite3 et tqdm pour fonctionner.  Si ces paquets sont disponibles dans votre distribution linux, privilegiez-les.  Sinon, installez-les avec pip. 
Sur Fedora par exemple:  
```bash
python3 -m pip install --user requests sqlite3 tqdm
```
Ce script va egalement fonctionner sous windows, en autant que python soit deja installe.

Maintenant il va vous falloir creer une application pour utiliser l'api de trakt en vous rendant sur [ce site](https://trakt.tv/oauth/applications/new)

![Application](./trakt.png)

Entrez vstream2trakt dans 'name', 

utilisez n'importe quoi comme image, 

entrez une courte description, 

entrez 'urn:ietf:wg:oauth:2.0:oob' comme redirect url, 

cliquez pour autoriser les permission checkin et scrobble, 

ensuite cliquez sur 'save app'.

  Si tout va bien, votre app est prete et vous obtiendrez vos identifiants.  Il va vous falloir editer le fichier vstream2trakt.py et entrer ces donnees avant de l'executer.  C'est la configuration requise avant de l'utiliser. Remplacez le texte dans le fichier vstream2trakt.py par ce que trakt vous a donne:

```python
CLIENT_ID = "ton_client_id_ici"

CLIENT_SECRET = "ton_client_secret_ici"
```
Changez egalement le chemin ou trouver la base de donnees de vStream.

Ici c'est deja configure pour une machine sous Fedora linux.

```python
DB_PATH = r"/home/TON_NOM_D_UTILISATEUR/.kodi/userdata/addon_data/plugin.video.vstream/video_cache.db"  # ← À MODIFIER
```
Ce chemin sera different pour windows.
```python
DB_PATH = r"%APPDATA%\Kodi\userdata\addon_data\plugin.video.vstream\video_cache.db"  # ← À MODIFIER
```
ou
```python
DB_PATH = r"C:\Users\TON_NOM_D_UTILISATEUR\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.vstream\video_cache.db  #  ← À MODIFIER
```

![Vstream](./vstream.webp)

Si vous voulez la date actuelle au lieu d'une date dans le passe comme date de visionnement, changez cela: 

```python
WATCHED_DATE = "2023-01-01T12:00:00.000Z"   # ou None pour la date actuelle
```
C'est tout pour la configuration.  Sauvegardez vstream2trakt.py.

## Documentation

La documentation pour l'API de trakt se trouve [ici](https://docs.trakt.tv/docs/create-an-app) si jamais vous en avez besoin.

## Utilisation

Une fois proprement configure - il y a une section 'configuration' au tout debut de vstream2trakt.py - executez le script de la facon suivante: 
```bash
python ~/bin/vstream2trakt.py
```
(en supposant que le script a ete place dans ~/bin) et suivez les instructions donnees par trakt.  Utilisez le bon chemin!  

![Execution](./execution.webp)

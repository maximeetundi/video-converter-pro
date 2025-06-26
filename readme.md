# 🎬 Convertisseur Vidéo Pro - Documentation Complète

**Auteur :** Maxime ETUNDI  
**GitHub :** https://github.com/maximeetundi/video-converter-pro  
**Contact :** maximeetundi@gmail.com

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Fonctionnalités](#fonctionnalités)
3. [Architecture technique](#architecture-technique)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Utilisation](#utilisation)
7. [API](#api)
8. [Dépannage](#dépannage)
9. [Contribution](#contribution)
10. [Licence](#licence)

## 🎯 Vue d'ensemble

Le **Convertisseur Vidéo Pro** est une application web Flask moderne qui permet de télécharger des vidéos depuis diverses sources (HTTP, torrents, liens magnets) et de les convertir dans différents formats et résolutions. L'interface utilisateur est élégante, responsive et inclut un mode sombre.

### Caractéristiques principales
- Interface web moderne avec thème sombre/clair
- Téléchargement de vidéos depuis URLs HTTP et torrents
- Conversion multi-format (MP4, MKV, AVI, WebM)
- Conversion multi-résolution (480p, 720p, 1080p)
- Lecteur vidéo intégré pour prévisualisation
- Suivi de progression en temps réel
- Historique des téléchargements
- Nettoyage automatique des fichiers (24h)
- Statistiques d'utilisation

## ⚡ Fonctionnalités

### 🔽 Téléchargement
- **URLs HTTP/HTTPS** : Téléchargement direct de fichiers vidéo
- **Torrents** : Support des liens magnet et fichiers .torrent
- **Progression** : Suivi en temps réel avec pourcentage

### 🔄 Conversion
- **Formats supportés** : MP4, MKV, AVI, WebM
- **Résolutions** : 480p, 720p, 1080p
- **Codec vidéo** : H.264 (libx264) avec preset rapide
- **Codec audio** : AAC 128kbps
- **Progression** : Suivi frame par frame avec pourcentage

### 🎮 Interface utilisateur
- **Design moderne** : Interface glassmorphique avec Tailwind CSS
- **Responsive** : Adapté mobile, tablette et desktop
- **Thème adaptatif** : Mode sombre/clair automatique
- **Lecteur intégré** : Prévisualisation avec Plyr.js
- **Icônes** : Font Awesome pour l'iconographie

### 📊 Gestion des fichiers
- **Stockage organisé** : Séparation fichiers originaux/convertis
- **Expiration** : Suppression automatique après 24h
- **Métadonnées** : Taille, date d'expiration
- **Actions** : Télécharger, supprimer, copier lien, prévisualiser

## 🏗️ Architecture technique

### Backend (Python/Flask)
```
server_pikpak.py
├── Flask Application
├── SQLite Database (historique)
├── File Management
├── Video Processing (FFmpeg)
├── Download Management (aria2c/requests)
└── Progress Tracking
```

### Frontend (HTML/CSS/JS)
```
HTML_TEMPLATE
├── Tailwind CSS (styling)
├── Font Awesome (icons)
├── Plyr.js (video player)
├── Vanilla JavaScript (interactions)
└── Responsive Design
```

### Structure des dossiers
```
projet/
├── server_pikpak.py          # Application principale
├── history.db                # Base de données SQLite
├── converted/                 # Dossier des fichiers convertis
├── fichier_original.mp4       # Fichiers téléchargés
└── autre_fichier.mkv         # Autres fichiers
```

## 🚀 Installation

### Prérequis système
- Python 3.7+
- FFmpeg
- aria2c
- Connexion Internet

### 🐧 Installation sur Linux (Ubuntu/Debian)

#### 1. Mise à jour du système
```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Installation de Python et pip
```bash
sudo apt install python3 python3-pip python3-venv -y
```

#### 3. Installation de FFmpeg
```bash
sudo apt install ffmpeg -y
```

#### 4. Installation d'aria2c
```bash
sudo apt install aria2 -y
```

#### 5. Vérification des installations
```bash
python3 --version
ffmpeg -version
aria2c --version
```

#### 6. Installation de l'application
```bash
# Créer un dossier pour le projet
mkdir convertisseur-video
cd convertisseur-video

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances Python
pip install flask requests

# Cloner le projet depuis GitHub
git clone https://github.com/maximeetundi/video-converter-pro.git .

# Ou télécharger manuellement le fichier server_pikpak.py
# wget https://raw.githubusercontent.com/maximeetundi/video-converter-pro/main/server_pikpak.py

# Rendre le fichier exécutable
chmod +x server_pikpak.py
```

#### 7. Lancement
```bash
python3 server_pikpak.py
```

### 🪟 Installation sur Windows

#### 1. Installation de Python
- Télécharger Python depuis [python.org](https://python.org)
- Cocher "Add to PATH" pendant l'installation
- Vérifier : `python --version`

#### 2. Installation de FFmpeg
```powershell
# Méthode 1 : Chocolatey (recommandée)
choco install ffmpeg

# Méthode 2 : Scoop
scoop install ffmpeg

# Méthode 3 : Manuelle
# Télécharger depuis https://ffmpeg.org/download.html
# Extraire dans C:\ffmpeg
# Ajouter C:\ffmpeg\bin au PATH
```

#### 3. Installation d'aria2c
```powershell
# Méthode 1 : Chocolatey
choco install aria2

# Méthode 2 : Scoop  
scoop install aria2

# Méthode 3 : Manuelle
# Télécharger depuis https://aria2.github.io/
# Extraire et ajouter au PATH
```

#### 4. Installation de l'application
```powershell
# Créer un dossier
mkdir convertisseur-video
cd convertisseur-video

# Créer environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer dépendances
pip install flask requests

# Cloner le projet depuis GitHub
git clone https://github.com/maximeetundi/video-converter-pro.git .

# Ou télécharger manuellement
# Invoke-WebRequest -Uri "https://raw.githubusercontent.com/maximeetundi/video-converter-pro/main/server_pikpak.py" -OutFile "server_pikpak.py"
```

#### 5. Lancement
```powershell
python server_pikpak.py
```

### 🍎 Installation sur macOS

#### 1. Installation de Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Installation des outils
```bash
# Python (si pas déjà installé)
brew install python

# FFmpeg
brew install ffmpeg

# aria2c
brew install aria2
```

#### 3. Installation de l'application
```bash
# Créer le projet
mkdir convertisseur-video
cd convertisseur-video

# Environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Dépendances
pip install flask requests

# Cloner le projet depuis GitHub
git clone https://github.com/maximeetundi/video-converter-pro.git .

# Ou télécharger manuellement
# curl -O https://raw.githubusercontent.com/maximeetundi/video-converter-pro/main/server_pikpak.py
```

#### 4. Lancement
```bash
python3 server_pikpak.py
```

### 🐳 Installation avec Docker

#### 1. Dockerfile
```dockerfile
FROM python:3.11-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Installation des dépendances Python
RUN pip install flask requests

# Copie du code source
COPY server_pikpak.py .

# Création des dossiers
RUN mkdir converted

# Exposition du port
EXPOSE 8000

# Commande de démarrage
CMD ["python", "server_pikpak.py"]
```

#### 2. Construction et lancement
```bash
# Construire l'image
docker build -t convertisseur-video .

# Lancer le conteneur
docker run -d -p 8000:8000 -v $(pwd)/data:/app convertisseur-video
```

#### 3. Docker Compose
```yaml
version: '3.8'
services:
  convertisseur:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app
      - ./converted:/app/converted
    restart: unless-stopped
```

## ⚙️ Configuration

### Variables d'environnement
```bash
# Port d'écoute (défaut: 8000)
export PORT=8000

# Répertoire de travail
export UPLOAD_DIR="/path/to/files"

# Répertoire des fichiers convertis
export CONVERTED_DIR="/path/to/converted"

# Chemin de la base de données
export DB_PATH="/path/to/history.db"
```

### Configuration FFmpeg
Les paramètres de conversion peuvent être modifiés dans la fonction `convert_video()` :

```python
cmd = [
    "ffmpeg", "-y", "-i", filepath,
    "-vf", f"scale=-2:{height}",
    "-c:v", "libx264",         # Codec vidéo
    "-preset", "fast",         # Preset de vitesse
    "-crf", "28",             # Qualité (18-28)
    "-c:a", "aac",            # Codec audio
    "-b:a", "128k",           # Bitrate audio
    output_path
]
```

### Configuration aria2c
Pour modifier les paramètres de téléchargement torrent :

```python
subprocess.run([
    "aria2c", 
    "--seed-time=0",          # Temps de seed
    "--max-connection-per-server=16",  # Connexions max
    "--split=16",             # Segments de téléchargement
    url, 
    "-d", UPLOAD_DIR
], check=True)
```

## 📖 Utilisation

### Interface web
1. Accéder à `http://localhost:8000`
2. Coller un lien vidéo (HTTP ou magnet)
3. Sélectionner résolutions et formats
4. Cliquer sur "Lancer"
5. Suivre la progression
6. Télécharger les fichiers convertis

### Fonctionnalités avancées

#### Reconversion
- Cliquer sur l'icône "baguette magique" d'un fichier original
- Sélectionner nouvelles résolutions/formats
- Lancer la reconversion

#### Prévisualisation
- Cliquer sur l'icône "play" pour ouvrir le lecteur
- Contrôles complets (lecture, pause, volume, plein écran)
- Fermer avec la croix ou clic extérieur

#### Gestion des fichiers
- **Télécharger** : Icône de flèche vers le bas
- **Copier lien** : Icône de copie (lien direct)
- **Supprimer** : Icône de poubelle (confirmation requise)

#### Thème
- Bouton "Thème" en haut à droite
- Bascule entre mode clair et sombre
- Préférence sauvegardée localement

## 🔌 API

### Endpoints principaux

#### GET /
```
Description: Page d'accueil avec interface utilisateur
Retour: HTML template avec liste des fichiers
```

#### POST /download
```
Description: Télécharge et convertit une vidéo
Paramètres:
  - url: URL de la vidéo
  - resolutions[]: Liste des résolutions
  - formats[]: Liste des formats
  - perform_conversion: Case à cocher pour conversion
Retour: Redirection vers /
```

#### POST /convert/<filename>
```
Description: Convertit un fichier existant
Paramètres:
  - resolutions[]: Nouvelles résolutions
  - formats[]: Nouveaux formats
Retour: Redirection vers /
```

#### GET /progress
```
Description: État de la progression actuelle
Retour: JSON
{
  "message": "Téléchargement... 45%",
  "percentage": 45,
  "done": false
}
```

#### GET /files/<filename>
```
Description: Télécharge un fichier converti
Retour: Fichier en téléchargement
```

#### GET /uploads/<filename>
```
Description: Télécharge un fichier original
Retour: Fichier en téléchargement
```

#### POST /delete/<type>/<filename>
```
Description: Supprime un fichier
Paramètres:
  - type: "original" ou "converted"
  - filename: Nom du fichier
Retour: Status 204
```

### Format des réponses JSON

#### Progression
```json
{
  "message": "Conversion... video_123 (2/6) - 67.3%",
  "percentage": 67.3,
  "done": false
}
```

#### Erreur
```json
{
  "message": "❌ Erreur: Fichier non trouvé",
  "done": true
}
```

## 🔧 Dépannage

### Problèmes courants

#### "ffmpeg: command not found"
```bash
# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

#### "aria2c: command not found"
```bash
# Linux
sudo apt install aria2

# macOS
brew install aria2

# Windows
choco install aria2
```

#### Port 8000 déjà utilisé
```bash
# Trouver le processus
sudo lsof -i :8000

# Tuer le processus
sudo kill -9 <PID>

# Ou changer le port
export PORT=8080
python3 server_pikpak.py
```

#### Erreur de permissions
```bash
# Donner les permissions au dossier
chmod 755 /path/to/project
chmod +x server_pikpak.py
```

#### Base de données corrompue
```bash
# Supprimer et recréer
rm history.db
# Redémarrer l'application
```

### Logs de débogage

#### Activer les logs Flask
```python
app.run(host='0.0.0.0', port=8000, debug=True)
```

#### Logs FFmpeg
```python
# Ajouter dans convert_video()
cmd.extend(["-v", "verbose"])
```

#### Logs aria2c
```python
# Ajouter dans download_task()
cmd.extend(["--log", "aria2.log", "--log-level=info"])
```

### Optimisation des performances

#### Paramètres FFmpeg
```python
# Conversion plus rapide (qualité réduite)
"-preset", "ultrafast"
"-crf", "30"

# Meilleure qualité (plus lent)
"-preset", "slow"
"-crf", "20"
```

#### Téléchargements plus rapides
```python
# aria2c optimisé
"--max-connection-per-server=16"
"--split=16"
"--max-concurrent-downloads=5"
```

## 🤝 Contribution

### Structure du code

#### Backend (server_pikpak.py)
```python
# Configuration et initialisation
Flask app, dossiers, base de données

# Fonctions utilitaires
format_size(), cleanup_old_files(), init_db()

# Fonctions de traitement
convert_video(), start_processing_thread()

# Routes Flask
@app.route() pour chaque endpoint

# Template HTML
HTML_TEMPLATE avec JavaScript intégré
```

#### Frontend (dans HTML_TEMPLATE)
```javascript
// Fonctions utilitaires
checkProgress(), deleteFile(), toggleTheme()

// Gestion des modales
openPlayerModal(), closePlayerModal()
openConversionModal(), closeModal()

// Interactions
copyToClipboard(), window.onclick
```

### Guidelines de développement

#### Code Python
- Utiliser les conventions PEP 8
- Documenter les fonctions complexes
- Gérer les exceptions proprement
- Utiliser les context managers pour les fichiers

#### Code JavaScript
- Utiliser des noms de fonctions explicites
- Gérer les erreurs avec try/catch
- Optimiser les requêtes AJAX
- Maintenir la compatibilité navigateurs

#### HTML/CSS
- Structure sémantique HTML5
- Classes Tailwind CSS consistantes
- Responsive design mobile-first
- Accessibilité (ARIA labels)

### Ajout de fonctionnalités

#### Nouveau format de sortie
```python
# Dans convert_video()
formats = ["mp4", "mkv", "avi", "webm", "nouveau_format"]

# Dans HTML_TEMPLATE
<option value="nouveau_format">Nouveau Format</option>
```

#### Nouvelle résolution
```python
# Dans convert_video()
resolutions = ["480p", "720p", "1080p", "1440p"]

# Ajuster la logique de hauteur
height = res.replace("p", "")
```

#### Nouveau service de téléchargement
```python
def download_from_new_service(url):
    # Logique de téléchargement
    pass

# Dans download_task()
elif "nouveau_service.com" in url:
    downloaded_filepath = download_from_new_service(url)
```

### Tests

#### Tests unitaires
```python
import unittest
import tempfile
import os

class TestVideoConverter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def test_format_size(self):
        self.assertEqual(format_size(1024), "1.00 KB")
        
    def test_file_cleanup(self):
        # Test de nettoyage des fichiers
        pass
```

#### Tests d'intégration
```python
def test_download_and_convert():
    # Test complet de téléchargement et conversion
    pass

def test_api_endpoints():
    # Test des endpoints Flask
    pass
```

## 📄 Licence

Ce projet est sous licence MIT. Vous êtes libre de l'utiliser, le modifier et le distribuer.

```
MIT License

Copyright (c) 2024 Maxime ETUNDI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support

Pour toute question ou problème :
1. Vérifiez la section [Dépannage](#dépannage)
2. Consultez les logs d'erreur
3. Créez une issue sur le [dépôt GitHub](https://github.com/maximeetundi/video-converter-pro)
4. Contactez le développeur : maximeetundi@gmail.com

## 🔗 Liens utiles

- **Dépôt GitHub :** https://github.com/maximeetundi/video-converter-pro
- **Auteur :** Maxime ETUNDI
- **Email :** maximeetundi@gmail.com

---

**Développé par :** Maxime ETUNDI  
**Version de la documentation :** 1.0  
**Dernière mise à jour :** Décembre 2024
from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory, jsonify
import os
import subprocess
import threading
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse
import sqlite3
import time
import re # NOUVEAU : pour analyser la sortie de ffmpeg

app = Flask(__name__)
UPLOAD_DIR = os.getcwd()
CONVERTED_DIR = os.path.join(UPLOAD_DIR, "converted")
DB_PATH = os.path.join(UPLOAD_DIR, "history.db")
os.makedirs(CONVERTED_DIR, exist_ok=True)
progress_status = {}

# Fichiers à exclure des listes
EXCLUDED_FILES = {os.path.basename(__file__), os.path.basename(DB_PATH), 'server_pikpak.py', 'converted'}

# Types de médias autorisés pour l'upload local
VIDEO_FORMATS = {"mp4", "webm", "mkv", "avi", "mov"}
AUDIO_FORMATS = {"mp3", "aac", "m4a", "wav", "flac", "ogg"}
ALLOWED_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.ts', '.m4v', '.mp3', '.aac', '.m4a', '.wav', '.flac', '.ogg'}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

init_db()

def save_history(link):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO history (url) VALUES (?)", (link,))

def load_history():
    with sqlite3.connect(DB_PATH) as conn:
        return [row[0] for row in conn.execute("SELECT url FROM history ORDER BY id DESC LIMIT 10")]

# --- MISE À JOUR DU TEMPLATE HTML ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr" class="">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🎬 Convertisseur Vidéo Pro</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.2/css/all.min.css">
  <script>
    tailwind.config = { darkMode: 'class' }
  </script>
  <style>
    .glass-effect { backdrop-filter: blur(16px) saturate(180%); -webkit-backdrop-filter: blur(16px) saturate(180%); background-color: rgba(255, 255, 255, 0.75); border: 1px solid rgba(209, 213, 219, 0.3); }
    .dark .glass-effect { background-color: rgba(17, 24, 39, 0.75); border: 1px solid rgba(255, 255, 255, 0.125); }
    #conversionModal, #playerModal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 100; justify-content: center; align-items: center; }
    .btn-action {
        display: inline-flex; align-items: center; justify-content: center;
        width: 2.5rem; height: 2.5rem; /* Larger size */
        border-radius: 9999px;
        background-color: rgba(156, 163, 175, 0.2);
        transition: all 0.2s ease-in-out;
        transform: scale(1);
    }
    .btn-action:hover {
        background-color: rgba(156, 163, 175, 0.4);
        transform: scale(1.1);
    }
    .dark .btn-action { background-color: rgba(75, 85, 99, 0.4); }
    .dark .btn-action:hover { background-color: rgba(75, 85, 99, 0.7); }
    .btn-action i { font-size: 1rem; }
    .dark .plyr {
        --plyr-video-background: #1f2937;
        --plyr-control-background: rgba(31, 41, 55, 0.8);
        --plyr-control-color: #d1d5db;
    }
  </style>
  <!-- NOUVEAU : Plyr.io Player -->
  <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
  <script src="https://cdn.plyr.io/3.7.8/plyr.js"></script>
  <script>
    function checkProgress() {
      fetch('/progress')
        .then(res => res.json())
        .then(data => {
          const progressEl = document.getElementById('progress');
          const progressBar = document.getElementById('progress-bar-inner');
          const spanEl = progressEl.querySelector('span');
          if (data.message) {
            progressEl.classList.remove('hidden');
            spanEl.textContent = data.message;
            if (data.percentage !== undefined) {
              progressBar.style.width = data.percentage + '%';
            }
            if (!data.done) {
              setTimeout(checkProgress, 1500);
            } else {
              progressBar.style.width = '100%';
              setTimeout(() => { location.reload(); }, 2000);
            }
          } else {
             progressEl.classList.add('hidden');
          }
        });
    }
    
    // Progression côté client pour l'upload local
    function setupUploadProgress() {
      const form = document.querySelector('form[action="/upload"]');
      if (!form) return;
      form.id = 'uploadForm';
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        const fileInput = form.querySelector('input[type="file"][name="file"]');
        if (!fileInput || !fileInput.files.length) { form.submit(); return; }
        const progressEl = document.getElementById('progress');
        const progressBar = document.getElementById('progress-bar-inner');
        const spanEl = progressEl.querySelector('span');
        progressEl.classList.remove('hidden');
        spanEl.textContent = 'Téléversement... 0%';
        progressBar.style.width = '0%';

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload');
        xhr.upload.onprogress = function (evt) {
          if (evt.lengthComputable) {
            const percent = Math.round((evt.loaded / evt.total) * 100);
            progressBar.style.width = percent + '%';
            spanEl.textContent = 'Téléversement... ' + percent + '%';
          }
        };
        xhr.onload = function () { window.location.reload(); };
        xhr.onerror = function () { spanEl.textContent = 'Erreur de téléversement'; };
        const fd = new FormData(form);
        xhr.send(fd);
      });
    }
    
    function deleteFile(fileType, filename) {
      if (confirm(`Êtes-vous sûr de vouloir supprimer ce fichier ? (${filename})`)) {
        fetch(`/delete/${fileType}/${filename}`, { method: 'POST' })
          .then(() => location.reload());
      }
    }
    
    function toggleTheme() {
      document.documentElement.classList.toggle('dark');
      localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    }
    
    function copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        const btn = event.target.closest('button');
        const originalIcon = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check text-green-500"></i>';
        setTimeout(() => { btn.innerHTML = originalIcon; }, 1200);
      });
    }

    // NOUVEAU : Fonctions pour le lecteur vidéo
    let player;
    function openPlayerModal(videoUrl) {
        const container = document.getElementById('player-container');
        container.innerHTML = `<video controls playsinline src="${videoUrl}"></video>`;
        player = new Plyr(container.querySelector('video'), { title: 'Prévisualisation' });
        document.getElementById('playerModal').style.display = 'flex';
        player.play();
    }

    function closePlayerModal() {
        if (player) {
            player.destroy();
            player = null;
        }
        document.getElementById('playerModal').style.display = 'none';
        document.getElementById('player-container').innerHTML = '';
    }

    // NOUVEAU : Fonctions pour la modale de re-conversion
    function openConversionModal(filename) {
        const modal = document.getElementById('conversionModal');
        const form = document.getElementById('reconvertForm');
        const filenameSpan = document.getElementById('filename-span');
        
        if (filenameSpan) {
            filenameSpan.textContent = filename;
        }
        if (form) {
            form.action = `/convert/${filename}`;
        }
        if (modal) {
            modal.style.display = 'flex'; // Utiliser flex pour centrer grâce à justify-center items-center
        }
    }

    function closeModal() { // Fonction unifiée pour fermer les modales
        const conversionModal = document.getElementById('conversionModal');
        if (conversionModal) {
            conversionModal.style.display = 'none';
        }
        
        // Si on a d'autres modales, on peut les cacher ici aussi
        const playerModal = document.getElementById('playerModal');
        if (playerModal && playerModal.style.display !== 'none') {
            closePlayerModal();
        }
    }
    
    window.onload = function() {
      if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
      }
      checkProgress();
      setupUploadProgress();
      // Fermer les modales si on clique en dehors
      window.onclick = function(event) {
        const convModal = document.getElementById('conversionModal');
        if (event.target == convModal) {
            closeConversionModal();
        }
        const playerModal = document.getElementById('playerModal');
        if (event.target == playerModal) {
            closePlayerModal();
        }
      }
    };
  </script>
</head>
<body class="bg-slate-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200 transition-colors duration-300">
  
  <!-- NOUVEAU : Modale pour le lecteur vidéo -->
  <div id="playerModal" class="fixed inset-0 bg-black bg-opacity-70 justify-center items-center z-50">
    <div class="relative w-full max-w-4xl mx-4">
      <button onclick="closePlayerModal()" class="absolute -top-10 right-0 text-white text-3xl font-bold">&times;</button>
      <div id="player-container"></div>
    </div>
  </div>
  
  <!-- NOUVEAU : Modale de Reconversion -->
  <div id="conversionModal" class="fixed inset-0 bg-black bg-opacity-50 justify-center items-center">
    <div class="glass-effect relative w-full max-w-md p-6 rounded-2xl shadow-xl">
      <button type="button" onclick="closeModal()" class="absolute top-4 right-4 text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-white transition-colors">
        <i class="fa-solid fa-xmark fa-lg"></i>
      </button>
      <h3 class="text-xl font-bold text-center text-gray-800 dark:text-white mb-4">Reconvertir le fichier</h3>
      <form id="reconvertForm" action="" method="POST" class="space-y-6">
        <p class="text-sm text-center text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 p-2 rounded-lg">Fichier: <strong id="filename-span" class="font-mono"></strong></p>
        
        <div>
          <label class="block text-md font-semibold text-gray-700 dark:text-gray-200 mb-2">Résolutions :</label>
          <div class="grid grid-cols-3 gap-2">
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-900 transition-colors"><input type="checkbox" name="resolutions" value="1080p" class="mr-2 accent-blue-500">1080p</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-900 transition-colors"><input type="checkbox" name="resolutions" value="720p" class="mr-2 accent-blue-500">720p</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-900 transition-colors"><input type="checkbox" name="resolutions" value="480p" class="mr-2 accent-blue-500">480p</label>
          </div>
        </div>

        <div>
          <label class="block text-md font-semibold text-gray-700 dark:text-gray-200 mb-2">Formats :</label>
          <div class="grid grid-cols-3 gap-2">
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="mp4" class="mr-2 accent-green-500">MP4</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="webm" class="mr-2 accent-green-500">WebM</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="mkv" class="mr-2 accent-green-500">MKV</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="avi" class="mr-2 accent-green-500">AVI</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="mov" class="mr-2 accent-green-500">MOV</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="mp3" class="mr-2 accent-green-500">MP3</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="aac" class="mr-2 accent-green-500">AAC</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="m4a" class="mr-2 accent-green-500">M4A</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="wav" class="mr-2 accent-green-500">WAV</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="flac" class="mr-2 accent-green-500">FLAC</label>
            <label class="flex items-center justify-center p-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-green-100 dark:hover:bg-green-900 transition-colors"><input type="checkbox" name="formats" value="ogg" class="mr-2 accent-green-500">OGG</label>
          </div>
        </div>

        <div class="pt-4">
          <button type="submit" class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white text-base font-bold rounded-lg shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-transform transform hover:scale-105">
            <i class="fa-solid fa-cogs"></i>
            Lancer la conversion
          </button>
        </div>
      </form>
    </div>
  </div>

  <div class="max-w-6xl mx-auto px-4 py-8">
      <header class="flex flex-col sm:flex-row justify-between items-center mb-8">
        <div class="flex items-center space-x-3">
            <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-xl shadow-lg"><i class="fa-solid fa-video"></i></div>
            <div><h1 class="text-3xl font-bold">Convertisseur Vidéo</h1><p class="text-gray-600 dark:text-gray-300 text-sm">Téléchargez et convertissez simplement</p></div>
        </div>
        <button onclick="toggleTheme()" class="mt-4 sm:mt-0 px-4 py-2 rounded-xl bg-slate-200 dark:bg-gray-800 hover:bg-slate-300 dark:hover:bg-gray-700 transition-all"><i class="fa-solid fa-moon dark:hidden"></i><i class="fa-solid fa-sun hidden dark:inline"></i><span class="ml-2 text-sm font-medium">Thème</span></button>
      </header>

      <!-- Upload local -->
      <div class="glass-effect p-6 rounded-2xl mb-6">
        <h3 class="font-semibold mb-4"><i class="fa-solid fa-upload text-purple-600 mr-2"></i>Importer un média local</h3>
        <form action="/upload" method="POST" enctype="multipart/form-data" class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <input type="file" name="file" required class="flex-1 px-4 py-2 rounded-xl bg-white/80 dark:bg-gray-900/80 border border-gray-200 dark:border-gray-600" accept=".mp4,.mkv,.avi,.mov,.flv,.wmv,.webm,.ts,.m4v" />
          <button type="submit" class="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold hover:from-purple-700 hover:to-blue-700 transition">
            Importer
          </button>
        </form>
      </div>

      <!-- Panneau de Progression -->
      <div id="progress" class="hidden mb-6">
        <div class="flex items-center space-x-3 p-4 bg-blue-50 dark:bg-gray-800 rounded-xl border border-blue-200 dark:border-gray-700">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <div class="w-full">
                <span class="text-blue-800 dark:text-blue-200 font-medium"></span>
                <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2.5 mt-2">
                    <div id="progress-bar-inner" class="bg-blue-600 h-2.5 rounded-full" style="width: 0%"></div>
                </div>
            </div>
        </div>
      </div>
      
      <div class="grid lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2">
          <form method="post" action="/download" class="glass-effect p-8 rounded-2xl space-y-6">
            <div><label class="block text-sm font-semibold mb-2">Lien Vidéo</label><input type="text" name="url" required class="w-full px-4 py-3 bg-white/80 dark:bg-gray-900/80 border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500" placeholder="Collez un lien HTTP, Magnet..."/></div>
            <div class="grid md:grid-cols-2 gap-6">
              <div><label class="block text-sm font-semibold mb-2">Résolutions</label><select name="resolutions" multiple class="w-full h-28 px-4 py-3 bg-white/80 dark:bg-gray-900/80 border-gray-200 dark:border-gray-600 rounded-xl"><option value="480p" selected>480p</option><option value="720p">720p</option><option value="1080p">1080p</option></select></div>
              <div><label class="block text-sm font-semibold mb-2">Formats</label><select name="formats" multiple class="w-full h-28 px-4 py-3 bg-white/80 dark:bg-gray-900/80 border-gray-200 dark:border-gray-600 rounded-xl">
                <optgroup label="Vidéo">
                  <option value="mp4" selected>MP4</option>
                  <option value="webm">WebM</option>
                  <option value="mkv">MKV</option>
                  <option value="avi">AVI</option>
                  <option value="mov">MOV</option>
                </optgroup>
                <optgroup label="Audio">
                  <option value="mp3">MP3</option>
                  <option value="aac">AAC</option>
                  <option value="m4a">M4A</option>
                  <option value="wav">WAV</option>
                  <option value="flac">FLAC</option>
                  <option value="ogg">OGG</option>
                </optgroup>
              </select></div>
            </div>
            <div class="flex items-center"><input type="checkbox" name="perform_conversion" id="perform_conversion" checked class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"><label for="perform_conversion" class="ml-3 block text-sm font-medium">Convertir la vidéo après le téléchargement</label></div>
            <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 text-white font-semibold py-4 rounded-xl transition transform hover:scale-105 shadow-lg"><i class="fa-solid fa-rocket mr-2"></i>Lancer</button>
          </form>
        </div>
        <div class="space-y-6"><div class="glass-effect p-6 rounded-2xl"><h3 class="font-semibold mb-4">Statistiques</h3><div class="space-y-3 text-sm"><div class="flex justify-between"><span>Originaux</span><span class="font-semibold text-blue-500">{{ original_files|length }}</span></div><div class="flex justify-between"><span>Convertis</span><span class="font-semibold text-green-500">{{ converted_files|length }}</span></div><div class="flex justify-between"><span>Historique</span><span class="font-semibold text-purple-500">{{ history|length }}</span></div></div></div></div>
      </div>

      <div class="mt-12"><h2 class="text-2xl font-bold mb-4"><i class="fa-solid fa-download text-blue-500 mr-3"></i>Fichiers Originaux</h2>{% if original_files %}<ul class="grid gap-4">{% for file in original_files %}<li class="glass-effect p-4 rounded-xl flex items-center justify-between"><div class="flex items-center space-x-4 min-w-0"><i class="fa-solid fa-file-archive text-blue-400 text-xl"></i><div class="min-w-0"><p class="font-medium truncate">{{ file.name }}</p><span class="text-sm text-gray-500 dark:text-gray-400">{{ file.size }}</span></div></div><div class="flex items-center space-x-2 flex-shrink-0">
        <button onclick="openPlayerModal('/uploads/{{ file.name }}')" class="btn-action text-blue-500" title="Prévisualiser"><i class="fa-solid fa-play-circle"></i></button>
        <button onclick="openConversionModal('{{ file.name }}')" class="btn-action text-purple-500" title="Convertir"><i class="fa-solid fa-magic"></i></button>
        <a href="/uploads/{{ file.name }}" download="{{ file.name }}" class="btn-action text-green-500" title="Télécharger"><i class="fa-solid fa-download"></i></a>
        <button onclick="copyToClipboard(window.location.origin + '/uploads/{{ file.name }}')" class="btn-action text-gray-500" title="Copier le lien"><i class="fa-solid fa-copy"></i></button>
        <button onclick="deleteFile('original', '{{ file.name }}')" class="btn-action text-red-500" title="Supprimer"><i class="fa-solid fa-trash"></i></button>
    </div></li>{% endfor %}</ul>{% else %}<p class="text-center text-gray-500 dark:text-gray-400 py-6">Aucun fichier original.</p>{% endif %}</div>
      <div class="mt-12"><h2 class="text-2xl font-bold mb-4"><i class="fa-solid fa-folder-open text-green-500 mr-3"></i>Fichiers Convertis</h2>{% if converted_files %}<ul class="grid gap-4">{% for file in converted_files %}<li class="glass-effect p-4 rounded-xl flex items-center justify-between"><div class="flex items-center space-x-4 min-w-0"><i class="fa-solid fa-file-video text-green-400 text-xl"></i><div class="min-w-0"><p class="font-medium truncate">{{ file.name }}</p><span class="text-sm text-gray-500 dark:text-gray-400">{{ file.size }} | Expire dans: {{ file.expires }}</span></div></div><div class="flex items-center space-x-2 flex-shrink-0">
        <button onclick="openPlayerModal('/files/{{ file.name }}')" class="btn-action text-blue-500" title="Prévisualiser"><i class="fa-solid fa-play-circle"></i></button>
        <a href="/files/{{ file.name }}" download="{{ file.name }}" class="btn-action text-green-500" title="Télécharger"><i class="fa-solid fa-download"></i></a>
        <button onclick="copyToClipboard(window.location.origin + '/files/{{ file.name }}')" class="btn-action text-gray-500" title="Copier le lien"><i class="fa-solid fa-copy"></i></button>
        <button onclick="deleteFile('converted', '{{ file.name }}')" class="btn-action text-red-500" title="Supprimer"><i class="fa-solid fa-trash"></i></button>
    </div></li>{% endfor %}</ul>{% else %}<p class="text-center text-gray-500 dark:text-gray-400 py-6">Aucun fichier converti.</p>{% endif %}</div>
      <footer class="mt-16 text-center text-sm text-gray-600 dark:text-gray-400"><p>Les fichiers sont supprimés après 24h.</p></footer>
  </div>
</body>
</html>
'''

def format_size(bytes_size):
    if bytes_size < 1024: return f"{bytes_size} B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024: return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} {unit}"

# --- MISE À JOUR MAJEURE DE LA FONCTION DE CONVERSION ---
def convert_video(filepath, resolutions, formats):
    name, _ = os.path.splitext(os.path.basename(filepath))

    # Détection des flux disponibles
    def probe_value(args):
        try:
            res = subprocess.run(args, capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except Exception:
            return ""

    def has_stream(kind):
        v = probe_value(["ffprobe", "-v", "error", "-select_streams", f"{kind}:0", "-show_entries", "stream=index", "-of", "csv=p=0", filepath])
        return v != ""

    def media_duration():
        try:
            s = probe_value(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath])
            return float(s)
        except Exception:
            return 0.0

    input_has_video = has_stream('v')
    input_has_audio = has_stream('a')
    total_duration = media_duration()

    # Mapping des codecs audio
    audio_codec_map = {
        'mp3': ('libmp3lame', []),
        'aac': ('aac', ["-b:a", "192k"]),
        'm4a': ('aac', ["-b:a", "192k"]),
        'wav': ('pcm_s16le', []),
        'flac': ('flac', []),
        'ogg': ('libvorbis', ["-q:a", "5"]),
    }

    # Préparer la liste de combinaisons: si format audio, ignorer résolutions
    format_tasks = []
    for fmt in formats:
        fmt_l = fmt.lower()
        if fmt_l in AUDIO_FORMATS:
            format_tasks.append((None, fmt_l))  # pas de résolution nécessaire
        else:
            # vidéo: itérer sur résolutions
            for res in resolutions:
                format_tasks.append((res, fmt_l))

    total_conversions = len(format_tasks)
    current_conversion = 0

    for res, fmt in format_tasks:
        current_conversion += 1
        is_audio_target = fmt in AUDIO_FORMATS
        is_video_target = fmt in VIDEO_FORMATS

        # Nom de sortie
        if is_audio_target:
            output_name = f"{name}.{fmt}"
        else:
            height = (res or "720p").replace("p", "")
            output_name = f"{name}_{res}.{fmt}"
        output_path = os.path.join(CONVERTED_DIR, output_name)

        # Construire la commande ffmpeg selon les cas
        cmd = ["ffmpeg", "-y"]

        if is_audio_target:
            # Video -> Audio (ou Audio -> autre audio)
            cmd += ["-i", filepath, "-vn"]
            acodec, extra = audio_codec_map.get(fmt, ('aac', ["-b:a", "192k"]))
            cmd += ["-c:a", acodec] + extra
            cmd += [output_path, "-progress", "pipe:1", "-nostats"]
        else:
            # Cible vidéo
            if input_has_video:
                # Vidéo -> Vidéo
                height = (res or "720p").replace("p", "")
                cmd += ["-i", filepath, "-vf", f"scale=-2:{height}", "-c:v", "libx264", "-preset", "fast", "-crf", "28"]
                if input_has_audio:
                    cmd += ["-c:a", "aac", "-b:a", "128k"]
                else:
                    cmd += ["-an"]
                cmd += [output_path, "-progress", "pipe:1", "-nostats"]
            else:
                # Audio -> Vidéo (générer un fond)
                height = (res or "720p").replace("p", "")
                width = {
                    '2160': '3840', '1440': '2560', '1080': '1920', '720': '1280', '480': '854', '360': '640'
                }.get(height, '1280')
                size = f"{width}x{height}"
                # flux couleur + audio, -shortest pour s'arrêter avec l'audio
                cmd += [
                    "-i", filepath,
                    "-f", "lavfi", "-i", f"color=size={size}:rate=30:color=black",
                    "-shortest",
                    "-map", "1:v:0", "-map", "0:a:0",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "28",
                    "-c:a", "aac", "-b:a", "192k",
                    output_path, "-progress", "pipe:1", "-nostats"
                ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        for line in process.stdout:
            if total_duration > 0 and "out_time_ms" in line:
                time_match = re.search(r"out_time_ms=(\d+)", line)
                if time_match:
                    elapsed_ms = int(time_match.group(1))
                    elapsed_sec = elapsed_ms / 1000000
                    percentage = (elapsed_sec / total_duration) * 100
                    msg = f"Conversion... {name} ({current_conversion}/{total_conversions}) - {percentage:.1f}%"
                    progress_status.update({"message": msg, "percentage": percentage})
            else:
                msg = f"Conversion... {name} ({current_conversion}/{total_conversions})"
                progress_status.update({"message": msg})

        process.wait()

def cleanup_old_files():
    now = time.time()
    for folder in [UPLOAD_DIR, CONVERTED_DIR]:
        for fname in os.listdir(folder):
            if fname in EXCLUDED_FILES or os.path.isdir(os.path.join(folder, fname)):
                continue
            fpath = os.path.join(folder, fname)
            if now - os.path.getmtime(fpath) > 86400:
                os.remove(fpath)

@app.route('/')
def index():
    cleanup_old_files()
    now = time.time()
    original_files = [
        {'name': f, 'size': format_size(os.path.getsize(os.path.join(UPLOAD_DIR, f)))}
        for f in os.listdir(UPLOAD_DIR)
        if f not in EXCLUDED_FILES and os.path.isfile(os.path.join(UPLOAD_DIR, f)) and allowed_file(f)
    ]
    converted_files = []
    for f in os.listdir(CONVERTED_DIR):
        fpath = os.path.join(CONVERTED_DIR, f)
        stats = os.stat(fpath)
        remaining = 86400 - (now - stats.st_mtime)
        converted_files.append({'name': f, 'size': format_size(stats.st_size), 'expires': str(timedelta(seconds=int(max(0, remaining))))})
    return render_template_string(HTML_TEMPLATE, original_files=original_files, converted_files=converted_files, history=load_history())

def start_processing_thread(target_func, **kwargs):
    """Démarre un thread pour une tâche longue (téléchargement ou conversion)."""
    try:
        target_func(**kwargs)
        progress_status['message'] = "✅ Tâche terminée !"
    except Exception as e:
        progress_status['message'] = f"❌ Erreur: {e}"
    finally:
        progress_status['done'] = True

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    resolutions = request.form.getlist('resolutions')
    formats = request.form.getlist('formats')
    should_convert = 'perform_conversion' in request.form
    
    save_history(url)
    progress_status.update({'message': "Initialisation...", 'done': False, 'percentage': 0})

    def download_task(url, resolutions, formats, should_convert):
        # ... la logique de téléchargement reste la même ...
        downloaded_filepath = None
        if url.startswith("magnet:") or ".torrent" in url:
            progress_status['message'] = "Téléchargement du torrent..."
            subprocess.run(["aria2c", "--seed-time=0", url, "-d", UPLOAD_DIR], check=True)
            list_of_files = [os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR) if f not in EXCLUDED_FILES and os.path.isfile(os.path.join(UPLOAD_DIR, f))]
            if not list_of_files: raise Exception("Aria2c n'a téléchargé aucun fichier.")
            downloaded_filepath = max(list_of_files, key=os.path.getctime)
        else:
            ext = os.path.splitext(urlparse(url).path)[1] or '.mp4'
            filename = f"video_{int(time.time())}{ext}"
            downloaded_filepath = os.path.join(UPLOAD_DIR, filename)
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                with open(downloaded_filepath, 'wb') as f:
                    downloaded_size = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        if total > 0:
                            downloaded_size += len(chunk)
                            percentage = int(downloaded_size*100/total)
                            progress_status.update({'message': f"Téléchargement... {percentage}%", 'percentage': percentage})
        
        if should_convert:
            if not downloaded_filepath: raise Exception("Aucun fichier à convertir.")
            if not resolutions or not formats: raise Exception("Sélectionnez au moins une résolution et un format.")
            convert_video(downloaded_filepath, resolutions, formats)

    args = {'url': url, 'resolutions': resolutions, 'formats': formats, 'should_convert': should_convert}
    threading.Thread(target=start_processing_thread, kwargs={'target_func': download_task, **args}).start()
    return redirect(url_for('index'))

# --- ROUTE D'UPLOAD LOCAL ---
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(save_path)
    return redirect(url_for('index'))

# --- NOUVELLE ROUTE POUR LA RE-CONVERSION ---
@app.route('/convert/<path:filename>', methods=['POST'])
def convert_existing(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        # permettre la reconversion depuis le dossier converted également
        alt = os.path.join(CONVERTED_DIR, filename)
        filepath = alt if os.path.exists(alt) else filepath
    if not os.path.exists(filepath):
        return "Fichier non trouvé", 404

    resolutions = request.form.getlist('resolutions')
    formats = request.form.getlist('formats')

    progress_status.update({'message': "Initialisation de la conversion...", 'done': False, 'percentage': 0})
    
    def conversion_task(filepath, resolutions, formats):
        if not resolutions or not formats: raise Exception("Sélectionnez au moins une résolution et un format.")
        convert_video(filepath, resolutions, formats)
    
    args = {'filepath': filepath, 'resolutions': resolutions, 'formats': formats}
    threading.Thread(target=start_processing_thread, kwargs={'target_func': conversion_task, **args}).start()

    return redirect(url_for('index'))

@app.route('/progress')
def progress():
    # Éviter la boucle de rechargement: effacer l'état une fois terminé
    data = dict(progress_status)
    if progress_status.get('done'):
        progress_status.clear()
    return jsonify(data)

@app.route('/files/<path:filename>')
def serve_converted_file(filename):
    return send_from_directory(CONVERTED_DIR, filename, as_attachment=True)

@app.route('/uploads/<path:filename>')
def serve_original_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

@app.route('/delete/<file_type>/<filename>', methods=['POST'])
def delete_file_route(file_type, filename):
    base_dir = UPLOAD_DIR if file_type == 'original' else CONVERTED_DIR
    path = os.path.join(base_dir, filename)
    if os.path.isfile(path): os.remove(path)
    return '', 204

if __name__ == '__main__':
    print("🌍 Serveur démarré sur http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000)

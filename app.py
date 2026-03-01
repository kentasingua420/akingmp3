from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    file_id = str(uuid.uuid4())

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{file_id}.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': r'C:\Users\kenta\Downloads\ffmpeg-2026-02-26-git-6695528af6-essentials_build\ffmpeg-2026-02-26-git-6695528af6-essentials_build\bin',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')

        return jsonify({'file_id': file_id, 'title': title})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_id>/<path:title>')
def download(file_id, title):
    file_path = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.mp3')
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True, download_name=f'{title}.mp3')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"✅ Server running! Open http://localhost:{port} in your browser")
    app.run(host='0.0.0.0', port=port, debug=False)

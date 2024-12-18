import os
import yt_dlp
from flask import Flask, render_template, request, jsonify
from pathlib import Path

app = Flask(__name__)

# Function to download audio
def download_audio(url, download_path, audio_bitrate):
    ydl_opts = {
        'format': f'bestaudio[ext=m4a]/best[abr={audio_bitrate}]',  # Filter audio by selected bitrate
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',  # Save the file in the selected folder
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download the audio
            ydl.download([url])
            return "Download complete!"
    except Exception as e:
        return f"Error downloading audio: {e}"

# Function to get available bitrates
def get_available_bitrates(url):
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            bitrates = set()

            for f in formats:
                if f.get('acodec') != 'none' and 'abr' in f:
                    if f['abr'] is not None:
                        bitrates.add(f['abr'])

            return sorted(bitrates, reverse=True)
    except Exception as e:
        return []

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to fetch available bitrates
@app.route('/get_bitrates', methods=['POST'])
def get_bitrates():
    url = request.form.get('url')
    available_bitrates = get_available_bitrates(url)
    
    if not available_bitrates:
        return jsonify({'error': 'No audio bitrates available for this video.'})
    
    return jsonify({'bitrates': available_bitrates})

# Endpoint to download audio
@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    bitrate = request.form.get('bitrate')  # bitrate can be a float like '129.9'
    download_path = str(Path.home() / 'Downloads')  # Save to the default Downloads folder
    
    # Ensure the bitrate is handled correctly
    try:
        bitrate = float(bitrate)  # Convert the bitrate to a float
    except ValueError:
        return jsonify({'error': 'Invalid bitrate selected.'})
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)  # Create directory if it doesn't exist

    message = download_audio(url, download_path, bitrate)
    
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True)











































from flask import Flask, render_template, request, send_file, jsonify
from yt_dlp import YoutubeDL, DownloadError
import os, pathlib, fnmatch, shutil, re
from pathvalidate import sanitize_filename


app = Flask(__name__)

def is_valid_twitter_url(url):
    """
    Function to validate if the provided URL is a valid Twitter video URL.
    """
    # Regular expression pattern for matching Twitter video URLs
    pattern = r'https?://(?:www\.)?twitter\.com/.+/status/\d+'
    return re.match(pattern, url) is not None

#def sanitize_filename(filename):
    """
    Function to sanitize the filename by replacing invalid characters with underscores.
    """
    return re.sub(r'[<:>"/\\|?*]', '_', filename)

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['video_url']
    resolution = request.form['resolution']

    if not is_valid_twitter_url(video_url):
        return jsonify({'error': 'Invalid Twitter video URL'}), 400

    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        def move_dir(src: str, dst: str, pattern: str = '*'):
            if not os.path.isdir(dst):
                pathlib.Path(dst).mkdir(parents=True, exist_ok=True)
            for filename in fnmatch.filter(os.listdir(src), pattern):
                shutil.move(os.path.join(src, filename), os.path.join(dst, filename))           
 
    except DownloadError as e:
        return jsonify({'error': str(e)}), 400
    
    
    return send_file(filename, as_attachment=True)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)




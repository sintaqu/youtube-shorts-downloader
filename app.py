from flask import Flask, render_template, request, send_file
from pytube import Channel, YouTube
import os, io, zipfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    channel_name = ''
    if request.method == 'POST':
        username = request.form['username']
        max_videos = int(request.form['max_videos'])
        channel_url = f'https://www.youtube.com/@{username}/shorts'
        c = Channel(channel_url)
        channel_name = c.channel_name or username
        folder = os.path.join("/tmp", channel_name)
        os.makedirs(folder, exist_ok=True)
        videos = []

        for url in list(c.video_urls)[:max_videos]:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
            filename = yt.title.replace('/', '_')[:50] + ".mp4"
            filepath = os.path.join(folder, filename)
            if not os.path.exists(filepath):
                stream.download(output_path=folder, filename=filename)
            videos.append({
                'title': yt.title,
                'filepath': filepath
            })

    return render_template("index.html", videos=videos, channel=channel_name)

@app.route("/download_selected_zip", methods=["POST"])
def download_selected_zip():
    selected_files = request.form.getlist("selected_videos")
    channel = request.form.get("channel")
    mem_zip = io.BytesIO()

    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in selected_files:
            if os.path.exists(file_path):
                arcname = os.path.basename(file_path)
                zf.write(file_path, arcname=arcname)

    mem_zip.seek(0)
    return send_file(mem_zip, mimetype="application/zip", download_name=f"{channel}_shorts.zip", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=10000)
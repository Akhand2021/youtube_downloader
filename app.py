from flask import Flask, render_template, request, Response
from pytube import YouTube, exceptions
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    try:
        yt = YouTube(url)
        video_title = yt.title
        safe_video_title = secure_filename(video_title)
        stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()

        if stream is not None:
            # Set the Content-Disposition header to prompt the user for download
            headers = {
                "Content-Disposition": f"attachment; filename={safe_video_title}.mp4"
            }

            # Stream the video content to the client
            video_url = stream.url
            response = requests.get(video_url, stream=True)
            return Response(response.iter_content(chunk_size=4096), content_type='video/mp4', headers=headers)

        result_message = 'Video download failed. No available progressive stream found.'
        return render_template('error_message.html', result_message=result_message)

    except exceptions.VideoUnavailable:
        result_message = 'Video download failed. The video is unavailable or restricted.'
        return render_template('error_message.html', result_message=result_message)

    except exceptions.PytubeError as e:
        result_message = f'Video download failed. Error: {str(e)}'
        return render_template('error_message.html', result_message=result_message)

if __name__ == '__main__':
    app.run()

from flask import Flask, render_template, request
from media_sync import FlareonMediaManager
from werkzeug.utils import secure_filename
from pprint import pprint
app = Flask(__name__)

manager = FlareonMediaManager()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/media/add', methods=['POST'])
def media_add():
    if request.method == 'POST':
        media_file = request.files['file']

        filename = secure_filename(media_file.filename)
        fp = media_file.stream
        manager.add_media(filename, fp)

        return render_template("media.html", media=manager.media)


@app.route('/media/remove', methods=['POST'])
def media_remove():
    if request.method == 'POST':
        local_media_id = request.form['media_id']
        manager.remove_media(local_media_id)
        return render_template("media.html", media=manager.media)


if __name__ == "__main__":
    app.run(port=4000, debug=True)

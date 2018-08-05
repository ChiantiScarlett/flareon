from flask import Flask, render_template, request, jsonify
from core import Flareon as _Flareon
import sys
import json
app = Flask(__name__)


# Initialize Flareon
Flareon = _Flareon()

# Load local file list


@app.route('/load/localfiles', methods=['POST'])
def load_localfiles():
    if request.method == 'POST':
        return render_template('file-list.html', files=Flareon.load())


@app.route('/load/mdfile', methods=['POST'])
def load_mdfile():
    if request.method == 'POST':
        index = int(request.form['index'])

        return jsonify(Flareon.md_files[index])


@app.route('/')
def index():
    return render_template('index.html', explorer_path=Flareon.dirpath)


if __name__ == "__main__":
    app.run(port=4000, debug=True)

from flask import Flask, render_template, request, jsonify
from core import Flareon as _Flareon
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)


# Initialize Flareon
Flareon = _Flareon()


@app.route('/validate/date', methods=['POST'])
def validate_date():
    if request.method == 'POST':
        # Validate date
        try:
            print(request.form['date'])
            date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            return jsonify({'date': date.strftime("%Y-%m-%d"),
                            'weekday': date.strftime("(%A)")})
        except Exception:
            return jsonify({'date': '', 'weekday': ''})


@app.route('/load/localfiles', methods=['POST'])
def load_localfiles():
    if request.method == 'POST':
        return render_template('file-list.html',
                               files=Flareon.load_local_files())


@app.route('/load/mdfile', methods=['POST'])
def load_mdfile():
    if request.method == 'POST':
        index = int(request.form['index'])
        data = Flareon.load_md(index)
        templates = render_template('dbx-list.html',
                                    files=Flareon.md_file.dbx_files)

        return jsonify({'status': True,
                        'data': data,
                        'templates': templates,
                        'folder_volume': Flareon.md_file.dbx_files_stat,
                        'dbx_sync_id': Flareon.md_file.dbx_sync_id})


@app.route('/save/mdfile', methods=['POST'])
def save_mdfile():
    if request.method == 'POST':
        new_filename = "-".join([request.form['date'],
                                 request.form['title'].replace(' ', '-')]
                                ) + '.flareon.md'
        md_file = {
            'filename': new_filename,
            'dbx_sync_id': request.form['dbx_sync_id'],
            'date': request.form['date'],
            'title': request.form['title'],
            'category': request.form['category'],
            'tags': request.form['tags'],
            'contents': request.form['contents']
        }
        status, filename = Flareon.save_md(md_file)
        # Return True or False
        return jsonify({'status': status,
                        'filename': filename})


@app.route('/dropbox/add', methods=['POST'])
def dropbox_add():
    if request.method == 'POST':
        dbx_file = request.files['file']

        filename = secure_filename(dbx_file.filename)
        fp = dbx_file.stream

        status = Flareon.add_dbx_file(fp, filename)
        if status:
            templates = render_template('dbx-list.html',
                                        files=Flareon.md_file.dbx_files)
            return jsonify({'status': True, 'templates': templates,
                            'folder_volume': Flareon.md_file.dbx_files_stat,
                            'dbx_sync_id': Flareon.md_file.dbx_sync_id})
        else:
            return jsonify({'status': False})


@app.route('/dropbox/remove', methods=['POST'])
def dropbox_remove():
    if request.method == 'POST':
        filename = request.form['filename']
        status = Flareon.remove_dbx_file(filename)

        if status:
            templates = render_template('dbx-list.html',
                                        files=Flareon.md_file.dbx_files)
            return jsonify({'status': True, 'templates': templates,
                            'folder_volume': Flareon.md_file.dbx_files_stat,
                            'dbx_sync_id': Flareon.md_file.dbx_sync_id})
        else:
            return jsonify({'status': False})


@app.route('/dropbox/createlink', methods=['POST'])
def dropbox_create_file_link():
    if request.method == 'POST':
        filename = request.form['filename']
        print('[*] FN: ', filename)
        status, file_link = Flareon.create_file_link(filename)

        if status:
            return jsonify({'status': True, 'link': file_link})
        else:
            return jsonify({'status': False})


@app.route('/')
def index():
    return render_template('index.html',
                           explorer_path=Flareon._local_path,
                           default_date=datetime.now().strftime('%Y-%m-%d'),
                           default_date_wd=datetime.now().strftime('(%A)'),
                           tmp_dir=Flareon._dbx_tmp_dir)


if __name__ == "__main__":
    app.run(port=4000, debug=True)

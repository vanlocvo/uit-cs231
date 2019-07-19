from flask import Flask, render_template, send_from_directory, request, session,  url_for, redirect
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import os
import shutil
import stitcher
import uuid

app = Flask(__name__)
dropzone = Dropzone(app)

app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.png, .jpg, .jpeg'
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'
app.config['DROPZONE_UPLOAD_ON_CLICK'] = True
app.config['DROPZONE_PARALLEL_UPLOADS'] = 100

app.config['SECRET_KEY'] = 'UITCSGANG<3CS231'

app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads/'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/", methods=['GET', 'POST'])
def index():
    if "file_names" not in session or "uuid_folder" not in session:
        session['file_names'] = []
        session['uuid_folder'] = []
    file_names = session['file_names']

    if request.method == 'POST':
        uuid_folder = uuid.uuid4().hex
        os.mkdir('./static/uploads/'+uuid_folder)
        os.mkdir('./static/uploads/'+uuid_folder+'/result')
        session['uuid_folder'] = uuid_folder
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            filename = photos.save(
                file,
                folder=uuid_folder,
                name=file.filename
            )
            file_names.append(photos.url(filename))
        session['file_names'] = file_names
        return "uploading..."
    return render_template('index.html')


@app.route('/results')
def results():
    if 'uuid_folder' not in session or session['uuid_folder'] == []:
        return redirect(url_for('index'))
    if "file_names" not in session or session['file_names'] == []:
        return redirect(url_for('index'))

    file_names = session['file_names']
    session.pop('file_names', None)
    uuid_folder = session['uuid_folder']
    session.pop('uuid_folder', None)

    # Xu ly tren tap file file_namess
    work_dir = './static/uploads/'+uuid_folder+'/'
    input_file = [f for f in os.listdir(
        work_dir) if os.path.isfile(os.path.join(work_dir, f))]
    if len(input_file) >= 2:
        stitcher.stitching(input_file, uuid_folder)
    else:
        return render_template('index.html')
    result = work_dir + 'result/result.png'
    return render_template('results.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)

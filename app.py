
# A very simple Flask Hello World app for you to get started with...
# http://flask.palletsprojects.com/en/1.0.x/patterns/fileuploads/
import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, session
from secretpy import Caesar
from secretpy import alphabets

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

from werkzeug.utils import secure_filename
VERSION="1.4"

UPLOAD_FOLDER = '/opt/ist440/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

pytesseract.pytesseract.tesseract_cmd = r'/opt/tesseract-4.1.0/src/vs2010/tesseract'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VERSION'] = VERSION

@app.route('/')
def hello_world():
    return render_template('index.html', title='Cracking The Code', version=VERSION, login=False, imagetext="")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/', methods=['GET', 'POST'])
def upload_page():
    header = "<h1>Upload</h1>"
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print "Upload Folder: " + app.config['UPLOAD_FOLDER']
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagetext = ocr(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('index.html', title="Results", imagetext=imagetext, version=VERSION, login=False)
            # return redirect(url_for('uploaded_file', filename=filename))
    else:
        return render_template('upload.html', title='Upload', version=VERSION)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def ocr(imagefile):
    # Convert image to text
    print imagefile
    # store in database
    # return the database record
    return pytesseract.image_to_string(Image.open(imagefile))
    # return Text
    # return "test string"

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=3000)

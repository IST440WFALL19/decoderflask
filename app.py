from __future__ import print_function
# A very simple Flask Hello World app for you to get started with...
# http://flask.palletsprojects.com/en/1.0.x/patterns/fileuploads/
import os
from googletrans import Translator
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, session, escape
from secretpy import Caesar, Rot13, alphabets, CryptMachine
from secretpy.cmdecorators import SaveCase, SaveSpaces
import ConfigParser
from redis import Redis
import rq

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

# Parse Config
config = ConfigParser.RawConfigParser()
# If file exists
if os.path.exists('decoder.cfg'):
    # Logging config
    config.read('decoder.cfg')
    secretkey = config.get('server', 'sercretkey')
    grouppass = config.get('server', 'grouppass')
else:
    # Creating new configuration file
    config.add_section("server")
    config.set('server',"sercretkey")
    config.set('server',"grouppass")
    with open('decoder.cfg', 'wb') as configfile:
        config.write(configfile)
    print("Config File Created. Please edit decoder.cfg and run again.")
    exit(0)


class codedMessage:
    def __init__(self, imagefile):
        self.image = imagefile
        self.filepath, self.ext = os.path.splitext(imagefile)

    def set_type(self, extension):
        self.ext = extension


q = rq.Queue(connection=Redis.from_url('redis://:83uaf_1313n_3r3-wfbu3bsih3-23urbkjbfu3b@128.118.192.79:6379/0'))


from werkzeug.utils import secure_filename
VERSION="1.9"

UPLOAD_FOLDER = '/opt/ist440/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# grouppass = "IST440W"
# secretkey = "9g3fiuwgpqw8g8gp98GP*&O&D*I^UYGp[97gfo76fOIP&FO&^F]"
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VERSION'] = VERSION
app.secret_key = secretkey

@app.route('/')
def index():
    # If we have a user logged in
    if 'username' in session:
        # return home with welcome
        return render_template('index.html', username=str(escape(session['username'])), welcome="true",version=VERSION)
    # else return home with login page
    return render_template('index.html', title='Cracking The Code', version=VERSION, login=True, imagetext="")
    
    # return render_template('index.html')

# route and function for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the page is loading with a post
    if request.method == 'POST':
        # Check post form password to see if it matches
        if request.form['password'] == grouppass:
            # Create new session with form username
            session['username'] = request.form['username']
            # Log the user login
            print("Logging In: " + str(escape(session['username'])))
            # Return to index
            return redirect(url_for('index'))
        else:
            # Return home with failed login when password is incorrect
            return render_template('index.html', login="failed", title='Cracking The Code', version=VERSION, imagetext="")
    # Return home page when loaded with get
    return render_template('index.html', title='Cracking The Code', version=VERSION, login=False, imagetext="")

@app.route('/logout')
def logout():
    # Log the log out
    print("Logging Out: " + str(escape(session['username'])))
    # remove the username from the session if it's there
    session.pop('username', None)
    # Return home page
    return redirect(url_for('index'))
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/', methods=['GET', 'POST'])
def upload_page():
    # If we have a user logged in
    if 'username' in session:
        header = "<h1>Upload</h1>"
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print("Upload Folder: " + app.config['UPLOAD_FOLDER'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Translate image to text with OCR function
                imagetext = ocr(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Translate the image text to english
                transtext = translate(imagetext)
                # Get output of text (best guess)
                transorigin = transtext.text
                # Get original language of text
                transsrc = transtext.src
                # Get language translaged to (En)
                transdest = transtext.dest
                # Try a rot13 decipher
                rot13output = rot13_decipher(imagetext)
                # Run background task
                # deleted_action = q.enqueue(ocr,filepath)
                caesaroutput = caesar_decipher(imagetext)
                #returntext = "origin: {0}   </ br > src: {1}  </ br >  dest: {2}     ".format(transorigin, transsrc,transdest)
                return render_template('results.html', transsrc=transsrc, transdest=transdest, transwords=transorigin, title='Cracking The Code', imagetext=imagetext, version=VERSION, login=False,  username=str(escape(session['username'])))
            else:
                return render_template('upload.html', error="Image Format Not Supported.", title='Cracking The Code', version=VERSION, login=False,  username=str(escape(session['username'])))
                # return redirect(url_for('uploaded_file', filename=filename))
        else:
            return render_template('upload.html', title='Upload', version=VERSION,  username=str(escape(session['username'])))
    else:
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    '''This function shows the filename after an upload'''
    # If we have a user logged in
    if 'username' in session:
        # Return the image from the app directory
        return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
    else:
        # Return to index for non-logged in user
        return redirect(url_for('index'))
        
@app.route('/results/')
def results():
    '''This page will show the results of the image'''
    # If we have a user logged in
    if 'username' in session:
        # Return the results html
        return render_template("results.html", title='Results', version=VERSION)
    else:
        # Return to index for non-logged in user
        return redirect(url_for('index'))

def ocr(imagefile):
    '''Function to convert image to text'''
    # Split the filename and extension
    filename, file_extension = os.path.splitext(imagefile)
    
    # Create new codedMesssage object with image path
    codemessage = codedMessage(imagefile)
    # Set the codedMessage type based on file_extension
    codemessage.set_type(file_extension)
    # Attempt to OCR based on file extension
    if file_extension == ".pdf":
        # PDF requires different function
        return pytesseract.image_to_pdf_or_hocr(imagefile, extension='pdf')
    else:
        # Attempt to OCR image file
        return pytesseract.image_to_string(Image.open(imagefile))

def translate(text):
    '''Function to translate text to english'''
    # Create new translator
    translator = Translator()
    # Return the translated text in English
    return translator.translate(text, dest="en")

def caesar_decipher(caesartext):
    '''Function to attempt caesar decipher by cycling through each number'''
    # Create Empty Array
    results_array = []
    # Set text we received to lowercase
    lowercase_text = caesartext.lower()
    # For 1 through 27
    for key in range(1,27):
        # Create new CryptMachine with Caesar cipher and key
        cm = SaveSpaces(SaveCase(CryptMachine(Caesar(), key)))
        # Add each decipher attempt to the results_array
        results_array.append(cm.decrypt(lowercase_text))
    # return the array of decipher attempts
    for result in results_array:
        print("result: {0}".format(result))
        if translate(result).src.lower() == "en":
            print("English!")
    return results_array
    # This return could be replaced with a function to test each result and return 
    # the result with the most english words found and return that single result

def rot13_decipher(rot13text):
    # Create CryptMachine for Rot13 with saving case and space on
    cm = SaveSpaces(SaveCase(CryptMachine(Rot13())))
    print(rot13text)
    dec = cm.decrypt(rot13text)
    print(dec)
    return dec

if __name__ == "__main__":
    app.secret_key = secretkey
    app.run(host='0.0.0.0',port=3000)


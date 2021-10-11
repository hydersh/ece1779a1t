from flask import render_template, redirect, url_for, request, g, session
from app import webapp
from app.config import db_config
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import tempfile
import os

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db=getattr(g, '_database', None)
    if db is None:
        db =g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route('/test/FileUpload/form',methods=['GET'])
#Return file upload form
def upload_form():
    return render_template("fileupload/form.html")



@webapp.route('/',methods=['POST'])
@webapp.route('/api/login',methods=['POST'])
#Upload a new file and store in the systems temp directory
def login():
    userid = request.form.get('username')
    password = request.form.get('password')
    session['userID'] = userid
    cnx = get_db()
    cursor = cnx.cursor()

    query = 'SELECT * FROM user WHERE username = %s'
    cursor.execute(query, (userid,))
    user, passdb = cursor.fetchone()
    if user is None:
        print("Missing User")
        return render_template("login.html")
    elif user == "Test1":
        if password == passdb:
            return redirect("/register")
        else:
            return render_template("login.html")
    else:
        if check_password_hash(passdb, password):
            return redirect("/imghome")
        else:
            return render_template("login.html")

@webapp.route('/api/upload', methods=['POST'])
def file_upload():
    # check if the post request has the file part
    if 'uploadedfile' not in request.files:
        return "Missing uploaded file"

    new_file = request.files['uploadedfile']

    # if user does not select file, browser also
    # submit a empty part without filename
    if new_file.filename == '':
        return 'Missing file name'

    tempdir = tempfile.gettempdir()

    new_file.save(os.path.join(tempdir,new_file.filename))

    return "Success"

@webapp.route('/imghome')
def imghome():
	return render_template("imagetransform/imghome.html")


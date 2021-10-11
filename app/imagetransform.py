from flask import render_template, redirect, url_for, request, g, session, jsonify
from app import webapp
from app.config import db_config
import mysql.connector
import tempfile
import os

from wand.image import Image

webapp.secret_key = '\x8e\xfa\xbf\xff\x07A&\x84\xec\xc1\xad+c=\xd3:hC\x98*\xc4\xcc8\xcd'

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

@webapp.route('/api/imagetransform/form',methods=['GET'])
#Return file upload form
def image_form():
    return render_template("imagetransform/form.html")


@webapp.route('/imagetransform',methods=['POST'])
#Upload a new image and tranform it
def image_transform():

    # check if the post request has the file part
    if 'image_file' not in request.files:
        return "Missing uploaded file"

    new_file = request.files['image_file']

    cnx = get_db()
    cursor = cnx.cursor()
    userID = str(session['userID'])


    # if user does not select file, browser also
    # submit a empty part without filename
    if new_file.filename == '':
        return 'Missing file name'

    tempdir = tempfile.gettempdir()

    fname = os.path.join('app/static',new_file.filename)


    new_file.save(fname)

    fname_blur, fname_shade, fname_spread, response = transform(userID, fname, new_file.filename)

    query = 'SELECT * FROM image WHERE username = %s'
    cursor.execute(query, (userID, ))
    countuser = cursor.fetchone()
    if countuser == None:
        query = 'INSERT INTO image VALUES(%s, %s, %s,' \
            '%s, %s);'
        cursor.execute(query, (userID, fname, fname_blur, fname_shade, fname_spread))
        cnx.commit();
        cnx.close();
    else:
        query1 = 'UPDATE image SET original = %s, blur =%s, shade =%s, spread =%s ' \
            'WHERE username = %s;'
        cursor.execute(query1, ( fname, fname_blur, fname_shade, fname_spread, userID))
        cnx.commit();
        cnx.close();
    return render_template("imagetransform/imghome.html", data=jsonify(response))

@webapp.route('/view')
    # Upload a new image and tranform it
def image_view():

    cnx = get_db()
    cursor = cnx.cursor()

    userID = str(session['userID'])

    query = 'Select * FROM image  WHERE username = %s'
    cursor.execute(query, (userID,))
    username, f1, f2, f3, f4 = cursor.fetchone()
    return render_template("imagetransform/view.html",
                           f1=f1[4:],
                           f2=f2[4:], f3=f3[4:], f4=f4[4:])

def transform(userID, fname, filename):
    img = Image(filename=fname)
    iblur = img.clone()
    ishade = img.clone()
    ispread = img.clone()

    iblur.blur(radius=0, sigma=8)
    ishade.shade(gray=True, azimuth=286.0, elevation=45.0)
    ispread.spread(radius=8.0)

    fname_blur = os.path.join('app/static', userID + 'blur_' + filename)
    fname_shade = os.path.join('app/static', userID + 'shade_' + filename)
    fname_spread = os.path.join('app/static', userID + 'spread_' + filename)

    iblur.save(filename=fname_blur)
    ishade.save(filename=fname_shade)
    ispread.save(filename=fname_spread)
    response = {
        'success' : 'true',
        'payload' : {
            'original_size' : os.path.getsize(fname),
            'blur_size' : os.path.getsize(fname_blur),
            'shade_size' : os.path.getsize(fname_shade),
            'spread_size' : os.path.getsize(fname_spread),
        }
    }
    return fname_blur, fname_shade, fname_spread, response


#def transform_response(fname.size):





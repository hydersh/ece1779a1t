from flask import render_template, redirect, url_for, request, g, session
from app import webapp
from app.config import db_config
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
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

@webapp.route('/register')
def register():
    return render_template("register.html")



@webapp.route('/api/register',methods=['POST'])
def register_user():
    if session['userID'] != 'Test1':
        redirect("/api/login")

    cnx = get_db()
    cursor = cnx.cursor()

    #form = Form()
    userid = request.form.get('username')
    password = request.form.get('password')

    query = 'SELECT * FROM user WHERE username = %s'
    cursor.execute(query, (userid, ))

    record= cursor.fetchone()

    if record == None:
        query1 = 'INSERT INTO user VALUES(%s, %s);'
        hashPw = generate_password_hash(password)
        cursor.execute(query1, (userid, hashPw))
        cnx.commit()
        cnx.close()
        return redirect("/api/login")
    else:
        cnx.close()
        return redirect("/register")


from flask import render_template, redirect, url_for, request, g
from app import webapp
import mysql.connector
import tempfile
import os

db_config={'user': 'ece1779',
           'password':'secret12',
           'host':'127.0.0.1',
           'database':'A1'}

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
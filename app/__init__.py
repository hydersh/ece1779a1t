
from flask import Flask

webapp = Flask(__name__)

from app import fileupload
from app import imagetransform
from app import register
from app import main



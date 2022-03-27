import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
	SECRET_KEY =  os.environ.get('SECRET_KEY') or 'dncienf'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MIDI_FILES_PATH = os.path.join(basedir, 'app', 'midifiles')
	MAX_CONTENT_LENGTH = 1024*1024*10 # 10 MB
	UPLOAD_EXTENSIONS = ['.mid']

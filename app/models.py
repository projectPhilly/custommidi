from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	isadmin = db.Column(db.Boolean())

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
	return User.query.get(int(id))


class Session(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)


class Midi(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
	name = db.Column(db.String(64))
	status = db.Column(db.Integer)
	details = db.Column(db.PickleType)

	def __repr__(self):
		return '<Midi {}>'.format(self.name)
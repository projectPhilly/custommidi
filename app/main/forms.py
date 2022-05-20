from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, \
					HiddenField, MultipleFileField, SelectField, \
					IntegerField, FieldList, FormField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User, Session
from app.scripts.midi_check import INSTRUMENT_NAMES


class EditTrackForm(FlaskForm):
	instrument = SelectField('Instrument', choices=[(key, f'{INSTRUMENT_NAMES[key]}') for key in INSTRUMENT_NAMES], coerce=int)
	volume = IntegerField('Volume')


class EditTracksForm(FlaskForm):
	globalinstrument = SelectField('Instrument', choices=[(key, f'{INSTRUMENT_NAMES[key]}') for key in INSTRUMENT_NAMES], coerce=int)
	globalvolume = IntegerField('Volume')
	globaltempo = IntegerField('Tempo')
	tracks = FieldList(FormField(EditTrackForm), min_entries=1)


class FileUploadForm(FlaskForm):
	file = MultipleFileField('File')
	submit = SubmitField('Upload')

	def __init__(self, folder, *args, **kwargs):
		super(FileUploadForm, self).__init__(*args, **kwargs)
		self.submit.name = folder


class AddSessionForm(FlaskForm):
	submit = SubmitField('+ Add Session')
	name = StringField('Name', validators=[DataRequired()])


class TrackNameField(FlaskForm):
	trackName = StringField('Track Name')

class NameTracksForm(FlaskForm):
	submit = SubmitField('Update')
	midiName = StringField('Name', validators=[DataRequired()])
	trackNames = FieldList(FormField(TrackNameField), min_entries=1, validators=[DataRequired()])

class EmptyForm(FlaskForm):
	submit = SubmitField('Submit')
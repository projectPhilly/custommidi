from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
	jsonify, current_app, abort, send_file, Response
from flask_login import current_user, login_required
from app import db
from app.main.forms import EmptyForm, FileUploadForm, AddSessionForm, EditTracksForm
from app.models import User, Session, Midi
from app.main import bp
import os
from werkzeug.utils import secure_filename
from app.scripts.midi_check import get_midi_data
from app.scripts.midi_edit import edit_midi_file
import shutil
from io import BytesIO
from werkzeug.wsgi import FileWrapper


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():

	if request.method == 'POST':
		keys = list(request.form.keys())
		if 'apply-to-all' in keys: # apply global values to all tracks
			midi_id = request.args.get('midi')
			global_instrument = int(request.form['globalinstrument'])
			try:
				global_volume = int(request.form['globalvolume'])
			except ValueError:
				global_volume = 100
			if global_volume > 100:
				global_volume = 100
			elif global_volume < 0:
				global_volume = 0
			try:
				global_tempo = int(request.form['globaltempo'])
			except ValueError:
				global_tempo = 100
			if global_tempo <= 0:
				global_tempo = 1
			elif global_tempo > 1000:
				global_tempo = 1000
			return redirect(url_for('main.index', midi=midi_id, instr=global_instrument, vol=global_volume, tempo=global_tempo))
		elif 'create' in keys:
			midi_id = request.args.get('midi')
			if midi_id:
				midi = Midi.query.get(midi_id)
				session = midi.session_id
				original_midi_filepath = os.path.join(current_app.config['MIDI_FILES_PATH'], str(session), f'{str(midi.id)}.mid')
				track = 0
				tracks = []
				while True:
					base_key = f'tracks-{track}-'
					try:
						instr = int(request.form[f'{base_key}instrument'])
					except KeyError:
						break
					try:
						vol = int(request.form[f'{base_key}volume'])
					except ValueError:
						vol = 0
					tracks.append((track, instr, vol))
					track += 1
				try:
					tempo = int(request.form['globaltempo'])
				except:
					tempo = 100
				data = edit_midi_file(original_midi_filepath, tracks, tempo)
				headers = {
					'Content-Disposition': f'attachment; filename="{midi.name}"'
				}
				return Response(FileWrapper(BytesIO(data)),
								direct_passthrough=True, mimetype='audio/sp-midi',
								headers=headers)
				#return send_file(BytesIO(data), as_attachment=True, attachment_filename='test.mid')

	# Collect sessions to display in left sidebar
	sessions = {}
	for s in Session.query.order_by(Session.id.desc()).all():
		sessions[s.name] = Midi.query.filter_by(session_id=s.id).all()

	# Determine which MIDI is being edited
	midi = None
	session_name = None
	form = None
	midi_id = request.args.get('midi')
	if midi_id:
		midi = Midi.query.get(midi_id)
		session_name = Session.query.get(midi.session_id).name
		try:
			global_instrument = int(request.args.get('instr'))
		except:
			global_instrument = None
		try:
			global_volume = int(request.args.get('vol'))
		except:
			global_volume = None
		try:
			global_tempo = int(request.args.get('tempo'))
		except:
			global_tempo = None

		# Create forms
		form = EditTracksForm(tracks=[(i, midi.details['trackInfo'][i][0]) for i in range(len(midi.details['trackInfo']))])
		for (i, track) in enumerate(form.tracks):
			# set current instruments
			if global_instrument is not None:
				track.instrument.data = global_instrument
			else:
				try:
					track.instrument.data = int(midi.details['trackInfo'][i][1][0].split(' ')[0]) + 1
				except ValueError: # For unknown instrument values
					pass
			# set current volumes
			if global_volume is not None:
				track.volume.data = global_volume
			else:
				try:
					track.volume.data = int(round(float(midi.details['trackInfo'][i][2][0])))
				except: # For unknown volume data
					pass

		if global_instrument is not None:
			form.globalinstrument.data = global_instrument
		else:
			form.globalinstrument.data = 1
		if global_volume is not None:
			form.globalvolume.data = global_volume
		else:
			form.globalvolume.data = 100
		if global_tempo is not None:
			form.globaltempo.data = global_tempo
		else:
			form.globaltempo.data = 100

	return render_template('index.html', title='Home',
						   sessions=sessions, midi=midi, session_name=session_name,
						   edit_tracks_form=form)


@bp.route('/manage/delete_session/<string:session>', methods=['POST'])
@login_required
def delete_session(session):
	if not current_user.isadmin:
		return redirect(url_for('main.index'))

	s = Session.query.filter_by(name=session).first()
	if s is None:
		flash('Unable to delete: Session not found.')
		return redirect(url_for('main.manage'))
	db.session.delete(s)
	
	for m in Midi.query.filter_by(session_id=s.id).all():
		db.session.delete(m)

	db.session.commit()

	shutil.rmtree(os.path.join(current_app.config['MIDI_FILES_PATH'], str(s.id)))
	flash(f'Session "{s.name}" successfully deleted.')

	return redirect(url_for('main.manage'))


@bp.route('/manage/delete_midi/<string:session>/<string:name>', methods=['POST'])
@login_required
def delete_midi(session, name):
	if not current_user.isadmin:
		return redirect(url_for('main.index'))

	s = Session.query.filter_by(name=session).first()
	if s is None:
		flash('Unable to delete: Session not found.')
		return redirect(url_for('main.manage'))
	m = Midi.query.filter_by(name=name).first()
	if m is None:
		flash('Unable to delete: File not found.')
		return redirect(url_for('main.manage'))
	db.session.delete(m)
	db.session.commit()
	try:
		os.remove(os.path.join(current_app.config['MIDI_FILES_PATH'], str(s.id), str(m.id)))
	except FileNotFoundError:
		flash('Unable to delete: The file was already deleted.')
	else:
		flash(f'File "{m.name}" from session "{s.name}" successfully deleted.')
	return redirect(url_for('main.manage'))


@bp.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
	if not current_user.isadmin:
		return redirect(url_for('main.index'))

	if request.method == 'POST':

		# Upload files:
		try:
			# complicated way to get "name" attribute of form item with "Upload" key
			session_name = list(request.form.keys())[list(request.form.values()).index('Upload')]
		except ValueError: # "Upload" key not found
			pass
		else:
			for uploaded_file in request.files.getlist('file'):
				if uploaded_file.filename != '':
					file_ext = os.path.splitext(uploaded_file.filename)[1]
					if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
						abort(400)
					midi_details = get_midi_data(uploaded_file.read())
					if midi_details['nErrors'] == 0:
						status = 1
					else:
						status = 0
					s = Session.query.filter_by(name=session_name).first()
					m = Midi(session_id=s.id, name=uploaded_file.filename,
							 status=status, details=midi_details)
					db.session.add(m)
					db.session.commit()
					m = Midi.query.filter_by(name=uploaded_file.filename).first()
					uploaded_file.seek(0) # important! otherwise file is blank (unsure why, pointer issue I guess)
					uploaded_file.save(os.path.join(current_app.config['MIDI_FILES_PATH'], str(s.id), f'{str(m.id)}.mid'))
			return redirect(url_for('main.manage'))

	# Add session:
	add_session_form = AddSessionForm()
	if add_session_form.validate_on_submit():
		s = Session.query.filter_by(name=add_session_form.name.data).first()
		if s is not None:
			flash(f'Session "{add_session_form.name.data}" already exists. Please use a different name.')
			return redirect(url_for('main.manage'))
		s = Session(name=add_session_form.name.data)
		db.session.add(s)
		db.session.commit()
		s = Session.query.filter_by(name=add_session_form.name.data).first()
		os.mkdir(os.path.join(current_app.config['MIDI_FILES_PATH'], str(s.id)))
		return redirect(url_for('main.manage'))

	files = {}
	forms = {}
	
	for s in Session.query.order_by(Session.id.desc()).all():
		files[s.name] = []
		forms[s.name] = FileUploadForm(s.name)
		for m in Midi.query.filter_by(session_id=s.id).all():
			files[s.name].append({
					'session': s.name,
					'name': m.name,
					'status': m.status,
					'details': m.details
				})
	
	return render_template('manage.html', title='Manage', files=files, 
					upload_forms=forms, add_session_form=add_session_form)
import os
import re
import fnmatch


INSTRUMENT_NAMES = {
	1: 'Acoustic Grand Piano',
	2: 'Bright Acoustic Piano',
	3: 'Electric Grand Piano',
	4: 'Honky-tonk Piano',
	53: 'Choir Aahs',
	90: 'Pad 2 (warm)'
}

def edit_midi_file(filename, tracks, tempo):
	# tracks format:
	# 	[(int trackNum, int instrument, int volume), ..., (int trackNum, int instrument, int volume)]
	
	with open(filename, 'rb') as file:
		data = bytearray(file.read())

	for track in tracks:
		trackNum = track[0]
		trackInstr = track[1] # key/index from INSTRUMENT_NAMES
		trackVol = track[2] # in percent

		data = change_instrument(data, trackNum, trackInstr)
		data = change_volume(data, trackNum, trackVol/100)

	data = change_tempo(data, tempo/100) # tempo passed in %

	return data

def change_tempo(data, factor):
	tracks = data.split(b'MTrk')
	#tracks.pop(0) # first element will be header chunk

	ind = tracks[1].find(b'\xFF\x51\x03')
	uspqn = int.from_bytes(tracks[1][ind+3:ind+6], 'big') # us per quarter note
	qnpm = 1000000/uspqn*60 # quarter notes per minute, aka bpm

	#print(f'BPM = {qnpm:.1f}\n')

	uspqnNew = int(uspqn/factor)
	tracks[1][ind+3:ind+6] = int(uspqnNew).to_bytes(3, 'big')

	return bytearray(b'MTrk'.join(tracks))

def change_instrument(data, trackNum, instrument):
	tracks = [bytearray(track) for track in data.split(b'MTrk')]
	header = tracks.pop(0)
	
	for j in range(16):
		ind = tracks[trackNum].find(int(0xc0+j).to_bytes(1, 'big'))
		if ind > -1:
			tracks[trackNum][ind+1] = int(instrument)

	return bytearray(b'MTrk'.join([header]+tracks))

def change_volume(data, channel, factor):
	if (factor > 1) or (factor < 0):
		print('Invalid volume scale factor (must be between 0 and 1).')
		return data
	if (channel > 15) or (channel < 0):
		print('Invalid channel number (must be between 0 and 15).')
	
	tracks = data.split(b'MTrk')
	header = tracks.pop(0)
	
	var = int(0xb0 + channel).to_bytes(1, 'big')
	data = re.sub(var + b'\x07.', var + b'\x07' + int(0x7f*factor).to_bytes(1, 'big'), data)

	return bytearray(data)
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

def get_midi_data(data):
	midiData = {
		'nErrors': 0,
		'headerFound': True,
		'headerChunkLen': -1,
		'formatType': -1,
		'nTracks': -1,
		'timing': '',
		'trackInfo': [],
		'errorList': []
	}

	data = bytearray(data)

	if data[0:4] != b'MThd':
		midiData['nErrors'] += 1
		midiData['headerFound'] = False
		midiData['errorList'].append('Could not find Header Chunk Identifier.')
	
	chunklen = int.from_bytes(data[4:8], 'big')
	midiData['headerChunkLen'] = chunklen
	if chunklen != 6:
		midiData['nErrors'] += 1
		midiData['errorList'].append(f'Header Chunk length is not 6. Got {chunklen} instead.')
	
	formatType = int.from_bytes(data[8:10], 'big')
	midiData['formatType'] = formatType
	if formatType not in [0, 1, 2]:
		midiData['nErrors'] += 1
		midiData['errorList'].append(f'Invalid format type. Expected 0, 1, or 2. Got {formatType} instead.')

	nTracks = int.from_bytes(data[10:12], 'big')
	midiData['nTracks'] = nTracks
	if (formatType == 0) and (nTracks != 1):
		midiData['nErrors'] += 1
		midiData['errorList'].append(f'For format type "0", ntracks can only be 1. Got {nTracks} instead.')

	tickdiv = int.from_bytes(data[12:14], 'big')
	timing = tickdiv & 0x8000
	if timing == 0:
		ppqn = tickdiv & 0x7FFF
		timingString = f'metrical, ppqn = {ppqn}'
	elif timing == 1:
		fps = (tickdiv & 0xFF00) >> 8
		subFrameRes = tickdiv & 0xFF
		timingString = 'timecode, fps = {fps}, sub-frame resolution = {subFrameRes}'
	else:
		timingString = ''
		midiData['nErrors'] += 1
		midiData['errorList'].append('Could not parse timing data.')
	midiData['timing'] = timingString

	tracks = data.split(b'MTrk')
	tracks.pop(0)
	for (i, track) in enumerate(tracks):
		trackName = get_track_name(track)
		instrument, instrumentCh = get_track_instrument(track)
		volume, volumeCh = get_track_volume(track)
		midiData['trackInfo'].append([trackName, (instrument, instrumentCh), (volume, volumeCh)])

	return(midiData)

def get_track_name(track):
	ind = track.find(b'\xff\x03')
	trackName = 'N/A'
	if ind:
		nameLen = track[ind+2]
		trackName = track[ind+3:ind+3+nameLen].decode('utf-8')

	return trackName

def get_track_instrument(track):
	instrument = 'Unknown'
	channel = 'N/A'
	for j in range(16):
		ind = track.find(int(0xc0+j).to_bytes(1, 'big'))
		if ind > -1:
			instrInd = track[ind+1]
			instrument = f'{instrInd} ({INSTRUMENT_NAMES[instrInd+1]})'
			channel = track[ind] & 0x0f
			break

	return instrument, channel

def get_track_volume(track):
	volume = 'Unknown'
	channel = 'N/A'
	for j in range(16):
		ind = track.find(int(0xb0+j).to_bytes(1, 'big') + b'\x07')
		if ind > -1:
			volume = track[ind+2]/0x7f*100
			channel = track[ind] & 0x0f
			break

	return volume, channel
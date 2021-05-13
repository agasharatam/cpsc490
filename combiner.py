#!/usr/local/bin/python3

# Agasha Ratam
# Version May 7, 2021

import csv
import datetime
import utils
import json

def get_songs():
	f = open('data/songs.json', 'r')
	features = json.loads(f.read())
	f.close()

def get_week_conversion():
	"""
	Returns a dictionary d.
	Example:
		d['08/02/1958'] = 1
		d['08/09/1958'] = 2
	"""
	weekIds = dict()

	f = open('data/billboard-list.csv', 'r')
	obj = csv.reader(f)

	variables = next(obj)
	for row in obj:
		weekId = row[variables.index('WeekID')]

		if weekId not in weekIds:
			weekIds[weekId] = 1
	f.close()

	weekList = sorted([key for key in weekIds], key = lambda x: datetime.datetime.strptime(x, '%m/%d/%Y'))

	weekConv = dict()
	for i in range(len(weekList)):
		weekConv[weekList[i]] = i + 1

	return weekConv

def get_unique_songs():
	f = open('data/unique-tracks.json', 'r')
	unique_songs = json.loads(f.read())
	f.close()

	return unique_songs

def get_unique_performers():
	f = open('data/unique-performers.json', 'r')
	unique_performers = json.loads(f.read())
	f.close()

	return unique_performers
		
def combine():
	features = get_features()
	weekConv = get_week_conversion()
	unique_songs = get_unique_songs()
	unique_performers = get_unique_performers()

	hot_songs = []

	f = open('data/hot-100.csv', 'r')
	obj = csv.reader(f)

	variables = next(obj)
	for row in obj:
		weekId = row[variables.index('WeekID')]
		weekPosition = row[variables.index('Week Position')]
		songId = row[variables.index('SongID')]
		performer = row[variables.index('Performer')]
		song = row[variables.index('Song')]

		item = dict()

		item['WeekNumber'] = weekConv[weekId]
		item['WeekID'] = weekId
		item['WeekPosition'] = weekPosition
		item['SongID'] = songId
		item['Performer'] = performer
		item['Song'] = song

		if songId in features:
			songFeat = features[songId]
			item['Album'] = songFeat['spotify_track_album']
			item['Genre'] = songFeat['spotify_genre']
			item['SpotifyID'] = songFeat['spotify_track_id']
			item['PreviewURL'] = songFeat['spotify_track_preview_url'] 

			if songFeat['spotify_track_explicit'] == 'TRUE':
				item['Explicit'] = 1
			elif songFeat['spotify_track_explicit'] == 'FALSE':
				item['Explicit'] = 0
			else:
				item['Explicit'] = ''

			item['Duration'] = songFeat['spotify_track_duration_ms']
			item['Danceability'] = songFeat['danceability']
			item['Energy'] = songFeat['energy']

			if songFeat['key'] != '':
				for i in range(0, 12):
					item['Key' + str(i)] = 0
				item['Key' + songFeat['key']] = 1

			item['Loudness'] = songFeat['loudness']
			item['Mode'] = songFeat['mode']
			item['Speechiness'] = songFeat['speechiness']
			item['Acousticness'] = songFeat['acousticness']
			item['Instrumentalness'] = songFeat['instrumentalness']
			item['Liveness'] = songFeat['liveness']
			item['Valence'] = songFeat['valence']
			item['Tempo'] = songFeat['tempo']

			if songFeat['time_signature'] != '':
				for i in [0, 1, 3, 4, 5]:
					item['TimeSignature' + str(i)] = 0
				item['TimeSignature' + songFeat['time_signature']] = 1

		item['SongPopularity'] = len([x for x in unique_songs[songId] if x < item['WeekNumber']])
		#item['PerformerPopularity'] = len([x for x in unique_performers[performer] if x < item['WeekNumber']])
		
		hot_songs.append(item)

	f.close()

	# Sort
	hot_songs = sorted(hot_songs, key = lambda x: (x['WeekNumber'], int(x['WeekPosition'])))
		
	# Write CSV
	f_out = open('data/hot-combined.csv', 'w')

	new_variables = ['WeekNumber', 'WeekID', 'WeekPosition', 'SongID', 'Performer', 'Song', 'Album', 
					'Genre', 'SpotifyID', 'PreviewURL', 'Explicit', 'Duration', 
					'Danceability', 'Energy', 
					'Key0', 'Key1', 'Key2', 'Key3', 'Key4', 'Key5', 'Key6', 'Key7', 'Key8',
					'Key9', 'Key10', 'Key11',
					'Loudness', 'Mode', 'Speechiness', 'Acousticness',
					'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 
					'TimeSignature0', 'TimeSignature1', 'TimeSignature3', 'TimeSignature4', 'TimeSignature5',
					# 'SongPopularity', 'PerformerPopularity']
					'SongPopularity']

	f_out.write(utils.csv_row(new_variables))

	for item in hot_songs:
		tmp_row = []
		for v in new_variables:
			if v in item:
				tmp_row.append(item[v])
			else:
				tmp_row.append('')

		f_out.write(utils.csv_row(tmp_row))
	
	f_out.close()

def main():
	combine()

if __name__ == '__main__':
	main()

#!/usr/local/bin/python3

import csv
import datetime
import requests
import json
import utils
from bs4 import BeautifulSoup

def sort_billboard_list():
	f = open('data/hot-100.csv', 'r')
	obj = csv.reader(f)

	items = []

	variables = next(obj)
	for row in obj:
		items.append(row)
	f.close()

	items = sorted(items, key=lambda x: (datetime.datetime.strptime(x[1], '%m/%d/%Y'), int(x[2]))) 

	f_out = open('data/new-billboard-list.csv', 'w')
	f_out.write(utils.csv_row(variables))
	
	for item in items:
		f_out.write(utils.csv_row(item))
	f_out.close()	

def get_billboard_list(start_date, end_date):
	f_out = open('data/billboard-list.csv', 'w')

	new_variables = ['Url', 'WeekID', 'WeekPosition',
					'Song', 'Performer', 'SongID',
					'Instance', 'PreviousWeekPosition', 'PreviousPeakPosition', 'WeeksOnChart']

	f_out.write(utils.csv_row(new_variables))


	session = requests.Session()


	date = start_date
	while date <= end_date:
		print(datetime.datetime.strftime(date, '%m/%d/%Y'))
		url = 'https://www.billboard.com/charts/hot-100/' + datetime.datetime.strftime(date, '%Y-%m-%d') + '/'
		response = session.get(url)
		if not response.ok:
			print('Bad response for {}'.format(datetime.datetime.strftime(date, '%Y-%m-%d')))
	
		soup = BeautifulSoup(response.text, 'html.parser')

		ranks = soup.find_all('span', class_='chart-element__rank__number')
		if len(ranks) != 100:
			print('Number of ranks: {}'.format(len(ranks)))
	
		songs = soup.find_all('span', class_='chart-element__information__song text--truncate color--primary')
		if len(songs) != 100:
			print('Number of songs: {}'.format(len(songs)))
	
		performers = soup.find_all('span', class_='chart-element__information__artist text--truncate color--secondary')
		if len(performers) != 100:
			print('Number of performers: {}'.format(len(performers)))
	
		previous_lasts = soup.find_all('span', class_='chart-element__information__delta__text text--last')
		if len(previous_lasts) != 100:
			print('Number of previous lasts: {}'.format(len(previous_lasts)))
	
		previous_peaks = soup.find_all('span', class_='chart-element__information__delta__text text--peak')
		if len(previous_peaks) != 100:
			print('Number of previous peaks: {}'.format(len(previous_peaks)))
	
		previous_weeks = soup.find_all('span', class_='chart-element__information__delta__text text--week')
		if len(previous_weeks) != 100:
			print('Number of previous weeks: {}'.format(len(previous_weeks)))

		for i in range(100):
			f_out.write(utils.csv_row([url, 
										datetime.datetime.strftime(date, '%m/%d/%Y'), ranks[i].text, 
										songs[i].text, performers[i].text, songs[i].text + performers[i].text, '', 
										previous_lasts[i].text.split()[0].replace('-', ''), 
										previous_peaks[i].text.split()[0].replace('-', ''), 
										previous_weeks[i].text.split()[0].replace('-', '')]))
	
		date += datetime.timedelta(days=7)
	
	f_out.close()

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

def get_songs():
	weekConv = get_week_conversion()
	songs = dict()
	hotWeeks = dict()

	song_variables = ['Song', 'Performer', 'SpotifyID', 'Album', 'Genres', 
					'PreviewURL', 'Explicit', 'Duration', 'Danceability', 'Energy',
					'Key0', 'Key1', 'Key2', 'Key3', 'Key4', 'Key5', 'Key6', 'Key7', 'Key8', 'Key9', 'Key10', 'Key11',
					'Loudness', 'Mode', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence', 'Tempo',
					'TimeSignature0', 'TimeSignature1', 'TimeSignature3', 'TimeSignature4', 'TimeSignature5',
					'HotWeeks']

	f = open('data/billboard-list.csv', 'r')
	obj = csv.reader(f)

	variables = next(obj)
	for row in obj:
		weekId = row[variables.index('WeekID')]
		songId = row[variables.index('SongID')]
		song = row[variables.index('Song')]
		performer = row[variables.index('Performer')]

		if songId not in songs:
			item = {v: '' for v in song_variables}
			item['Song'] = song
			item['Performer'] = performer
			songs[songId] = item

		weekNum = weekConv[weekId]
		if songId not in hotWeeks:
			hotWeeks[songId] = [weekNum]
		else:
			hotWeeks[songId].append(weekNum)
			
	f.close()

	for songId in songs:
		songs[songId]['HotWeeks'] = hotWeeks[songId]

	f_out = open('data/songs.json', 'w')
	f_out.write(json.dumps(songs, indent=4))
	f_out.close()

def get_known_features():
	f = open('data/songs.json', 'r')
	songs = json.loads(f.read())
	f.close()

	f_feat = open('data/hot-100-features.csv', 'r')
	obj = csv.reader(f_feat)

	variables = next(obj)
	for row in obj:
		songId = row[variables.index('SongID')]

		if songId in songs:
			songs[songId]['SpotifyID'] = row[variables.index('spotify_track_id')]				
			
			songs[songId]['Album'] = row[variables.index('spotify_track_album')]
			songs[songId]['Genres'] = row[variables.index('spotify_genre')]
			songs[songId]['PreviewURL'] = row[variables.index('spotify_track_preview_url')]
		
			if row[variables.index('spotify_track_explicit')] == 'TRUE':
				songs[songId]['Explicit'] = 1
			elif row[variables.index('spotify_track_explicit')] == 'FALSE':
				songs[songId]['Explicit'] = 0

			songs[songId]['Duration'] = row[variables.index('spotify_track_duration_ms')]
			songs[songId]['Danceability'] = row[variables.index('danceability')]
			songs[songId]['Energy'] = row[variables.index('energy')]

			if row[variables.index('key')] != '':
				for i in range(0, 12):
					songs[songId]['Key' + str(i)] = 0
				songs[songId]['Key' + row[variables.index('key')]] = 1

			if row[variables.index('loudness')] != '':
				songs[songId]['Loudness'] = float(row[variables.index('loudness')])
			songs[songId]['Mode'] = row[variables.index('mode')]
			songs[songId]['Speechiness'] = row[variables.index('speechiness')]
			songs[songId]['Acousticness'] = row[variables.index('acousticness')]
			songs[songId]['Instrumentalness'] = row[variables.index('instrumentalness')]
			songs[songId]['Liveness'] = row[variables.index('liveness')]
			songs[songId]['Valence'] = row[variables.index('valence')]
			songs[songId]['Tempo'] = row[variables.index('tempo')]

			if row[variables.index('time_signature')] != '':
				for i in [0, 1, 3, 4, 5]:
					songs[songId]['TimeSignature' + str(i)] = 0
				songs[songId]['TimeSignature' + row[variables.index('time_signature')]] = 1

	f_feat.close()

	f_out = open('data/songs.json', 'w')
	f_out.write(json.dumps(songs, indent=4))
	f_out.close()

def get_features():
	pass

def merge():
	f_songs = open('data/songs.json', 'r')
	songs = json.loads(f_songs.read())
	f_songs.close()

	weekConv = get_week_conversion()


	f_out = open('data/billboard-merged.csv', 'w')

	new_variables = ['WeekNumber', 'WeekID', 'WeekPosition', 'SongID', 'Performer', 'Song', 'Album', 
					'Genres', 'SpotifyID', 'PreviewURL', 'Explicit', 'Duration', 
					'Danceability', 'Energy', 
					'Key0', 'Key1', 'Key2', 'Key3', 'Key4', 'Key5', 'Key6', 'Key7', 'Key8',
					'Key9', 'Key10', 'Key11',
					'Loudness', 'Mode', 'Speechiness', 'Acousticness',
					'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 
					'TimeSignature0', 'TimeSignature1', 'TimeSignature3', 'TimeSignature4', 'TimeSignature5',
					'SongPopularity']

	f_out.write(utils.csv_row(new_variables))

	f = open('data/billboard-list.csv', 'r')
	obj = csv.reader(f)

	variables = next(obj)
	for row in obj:
		item = {v: '' for v in new_variables}

		for v in variables:
			if v in new_variables:
				item[v] = row[variables.index(v)]
		item['WeekNumber'] = weekConv[item['WeekID']]
		
		songId = item['SongID']

		for k in songs[songId]:
			if k in item and item[k] == '':
				item[k] = songs[songId][k]

		item['SongPopularity'] = len([x for x in songs[songId]['HotWeeks'] if x < item['WeekNumber']])

		f_out.write(utils.csv_row([item[v] for v in new_variables]))
		
	f.close()
	f_out.close()

def main():
	# Write billboard-list.csv
	#sort_billboard_list()
	
	#start_date = datetime.datetime(2021, 4, 3)
	#end_date = datetime.datetime(2021, 5, 8)
	#get_billboard_list(start_date, end_date)

	# Write songs.json
	# Must be done with billboard-list.csv at this point
	get_songs()
	get_known_features()

	# Write billboard-merged.csv
	# Must be done with songs.json at this point
	#merge()

if __name__ == '__main__':
	main()	

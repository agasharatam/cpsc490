#!/usr/local/bin/python3

import csv
import json
import random
import math
import numpy as np
import numpy.random
from sklearn.decomposition import PCA

def get_billboard_by_week(inputs):	
	"""
	Returns a list.
	"""
	f = open('data/billboard-merged.csv', 'r')
	obj = csv.reader(f)

	res = []

	item = []
	count = 0

	variables = next(obj)
	for row in obj:
		try:
			for v in inputs:
				float(row[variables.index(v)])
			item.append([float(row[variables.index(v)]) for v in inputs])
		except:
			item.append(None)

		count += 1
		if count == 100:
			res.append(item)		
			item = []
			count = 0
	f.close()

	return res

def get_songs():
	"""
	Returns a dict.
	"""
	f = open('data/songs.json', 'r')
	songs = json.loads(f.read())
	f.close()

	return songs

def get_billboard_songs():
	f = open('data/billboard-merged.csv', 'r')
	obj = csv.reader(f)

	variables = next(obj)
	return [{v: row[variables.index(v)] for v in ['WeekNumber', 'SongID']} for row in obj]

def introduce_row(row, sets):
	if len(sets) % 1000 == 0:
		print(len(sets))
	return [sets[i] + [row[i]] for i in range(len(row))]

def update_maxes_mins(maxes, mins, row):
	maxes = [max(maxes[i], row[i]) for i in range(len(row))]
	mins = [min(mins[i], row[i]) for i in range(len(row))]

	return maxes, mins

def get_extreme_inputs(train_data):
	maxes = len(train_data[0][2]) * [float('-inf')]
	mins = len(train_data[0][2]) * [float('inf')]

	for i in range(len(train_data)):
		for j in range(len(train_data[i][0])):
			maxes, mins = update_maxes_mins(maxes, mins, train_data[i][0][j])

		maxes, mins = update_maxes_mins(maxes, mins, train_data[i][2])

	return maxes, mins

def normalize_row(row, maxes, mins):
	return [(row[i] - mins[i]) / (maxes[i] - mins[i]) for i in range(len(row))]

def max_min_normalize(data, maxes, mins):
	tmp = []
	for i in range(len(data)):
		#tmp.append([[(data[i][0][k] - mins[k % 30]) / (maxes[k % 30] - mins[k % 30]) if maxes[k % 30] > mins[k % 30] else 0 for k in range(len(data[i][0]))], 
		tmp.append([[normalize_row(data[i][0][j], maxes, mins) for j in range(len(data[i][0]))],
					data[i][1],
					normalize_row(data[i][2], maxes, mins),
					data[i][3]])
		#tmp.append([[math.exp(-abs((data[i][0][k] - data[i][0][k % 30 + 1890]) / (maxes[k % 30] - mins[k % 30]))) \
		#	if maxes[k % 30] > mins[k % 30] else 0 for k in range(len(data[i][0]) - 30)],
		#	data[i][1]])

	return tmp

def pca_transform(weekly_songs, num_pca_components):
	large = []
	for w in weekly_songs:
		large.extend([s for s in w if s is not None])

	idx = 0
	l = None
	while l is None:
		if large[idx] is not None:
			l = len(large[idx])
		else:
			idx += 1

	maxes = [max([song[i] for song in large]) for i in range(l)]
	mins = [min([song[i] for song in large]) for i in range(l)]

	for i in range(len(large)):
		large[i] = [(large[i][k] - mins[k]) / (maxes[k] - mins[k]) for k in range(len(maxes))]

	pca = PCA(n_components=num_pca_components)
	pca.fit(large)

	for i in range(len(weekly_songs)):
		for j in range(len(weekly_songs[0])):
			if weekly_songs[i][j] is not None:
				weekly_songs[i][j] = [(weekly_songs[i][j][k] - mins[k]) / (maxes[k] - mins[k]) for k in range(len(maxes))]
				weekly_songs[i][j] = pca.transform(np.array(weekly_songs[i][j]).reshape(1, -1)).reshape(-1).tolist()

	return weekly_songs, maxes, mins, pca

def write_dataset(num_rows):
	inputs = ['Explicit', 'Duration', 
			'Danceability', 'Energy', 
			'Key0', 'Key1', 'Key2', 'Key3', 'Key4', 'Key5', 'Key6', 'Key7', 'Key8', 'Key9', 'Key10', 'Key11',
			'Loudness', 'Mode', 'Speechiness', 'Acousticness',
			'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 
			'TimeSignature0', 'TimeSignature1', 'TimeSignature3', 'TimeSignature4', 'TimeSignature5',
			'SongPopularity']

	weekly_songs = get_billboard_by_week(inputs)
	songs = get_songs()
	billboard_songs = get_billboard_songs()

	weekly_songs, maxes, mins, pca = pca_transform(weekly_songs, 10)
	
	generated_data = []
	for i in range(num_rows):
		positive = random.randrange(0, 2)
		target = ''

		while target != positive:
			song = {v: '' for v in inputs}
			while '' in [song[v] for v in inputs if v != 'SongPopularity']:
				s = random.randrange(100 * 3200)
				songId = billboard_songs[s]['SongID']
				song = songs[songId]

			if positive == 0:
				t = random.randrange(0, 3200) + 1
			else:
				t = int(billboard_songs[s]['WeekNumber']) - 1

			song['SongPopularity'] = len([x for x in song['HotWeeks'] if x < t])
			
			if t < 1:
				target = None
			elif t + 1 in song['HotWeeks']:
				target = 1
			else:
				target = 0

		song = [float(song[v]) for v in inputs]
		song = [(song[k] - mins[k]) / (maxes[k] - mins[k]) for k in range(len(maxes))]

		pca_song = pca.transform(np.array(song).reshape(1, -1)).reshape(-1).tolist()
		
		x = []
		for week_song in weekly_songs[t - 1]:
			if week_song is None:
				x.append(0)
			else:
				x.append(math.exp(-np.square(np.linalg.norm([pca_song[k] - week_song[k] for k in range(len(week_song))]))))

		generated_data.append([x, target])

	# Write JSON files
	train_data = generated_data[:int(0.64 * num_rows)]
	validation_data = generated_data[int(0.64 * num_rows):int(0.80 * num_rows)]
	test_data = generated_data[int(0.80 * num_rows):]

	#maxes, mins = get_extreme_inputs(train_data)

	f_out = open('data/naive-train.json', 'w')
	f_out.write(json.dumps(train_data, indent=1))
	f_out.close()

	f_out = open('data/naive-validation.json', 'w')
	f_out.write(json.dumps(validation_data, indent=1))

	f_out.close()

	f_out = open('data/naive-test.json', 'w')
	f_out.write(json.dumps(test_data, indent=1))
	f_out.close()
		

def main():
	write_dataset(10000)

if __name__ == '__main__':
	main()

#!/usr/local/bin/python3

import csv
import json
import random
import numpy as np
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

def get_extreme_inputs(train_data, weekly_songs, weeks_in_train_data):
	num_vars = len(train_data[0][1])
	maxes = num_vars * [float('-inf')]
	mins = num_vars * [float('inf')]

	songs = []
	for i, w in enumerate(weekly_songs):
		if weeks_in_train_data[i]:
			songs.extend(weekly_songs[i])

	songs.extend([item[1] for item in train_data])

	maxes = [max([song[k] for song in songs]) for k in range(num_vars)]
	mins = [min([song[k] for song in songs]) for k in range(num_vars)]

	return maxes, mins

"""
def max_min_normalize(datapoint, maxes, mins):
	for t in range(len(datapoint[0])):
		for pos in range(len(datapoint[0][t])):
			datapoint[0][t][pos] = [(datapoint[0][t][pos][k] - mins[k]) / (maxes[k] - mins[k]) if maxes[k] > mins[k] else 0 for k in range(len(maxes))]
	datapoint[1] = [(datapoint[1][k] - mins[k]) / (maxes[k] - mins[k]) if maxes[k] > mins[k] else 0 for k in range(len(maxes))]

	return datapoint
"""

def max_min_normalize(weekly_songs, data, maxes, mins):
	for w in range(len(weekly_songs)):
		for pos in range(len(weekly_songs[w])):
			weekly_songs[w][pos] = [(weekly_songs[w][pos][k] - mins[k]) / (maxes[k] - mins[k]) if maxes[k] > mins[k] else 0 for k in range(len(maxes))]
	
	for i in range(len(data)):
		data[i][1] = [(data[i][1][k] - mins[k]) / (maxes[k] - mins[k]) if maxes[k] > mins[k] else 0 for k in range(len(maxes))]
	
	return weekly_songs, data

def get_similarity(week1, week2, num_top_songs, num_pca_components):
    """
    week1.shape = (Number of songs in week 1) X x_size
    week2.shape = (Number of songs in week 2) X x_size
    """
    combined = np.concatenate((np.array(week1), np.array(week2)), axis=0)

    pca = PCA(n_components=num_pca_components)
    transformed = pca.fit_transform(combined)

    week1_pca = transformed[:len(week1), :]
    week2_pca = transformed[len(week1):, :]

    dists = dict()

    for i in range(len(week1)):
        for j in range(len(week2)):
            dists[(i, j)] = np.linalg.norm(week1_pca[i] - week2_pca[j])
    
    dists = {k: v for k, v in sorted(dists.items(), key=lambda item: item[1])}
    pairs = [key for key in dists]

    week1_available = [i for i in range(len(week1))]
    week2_available = [i for i in range(len(week2))]
    mapping = dict()
    i = 0
    while len(mapping) < num_top_songs:
        idx1, idx2 = pairs[i]
        if idx1 in week1_available and idx2 in week2_available:
            mapping[str(idx1)] = idx2
            week1_available.remove(idx1)
            week2_available.remove(idx2)
        i += 1

    return mapping

def rearrange_sequences(weekly_songs, num_top_songs, num_pca_components):
    """
    sequences.shape = num_top_songs X sequence_length X x_seq_size
    """
    sequences = [[] for i in range(num_top_songs)]

    for i, (idx1, idx2) in enumerate(get_similarity(weekly_songs[0], weekly_songs[1], num_top_songs, num_pca_components).items()):
        idx1 = int(idx1)
        sequences[i].extend([weekly_songs[0][idx1], weekly_songs[1][idx2]])
    len_seq = 2
    
    while len_seq < 200:
        week1_songs = [s[len_seq - 1] for s in sequences]
        week2_songs = weekly_songs[len_seq]

        mapping = get_similarity(week1_songs, week2_songs, num_top_songs, num_pca_components)
        for i in range(num_top_songs):
            sequences[i].append(week2_songs[mapping[str(i)]])
    
        len_seq += 1
    
    return sequences

def get_tuple_conv(weekly_songs):
	conv = dict()
	for i in range(len(weekly_songs)):
		for pos in range(len(weekly_songs[i])):
			conv[(i, tuple(weekly_songs[i][pos]))] = (i, pos)

	return conv

def seqs_to_tuples(tuple_conv, t_start, sequences):
	res = []
	for pos in range(len(sequences)):
		item = []
		for t in range(len(sequences[0])):
			item.append(tuple_conv[(t_start + t, tuple(sequences[pos][t]))])
		res.append(item)

	return res

def get_sequences(weekly_songs, generated_data, sequence_length, num_top_songs, num_pca_components):
	try:
		f = open('data/sequences_{}_{}_{}.json'.format(sequence_length, num_top_songs, num_pca_components), 'r')
		saved = json.loads(f.read())
		print('Loaded {} sequences.'.format(len(saved)))
		f.close()
	except:
		saved = dict()

	tuple_conv = get_tuple_conv(weekly_songs)

	new_data = []
	for item in generated_data:
		t = item[0]
		
		if str(t) in saved:
			new_data.append([saved[str(t)], item[1], item[2]])
		else:
			sequences = rearrange_sequences(weekly_songs[t:t+sequence_length], num_top_songs, num_pca_components)	
			saved[str(t)] = seqs_to_tuples(tuple_conv, t, sequences)

			if len(saved) % 10 == 0:
				print('Saving...')
				f = open('data/sequences_{}_{}_{}.json'.format(sequence_length, num_top_songs, num_pca_components), 'w')
				f.write(json.dumps(saved))
				f.close()
				print('Saved {} items.'.format(len(saved)))

			new_data.append([saved[str(t)], item[1], item[2]])

		if len(new_data) % 10 == 0:
			print('Done with {} out of {}.'.format(len(new_data), len(generated_data)))

	return new_data

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
	print(pca.explained_variance_ratio_)

	for i in range(len(weekly_songs)):
		for j in range(len(weekly_songs[0])):
			if weekly_songs[i][j] is not None:
				weekly_songs[i][j] = [(weekly_songs[i][j][k] - mins[k]) / (maxes[k] - mins[k]) for k in range(len(maxes))]
				weekly_songs[i][j] = pca.transform(np.array(weekly_songs[i][j]).reshape(1, -1)).reshape(-1).tolist()

	#for i in range(len(weekly_songs)):
	#	weekly_songs[i] = pca.transform(np.array(weekly_songs[i]).reshape(-1, 1)).reshape(-1).tolist()

	return weekly_songs

def write_dataset(num_rows, seq_len):
	inputs = ['Explicit', 'Duration', 
			'Danceability', 'Energy', 
			'Key0', 'Key1', 'Key2', 'Key3', 'Key4', 'Key5', 'Key6', 'Key7', 'Key8', 'Key9', 'Key10', 'Key11',
			'Loudness', 'Mode', 'Speechiness', 'Acousticness',
			'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 
			'TimeSignature0', 'TimeSignature1', 'TimeSignature3', 'TimeSignature4', 'TimeSignature5',
			'SongPopularity']

	weekly_songs = get_billboard_by_week(inputs)
	weekly_songs = pca_transform(weekly_songs, 10)
	weeks_in_train_data = [False for _ in weekly_songs]
	songs = get_songs()
	billboard_songs = get_billboard_songs()
	
	generated_data = []
	for num_i in range(num_rows):
		print('Done with {} out of {}.'.format(num_i, num_rows))

		target = None
		
		while target == None:
			t = random.randrange(200, 3200)
			pos = random.randrange(0, 100)
			if weekly_songs[t][pos] is not None:
				target = weekly_songs[t][pos]

		x = 200 * [None]

		song = target
		for i in range(0, 200):
			j = 0
			smallest_dist = float('inf')
			smallest_idx = None

			while smallest_dist > 0 and j < 100:
				if weekly_songs[t - (i + 1)][j] != None:
					dist = np.linalg.norm([song[k] - weekly_songs[t - (i + 1)][j][k] for k in range(len(song))])
					if dist < smallest_dist:
						smallest_dist = dist
						smallest_idx = j

				j += 1

			x[200 - (i + 1)] = weekly_songs[t - (i + 1)][smallest_idx]
			song = weekly_songs[t - (i + 1)][smallest_idx]	
	
		#generated_data.append([t - 1, [float(song[v]) for v in inputs], target])
		generated_data.append([x, target])

	# Write JSON files
	#train_data = generated_data[:int(0.64 * num_rows)]

	
	#maxes, mins = get_extreme_inputs(train_data, weekly_songs, weeks_in_train_data)
	#weekly_songs, generated_data = max_min_normalize(weekly_songs, generated_data, maxes, mins)

	#new_data = get_sequences(weekly_songs, generated_data, 200, 63, 15)
	#new_data = 10000 * [0]

	train_data = generated_data[:int(0.64 * num_rows)]
	validation_data = generated_data[int(0.64 * num_rows):int(0.80 * num_rows)]
	test_data = generated_data[int(0.80 * num_rows):]

	f_out = open('data/new-multi-rnn-train.json', 'w')
	f_out.write(json.dumps(train_data, indent=1))
	f_out.close()

	f_out = open('data/new-multi-rnn-validation.json', 'w')
	f_out.write(json.dumps(validation_data, indent=1))
	f_out.close()

	f_out = open('data/new-multi-rnn-test.json', 'w')
	f_out.write(json.dumps(test_data, indent=1))
	f_out.close()
		

def main():
	write_dataset(10000, 200)

if __name__ == '__main__':
	main()

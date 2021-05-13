#!/usr/local/bin/python3

import matplotlib.pyplot as plt
import json
import csv


def save(obj, fname):
	f = open(fname, 'w')
	f.write(json.dumps(obj, indent=4))
	f.close()

def main():
	f = open('data/billboard-merged.csv')
	obj = csv.reader(f)

	bruno = dict()
	mariah = dict()
	variables = next(obj)
	for row in obj:
		songId = row[variables.index('SongID')]
		weekNum = int(row[variables.index('WeekNumber')])
		weekPos = int(row[variables.index('WeekPosition')])
		
		if songId == 'When I Was Your ManBruno Mars':
			bruno[str(weekNum)] = weekPos
		elif songId == 'All I Want For Christmas Is YouMariah Carey':
			mariah[str(weekNum)] = weekPos
	f.close()

	bruno_pos = []
	mariah_pos = []
	start = 2839
	end = 3259
	for i in range(start - 10, end + 10 + 1):
		if str(i) not in bruno:
			bruno_pos.append(-4)
		else:
			bruno_pos.append(101 - bruno[str(i)])

		if str(i) not in mariah:
			mariah_pos.append(-4)
		else:
			mariah_pos.append(101 - mariah[str(i)])

	save(bruno_pos, 'plot-data/bruno-pos.json')
	save(mariah_pos, 'plot-data/mariah-pos.json')
			
		
	
	"""
	i = 0
	loudness_totals = 64 * [0]
	explicit_totals = 64 * [0]
	tempo_totals = 64 * [0]
	counts = 64 * [0]
	variables = next(obj)
	for row in obj:
		weekId = row[variables.index('WeekID')]
		loudness = row[variables.index('Loudness')]
		explicit = row[variables.index('Explicit')].strip()
		tempo = row[variables.index('Tempo')]
		
		year = int(weekId[-4:]) - 1958
		
		if loudness != '':
			loudness_totals[year] += float(loudness)
			tempo_totals[year] += float(tempo)
			counts[year] += 1
			
	t = [x for x in range(1, 64)]
	loudness_averages = [loudness_totals[k] / counts[k] for k in range(len(counts))]
	explicit_averages = [explicit_totals[k] / counts[k] for k in range(len(counts))]
	tempo_averages = [tempo_totals[k] / counts[k] for k in range(len(counts))]
	
	save(loudness_averages, 'plot-data/loudness.json')
	save(tempo_averages, 'plot-data/tempo.json')
	"""

if __name__ == '__main__':
	main()




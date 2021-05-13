#!/usr/local/bin/python3
import matplotlib.pyplot as plt
import json

color_bg = 'white'
color1 = 'forestgreen'
color2 = 'indigo'

def load(fname):
	f = open(fname, 'r')
	obj = json.loads(f.read())
	f.close()

	return obj

def main():
	"""	
	t = list(range(1958, 2021))
	loudness = load('plot-data/loudness.json')
	tempo = load('plot-data/tempo.json')

	fig, ax = plt.subplots()
	ax.set_facecolor(color_bg)

	ax.plot(t, loudness[:-1], '--', color=color1)

	ax.set_xlabel("Year",fontsize=14)
	ax.set_ylabel("Loudness (decibels)",color=color1,fontsize=14)

	ax2 = ax.twinx()
	ax2.plot(t, tempo[:-1], color=color2) 
	ax2.set_ylabel('Tempo (beats per minute)', color=color2, fontsize=14)

	plt.show()
	fig.savefig('plot-data/cpsc490-avg-trends.png',
				format='jpg',
				dpi=100,
				bbox_inches='tight')
	"""
	"""
	t = list(range(2829, 3270))
	bruno = load('plot-data/bruno-pos.json')
	mariah = load('plot-data/mariah-pos.json')

	#fig, ax = plt.subplots()
	fig = plt.figure()
	ax = fig.add_axes([0.2, 0.15, 0.7, 0.7])
	ax.plot(t, bruno, '--', color=color1, label = 'Bruno Mars\' $\it{When}$ $\it{I}$ $\it{Was}$ $\it{Your}$ $\it{Man}$')
	ax.plot(t, mariah, color=color2, label = 'Mariah Carey\'s $\it{All}$ $\it{I}$ $\it{Want}$ $\it{For}$ $\it{Christmas}$ $\it{Is}$ $\it{You}$')
	ax.legend(loc='upper right')

	ax.set_ylim([-10, 130])
	ax.set_ylabel('Position on the Hot 100', fontsize=14)
	
	ax.set_xticks([2839, 3254])
	ax.set_xticklabels(['Dec 2012', 'Dec 2020'], fontsize=11)

	ax.set_yticks([-4, 1, 100])
	ax.set_yticklabels(['None', '100', '1'], fontsize=11)

	plt.show()
	fig.savefig('plot-data/cpsc490-mariah.jpg',
				format='jpg',
				dpi=100,
				bbox_inches='tight')
	"""
	t1 = list(range(0, 200))
	naive_train_losses = load('plot-data/naive-train-losses.json')
	naive_validation_losses = load('plot-data/naive-validation-losses.json')

	t2 = list(range(0, 500))
	rnn_train_losses = load('plot-data/rnn-train-losses.json')
	rnn_validation_losses = load('plot-data/rnn-validation-losses.json')


	#fig, ax = plt.subplots()
	fig = plt.figure()
	ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
	ax.plot(t2, rnn_train_losses, color=color1, label='Train')
	ax.plot(t2, rnn_validation_losses, '--', color=color2, label = 'Validation')
	ax.plot(t2, rnn_train_losses, color=color1)

	ax.legend(loc='upper right')
	
	plt.show()

if __name__ == '__main__':
	main()

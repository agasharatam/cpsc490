import datetime
import re
import requests
import json

def parse_date(s):
	"""
	2020-05-25
	"""
	split = s.split('-')
	return datetime.datetime(int(split[0]), int(split[1]), int(split[2]))

def date_to_str(d):
	return '{}-{}-{}'.format(d.year, str(d.month).zfill(2), str(d.day).zfill(2))

def parse_int(s):
	try:
		res = int(s)
	except:
		res = 0
	return res

def weekIdToNum(s):
	start = datetime.datetime(1958, 8, 2)
	d = datetime.datetime.strptime(s, '%m/%d/%Y')
	return d - start


def remove_newlines(s):
	return re.sub(r'\s+', ' ', s)

def remove_hashtags(s):
	return re.sub(r' #[A-Za-z0-9]+', '', ' ' + s)[1:]

def csv_row(vals, quotes=True):
	if quotes:
		return ','.join([csv_text(str(val)) for val in vals]) + '\n'		
	else:
		return ','.join([str(val) for val in vals]) + '\n'

def csv_text(s):
	return '\"{}\"'.format(s.replace('\"', '\"\"'))

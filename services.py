import json
import os
import re
import base64
from datetime import date
import logging

def createNewSession():
	return  os.urandom(64).encode('base-64')

	
def convertdateToDate(d):
	"""
	recieveing a date string in the format of yyyy-mm-dd and converting it to a date object to 
	be saved in the database
	"""
	count = d.count('-')
	if count == 2:
		y, m, d = map(int,d.split('-'))
	else: # error with date fromat
		logging.debug('error with date format')
		y, m, d = 1970,07,19
		
	return date(y,m,d)

def convertToboolean(v):
	"""
	convert yes or No to booleans, basically only Yes, is True all the rest in False
	"""
	if v.lower() == 'yes':
		return True
	else:
		return False

def convertToIntegerOrFloat(v, t):
	"""
	if t == float then convert unicode to float if t == integer convert to integer and if none, return empty
	string 
	"""
	if t == 'float':
		try:
			res = float(v)
		except ValueError:
			res = ''
	elif t == 'integer':
		try:
			res = int(v)
		except ValueError:
			res = ''
	else:
		res = ''
	return res
						 			
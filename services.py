import webapp2
import constants
import json
import os
import re
import base64
from datetime import date
import logging
import models


class baseHandler(webapp2.RequestHandler):
	"""
	This is a baseHandler to for all classes which use webapp2, and includes variable checks
	a short response and more
	"""
	def checkValues(self , *args):
		res =  constants.STATUS_OK, 'All is good'
		for a in args:
			test = self.request.get(a,'')
			if test == '':
				res =  constants.MISSING_PARAMS, 'value %s was not recieved'%a
				break
		
		return res	
				
	def write(self, text):
		self.response.out.write(text)		
		
		
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

def getCard(card_id=''):
	"""
	getting card_id and returning the card object if true or None if doesn't exist or empty.
	When a tag is activated the active tag should be set to True
	"""
	card = None
	q = models.Card.query(models.Card.id == card_id.upper())
	if q and q.count > 0:
		card = q.get()
	return card
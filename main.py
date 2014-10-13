import webapp2
import os
import models
import json
import services
import constants
import logging
import idfactory
from google.appengine.ext import ndb
from google.appengine.ext.ndb import metadata
from gaesessions import get_current_session
from google.appengine.ext.webapp import template


class registrationHandler(services.baseHandler):
	def post (self):
		res, message = self.checkValues('email','password')
		if res != constants.STATUS_OK:
			self.write(message)
			return
		email = self.request.get('email').lower()
		password = self.request.get('password')
		name = self.request.get('name','')
		phone = self.request.get('phone','')
		
		
		dr = models.MyDoctor()
		dr.email = email
		dr.password = password
		dr.name = name
		dr.phone_number = phone
		
		d_key = dr.put()
		
		reg_sess = models.RegistrationSession()
		reg_sess.user = d_key
		reg_sess.put()
		
		sess = models.Session()
		sess.user = d_key
		#sess.session = services.createNewSession()
		
		sess.put()
		
		self.write('all is OK')


class loginHandler(services.baseHandler):
	def get(self):
		"""
		Load the login page and if there is a session go directly to the DR page
		"""
		path = os.path.join(os.path.dirname(__file__), 'templates/ind.html')
		logging.debug(path)
		params= {}
		self.write(template.render(path,params))						
			  
	def post(self):
		res, message = self.checkValues('card_id','password')
		path = os.path.join(os.path.dirname(__file__), 'templates/ind.html')
		logging.debug('password = %s and card ID = %s'%(self.request.get('password',''),self.request.get('card_id','')))
		if res != constants.STATUS_OK:
			params= {constants.STATUS_CODE : constants.ERROR, "ERROR_MESSAGE": "card ID or password are incorrect"}
		#checking to see if passowrd on postcard matches and tag ID is in the DB	
		elif not ( (self.request.get('password','') == constants.POSTCARD_CODE) and
				(models.IDtable.exist(self.request.get('card_id','')) ) ):			
			params= {constants.STATUS_CODE : constants.ERROR, "ERROR_MESSAGE": "card ID or password are incorrect"}
		else:
			card = services.getCard(self.request.get('card_id',''))
			path = os.path.join(os.path.dirname(__file__), 'templates/card.html')
			if not card:			   
				params= {constants.STATUS_CODE : constants.STATUS_OK, "CARD": self.request.get('card_id','')}
			else:
				params = card.to_dict()
				params['CARD'] = params['id'] 
		self.write(template.render(path,params))									
					
		return	
					


class logoutHandler(services.baseHandler):
	def get (self):

		path = os.path.join(os.path.dirname(__file__), 'templates/ind.html')
		params= {}
		self.write(template.render(path,params))						
		

class newHandler(services.baseHandler):
	def post (self):
		session = get_current_session()
		if session.is_active() == False:
			path = os.path.join(os.path.dirname(__file__), 'templates/ind.html')
			params= {}
			self.write(template.render(path,params))						
			return
		
		path = os.path.join(os.path.dirname(__file__), 'templates/cards.html')
		card_id = self.request.get('ID','')
		params= {"id":card_id}
		
		self.write(template.render(path,params))						
		return

class savecardHandler(services.baseHandler):
	"""
	API name save - get all form data of an existing crad and save it to the DB
	It does rely on the client side to do some validation
	"""
	def post (self):
		session = get_current_session()
		if session.is_active() == False:
			path = os.path.join(os.path.dirname(__file__), 'templates/ind.html')
			params= {}
			self.write(template.render(path,params))						
			return
		path = os.path.join(os.path.dirname(__file__), 'templates/')
		current_card = session['active_card']
		if not (current_card and current_card != ''): # no active card - get out
			parms = {"message":"no active card for save"} 
			path_error = path + "error.html"
			self.write(template.render(path,params))						
		
		ret_dict = {}
		card = current_card.get()
		m = self.request.params
		res = populateValuesToCard(m, card)
		if res == True:
			card_key = card.put()
			session['active_card'] = card_key
			ret_dict["STATUS"] = "OK"		
		else:
			ret_dict["STATUS"] = "ERROR"
			ret_dict["message"] = "failed to save card to DB"
					
		self.write(json.dumps(ret_dict))
		
		
class submitcardHandler(services.baseHandler):
	"""
	API name submit - This is when a new card is added. get all form data and save it to the DB
	It does rely on the client side to do some validation
	"""
	def post (self):
		res = False
		ret_dict= {}	
		
		email = self.request.get('email','')
		id = self.request.get('id','')
		cardExist = checkIfEmailOrIdExist(email, id)
		if (cardExist == True or id == ''):
			ret_dict[constants.STATUS_CODE] = constants.ERROR
			ret_dict["MESSAGE"] = "Code patient ou Email  existant"
			self.write(json.dumps(ret_dict))
			return

			
		card = models.Card()
		m = self.request.params
		res = populateValuesToCard(m, card)
		if res == True:
			card_key = card.put()
			#session['active_card'] = card_key
			ret_dict[constants.STATUS_CODE] = constants.STATUS_OK		
		else:
			ret_dict[constants.STATUS_CODE] = constants.ERROR
			ret_dict["MESSAGE"] = "Une erreur est survenue pendant la sauvegarde, merci de ressayer"
					
		self.write(json.dumps(ret_dict))
		
class searchcardHandler(services.baseHandler):
	"""
	API name search - This is used via ajax, it get a search phrase
	and will look in id and email to see if it can match one
	"""
	def post (self):
		session = get_current_session()
		if session.is_active() == False:
			path = os.path.join(os.path.dirname(__file__), 'templates/ind.html')
			params= {}
			self.write(template.render(path,params))						
			return
		term = self.request.get('s','')

		if term == '':
			self.write(json.dumps({'STATUS':'error', 'ERR': 'no results'}))
			return	
			
		card = checkIfEmailExist(term ) 
		if ( card and card == True):
			self.write(json.dumps({'STATUS':'ok', 'FIELD': 'email'}))
			return	
		card = checkIfIdExist( term)
		if (card and card == True):
			self.write(json.dumps({'STATUS':'ok', 'FIELD': 'ID'}))
			return

		self.write(json.dumps({'STATUS':'error', 'ERR': 'no match'}))
		return	
					
class getcardHandler(services.baseHandler):
	"""
	API name get_card - This shoudl be called after the client verified that the card exist
	
	"""
	def post (self):
		session = get_current_session()
		if session.is_active() == False:
			path = os.path.join(os.path.dirname(__file__), 'templates/ind.html')
			params= {}
			self.write(template.render(path,params))						
			return
		term = self.request.get('ID','')
		session['active_card'] = '' # empty card session
		path = os.path.join(os.path.dirname(__file__), 'templates/cards.html')
		card = checkIfEmailExist(term, True ) 
		if ( card ):
			params = card.to_dict() 
			params['existing_card'] = True
			session['active_card'] = card.key # keeping track of card id
			self.write(template.render(path,params))						
			return	
		card = checkIfIdExist( term, True)
		if (card):
			params = card.to_dict()
			params['existing_card'] = True
			session['active_card'] = card.key # keeping track of card id
			self.write(template.render(path,params))						
			return
		
		self.write(json.dumps({'STATUS':'error', 'message': ' Pas de correspondance avec votre recherche'}))
		return	

class getCardForMobileHandler(services.baseHandler):
	"""
	API name getMobileCard - call with get and a resource, if found returns a mobile page
	
	"""
	def get(self,uid):
		params = {}
		if not uid:
			path = os.path.join(os.path.dirname(__file__), 'templates/mobile-error.html')
			self.write(template.render(path,params))						
			return

		path = os.path.join(os.path.dirname(__file__), 'templates/mobile.html')
		card_q = models.Card.query(models.Card.id == uid)
		if card_q.count() < 1:
			path = os.path.join(os.path.dirname(__file__), 'templates/mobile-error.html')
			self.write(template.render(path,params))						
			return
		card = card_q.get()	
		if card:
			params = card.to_dict() 
			self.write(template.render(path,params))						
			return	
		else:
			path = os.path.join(os.path.dirname(__file__), 'templates/mobile-error.html')
			self.write(template.render(path,params))						
			return
			
		
def checkIfEmailOrIdExist(email='', id = ''):
	"""
	check if email or ID exists
	"""
	email = checkIfEmailExist(email, False)
	id = checkIfIdExist(id, False)
	if (email or id):
		return True
	else:
		return False

		
def checkIfEmailExist(term, getObject=False):
	"""
	check if ID exist in cards, if yes returns the object, if no return None
	"""
	card_q = models.Card.query(models.Card.email == term)
	if card_q.count() > 0:
		if getObject == True: 
			card = card_q.get()
		else:
			card = True
	else:
		card = None
	return card		 
	
def checkIfIdExist(term, getObject=False):
	"""
	check if ID exist in cards, if yes returns the object, if no return None
	"""
	card_q = models.Card.query(models.Card.id == term)
	if card_q.count() > 0:
		if getObject == True: 
			card = card_q.get()
		else:
			card = True
	else:
		card = None
	return card		 

def populateValuesToCard(data, card):
	string_for_error = ""
	try:
		for key, value in data.iteritems():
			string_for_error = key + '  is : ' + value 	
			if hasattr(card,key):
				if key == 'birth_date':
					value = services.convertdateToDate(value)
				elif key in['cardio', 'lung', 'kidney', 'digestive','neurologic' , 'eye',
							'skin', 'other', 'allergy']:
					value = services.convertToboolean(value)
				elif key == 'CR_pulse':
					if value == '': value = 0 
					value = services.convertToIntegerOrFloat(value, 'integer')
				elif key == 'CR_t':
					if value == '': value = 0 
					value = services.convertToIntegerOrFloat(value, 'float')
					
					
				setattr(card,key,value)
	except:
		logging.debug('we have an error with ' + string_for_error)
		return False
		
	return True
	
app = webapp2.WSGIApplication(
    	[
			('/login?', loginHandler),
			('/logout?', logoutHandler),
			('/new?', newHandler),
			('/submit?', submitcardHandler),
			('/save?', savecardHandler),
			('/search?', searchcardHandler),
			('/get_card?', getcardHandler),
			('/getMobileCard/([^/]+)?', getCardForMobileHandler),
			('/register?', registrationHandler),
			('/admin/createID?',idfactory.CreateIDHandler),
			('/admin/createIDTQ', idfactory.CreateIDHandlerTQ)
    	],
                                         debug=True) 		


 		
			
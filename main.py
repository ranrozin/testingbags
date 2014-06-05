import webapp2
import os
import models
import json
import services
import constants
from google.appengine.ext import ndb
from google.appengine.ext.ndb import metadata
from gaesessions import get_current_session
from google.appengine.ext.webapp import template

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
			

class registrationHandler(baseHandler):
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


class loginHandler(baseHandler):
	def get(self):
		"""
		Load the login page and if there is a session go directly to the DR page
		"""
		session = get_current_session()
		if session.is_active(): # we have a session but let check and see if email and password are OK
			if session.has_key('email') and session.has_key('password'):
				if models.MyDoctor.exist(session['email'].lower(), session['password'].lower()):			
					email = session['email'] 
					password = session['password']
					self.redirect('static/search.html') 
					return
			else:
				path = os.path.join(os.path.dirname(__file__), 'templates\ind.html')
				params= {}
				self.write(template.render(path,params))						
		else:	
			path = os.path.join(os.path.dirname(__file__), 'templates\ind.html')
			params= {}
			self.write(template.render(path,params))						
			  
	def post(self):
		res, message = self.checkValues('email','password')
		if res != constants.STATUS_OK:
			self.write(message)
			return

		session = get_current_session()
		if models.MyDoctor.exist(self.request.get('email','').lower(), self.request.get('password','').lower()):			
			session['email'] = self.request.get('email','').lower()
			session['password'] = self.request.get('password','').lower()
			self.redirect('static/search.html') 
		else:
			path = os.path.join(os.path.dirname(__file__), 'templates\ind.html')
			params= {"ERROR": "email or password are incorrect"}
			self.write(template.render(path,params))						
					
		return	


class logoutHandler(baseHandler):
	def get (self):
		session = get_current_session()
		if session.is_active(): # we have the credentials
			session.terminate()

		path = os.path.join(os.path.dirname(__file__), 'templates\ind.html')
		params= {}
		self.write(template.render(path,params))						
		

class newHandler(baseHandler):
	def get (self):
		session = get_current_session()
		if session.is_active() == False:
			self.redirect('/')
		
		path = os.path.join(os.path.dirname(__file__), 'templates\card.html')
		params= {}
		self.write(template.render(path,params))						
		return

class submitcardHandler(baseHandler):
	"""
	API name submit - get all form data and save it to the DB
	It does rely on the client side to do some validation
	"""
	def post (self):
		session = get_current_session()
		if session.is_active() == False:
			path = os.path.join(os.path.dirname(__file__), 'templates\ind.html')
			params= {}
			self.write(template.render(path,params))						
			return
		
		card = models.Card()
		m = self.request.params
		for key, value in m.iteritems():
			if hasattr(card,key):
				if key == 'birth_date':
					value = services.convertdateToDate(value)
				elif key in['cardio', 'lung', 'kidney', 'digestive','neurologic' , 'eye',
							'skin', 'other', 'allergy']:
					value = services.convertToboolean(value)
				elif key == 'CR_pulse':
					value = services.convertToIntegerOrFloat(value, 'integer')
				elif key == 'CR_t':
					value = services.convertToIntegerOrFloat(value, 'float')
					
					
				setattr(card,key,value)
				
		card.put()
		
class searchcardHandler(baseHandler):
	"""
	API name search - This is used via ajax, it get a search phrase
	and will look in id and email to see if it can match one
	"""
	def post (self):
		session = get_current_session()
		if session.is_active() == False:
			path = os.path.join(os.path.dirname(__file__), 'templates\ind.html')
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
					
class gethcardHandler(baseHandler):
	"""
	API name get_card - This shoudl be called after the client verified that the card exist
	
	"""
	def post (self):
		session = get_current_session()
		if session.is_active() == False:
			path = os.path.join(os.path.dirname(__file__), 'templates\ind.html')
			params= {}
			self.write(template.render(path,params))						
			return
		term = self.request.get('ID','')

		path = os.path.join(os.path.dirname(__file__), 'templates\card.html')
		card = checkIfEmailExist(term, True ) 
		if ( card ):
			params = card.to_dict() 
			self.write(template.render(path,params))						
			return	
		card = checkIfIdExist( term, True)
		if (card):
			params = card.to_dict() 
			self.write(template.render(path,params))						
			return

		self.error(404)
		return	


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
	card_q = models.Card.query(models.Card.id == term.lower())
	if card_q.count() > 0:
		if getObject == True: 
			card = card_q.get()
		else:
			card = True
	else:
		card = None
	return card		 
	
app = webapp2.WSGIApplication(
    	[
			('/login?', loginHandler),
			('/logout?', logoutHandler),
			('/new?', newHandler),
			('/submit?', submitcardHandler),
			('/search?', searchcardHandler),
			('/get_card?', gethcardHandler),
			('/register?', registrationHandler)
    	],
                                         debug=True) 		


 		
			
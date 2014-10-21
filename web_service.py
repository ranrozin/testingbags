import webapp2
import os
import models
import json
import services
import constants
import logging
from google.appengine.ext import ndb
from google.appengine.ext.ndb import metadata
from gaesessions import get_current_session
from google.appengine.ext.webapp import template

class 


app = webapp2.WSGIApplication(
    	[
			('/createID?', createIDHandler),
			('/logout?', logoutHandler),
			('/new?', newHandler),
			('/submit?', submitcardHandler),
			('/save?', savecardHandler),
			('/search?', searchcardHandler),
			('/get_card?', getcardHandler),
			('/getMobileCard/([^/]+)?', getCardForMobileHandler),
			('/register?', registrationHandler)
    	],
                                         debug=True) 		


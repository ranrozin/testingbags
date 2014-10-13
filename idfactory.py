
#idFactory.py
import sys
import webapp2
import constants
import models
import services
import json
import logging
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from ID import taghash
"""
IDFactory has two exposed function, checkID and createID which check to see if
ID is correct and create IDs. The create ID is using task Push 
(calling createIDTQ) to avoid failure due to the 60 seconds deadline.
The downside is that if the task fails, there client has no way of knowing, 
other than calling the last number generated for a specifc vendor 
"""

class CreateIDHandler( services.baseHandler):
	"""
	recieves:
	user - this is not an app user but an admin user and password, which is not stored in the DB and only in this file
	password - the same as above, the password is stored only in this file
	seed [Optional] - this is the seed for starting the numbers serial number to be generated. The start is 1000000 (1M)
			and if seed is smaller than the last number in the DB, it will ignore and conntinue from the last number
			the only place where seed can be useful is if there is a need to skip numbers
	pf - this is the code for th evendor (prefix). As each vendor has it's own numbers, this is a must field. for a generic 
		 tag-a-bag tag, the vendor pf = TB
	number{optional] - this is the number of the IDs to be generated, if omitted number=1
    
	This function uses a task push so there is no error or sucess returned if all params are OK	
	"""


	user_key = "ranrozinandmybags"
	password_key = '233jhnLGTMF45432P'
	def get(self):
		res, message = self.checkValues('user','password')
		if res != constants.STATUS_OK:
			self.write(message)
			return
	
		user = self.request.get('user', 'NULL')
		password = self.request.get('password', 'NULL')
		seed = int(self.request.get('seed', '100000'))
		number = int(self.request.get('number', '1'))
		pf = self.request.get('pf', 'AA')
		
		# Add the task to the default queue.
		taskqueue.add(url='/admin/createIDTQ?', params={'user': user, 'password':password, 'seed':seed,'number':number,'pf': pf})
		return_dict = { constants.STATUS_CODE :constants.STATUS_OK,
					    'MESSAGE' : 'task was called successfuly'
					}
		self.response.out.write(json.dumps(return_dict))
		
class CreateIDHandlerTQ( services.baseHandler):
	"""
	This is the function that actually cerate the ID's. it receives the params from the exposed function CrteateID 
	"""
	user_key = "ranrozinandmybags"
	password_key = '233jhnLGTMF45432P'
	
	def post(self):

		user = self.request.get('user', 'NULL')
		password = self.request.get('password', 'NULL')
		seed = int(self.request.get('seed', '0'))
		number = int(self.request.get('number', '1'))
		pf = self.request.get('pf', 'AA')

		if  self.user_key == user and  self.password_key == password:
			
			
			last = seed
			if last == 0:
				last = IDtable.All().count()
				
			res = taghash.generateTagIds(last+1, number, pf, constants.HASH_KEY )
			if res and len(res) > 0:
				m_res = writeIDtoDB(res, pf)
				if m_res > 0:
					logging.info('the numbers of records written to the DB are %s'%m_res)
				else:
					logging.error('there was an error number %s'%m_res)

			else:
				logging.error('taghash failed to return values')
			
				

def writeIDtoDB(lst, prf):
	"""
	Receives :
	lst - list of IDtable objects to be written to the DB
	prf - the vendor prefix to be written under
	On success returns the number of ID's generated
	On fail - return -1
	This function adds an s at the end of every ID that is written to the DB 
	"""
	
	dblst = []
	for counter, item in enumerate(lst):
		try:
			logging.debug('in wrtie to db about to crate %s IDtables'%lst)
			dblst.append( models.IDtable(id=item))
		except BadArgumentError:
			logging.debug('Failed to cerate idtable')
			logging.debug ("Unexpected error:", sys.exc_info()[0])
			return -1
		logging.debug('about to write list of idtable to the DB')
		try:
			ndb.put_multi(dblst)
			logging.debug('Wrote to %s idtable to the db'%len(dblst))
		except ComputedPropertyError:
			logging.debug('failed to write to db')
			return -1			  
		 

	return counter
			




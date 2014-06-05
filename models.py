from google.appengine.ext import ndb
import webapp2

class MyDoctor (ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    is_email_confirmed = ndb.BooleanProperty(default = True)
    phone_number = ndb.StringProperty()
    
    
    @classmethod
    def exist(cls,mail,password):
        qry = cls.query().filter(MyDoctor.email == mail).filter(MyDoctor.password == password)
        if qry.count() > 0:
            return True
        else:
            return False    
        


class RegistrationSession(ndb.Model):    
    user = ndb.KeyProperty(MyDoctor, "registration") 
    last_login = ndb.DateTimeProperty(auto_now_add=True)
    
class Session(ndb.Model):    
    user = ndb.KeyProperty(MyDoctor, "sessions")  
    last_login = ndb.DateTimeProperty(auto_now=True)
    session = ndb.StringProperty()
        
class Card(ndb.Model):
    id = ndb.StringProperty()
    fName = ndb.StringProperty()
    lName = ndb.StringProperty()
    address = ndb.StringProperty()
    tel_home = ndb.StringProperty()
    email = ndb.StringProperty()
    birth_date = ndb.DateProperty()
    ref_doctor_name = ndb.StringProperty()
    ref_doctor_tel = ndb.StringProperty()
    spec_doctor_name = ndb.StringProperty()
    spec_doctor_tel = ndb.StringProperty()
    id_number = ndb.StringProperty()
    blodType = ndb.StringProperty()
    mutual = ndb.StringProperty()
    emergency_contact_name = ndb.StringProperty()
    emergency_contact_tel = ndb.StringProperty()
    
    cardio = ndb.BooleanProperty(default = False)
    cardio_info = ndb.StringProperty()
    lung = ndb.BooleanProperty(default = False)
    kidney = ndb.BooleanProperty(default = False)
    digestive = ndb.BooleanProperty(default = False)
    neurologic = ndb.BooleanProperty(default = False)
    eye = ndb.BooleanProperty(default = False)
    skin = ndb.BooleanProperty(default = False)
    other = ndb.BooleanProperty(default = False)
    allergy = ndb.BooleanProperty(default = False)
    allergy_info = ndb.StringProperty()
    
    surgical_history = ndb.TextProperty()
    current_treatment = ndb.TextProperty()
    
    CR_cardio = ndb.StringProperty()
    CR_lung = ndb.StringProperty()
    CR_other = ndb.StringProperty()
    CR_ta = ndb.StringProperty()
    CR_pulse = ndb.IntegerProperty()
    CR_t = ndb.FloatProperty()
    
    examination = ndb.TextProperty()
    diagnostic = ndb.TextProperty()
    treatment = ndb.TextProperty()
    remarks = ndb.TextProperty()
    
    
    
    @classmethod
    def exist(cls,ide):
        qry = cls.query().filter('id =', ide)
        if qry.count() > 0:
            return True
        else:
            return False    
    
 

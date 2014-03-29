from peewee import *
from hashlib import sha1
from datetime import datetime
from mailer import send_email
from urllib import quote_plus
import random

secret = ''
db = PostgresqlDatabase('',user='')
db.connect()
db.get_conn().set_client_encoding('UTF8')

class Signature(Model):
  token = CharField(max_length=40, index=True, unique=True)
  first = CharField(null=True)
  last = CharField(null=True)
  zip_code = CharField(max_length=5, null=True)
  email_sent = DateTimeField(null=True)
  signed = DateTimeField(null=True)
  redacted = BooleanField()
  
  @staticmethod 
  def token_for_email(email):
    return sha1(email + secret).hexdigest()
  
  @classmethod 
  def check_for_duplicates(cls, email):
    return len(list(cls.select().where(cls.token == cls.token_for_email(email)))) == 0
     
  @classmethod
  def send_confirmation_email(cls, email):
    confirmation_link = "https://shameonfeinstein.org/sign?token={}".format(cls.token_for_email(email))
    confirmation_html = "Please click this link to confirm your signature on the Shame on Feinstein letter. If you do not click this link, your signature will not be counted: <a href='{}'> sign letter</a>.".format(confirmation_link)
    confirmation_text = "Please click this link to confirm your signature on the Shame on Feinstein letter. If you do not click this link, your signature will not be counted: {}".format(confirmation_link)
    send_email(to=email, subject="Confirm signature for Shame on Feinstein letter", text=confirmation_link,html=confirmation_html)
  
  @db.commit_on_success
  def record_email_sent(self):
    self.email_sent = datetime.now()
    self.save()

  def verify(self,token):
    if self.token == token:
      with db.transaction():
        self.signed = datetime.now()
        self.save()
        return True

    else:
      return False

  class Meta:
    database = db 




Signature.create_table(True)

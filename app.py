from flask import Flask, request, redirect
from models import Signature, db
from psycopg2 import IntegrityError

import json

app = Flask(__name__)
app.debug = True

def check_referrer():
  if request.referrer and "shameonfeinstein" in request.referrer:
    return True
  else:
    return False

def under_rate_limit():
  return True #for now

@app.route("/sign", methods=['POST'])
def confirm_email():
  if not check_referrer():
    return redirect("/index.html")

  if not under_rate_limit(): 
    return json.dumps({
      "result" : "failed",
      "error" : "too many requests, try again later"
    }, 420)

  with db.transaction():
    try:
      params = {}
      form = request.form
      params['first'] = form.get('first')
      params['last'] = form.get('last')
      params['zip_code'] = form.get('zip_code')
      email = form.get('email')
      params['redacted'] = int(form.get('redacted', False))
      params['token'] = Signature.token_for_email(email)
      if not Signature.check_for_duplicates(email):
        return (json.dumps({
        "result" : "error",
        "exception": "Duplicate email entered" 
        }), 401)
      signature = Signature.create(**params)
      signature.save()
      signature.send_confirmation_email(email)
      signature.record_email_sent()
      return json.dumps({
        "result" : "success"
        })
    except IntegrityError as ie: # duplicate email. maybe query first instead of this?
      return(json.dumps({
        "result" : "error",
        "exception": str(ie) 
        }), 401)


@app.route("/sign", methods=['GET'])
def sign_petition():
  token = request.args.get('token')
  if not token:
    return redirect("/")
  else:
    print token
    signatures = list(Signature.select().where(Signature.token == token))
    if len(signatures) == 0:
      return redirect("/invalid_token.html")
    signatures[0].verify(token)
    return redirect("/success.html")


@app.route("/signatures", methods=['GET'])
def get_signatures():
  with db.transaction():
    signatures = Signature.select().where((Signature.redacted == False) & ~(Signature.signed >> None))
    return json.dumps([{"first": s.first, "last": s.last, "zip_code": s.zip_code,"date":str(s.signed)} for s in signatures])

@app.route("/signatures_redacted", methods=['GET'])
def get_signatures_redacted():
  with db.transaction():
    signatures = Signature.select().where((Signature.redacted == True) & ~(Signature.signed >> None))
    return json.dumps([{"firstLen": len(s.first), "lastLen": len(s.last), "zip_code": s.zip_code, "date":str(s.signed)} for s in signatures])



if __name__ == "__main__":
    app.run()

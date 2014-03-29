import requests 

base = "https://api.mailgun.net/v2"
domain = "shameonfeinstein.org"
def send_email(**kwargs):
  """
  sends an email.
  keyword args:
    * to
    * text
  optional keyword args:
    * subject
    * html
  """
  kwargs['from'] = "'Shame On Feinstein' noreply@{}".format(domain)
  return requests.post("{}/{}/messages".format(base,domain), 
                    data=kwargs, auth=('api','')) #Key Withheld from repo

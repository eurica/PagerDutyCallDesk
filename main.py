# PagerDuty incidents triggered by phone: 
import logging
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib
from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

SERVICE_KEY = "6f4d18600a9b012f6a9722000a9040cf"

#Half of the code is just dedicated to URL shortening, so that we can fit the MP3's URL in an SMS:
def shorten(url):
    gurl = 'http://goo.gl/api/url?url=%s' % urllib.unquote(url)
    req = Request(gurl, data='')
    req.add_header('User-Agent', 'toolbar')
    logging.info('Shortening ' + gurl)
    try:
      res = urlopen(req)
      results = json.load(res)
      logging.info( res.code )
    except HTTPError, e: #triggers on HTTP code 201
      logging.info( e.code )
      error_content = e.read() 
      results = json.JSONDecoder().decode(error_content)
      
    return results['short_url']

# Outbput the TwilML to record a message and pass it to /record
class CallHandler(webapp.RequestHandler):
  def get(self):
    response = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
      "<Response><Say>Leave a message at the beep.</Say>"
      "<Record action=\"http://pdtestthrough.appspot.com/record\" method=\"GET\"/>"
      "<Say>I did not receive a recording</Say></Response>")
    self.response.out.write(response)
    logging.info('Recieved CALL ' + self.request.query_string)

# Shorten the URL and trigger a PD incident with it
class RecordHandler(webapp.RequestHandler):
  def get(self):
    response = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Say>Thanks.  Directing your message to the agent on call.</Say></Response>")
    self.response.out.write(response)
    logging.info('Recieved RECORDING: ' + self.request.query_string)
    recUrl = self.request.get("RecordingUrl")
    phonenumber = self.request.get("From")

    logging.info('Recieved RECORDING ' + recUrl)
    if(recUrl):
      logging.info('Found recording!')
    else:
      recUrl = "http%3A%2F%2Fwww.pagerduty.com%2F"
      phonenumber = ""
    shrten = "Error"
    
    try:
      shrten = shorten('%s.mp3' % recUrl)
    except HTTPError, e:
      shrten = "HTTPError"
      logging.warn( e.code )
    except URLError, e:
      shrten = "URLError"
      logging.warn(e.reason) 
    
    logging.info('Shortened to: ' + shrten)
  
    # Obviously use your own key:
    incident = '{"service_key": "%s","incident_key": "%s","event_type": "trigger","description": "%s %s"}'%(SERVICE_KEY,shrten,shrten,phonenumber)
    try:
      r = Request("http://events.pagerduty.com/generic/2010-04-15/create_event.json", incident) #Note according to the API this should be retried on failure
      results = urlopen(r)
      logging.info(incident)
      logging.info(results)
    except HTTPError, e:
      logging.warn( e.code )
    except URLError, e:
      logging.warn(e.reason)   

class IndexHandler(webapp.RequestHandler):
  def get(self):
    response = ("<html><h1>Trigger a <a href='http://www.pagerduty.com'>PagerDuty</a> incident from a phone call</h1><ul>"
      "<li><a href='http://blog.pagerduty.com/2012/02/23/triggering-an-alert-from-a-phone-call'>Docs</a>"
      "<li><a href='https://github.com/eurica/PagerDutyCallDesk/'>GitHub page</a>"
      "<li><a href='/call'>/call</a> (returns XML)"
      "<li><a href='/record?RecordingUrl=http%3A%2F%2Fapi.twilio.com%2F2010-04-01%2FAccounts%2FACfdf710462c058abf3a987f393e8e9bc8%2FRecordings%2FRE6f523cd7734fa86e56e5ef0ea5ffd4cf'>/record</a> (test with 'Hey this is Jim...')"
      "</ul>Remember to change the application identifier and the service API key, or else you'll just alert me :)</html>")
    self.response.out.write(response)

def main():
  application = webapp.WSGIApplication([
                                    ('/call', CallHandler),
                                    ('/record', RecordHandler),
                                    ('/', IndexHandler)],
                                       debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
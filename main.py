
import logging
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


def shorten(url):
    gurl = 'http://goo.gl/api/url?url=%s' % urllib.unquote(url)
    req = Request(gurl, data='')
    req.add_header('User-Agent', 'toolbar')
    logging.info('Shortening ' + gurl)
    try:
      res = urlopen(req)
      results = json.load(res)
      logging.info( res.code )
    except HTTPError, e: #triggers on code 201
      logging.info( e.code )
      error_content = e.read() 
      results = json.JSONDecoder().decode(error_content)
      
    return results['short_url']

class CallHandler(webapp.RequestHandler):
  def get(self):
    response = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
      "<Response><Say>Leave a message at the beep.</Say>"
      "<Record action=\"http://pdtestthrough.appspot.com/record\" method=\"GET\"/>"
      "<Say>I did not receive a recording</Say></Response>")
    self.response.out.write(response)
    logging.info('Recieved CALL ' + self.request.query_string)
class RecordHandler(webapp.RequestHandler):
  def get(self):
    response = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Say>Thanks.  Directing your message to the agent on call.</Say></Response>")
    self.response.out.write(response)
    logging.info('Recieved RECORDING0 ' + self.request.query_string)
    recUrl = self.request.get("RecordingUrl")
    phonenumber = self.request.get("From")
    
    
    logging.info('Recieved RECORDING1 ' + recUrl)
    if(recUrl):
      logging.info('Found recording!')
    else:
      recUrl = "http%3A%2F%2Fwww.pagerduty.com%2F"
      phonenumber = ""

    logging.info('Recieved RECORDING2 ' + recUrl)

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
    incident = '{"service_key": "6f4d18600a9b012f6a9722000a9040cf","incident_key": "%s","event_type": "trigger","description": "%s %s"}'%(shrten,shrten,phonenumber)
    try:
      r = Request("http://events.pagerduty.com/generic/2010-04-15/create_event.json", incident) #Note according to the API this should be retried on failure
      results = urlopen(r)
      logging.info(results)
    except HTTPError, e:
      logging.warn( e.code )
    except URLError, e:
      logging.warn(e.reason)   


def main():
  application = webapp.WSGIApplication([
                                    ('/call', CallHandler),
                                    ('/record', RecordHandler)],
                                       debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
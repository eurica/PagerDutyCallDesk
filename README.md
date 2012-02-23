# Trigger a PagerDuty incident from a phone call

This is not an officially supported PagerDuty product, and not covered by our SLA.  But I do work for PagerDuty, so feel free to [email me](mailto:dave@pagerduty.com) about it.

# Requirements

1. Set up a [PagerDuty account](http://www.pagerduty.com/pricing) if you don't already have one, and create a Generic API service.  We'll use the Service API key.
2. You'll need to set up a Google App Engine account, and create an application.  We'll use the application identifier.
3. Change the "application: pdtestthrough" line in app.yaml to your application identifier, and the SERVICE_KEY = "6f4d18600a9b012f6a9722000a9040cf" line in main.py to your service API key
4. Deploy to [Google App Engine](https://appengine.google.com)
5. Create a [Twilio](http://twilio.com) account, and set up an incoming phone number to point to http://[your-application-identifier].appspot.com/call
6. Call that number and leave a message, you'll trigger an alert that links to the MP3 recording of the call:

    ALRT #145 on Phone in: <a href="http://goo.gl/UMmDx">http://goo.gl/UMmDx</a> <a href="#">+14153490382</a> Reply 4:Ack, 6:Resolv.

# Walkthrough in pictures:

![PagerDuty Setup](/eurica/PagerDutyCallDesk/raw/master/help/PagerDutyAPI.png)

![Google setup](/eurica/PagerDutyCallDesk/raw/master/help/AppEngineApplication.png)

![TwilioConf](/eurica/PagerDutyCallDesk/raw/master/help/TwilioConfig.png)

![Triggers](/eurica/PagerDutyCallDesk/raw/master/help/incident.png)

# Background

We have regular hackdays at <a href="http://www.pagerduty.com">PagerDuty</a>, where we build things outside the core product without management (another reason you should <a href="//www.pagerduty.com/jobs">work here</a>).  A few weeks ago, I rolled out a proof of concept <a href="">Google App Engine</a> script to use Twilio to record a voicemail and then to pass it around like a regular alert.  Triggering alerts from phone calls hasn't made it's way on to the development roadmap, so I'm sharing this code sample as a work around for our more technically inclined users -- so all the usual caveats and disclaimers apply, namely that our SLAs don't apply.

<a href="http://twilio.com">Twilio</a> will happily turn a phone call into an MP3 and give us a link to it (which means to get this to work you're going to need to sign up for a Twilio account as well as a <a href="https://appengine.google.com">Google App Engine</a> account).  We then use Google's URL shortener to shrink the URL into something that will fit in an SMS -- all modern smart phones can figure out what to do with that. -- [Source](http://blog.pagerduty.com/index.php/2012/02/triggering-an-alert-from-a-phone-call-code-sample)
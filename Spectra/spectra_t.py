#!/usr/bin/env python

# Some curl stuff here:
#   http://pycurl.sourceforge.net/doc/quickstart.html
#   http://curl.haxx.se/docs/manpage.html

# Some SGI references
#   http://www.spectralogic.com/index.cfm?fuseaction=support.docsByProd&CatID=488
#
# XML reference: 
#   https://support.spectralogic.com/documentation/user-guides/spectra-t-series-libraries-xml-command-reference
#
# Spectra T950 Library:
#   http://www.spectralogic.com/index.cfm?fuseaction=home.displayFile&DocID=283

# Some variables (huzzah)

# fg, apparently, is the directory of the xml stuff

#   REMOVE THE FOLLOWING PRIOR TO PUBLIC COMMIT
luser = 'su'
lpass = None

import os

def __main__():
  if 'T950_URL' in os.environ:
    t950_url = os.environ['T950_URL']
  else:
    t950_url = None

  if 'T950_USERNAME' in os.environ:
    t950_username = os.environ['T950_USERNAME']
  else:
    t950_username = None

  if 'T950_PASSWORD' in os.environ:
    t950_password = os.environ['T950_PASSWORD']
  else:
    t950_password = None

  if 'T950_COOKIEFILE' in os.environ:
    t950_cookiefile = os.environ['T950_COOKIEFILE']
  else:
    t950_cookiefile = None

  # Read some options
  parser = ArgumentParser(description='T950, yo')
  parser.add_argument("-D", "--dump", action="append", help="Dump ''xml''")
  parser.add_argument("-x", "--xml", type=str, default=None, help="Read XML from this file instead of polling server.")
  args, leftover = parser.parse_known_args()

  t950 = Spectralogic.T950(
    url=t950_url,
    username=t950_username,
    password=t950_password,
    cookiefile = t950_cookiefile,
    args = args
  )
 
  if args.xml:
    with open(args.xml, 'r') as myfile:
      t950.xml = myfile.read()

  t950.drivelist()


import pycurl
# https://docs.python.org/2/library/xml.etree.elementtree.html
import xml.etree.ElementTree as ET # :)
import cStringIO

from argparse import ArgumentParser

# http://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
import os.path, time
try:
  from urllib.parse import urlencode
except ImportError:
  from urllib import urlencode # h8 python people


#
#  arguments to the spectralogic stuff:
#    url = fg_url
#    username = username
#    password = password. :Well, duh.
#

class Spectralogic:
  class T950:
    def __init__(self, **args):

      if 'dump' in args['args']:
        self.dump = args['args'].dump
      else:
        self.dump = {}

      self.cookiefile = args['cookiefile']
      self.url = args['url']
      self.alive = False

      if self.has_cookiefile() and self.cookiefile_age() > time.time()-(2*60):
        self.alive = True # Assumption!

      # Init curl session.
      self.curl_session_init()
      
      if not self.alive and "url" in args and "username" in args and "password" in args:
        self.login(**args)

      if not self.alive:
        print "Could not login"
        sys.exit(1)

    def has_cookiefile(self):
      if os.path.isfile(self.cookiefile):
        return True
      return False

    # http://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
    def cookiefile_age(self):
        return os.path.getmtime(self.cookiefile)

    # No handling. 
    def curl_session_init(self):
      # http://stackoverflow.com/questions/2221191/logging-in-and-using-cookies-in-pycurl
      self.curl_session = pycurl.Curl()
      self.curl_session.setopt(pycurl.TIMEOUT, 10)
      self.curl_session.setopt(pycurl.FOLLOWLOCATION, 1)

      # Set cookie file. Well. Read the code.
      self.curl_session.setopt(pycurl.COOKIEFILE, self.cookiefile)
      self.curl_session.setopt(pycurl.COOKIEJAR, self.cookiefile)

    # Login to spectralogic
    #   login.xml?username=[username]&password=[password]
    def login(self, **args):
      # Create login url and post data
      login_url = self.url + '/login.xml'
      postdata = urlencode(
        {
          'username': args['username'], 
          'password': args['password']
        }
      )

      self.curl_session.setopt(self.curl_session.URL, login_url)

      # Initiate postdata
      self.curl_session.setopt(self.curl_session.POSTFIELDS, postdata)
     
      # Initate stringoo object for response
      response = cStringIO.StringIO()
      self.curl_session.setopt(pycurl.WRITEFUNCTION, response.write)
      self.curl_session.perform()
      #self.curl_session.close()
      
      
      # Get response value
      value = response.getvalue()
      # http://stackoverflow.com/questions/1912434/how-do-i-parse-xml-in-python
      
      stuff = ET.fromstring(value)
      response.close()

      status = stuff.find('status')
      status_ok = status.text.strip()

      if not status_ok == 'OK':
        self.alive = False
        return False

      self.alive = True      
      return True

    def drivelist(self):
      drivelist_url = self.url+"/driveList.xml"
      self.curl_session.setopt(self.curl_session.URL, drivelist_url)

      # Initate stringoo object for response
      response = cStringIO.StringIO()
      self.curl_session.setopt(pycurl.WRITEFUNCTION, response.write)
      self.curl_session.perform()
      self.curl_session.close()
      
      
      # Get response value
      value = response.getvalue()
      if self.dump and 'xml' in self.dump:
        print value

      stuff = ET.fromstring(value)
__main__() 

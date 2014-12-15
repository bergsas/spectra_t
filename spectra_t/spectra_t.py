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

import os
import sys
import pycurl
# https://docs.python.org/2/library/xml.etree.elementtree.html
import xml.etree.ElementTree as ET # :)
import cStringIO

# http://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
import os.path, time
try:
  from urllib.parse import urlencode
except ImportError:
  from urllib import urlencode # h8 python people


def __main__():
  spectra_t_url = os.environ.get("SPECTRA_T_URL")
  spectra_t_username = os.environ.get("SPECTRA_T_USERNAME")
  spectra_t_password = os.environ.get("SPECTRA_T_PASSWORD")
  spectra_t_cookiefile = os.environ.get("SPECTRA_T_COOKIEFILE")

  # Read some options
  parser = ArgumentParser(description='Spectralogic T Series, yo')
  parser.add_argument("-D", "--dump", action="append", help="Dump ''xml''")
  parser.add_argument("-x", "--xml", type=str, default=None, help="Read XML from this file instead of polling server.")
  args, leftover = parser.parse_known_args()

  if not spectra_t_url:
    print "blurp: no Url"
    sys.exit(1)

  spectra_t = Spectra_T(
    url=spectra_t_url,
    username=spectra_t_username,
    password=spectra_t_password,
    cookiefile = spectra_t_cookiefile,
    args = args
  )

  if args.xml:
    with open(args.xml, 'r') as myfile:
      spectra_t.xml = myfile.read()

  spectra_t.drivelist()



#
#  arguments to the spectralogic stuff:
#    url = fg_url
#    username = username
#    password = password. :Well, duh.
#

class Spectra_T:
  def __init__(self, **args):

    if 'dump' in args['args']:
      self.dump = args['args'].dump
    else:
      self.dump = {}

    self.cookiefile = args['cookiefile']
    self.url = args['url']
    self.alive = False
    
    if not self.has_cookiefile() or (self.cookiefile_age() < time.time()-(2*60)):
      self.alive = True # Assumption!

    # Init curl session.
    self.curl_session_init()
      
    if not self.alive and "url" in args and "username" in args and "password" in args:
      self.login(**args)

    if not self.alive:
      print "Could not login"
      sys.exit(1)

  def has_cookiefile(self):
    if not self.cookiefile or not os.path.isfile(self.cookiefile):
      return False
    return True

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
    if self.cookiefile:
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

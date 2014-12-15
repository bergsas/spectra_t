#!/usr/bin/env python
#
# This file, I hope, will handle the following for the Spectra T stuff:
#
#   login,
#   logout,
#   errorus outputs,
#   progress.
# 
#   And a help message
#

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

class Spectra_T:
  # Only make the Spectra_T object "sane" in here:
  def __init__(self, **args):
    # From args. :)
    self.url = args.get('url')
    self.cookiefile = args.get('cookiefile')

    self.logged_in = False
    if self.has_cookiefile() and self.cookiefile_age() > (time.time()-(2*60)):
      self.crisp_cookie = True
    else:
      self.crisp_cookie = False
    
    
    # Ugh. it's a mess!
    self.fake_xml_input = None
    self.dump = ()
    
    self.curl_session = None
    self.commands = {
      "help": (self.helpcmd,0),
      "helphelp": (self.helphelpcmd,0),
      "login": (self.logincmd,1),
      "drivelist": (self.drivelistcmd,0),
      "logout": (self.logoutcmd,0)
    }

  def execute(self, cmd = None, *args):
    if cmd == None:
      cmd = 'helphelp'

    if not (self.url or cmd == 'help'):
      print >> sys.stderr, "%s: No url! No fun." %(sys.argv[0])
      sys.exit(1)

    if not cmd in self.commands:
      print >> sys.stderr, "%s: Unknown command: %s" %(sys.argv[0], cmd)
      sys.exit(1)

    if len(args) < self.commands[cmd][1]:
      print >> sys.stderr, "%s: %s requires at least %d arguments" %(sys.argv[0], cmd, self.commands[cmd][1])
      sys.exit(1)

    return self.commands[cmd][0](*args)   

  def helphelpcmd(self, *args):    
    print >> sys.stderr, "%s help for help!" %(sys.argv[0])
    sys.exit(1)

  def helpcmd(self, *args):
    '''Help cmd: help [<expression>]'''
    print "Spectra_T: Do stuff using the xml API of your Spectralogic T Series box."

  def logincmd(self, *args):
    '''Login command: login <username> [<password>]'''
    
    username = args[0]
    if len(args) > 1:
      password = args[1]
    else:
      password = None


    if self.login(username=username,password=password):
      print "%s: logged in as %s" %(sys.argv[0], username)
    else:
      print "%s: Failed to log in as %s" %(sys.argv[0], username)
      sys.exit(1)

  def logoutcmd(self, *args):
    '''Logout command.'''
    return self.logout()
 
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
    if not self.url:
      print "Need better error handling: cannot login w/o url"
      return False
    
    if not self.curl_session:
      self.curl_session_init()
    
    login_url = self.url + '/login.xml'
    postdata = urlencode(
      {
        'username': args['username'], 
        'password': args['password']
      }
    )
    
    # Set login url
    self.curl_session.setopt(self.curl_session.URL, login_url)
    self.curl_session.setopt(self.curl_session.POSTFIELDS, postdata)
    xml, xml_dump = self.getxmlresponse(self.curl_session) 

    status = xml.find('status')
    status_ok = status.text.strip()

    if not status_ok == 'OK':
      self.logged_in = False
      return False
    
    self.username = args['username']
    self.logged_in = True
    return True

  def drivelistcmd(self, *args):
    return self.drivelist()

  def drivelist(self, **args):
    if self.fake_xml_input:
      xml, xml_dump = self.fakexmlresponse(self.fake_xml_input)
    else:
      drivelist_url = self.url+"/driveList.xml"

      if not (self.crisp_cookie or self.logged_in):
        print "Blargh: login or somrthing"
        sys.exit(1)

      if not self.curl_session:
        self.curl_session_init()

      self.curl_session.setopt(pycurl.URL, drivelist_url)
      xml, xml_dump = self.getxmlresponse(self.curl_session)

    if 'xml' in self.dump:
      print xml_dump
      if 'exit' in self.dump:
        sys.exit(0)
    
    self.twodee_list(xml, self.output_format, self.output.split(","))

# Some generic functions down here. 
# http://stackoverflow.com/questions/1912434/how-do-i-parse-xml-in-python
  def getxmlresponse(self,cs):
    response = cStringIO.StringIO()
    cs.setopt(pycurl.WRITEFUNCTION, response.write)
    cs.perform()
    value = response.getvalue()
    response.close()
    # http://stackoverflow.com/questions/1912434/how-do-i-parse-xml-in-python
    return ET.fromstring(value), value

  def fakexmlresponse(self,cs):
    with open(cs, 'r') as myfile:
      data=myfile.read()
    return ET.fromstring(data), data

  # probably mega slow. :)
  def twodee_list(self,xml, fmt=None, tags=[]):
    output = []
    for onedee in xml:
      if not tags:
        tmp = onedee.findall("*")
        for tag in tmp:
          tags += [tag.tag]
      this=[]
      for tag in tags:
        this += [onedee.find(tag).text]
      output += [this]

    if not fmt:
      # Calculate column size.

      # First for header
      maxlen = [0]*len(tags)
      for i, maxl in enumerate(maxlen):
        ilen = len(tags[i])
        if ilen > maxl:
          maxlen[i] = ilen

      # The for data
      for line in output:
        for i, maxl in enumerate(maxlen):
          ilen = len(line[i])
          if ilen > maxl:
            maxlen[i] = ilen
    
      # The following stuff is less elegang than this: :(
      #   fmt = "\t".join(["%s"]*len(tags))
      sfmt = []
      for n in maxlen:
        sfmt += ["%%-%ds" %(n)]
      fmt = "\t".join(sfmt)
    
    try: 
      print fmt%tuple(tags)
      
      print "---"
      for line in output:
        print fmt%tuple(line)
      return True
    except TypeError:
      print >> sys.stderr, "Fix your formatting"
      return False


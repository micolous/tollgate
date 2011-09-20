#!/usr/bin/env python

from socket import SOL_IP
from warnings import warn
from os.path import join, dirname

try:
	# py3
	from urllib.parse import quote
except ImportError:
	# py2
	from urllib import quote

try:
	# py3
	from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
	# py2
	from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
	
try:
	from socket import IP_TRANSPARENT
except ImportError:
	# this isn't implemented in python yet, submitted a patch.
	# /usr/include/linux/in.h says this is 19.
	IP_TRANSPARENT = 19
	warn("Your version of Python doesn't support socket.IP_TRANSPARENT.  It could also be that you're running this on a non-Linux platform, which probably won't work.")

class TProxyRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		url = self.server.redirect % quote('http://' + self.headers['Host'] + self.path)
		self.send_response(302, 'Captive Portal Login Required')
		self.send_header('Content-Type', 'text/html')
		self.send_header('Location', url)
		self.send_header('Last-Modified', 'Thu, 01 Jan 1970 03:13:37 GMT')
		self.send_header('Expires', 'Thu, 01 Jan 1970 03:13:37 GMT')
		self.send_header('Pragma', 'no-cache')
		self.send_header('Cache-Control', 'no-cache')
		self.send_header('Connection', 'close')
		self.end_headers()
		
		page = """
<html>
  <head>
    <title>Captive Portal Logon Required</title>
    <meta http-equiv="refresh" content="0;URL=%(url)s">
  </head>

  <body>
    <h1>Captive Portal Logon Required</h1>
    <p>A captive portal logon is required to access the requested site.  <a href="%(url)s">Click here to login.</a></p>
  </body>
</html>""" % dict(url=url)
		
		# in py3, we need to do some encoding
		if str != bytes:
			page = bytes(page, 'UTF-8')
			
		self.wfile.write(page)
		
	do_HEAD = do_POST = do_GET

class TProxyServer:
	keep_running = True
	server_address = ('', 50080)
	mark = 1
	
	def run(self):
		self.httpd = HTTPServer(self.server_address, TProxyRequestHandler)
		self.httpd.server_version = 'tollgate'
		try:
			LANDING_URI = open(join(dirname(__file__),'tollgate_uri'), 'rb').read().strip()
		except IOError:
			raise IOError, 'Please create a file called "tollgate_uri" with the path to to tollgate\'s HTTPS site.'

		self.httpd.redirect = '%s/captive_landing/?u=%%s' % LANDING_URI
		self.httpd.socket.setsockopt(SOL_IP, IP_TRANSPARENT, self.mark)
		
		while self.keep_running:
			self.httpd.handle_request()
			
if __name__ == '__main__':
	# boot the httpd
	print("Booting httpd.")
	server = TProxyServer()
	server.run()


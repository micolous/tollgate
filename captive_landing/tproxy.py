#!/usr/bin/env python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urllib import quote
from socket import SOL_IP
try:
	from socket import IP_TRANSPARENT
except ImportError:
	# this isn't implemented in python yet
	# /usr/include/linux/in.h says this is 19.
	IP_TRANSPARENT = 19

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
		
		self.wfile.write("""
<html>
  <head>
    <title>Captive Portal Logon Required</title>
    <meta http-equiv="refresh" content="0;URL=%(url)s">
  </head>

  <body>
    <h1>Captive Portal Logon Required</h1>
    <p>A captive portal logon is required to access the requested site.  <a href="%(url)s">Click here to login.</a></p>
  </body>
</html>""" % dict(url=url))		
		
	do_HEAD = do_POST = do_GET

class TProxyServer:
	keep_running = True
	server_address = ('', 50080)
	mark = 2
	
	def run(self):
		self.httpd = HTTPServer(self.server_address, TProxyRequestHandler)
		self.httpd.server_version = 'tollgate'
		self.httpd.redirect = 'https://portal.onadelaide.blackhats.net.au/captive_landing/?u=%s'
		self.httpd.socket.setsockopt(SOL_IP, IP_TRANSPARENT, self.mark)
		
		while self.keep_running:
			self.httpd.handle_request()
			
if __name__ == '__main__':
	# boot the httpd
	server = TProxyServer()
	server.run()


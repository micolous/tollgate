#!/usr/bin/env python

from socket import SOL_IP
from warnings import warn
from os.path import join, dirname
from optparse import OptionParser

try:
	# py3
	from urllib.parse import quote
except ImportError:
	# py2
	from urllib import quote

try:
	# py3
	from http.server import HTTPServer, BaseHTTPRequestHandler
	from socketserver import ForkingMixIn
except ImportError:
	# py2
	from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
	from SocketServer import ForkingMixIn
	
try:
	from socket import IP_TRANSPARENT
except ImportError:
	# this isn't implemented in python yet, submitted a patch.
	# /usr/include/linux/in.h says this is 19.
	IP_TRANSPARENT = 19
	warn("Your version of Python doesn't support socket.IP_TRANSPARENT.  It could also be that you're running this on a non-Linux platform, which probably won't work.")

# http://stackoverflow.com/questions/10003866/http-server-hangs-while-accepting-packets
class ForkingHTTPServer(ForkingMixIn, HTTPServer):
	def finish_request(self, request, client_address):
		request.settimeout(30)
		# explicitly call HttpServer.finish_request
		HTTPServer.finish_request(self, request, client_address)


class TProxyRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		url = self.server.redirect % quote('http://' + self.headers['Host'] + self.path)
		self.send_response(511, 'Network Authentication Required')
		self.send_header('Content-Type', 'text/html')
		#self.send_header('Location', url)
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
    <!--
    
    Prevent certain popular Microsoft UAs from hiding our "error" page.
    
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    -->
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
		self.wfile.close()
		
	do_HEAD = do_POST = do_GET

class TProxyServer:
	keep_running = True
	
	def __init__(self, tollgate_uri, server_port, mark):
		self.server_address = ('', server_port)
		self.mark = mark
		self.tollgate_uri = tollgate_uri
		
	
	def run(self):
		self.httpd = ForkingHTTPServer(self.server_address, TProxyRequestHandler)
		self.httpd.server_version = 'tollgate'
		self.httpd.redirect = '%s/captive_landing/?u=%%s' % self.tollgate_uri
		self.httpd.socket.setsockopt(SOL_IP, IP_TRANSPARENT, self.mark)
		
		while self.keep_running:
			try:
				self.httpd.handle_request()
			except:
				# don't die when there's a pathetic error
				pass
			
def main_optparse():
	"Entrypoint for the tproxy handler, that uses optparse to parse commandline arguments."
	parser = OptionParser(usage="%prog [-D] -l 'https://tollgate.example.com'")
	parser.add_option('-D', '--daemon', action='store_true', dest='daemon', help='start as a daemon')
	parser.add_option('-l', '--tollgate-uri', dest='tollgate_uri', metavar='URI', help='root URI of tollgate frontend HTTPS server')
	parser.add_option('-P', '--pid', dest='pid_file', default='/var/run/tollgate-captivity.pid', help='Location to write the PID file.  Only has effect in daemon mode.  [default: %default]')
	parser.add_option('-p', '--port', dest='port', type='int', metavar='PORT', help='port of the tproxy service [default: %default]', default=50080)
	parser.add_option('-m', '--mark', dest='mark', type='int', metavar='MARK', help='TPROXY mark tag for this service [default: %default]', default=1)
	options, args = parser.parse_args()
	
	if not options.tollgate_uri:
		parser.error('A URI to the tollgate site is required.')
	
	if not options.port:
		parser.error('A port to listen on is required.')
	
	if options.port < 0 or options.port > 65535:
		parser.error('Port specified is invalid.')
	
	if not options.mark:
		parser.error('Mark tag is required.')
		
	if options.mark <= 0 or options.mark > 255:
		parser.error('Mark value is invalid.')
	
	if not options.pid_file and options.daemon:
		parser.error('No PID file specified and running in daemon mode!')
	
	server = TProxyServer(options.tollgate_uri, options.port, options.mark)
	
	if options.daemon:
		from daemon import daemonize
		daemonize(options.pid_file)
		
	server.run()

if __name__ == '__main__':
	main_optparse()

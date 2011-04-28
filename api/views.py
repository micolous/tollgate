#!/usr/bin/env python
"""tollgate frontend api views
Copyright 2008-2010 Michael Farrell <http://micolous.id.au/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.http import HttpResponse
from tollgate.frontend.models import *
from tollgate.api.models import *
from sys import exc_info
import cPickle
from datetime import datetime, timedelta
from time import mktime

try:
	# python 2.6
	import json
except:
	import simplejson as json

# Create a Dispatcher; this handles the calls and translates info to function maps
dispatcher = SimpleXMLRPCDispatcher(allow_none=False, encoding=None) # Python 2.5

def xmlrpc_handler(request):
	"""
	the actual handler:
	if you setup your urls.py properly, all calls to the xml-rpc service
	should be routed through here.
	If post data is defined, it assumes it's XML-RPC and tries to process as such
	Empty post assumes you're viewing from a browser and tells you about the service.
	"""

	response = HttpResponse()
	if len(request.POST):
		response.write(dispatcher._marshaled_dispatch(request.raw_post_data))
	else:
		response.write("<b>This is an XML-RPC Service.</b><br>")
		response.write("You need to invoke it using an XML-RPC Client!<br>")
		response.write("The following methods are available:<ul>")
		methods = dispatcher.system_listMethods()

		for method in methods:
			# right now, my version of SimpleXMLRPCDispatcher always
			# returns "signatures not supported"... :(
			# but, in an ideal world it will tell users what args are expected
			sig = dispatcher.system_methodSignature(method)

			# this just reads your docblock, so fill it in!
			help = dispatcher.system_methodHelp(method)

			#response.write("<li><b>%s</b>: [%s] %s" % (method, sig, help))
			response.write("<li><b>%s</b>: <pre>\n%s</pre></li>" % (method, help))

		response.write("</ul>")
		response.write('')

	response['Content-length'] = str(len(response.content))
	return response


def whatis_ip(ip):
	"""Returns the identity of the computer associated with that IPv4 address.
	Takes one argument, the IP of the computer to look up, in dotted-quad format (XXX.XXX.XXX.XXX).
	Returns False if the host is unknown or offline.
	Raises an error if input is invalid."""
	
	if not is_valid_ip(ip):
		raise ValueError, 'Invalid IPv4 address specified'
	
	# lookup the IP address
	try:
		h = NetworkHost.objects.filter(ip_address__exact=ip, online__exact=True)[0]
		return marshal_NetworkHost(h)
	except:
		return False

def whoami():
	"""Returns the identity of the user who is currently logged in (via cookies),
	or the one who is logged in this computer (via mac address).
	Returns False if the user is unknown."""
	
	request = steal_request()
	if request.user.is_authenticated():
		return marshal_UserProfile(request.user.get_profile(), hide_name=False)

	profile = None	
	ip = request.META['REMOTE_ADDR']
	mac = get_mac_address(ip)
	if mac == None:
		return False
		
	try:
		h = NetworkHost.objects.get(mac_address__iexact=mac)
		if h.user_profile == None:
			return False # no user association
		
		return marshal_UserProfile(h.user_profile, hide_name=False)
	except:
		return False
	
def whois_ip(ip):
	"""Returns the identity of the user associated with a computer on an IPv4 address.
	Takes one argument, the IP of the computer to look up, in dotted-quad format (XXX.XXX.XXX.XXX).
	Returns False if the user is unknown or offline.
	Raises an error if the input is invalid."""

	if not is_valid_ip(ip):
		raise ValueError, 'Invalid IPv4 address specified'
	
	# lookup the IP address
	try:
		h = NetworkHost.objects.filter(ip_address__exact=ip, online__exact=True)[0]
		
		if h.user_profile == None:
			return False # no user association
		
		return marshal_UserProfile(h.user_profile)
	except:
		return False
		
def ping():
	"""Always returns True."""
	return True
	
def usage():
	"""Returns the usage data for the person logged in (via cookies), or the person
	logged in to this computer (by IP).
	Returns a dict of Usage, or False if there are problems."""
	
	request = steal_request()
	if request.user.is_authenticated():
		try:
			return marshal_Usage(get_attendance_currentevent(request.user.get_profile()))
		except:
			# fallback to ip method
			pass
	
	ip = request.META['REMOTE_ADDR']
	mac = get_mac_address(ip)
	if mac == None:
		return False
		
	try:
		h = NetworkHost.objects.get(mac_address__iexact=mac)
		if h.user_profile == None:
			return False # no user association
		
		# now get the event information
		attendance = get_attendance_currentevent(h.user_profile)
		
		return marshal_Usage(attendance)
	except:
		return False
		
def usage_history():
	"""Returns a 2-list of usage history information attached to the account for
	the last 36 hours.  Returns False if the user is not logged in.
	
	This is determined first by cookies, then by mac address if that fails.
	
	It is formatted as such:
		[
			[datetime, usageBytes],
			[datetime, usageBytes],
			...
		]
	"""
	request = steal_request()
	attendance = None
	if request.user.is_authenticated():
		try:
			attendance = get_attendance_currentevent(request.user.get_profile())
		except:
			# fallback
			pass
			
	if attendance == None:
		# try to get by other means
		ip = request.META['REMOTE_ADDR']
		mac = get_mac_address(ip)
		if mac == None:
			return False
		
		try:
			h = NetworkHost.objects.get(mac_address__iexact=mac)
			if h.user_profile == None:
				return False # no user association
		
			# now get the event information
			attendance = get_attendance_currentevent(h.user_profile)
		except:
			# couldn't get attendance object
			return False
	
	try:
		# try to get usage
		usage_points = NetworkUsageDataPoint.objects.filter(event_attendance=attendance, when__gte=datetime.now()-timedelta(hours=36))
		o = []
		for point in usage_points:
			o.append(marshal_NetworkUsageDataPoint(point))
		
		return o
	except:
		return False
	
	
def r_disown_mac(mac, authhash):
	"""Attempts to remotely log out a specific computer by MAC.  Returns True on successful call, False otherwise.
	This function requires that you send an authhash, which is an SHA512 hashed string (in BASE16 representation) in the following format:
	  ${RESTRICTED_CALLS_KEY}:${UNIX_MINUTE}:${MAC}
	The UNIX_MINUTE parameter must be in plus or minus 1 minute of server time.  It is =floor(unix_timestamp/60).
	MAC Address should be in base-16 encoded format.
	"""
	# validate the MAC
	if not is_valid_mac(mac):
		return (False, 'invalmac')
	
	# validate the authhash
	if not verify_authhash(mac, authhash):
		return (False,'invalauthhash')
	
	# now see if the computer exists
	try:
		h = NetworkHost.objects.get(mac_address__iexact=mac)
		
		if h.user_profile != None:
			profile = h.user_profile
			NetworkHostOwnerChangeEvent.objects.create(old_owner=profile, new_owner=None, network_host=h)
			h.user_profile = None
	                h.save()
	                
			# resync internet for user
        	        sync_user_connections(profile)
                
        	        # now we're done
	                return True
		else:
			# already disowned, we'll say it was ok anyway
			return True
	except:
		# host not found
		return False

def coffee_ip(ip):
	"""Returns a bool indicating whether the user has paid for unlimited coffee or not and is allowed to use the coffee request system.
    Returns False if the IP address is not assigned to a user, the user has been banned from using the coffee request system, or that user hasn't paid for unlimited coffee.
    Returns True if the user has paid for unlimited coffee and is allowed to use the coffee request system. Also implies the user's coffee gland was lost in a tragic accident as a child.
    There is currently no API call to indicate whether the user has paid for four cooked meals."""

	if not is_valid_ip(ip):
		raise ValueError, 'Invalid IPv4 address specified'
	
	# lookup the IP address
	try:
		h = NetworkHost.objects.filter(ip_address__exact=ip, online__exact=True)[0]
		attendance = get_attendance_currentevent(h.user_profile)
		return attendance.coffee == 1
	except:
		return False
	
		
registrations = {
	'whatis_ip': whatis_ip,
	'whois_ip': whois_ip,
	'whoami': whoami,
	'ping': ping,
	'usage': usage,
	'usage_history': usage_history,
	'coffee_ip': coffee_ip,
	'r_disown_mac': r_disown_mac,
}

for k in registrations:
	dispatcher.register_function(registrations[k], k)

# converts a datetime object to an integer with seconds since the unix epoch
class JSONDateTimeEncoder(json.JSONEncoder):
	def default(self, o=datetime):
		return mktime(o.timetuple())
	
def httpget_handler(request, output_format, method):
	# this handles requests through our "simple" api handler.
	# this outputs in a few formats.
	output_format = output_format.lower()
	supported_formats = ['json', 'pickle', 'csv', 'python']
	
	if output_format not in supported_formats:
		raise Exception, "Unsupported output format"
	
	if method not in registrations.keys():
		raise Exception, "Unknown method"
	
	# argument names and values mustn't be unicode
	args = {}
	for k in request.GET.keys():
		args[str(k)] = str(request.GET[k])
		
	output = registrations[method](**args)
		
	response = HttpResponse()
	if output_format == 'json':
		response['Content-Type'] = 'text/javascript'
		json.dump(output, response, cls=JSONDateTimeEncoder)
	elif output_format == 'pickle':
		response['Content-Type'] = 'text/plain'
		cPickle.dump(output, response)
	elif output_format == 'python':
		response['Content-Type'] = 'text/plain'
		response.write(repr(output))
	elif output_format == 'csv':
		response['Content-Type'] = 'text/plain'
		if type(output) is list or type(output) is tuple:
			for l in output:
				if type(l) is list or type(l) is tuple:
					for c in l:
						response.write("%s, " % c)
					response.write("\n")
				else:
					response.write(l)
		elif type(output) is dict:
			for k in output:
				response.write("%s, %s\n" % (k, output[k]))
		else:
			response.write(output)
		
		
	
	return response
	
	
#def httpget_handler(request, method):
#	"""HTTP GET API.  This needs to be after all the methods as we use a rather
#	hackish way of dealing with stuff so we don't have to repeat ourselves."""
#	if not registrations.has_key(method):
#		return 'ERR:InvalidMethod:That method does not exist.'
#	
#	m = registrations[method]
#	try:
#		v = m(**kwargs=request.REQUEST)
#	except Exception:
#		e = exc_info()
#		return 'ERR:%s:%s' % )e[0], e[1])
#	
#	return 'OK' # need to output the data in a crossplatform and easy to deal with way.


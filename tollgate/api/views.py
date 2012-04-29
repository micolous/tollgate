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
from djangorestframework.views import ModelView
from djangorestframework.mixins import ReadModelMixin
from djangorestframework import status
from djangorestframework.response import ErrorResponse

try:
	# python 2.6
	import json
except:
	import simplejson as json


class ReadOnlyInstanceModelView(ReadModelMixin, ModelView):
	"""
	A read-only InstanceModelView, that only allows GET requests.
	"""
	_suffix="ReadOnlyInstance"

class MyUserProfileModelView(ModelView):
	"""
	Reads the current NetworkHost record for this user.
	"""
	
	def get(self, request, *args, **kwargs):
		model = self.resource.model
		
		try:
			if request.user.is_authenticated():
				# take the user data from the authentication.
				return request.user.get_profile()
			
			# look up based on the NetworkHost of this request
			profile = None
			
			ip = request.META['REMOTE_ADDR']
			mac = get_mac_address(ip)
			if mac == None:
				# unknown MAC
				raise ErrorResponse(status.HTTP_404_NOT_FOUND)

			try:
				h = NetworkHost.objects.get(mac_address__iexact=mac)
				if h.user_profile == None:
					# no user associated with this host
					raise ErrorResponse(status.HTTP_404_NOT_FOUND)

				return h.user_profile
			except:
				# networkhost record does not exist
				raise ErrorResponse(status.HTTP_404_NOT_FOUND)
		except:
			pass
			
		# other error
		raise ErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR)
	
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


registrations = {
	'usage': usage,
	'usage_history': usage_history,
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


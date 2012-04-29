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
from datetime import datetime, timedelta
from time import mktime
from djangorestframework.views import ModelView
from djangorestframework.mixins import ReadModelMixin
from djangorestframework import status
from djangorestframework.response import ErrorResponse



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


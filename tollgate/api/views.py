#!/usr/bin/env python
"""tollgate frontend api views
Copyright 2008-2012 Michael Farrell <http://micolous.id.au/>

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
import tollgate
from tollgate.frontend.models import *
from datetime import datetime, timedelta
from djangorestframework.views import ModelView, View
from djangorestframework.mixins import ReadModelMixin
from djangorestframework import status
from djangorestframework.response import ErrorResponse
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _


class ReadOnlyInstanceModelView(ReadModelMixin, ModelView):
	"""
	A read-only InstanceModelView, that only allows GET requests.
	"""
	_suffix = "ReadOnlyInstance"


class NetworkHostRootView(View):
	"""
	Root of NetworkHost API.
	Allows the client to get a complete list of all online NetworkHosts.
	"""
	
	def get(self, request):
		"""
		Returns a list of all NetworkHost urls.
		"""
		hosts = NetworkHost.objects.filter(online=True).only('ip_address')
		
		return [reverse(
			'api_whatis_ip',
			kwargs={'ip_address': h.ip_address}
		) for h in hosts]


class UserProfileRootView(View):
	"""
	Root of User API.
	Allows the client to information about users with online NetworkHosts.
	"""
	
	def get(self, request):
		"""
		Returns a list of all NetworkHost urls.
		"""
		hosts = NetworkHost.objects.filter(online=True).only('ip_address')
		
		return dict(
			me=reverse('api_whoami'),
			all_users=[reverse(
				'api_whois_ip',
				kwargs={'networkhost__ip_address': h.ip_address}
			) for h in hosts]
		)


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


class MyEventAttendanceModelView(MyUserProfileModelView):
	"""
	Reads the current EventAttendance for the user.
	"""
	def get(self, request, *args, **kwargs):
		# gets the user_profile associated with the request.
		user_profile = super(MyEventAttendanceModelView, self).get(
			request,
			*args,
			**kwargs
		)
		
		# now look up their attendance.
		try:
			attendance = get_attendance_currentevent(user_profile)
		except:
			# there is no attendance currently for the user.
			raise ErrorResponse(status.HTTP_404_NOT_FOUND)
		
		# now return the attendance.
		return attendance


class MyNetworkUsageDataPointsView(MyEventAttendanceModelView):
	"""
	Reads the NetworkUsageDataPoints associated with the user's attendance at
	the current event.
	"""
	def get(self, request, *args, **kwargs):
		# gets the attendance associated with the request.
		attendance = super(MyNetworkUsageDataPointsView, self).get(
			request,
			*args,
			**kwargs
		)
		
		# now lookup their usages in the last 36 hours
		return attendance.networkusagedatapoint_set.filter(
			when__gte=utcnow() - timedelta(hours=36)
		).order_by('when')


class TollgateAPIView(View):
	"""
	This is the API for tollgate.
	"""
	def get(self, request):
		return dict(
			tollgate_api_version=1,
			tollgate_version=tollgate.__version__,
			methods=[
				dict(
					name='networkhost_root',
					description=_('Get information about a NetworkHost'),
					url=reverse('api_networkhost_root')
				),
				
				dict(
					name='user_root',
					description=_('Get owner and user information'),
					url=reverse('api_user_root')
				),
				
				dict(
					name='usage', 
					description=_('Get your usage information'),
					url=reverse('api_usage')
				),
				
				dict(
					name='usage_history',
					description=_('Get your usage history'),
					url=reverse('api_usage_history')
				),
			]
		)

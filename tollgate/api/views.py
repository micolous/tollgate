#!/usr/bin/env python
"""tollgate frontend api views
Copyright 2008-2013 Michael Farrell <http://micolous.id.au/>

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
from __future__ import absolute_import
import tollgate
from ..frontend.models import *
from .resources import *
from datetime import datetime, timedelta
from rest_framework import generics, mixins, views, status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.utils.translation import ugettext as _


def get_userprofile_for_request(request):
	if request.user.is_authenticated():
		# take the user data from the authentication.
		return request.user.get_profile()
	
	# look up based on the NetworkHost of this request
	profile = None
	
	ip = request.META['REMOTE_ADDR']
	mac = get_mac_address(ip)
	if mac == None:
		# unknown MAC
		return None

	try:
		h = NetworkHost.objects.get(mac_address__iexact=mac)
		if h.user_profile == None:
			# no user associated with this host
			return None

		return h.user_profile
	except NetworkHost.DoesNotExist:
		# networkhost record does not exist
		return None


class ReadOnlyInstanceModelView(mixins.ListModelMixin, generics.GenericAPIView):
	"""
	A read-only InstanceModelView, that only allows GET requests.
	"""
	_suffix = "ReadOnlyInstance"
	serializer_class = None
	queryset = None
	
	def get(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)



class NetworkHostRootView(views.APIView):
	"""
	Root of NetworkHost API.
	Allows the client to get a complete list of all online NetworkHosts.
	"""
	
	def get(self, request):
		"""
		Returns a list of all NetworkHost urls.
		"""
		hosts = NetworkHost.objects.filter(online=True).only('ip_address')
		
		return Response([
			reverse(
				'api_whatis_ip',
				kwargs={'ip_address': h.ip_address}
			) for h in hosts
		])


class UserProfileRootView(views.APIView):
	"""
	Root of User API.
	Allows the client to information about users with online NetworkHosts.
	"""
	
	def get(self, request):
		"""
		Returns a list of all NetworkHost urls.
		"""
		hosts = NetworkHost.objects.filter(online=True).only('ip_address')
		
		return Response(dict(
			me=reverse('api_whoami'),
			all_users=[reverse(
				'api_whois_ip',
				kwargs={'networkhost__ip_address': h.ip_address}
			) for h in hosts]
		))


class MyUserProfileModelView(views.APIView):
	"""
	Reads the current NetworkHost record for this user.
	"""
	
	def get(self, request, *args, **kwargs):
		#model = self.resource.model
		
		profile = get_userprofile_for_request(request)
		
		if profile is None:
			return Response(status=status.HTTP_404_NOT_FOUND)
		else:
			return Response(PermissiveUserProfileResource(request.user.get_profile()).data)


class MyEventAttendanceModelView(views.APIView):
	"""
	Reads the current EventAttendance for the user.
	"""
	def get(self, request, *args, **kwargs):
		# gets the user_profile associated with the request.
		user_profile = get_userprofile_for_request(request)
		attendance = None
		if user_profile is not None:
			# now look up their attendance.
			try:
				attendance = get_attendance_currentevent(user_profile)
			except:
				# there is no attendance currently for the user.
				pass
		
		if attendance is not None:
			return Response(EventAttendanceResource(attendance).data)

		return Response(status=status.HTTP_404_NOT_FOUND)


class MyNetworkUsageDataPointsView(views.APIView):
	"""
	Reads the NetworkUsageDataPoints associated with the user's attendance at
	the current event.
	"""
	def get(self, request, *args, **kwargs):
		# gets the user_profile associated with the request.
		user_profile = get_userprofile_for_request(request)
		attendance = None
		if user_profile is not None:
			# now look up their attendance.
			try:
				attendance = get_attendance_currentevent(user_profile)
			except:
				# there is no attendance currently for the user.
				pass
		
		if attendance is not None:
			return Response(NetworkUsageDataPointResource(
				attendance.networkusagedatapoint_set.filter(
					when__gte=utcnow() - timedelta(hours=36)
				)		
			).data)

		return Response(status=status.HTTP_404_NOT_FOUND)


class TollgateAPIView(views.APIView):
	"""
	This is the API for tollgate.
	"""
	def get(self, request):
		return Response(dict(
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
		))


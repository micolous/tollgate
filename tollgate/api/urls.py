"""tollgate api urls
Copyright 2008-2012 Michael Farrell

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

from django.conf.urls.defaults import *
from django.conf import settings
#from tollgate.frontend.forms import *
from tollgate.api.resources import NetworkHostResource, PermissiveUserProfileResource, UserProfileResource, EventAttendanceResource, NetworkUsageDataPointResource
from tollgate.api.views import ReadOnlyInstanceModelView, MyUserProfileModelView, MyEventAttendanceModelView, MyNetworkUsageDataPointsView


urlpatterns = patterns('tollgate.api.views',

	# Gets information about a network host by IP.
	# Equivalent to the old whatis_ip() API call.
	url(
		r'networkhost/by-ip/(?P<ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$',
		ReadOnlyInstanceModelView.as_view(resource=NetworkHostResource),
		dict(online=True),
		name='whatis_ip'
	),
	
	# Gets information about a user by IP.
	# Equivalent to the old whois_ip() API call.
	url(
		u'user/by-ip/(?P<networkhost__ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$',
		ReadOnlyInstanceModelView.as_view(resource=UserProfileResource),
		dict(networkhost__online=True),
		name='whois_ip'
	),
	
	# Gets information about the current user.
	# Equivalent to the old whoami() API call.
	url(
		u'user/me/$',
		MyUserProfileModelView.as_view(resource=PermissiveUserProfileResource),
		name='whoami'
	),
	
	# Gets information about the user's quota usage.
	# Equivalent to the old usage() API call.
	url(
		u'attendance/me/$',
		MyEventAttendanceModelView.as_view(resource=EventAttendanceResource),
		name='usage'
	),
	
	# Gets a list of usage data points for the user in the current event.
	# Equivalent to the old usage_history() API call.
	url(
		u'attendance/me/usage/$',
		MyNetworkUsageDataPointsView.as_view(resource=NetworkUsageDataPointResource),
		name='usage_history'
	),
)

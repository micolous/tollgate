"""tollgate api urls
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

from django.conf.urls.defaults import *
from django.conf import settings
#from tollgate.frontend.forms import *
from tollgate.api.resources import *
from tollgate.api.views import *


urlpatterns = patterns('tollgate.api.views',
	# Gets information about a network host by IP.
	# Equivalent to the old whatis_ip() API call.
	url(
		r'^networkhost/by-ip/(?P<ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/$',
		ReadOnlyInstanceModelView.as_view(
			serializer_class=NetworkHostResource,
			queryset=NetworkHost.objects.filter(online=True)
		),
		name='api_whatis_ip'
	),
	
	url(
		r'^networkhost/$',
		NetworkHostRootView.as_view(),
		name='api_networkhost_root'
	),
	
	url(
		r'^user/$',
		UserProfileRootView.as_view(),
		name='api_user_root'
	),
	
	# Gets information about a user by IP.
	# Equivalent to the old whois_ip() API call.
	url(
		r'^user/by-ip/(?P<networkhost__ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}' +\
		r'\.\d{1,3})/$',
		ReadOnlyInstanceModelView.as_view(
			serializer_class=UserProfileResource,
			queryset=UserProfile.objects.filter(user__hosts__online=True)
		),
		name='api_whois_ip'
	),
	
	# Gets information about the current user.
	# Equivalent to the old whoami() API call.
	url(
		r'^user/me/$',
		MyUserProfileModelView.as_view(),
		name='api_whoami'
	),
	
	# Gets information about the user's quota usage.
	# Equivalent to the old usage() API call.
	url(
		r'^attendance/me/$',
		MyEventAttendanceModelView.as_view(),
		name='api_usage'
	),
	
	# Gets a list of usage data points for the user in the current event.
	# Equivalent to the old usage_history() API call.
	url(
		r'^attendance/me/usage/$',
		MyNetworkUsageDataPointsView.as_view(),
		name='api_usage_history'
	),
	
	url(
		r'^$',
		TollgateAPIView.as_view(),
		name='api_index'
	),
)

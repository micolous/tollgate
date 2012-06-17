"""tollgate api resources
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
from djangorestframework.resources import ModelResource
from tollgate.frontend.models import \
	NetworkHost, UserProfile, EventAttendance, NetworkUsageDataPoint
from django.core.urlresolvers import reverse


class NetworkHostResource(ModelResource):
	model = NetworkHost
	fields = (
		'mac_address',
		'ip_address',
		'first_connection',
		'online',
		'vendor',
		'is_console'
	)
	ordering = ('mac_address')


class PermissiveUserProfileResource(ModelResource):
	"""
	Permissive version of UserProfileResource, which provides the user's real
	name.
	"""
	model = UserProfile
	fields = ('internet_on', 'username', 'user_id', 'first_name', 'last_name')
	

class UserProfileResource(ModelResource):
	"""
	Restricted UserProfile resource, which doesn't provide the user's real
	name.
	"""
	model = UserProfile
	fields = ('internet_on', 'username', 'user_id')


class EventAttendanceResource(ModelResource):
	"""
	Event attendance object.
	"""
	model = EventAttendance
	fields = (
		'quota_amount',
		'reset_count',
		'quota_unmetered',
		'quota_used',
		'quota_remaining'
	)


class NetworkUsageDataPointResource(ModelResource):
	"""
	NetworkUsageDataPoint object.
	"""
	model = NetworkUsageDataPoint
	fields = ('when', 'bytes')
	
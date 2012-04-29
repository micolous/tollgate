from djangorestframework.resources import ModelResource
from tollgate.frontend.models import NetworkHost, UserProfile, EventAttendance, NetworkUsageDataPoint

class NetworkHostResource(ModelResource):
	model = NetworkHost
	fields = ('mac_address', 'ip_address', 'first_connection', 'online', 'vendor', 'is_console')
	ordering = ('mac_address')

class PermissiveUserProfileResource(ModelResource):
	"""
	Permissive version of UserProfileResource, which provides the user's real name.
	"""
	model = UserProfile
	fields = ('internet_on', 'username', 'user_id', 'first_name', 'last_name')

class UserProfileResource(ModelResource):
	"""
	Restricted UserProfile resource, which doesn't provide the user's real name.
	"""
	model = UserProfile
	fields = ('internet_on', 'username', 'user_id')
	
class EventAttendanceResource(ModelResource):
	"""
	Event attendance object.
	"""
	model = EventAttendance
	fields = ('quota_amount', 'reset_count', 'quota_unmetered', 'quota_used', 'quota_remaining')

class NetworkUsageDataPointResource(ModelResource):
	"""
	NetworkUsageDataPoint object.
	"""
	model = NetworkUsageDataPoint
	fields = ('when', 'bytes')
	
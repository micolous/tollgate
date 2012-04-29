from djangorestframework.resources import ModelResource
from tollgate.frontend.models import NetworkHost, UserProfile


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

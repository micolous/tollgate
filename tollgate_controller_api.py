#!/usr/bin/python
"""Tollgate Controller API
Copyright 2008-2011 Michael Farrell <http://micolous.id.au/>

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
from pickle import loads
from django.conf import settings
import warnings

try:
	import dbus
except ImportError:
	warnings.warn("The Python DBUS module is unavailable.  We cannot connect to the backend.", UserWarning)
	dbus = None

DBUS_INTERFACE = 'au.id.micolous.TollgateBackendInterface'
DBUS_SERVICE = 'au.id.micolous.TollgateBackendService'
DBUS_PATH = '/TollgateBackendAPI'

def convert_mac(i):
	return "%s:%s:%s:%s:%s:%s" % (i[0:2], i[2:4], i[4:6], i[6:8], i[8:10], i[10:12])

class NotAConsoleException(Exception): pass

class TollgateController:
	def __init__(self):
		bus = dbus.SystemBus()
		remote_object = bus.get_object(DBUS_SERVICE, DBUS_PATH)
		self.__interface = dbus.Interface(remote_object, DBUS_INTERFACE)

	def connect(self, user_id, mac_address, ip):
		user_id = str(user_id)
		self.__interface.create_user(user_id)
		self.__interface.add_host(user_id, convert_mac(mac_address), ip)

	def disconnect(self, user_id, mac_address, ip):
		self.__interface.del_host(str(user_id), convert_mac(mac_address), ip)

	def flush(self, user_id):
		self.__interface.flush_hosts(str(user_id))

	def get_quota(self, user_id):
		result, remaining = self.__interface.get_quota(str(user_id))
		if result == False:
			# there was an error getting it
			return None
		return remaining

	def enable(self, user_id, quota=None):
		user_id = str(user_id)
		self.__interface.create_user(user_id)
		if quota != None:
			self.__interface.enable_user(user_id, quota)
		else:
			self.__interface.enable_user_unmetered(user_id)

	def disable(self, user_id):
		self.__interface.disable_user(str(user_id))

	def ip4pf_flush(self):
		self.__interface.ip4pf_flush()

	def ip4pf_add(self, ip, protocol, port, external_port):
		self.__interface.ip4pf_add(ip, protocol, port, external_port)


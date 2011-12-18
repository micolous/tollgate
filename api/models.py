#!/usr/bin/env python
"""tollgate frontend api models
Copyright 2008-2010 Michael Farrell <http://micolous.id.au/>
$Id: py 109 2010-11-10 12:23:25Z michael $

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

from django.db.models import *
from django.conf import settings

from sys import exc_info
from hashlib import sha512
from math import floor
from time import time

# don't really have models here, just validation for stuff.

def is_valid_ip(ip):
	"""Validate an IP address input."""
	a = ip.split('.')

	if len(a) != 4:
		return False

	for x in a:
		try:
			y = int(x)
			if y < 0 or y > 255:
				return False
		except:
			return False

	return True

def is_valid_mac(mac):
	mac = mac.upper()

	if len(mac) != 12:
		return False

	for x in mac:
		y = ord(x)
		if (y < ord('0') or y > ord('9')) and (y < ord('A') or y > ord('F')):
			return False

	return True

def steal_local(n):
	"""Steals a local variable from higher up in the call stack.  This will
	continually work it's way backwards, until it reaches the main, and return the
	first result it finds.  Throws an Exception if the variable cannot be found.

	Yes, this function is evil, but unfortunately this is required to work around
	a limitation in Django's handling of XMLRPC."""
	try:
		raise Exception
	except:
		tb = exc_info()[2].tb_frame
		while tb != None:
			if tb.f_locals.has_key(n):
				return tb.f_locals[n]
			tb = tb.f_back
		# we have a problem
		raise Exception, "That doesn't exist."

def steal_request():
	return steal_local('request')

def calculate_authhash(secret, unix_minute, data):
	if secret == '' or secret == None:
		raise Exception("RESTRICTED_CALLS_KEY was not set!")
	s = "%s:%s:%s" % (secret, unix_minute, data)
	return sha512(s).hexdigest()

def verify_authhash(data, authhash):
	now = long(floor(time()/60.0))
	for x in range(now-1, now+2):
		real_ah = calculate_authhash(settings.RESTRICTED_CALLS_KEY, x, data)
		if real_ah == authhash:
			return True
	return False


def marshal_NetworkHost(nh):
	"""Marshalls a NetworkHost into a simple dict for xmlrpc calls"""
	if nh.online:
		ip = nh.ip_address
	else:
		ip = False
	return dict(
		mac_address = nh.mac_address,
		ip_address = ip,
		computer_name = nh.computer_name,
		first_connection = nh.first_connection,
		online = nh.online == 1,
		type = nh.get_console_type(),
		is_console = nh.is_console()
	)

def marshal_UserProfile(p, hide_name=True):
	o = dict(
		internet_on = p.internet_on == 1,
		username = p.user.username,
		forum_uid = p.user.id,
		first_name = p.user.first_name,
		last_name = p.user.last_name
	)


	if hide_name:
		o['first_name'] = ''
		o['last_name'] = ''

	return o

def marshal_Usage(a):
	o = dict(
		unmetered = a.is_unmetered() == 1,
		used = str(a.quota_used),
		remaining = False,
		total = False,
		resets = False,
		available = True
	)

	if not a.is_unmetered():
		o['remaining'] = str(a.quota_remaining())
		o['total'] = str(a.quota_amount)
		o['resets'] = a.reset_count()
		o['available'] = a.is_quota_available()
	return o

def marshal_NetworkUsageDataPoint(a):
	return (a.when, str(a.bytes))


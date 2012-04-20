#!/usr/bin/env python
"""
tollgate frontend commonly-platform-specific-code
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
from django.conf import settings
try:
	from iplib import CIDR
except ImportError:
	CIDR = None
	import IPy
	
if CIDR:
	LAN_CIDR = CIDR(settings.LAN_SUBNET)
else:
	LAN_CIDR = IPy.IP(settings.LAN_SUBNET)

def in_lan_subnet(ip):
	if CIDR:
		return LAN_CIDR.is_valid_ip(ip)
	else:
		return IPy.IP(ip) in LAN_CIDR

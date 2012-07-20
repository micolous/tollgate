#!/usr/bin/env python
"""
tollgate frontend platform-specific code for Linux
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

from tollgate.frontend.platform.common import *


def get_ip_address(mac):
	fh = open('/proc/net/arp', 'r')
	# skip header
	fh.readline()
	d = fh.readlines()
	fh.close()

	# try active entries first
	for l in d:
		a = l.split()
		if a[3] == mac and a[5] == settings.LAN_IFACE and in_lan_subnet(a[0]) \
			and a[2] == "0x2":
			return a[0]

	# try expired ones.
	for l in d:
		a = l.split()
		if a[3] == mac and a[5] == settings.LAN_IFACE and in_lan_subnet(a[0]):
			return a[0]
	return None


def get_arp_cache():
	fh = open('/proc/net/arp', 'r')
	# skip header
	fh.readline()
	d = fh.readlines()
	fh.close()

	# now generate pretty table
	o = {}

	# expired entries first, so they get overwritten by active ones.
	for l in d:
		a = l.split()
		if a[3] != '00:00:00:00:00:00' and a[5] == settings.LAN_IFACE and \
			in_lan_subnet(a[0]) and a[2] == "0x0":
			mac = a[3].replace(":", "")

			o[a[0]] = mac

	# active entries overwrite expired ones.
	for l in d:
		a = l.split()
		if a[3] != '00:00:00:00:00:00' and a[5] == settings.LAN_IFACE and \
			in_lan_subnet(a[0]) and a[2] == "0x2":
			mac = a[3].replace(":", "")
			o[a[0]] = mac
	return o


def get_mac_address(ip):
	fh = open('/proc/net/arp', 'r')
	# skip header
	fh.readline()
	d = fh.readlines()
	fh.close()

	# don't return anything if this is not part of the LAN subnet.
	if not in_lan_subnet(ip):
		return None

	# try active entries first
	for l in d:
		a = l.split()
		if a[0] == ip and a[3] != '00:00:00:00:00:00' and \
			a[5] == settings.LAN_IFACE and a[2] == "0x2":
			mac = a[3].replace(':', '')
			return mac

	# now expired ones.
	for l in d:
		a = l.split()
		if a[0] == ip and a[3] != '00:00:00:00:00:00' and \
			a[5] == settings.LAN_IFACE:
			mac = a[3].replace(':', '')
			return mac

	return None

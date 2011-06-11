#!/usr/bin/python
"""tollgate backend service
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
from configparser_plus import ConfigParserPlus
from sys import argv, exit
import BaseHTTPServer, iptables

# constants
# default settings doesn't quite work yet.
DEFAULT_SETTINGS = {
	'tollgate': {
		'reject_mode': 'icmp-net-unreachable',
		'reject_tcp_rst': True,
		'iptables': '/sbin/iptables',
		'ip6tables': '/sbin/ip6tables',
		'internal_iface': 'eth1',
		'external_iface': 'eth0',
		'captive_rule': 'p2_captive',
		'allowed_rule': 'p2_allowed',
		'unmetered_rule': 'p2_unmetered',
		'blacklist_rule': 'p2_blacklist',
		'ip4pf_rule': 'p2_ip4pf',
		'user_rule_prefix': 'p2u_',
		'limit_rule_prefix': 'p2l_',
		'debug': True,
		'ipv6': False,
		'reject6_mode': 'icmp6-port-unreachable'
	},
	'captive': {
		'enable': True,
		'port': 81
	}

}
SETTINGS_FILE = 'tollgate.ini'

def parse_hostlist(hostlist, action):
	for x, v in hostlist:
		if type(v) is not dict:
			a = v.split(':')
			host = a[0]
			if len(a) == 1:
				port = None
				proto = None
			else:
				a2 = a[1].split('/')
				if a2[0] != "*":
					port = a2[0]
				else:
					port = None

				if len(a2) == 2:
					proto = a2[1]
				else:
					proto = None

			if proto == None and port != None:
				action(host, 'tcp', port)
				action(host, 'udp', port)
			else:
				action(host, proto, port)

# begin!
config = ConfigParserPlus(DEFAULT_SETTINGS)

if len(argv) >= 2:
	SETTINGS_FILE = argv[1]

print "Loading configuration: %s" % SETTINGS_FILE
config.read(SETTINGS_FILE)

print "Setting configuration values..."
iptables.IPTABLES = config.get('tollgate', 'iptables')
iptables.INTERN_IFACE = config.get('tollgate', 'internal_iface')
iptables.EXTERN_IFACE = config.get('tollgate', 'external_iface')
iptables.CAPTIVE_RULE = config.get('tollgate', 'captive_rule')
iptables.ALLOWED_RULE = config.get('tollgate', 'allowed_rule')
iptables.UNMETERED_RULE = config.get('tollgate', 'unmetered_rule')
iptables.BLACKLIST_RULE = config.get('tollgate', 'blacklist_rule')
iptables.IP4PF_RULE = config.get('tollgate', 'ip4pf_rule')
iptables.USER_RULE_PREFIX = config.get('tollgate', 'user_rule_prefix')
iptables.LIMIT_RULE_PREFIX = config.get('tollgate', 'limit_rule_prefix')
iptables.REJECT_MODE = config.get('tollgate', 'reject_mode')
iptables.REJECT_TCP_RESET = config.getboolean('tollgate', 'reject_reset_tcp')
iptables.DEBUG = config.getboolean('tollgate', 'debug')

iptables.IPV6 = config.getboolean('tollgate', 'ipv6')
iptables.IP6TABLES = config.get('tollgate', 'ip6tables')
iptables.REJECT6_MODE = config.get('tollgate', 'reject6_mode')

iptables.CAPTIVE_ENABLED = config.getboolean('captive', 'enable')
iptables.CAPTIVE_PORT = config.getint('captive', 'port')


if iptables.USER_RULE_PREFIX == iptables.LIMIT_RULE_PREFIX:
	raise Exception, "user rule prefix must be different to the limit rule prefix"

# get unmetered firewall rules
unmetered_hosts = None
if config.has_section('unmetered'):
	unmetered_hosts = config.items('unmetered')

# get blacklist
blacklist_hosts = None
if config.has_section('blacklist'):
	blacklist_hosts = config.items('blacklist')

print "Creating DBUS API..."
iptables.setup_dbus()

print "Creating NAT..."
iptables.create_nat()

if iptables.IPV6:
	print "Creating IPv6 routing rules..."
	iptables.create_ipv6_router()

if unmetered_hosts != None:
	print "Setting unmetered hosts..."
	parse_hostlist(unmetered_hosts, iptables.add_unmetered)
if blacklist_hosts != None:
	print "Setting blacklist hosts..."
	parse_hostlist(blacklist_hosts, iptables.add_blacklist)


print "Starting DBUS Server (only debug messages will appear now)"
try:
	iptables.boot_dbus()
except KeyboardInterrupt:
	print "Got Control-C!"
	exit(0)



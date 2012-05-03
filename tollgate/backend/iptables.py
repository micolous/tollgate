#!/usr/bin/python
"""iptables support module for tollgate
Copyright 2008-2010 Michael Farrell <http://micolous.id.au/>

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
from subprocess import call, Popen, PIPE
from os import system, listdir
from os.path import exists, join, isfile
from sys import exit
from re import compile as re_compile
import dbus, dbus.service, dbus.glib, gobject

DEBUG = False

PARSE_REGEXP_RULE = r'^[\s]*(?P<rule_num>\d+)[\s]+(?P<user>p2u_\d+)[\s]+all[\s]+\-\-[\s]+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(.+MAC (?P<mac>[A-F0-9]{2}:[A-F0-9]{2}:[A-F0-9]{2}:[A-F0-9]{2}:[A-F0-9]{2}:[A-F0-9]{2}).*$)?'
PARSE_RULE = re_compile(PARSE_REGEXP_RULE)

DBUS_INTERFACE = 'au.org.tollgate.TollgateBackendInterface'
DBUS_SERVICE = 'au.org.tollgate.TollgateBackendService'
DBUS_PATH = '/TollgateBackendAPI'

QUOTA2_PATH = '/proc/net/xt_quota/'

GC_THRESH = None

# global level functions that aren't supposed to be exposed to the API
def run(args):
	"""Wrapper function for executing commands in a blocking fashion.  This is
	a wrapper so we can replace things in future if needed, and implement
	security fixes, logging, and other features in all commands.

	Should return the errorcode from iptables."""
	if DEBUG:
		print "call(%s)" % str(args)
	return call(args)

def run_capture_output(args):
	"""Runs a command and returns it's output in a string."""
	if DEBUG:
		print "capturing output from call(%s)" % str(args)

	p = Popen(args, stdout=PIPE)
	stdout = p.communicate()[0]
	return stdout
	
def read_all_file(filename):
	fh = open(filename)
	d = fh.read()
	fh.close()
	return d
	
def check_modules(*modules):
	"""
	Checks if modules have been loaded successfully.

	Returns None if they are all there, otherwise a list of modules missing.
	"""
	modules = list(modules)
	d = read_all_file('/proc/modules')
	for l in d.split('\n'):
		module_name = l.split(' ')[0]
		if module_name in modules:
			modules.remove(module_name)
		if not bool(modules):
			# modules list is empty, pass!
			return None
	
	# modules list has stuff in it still
	return modules

def check_symbols(*symbols):
	"""
	Checks if symbols are in the kernel.

	Returns None if they are all there, otherwise a list of symbols missing.
	"""
	symbols = list(symbols)
	d = read_all_file('/proc/kallsyms')
	for l in d.split('\n'):
		symbol_name = l.split(' ')[2].split("\t")[0]
		if symbol_name in symbols:
			symbols.remove(symbol_name)
		if not bool(symbols):
			# symbols list is empty, pass!
			return None
	
	# symbols list has stuff in it still
	return symbols

def load_modules(*modules):
	for module in modules:
		run(('modprobe', '-v', module))
	
def create_nat():
	# load kernel modules that may not have loaded.
	modules = set(('x_tables', 'xt_quota2', 'xt_TPROXY', 'nf_conntrack', 'nf_conntrack_ipv4', 'iptable_nat', 'ipt_MASQUERADE', 'iptable_filter', 'xt_state', 'ipt_REJECT', 'iptable_mangle', 'xt_mark'))

	symbols = set((
		'xt_table_open', # x_tables
		'quota_mt2', # xt_quota2
		'tproxy_tg4', # xt_TPROXY
		'nf_conntrack_net_init', # nf_conntrack
		'ipv4_conntrack_in', # nf_conntrack_ipv4
		'nf_nat_in', # iptable_nat
		'masquerade_tg', # ipt_MASQUERADE
		'iptable_filter_net_init', # iptable_filter
		'state_mt', # xt_state
		'reject_tg', # ipt_REJECT
		'iptable_mangle_net_init', # iptable_mangle
		'mark_tg', # xt_mark
	))
	
	load_modules(*modules)
	
	missing_modules = check_modules(*modules)
	
	if missing_modules:
		# check for symbols too, in case it is built into the kernel.
		missing_symbols = check_symbols(*symbols)
		if missing_symbols:
			print "Error: not all modules could be loaded successfully.  The following are missing:"
			print missing_modules
			print ""
			print "Though some of those modules may be in-kernel.  These symbols are missing:"
			print missing_symbols
			print ""
			print "This may mean that you have not built all dependancies."
			exit(1)
		else:
			# all symbols are there, continue onward.
			# probably using fedora where some of this is in-kernel
			pass

	# enable forwarding
	write_file('/proc/sys/net/ipv4/ip_forward', 1)
	
	# enable tproxy captivity routing
	system('ip rule add fwmark 0x1/0x1 lookup 100')
	system('ip route add local 0.0.0.0/0 dev lo table 100')
	
	if GC_THRESH != None:
		write_file('/proc/sys/net/ipv4/neigh/default/gc_thresh1', GC_THRESH)
		write_file('/proc/sys/net/ipv4/neigh/default/gc_thresh2', GC_THRESH * 4)
		write_file('/proc/sys/net/ipv4/neigh/default/gc_thresh3', GC_THRESH * 8)
		
	# define NAT rule
	run((IPTABLES,'-t','nat','-F','POSTROUTING'))
	run((IPTABLES,'-t','nat','-A','POSTROUTING','-o',EXTERN_IFACE,'-j','MASQUERADE'))

	# define allowed chain
	run((IPTABLES,'-N',ALLOWED_RULE))
	run((IPTABLES,'-F',ALLOWED_RULE))
	run((IPTABLES,'-A',ALLOWED_RULE,'-i',EXTERN_IFACE,'-o',INTERN_IFACE,'-m','state','--state','RELATED,ESTABLISHED','-j','ACCEPT'))
	run((IPTABLES,'-A',ALLOWED_RULE,'-i',INTERN_IFACE,'-o',EXTERN_IFACE,'-j','ACCEPT'))

	# define unmetered chain
	run((IPTABLES,'-D','FORWARD','-j',UNMETERED_RULE))
	run((IPTABLES,'-N',UNMETERED_RULE))
	run((IPTABLES,'-F',UNMETERED_RULE))
	run((IPTABLES,'-I','FORWARD','1','-j',UNMETERED_RULE))

	# define blacklist chain
	run((IPTABLES,'-D','FORWARD','-j',BLACKLIST_RULE))
	run((IPTABLES,'-N',BLACKLIST_RULE))
	run((IPTABLES,'-F',BLACKLIST_RULE))
	run((IPTABLES,'-I','FORWARD','2','-j',BLACKLIST_RULE))

	# create rejection rule
	run((IPTABLES,'-D','FORWARD','-p','tcp','-j','REJECT','--reject-with','tcp-reset'))
	run((IPTABLES,'-D','FORWARD','-j','REJECT','--reject-with',REJECT_MODE))
	
	# handle captivity properly with tproxy
	run((IPTABLES,'-D','FORWARD','--mark','0x1','-i',INTERN_IFACE,'-p','tcp','--dport','80','-j','ACCEPT'))
	run((IPTABLES,'-D','FORWARD','--mark','0x1','-o',INTERN_IFACE,'-p','tcp','--sport','80','-j','ACCEPT'))
	run((IPTABLES,'-A','FORWARD','--mark','0x1','-i',INTERN_IFACE,'-p','tcp','--dport','80','-j','ACCEPT'))
	run((IPTABLES,'-A','FORWARD','--mark','0x1','-o',INTERN_IFACE,'-p','tcp','--sport','80','-j','ACCEPT'))
	
	if REJECT_TCP_RESET:
		run((IPTABLES,'-A','FORWARD','-p','tcp','-j','REJECT','--reject-with','tcp-reset'))
	run((IPTABLES,'-A','FORWARD','-j','REJECT','--reject-with',REJECT_MODE))
	
	run((IPTABLES,'-P','FORWARD','DROP'))

	# captivity related entries

	# define port forwarding chain
	run((IPTABLES,'-t','mangle','-D','PREROUTING','-j',IP4PF_RULE))
	run((IPTABLES,'-t','mangle','-N',IP4PF_RULE))
	run((IPTABLES,'-t','mangle','-F',IP4PF_RULE))
	run((IPTABLES,'-t','mangle','-I','PREROUTING','1','-j',IP4PF_RULE))

	run((IPTABLES,'-t','filter','-D','FORWARD','-j',IP4PF_RULE))
	run((IPTABLES,'-t','filter','-N',IP4PF_RULE))
	run((IPTABLES,'-t','filter','-F',IP4PF_RULE))
	run((IPTABLES,'-t','filter','-I','FORWARD','1','-j',IP4PF_RULE))
	# define unmetered chain
	run((IPTABLES,'-t','mangle','-D','PREROUTING','-j',UNMETERED_RULE))
	run((IPTABLES,'-t','mangle','-N',UNMETERED_RULE))
	run((IPTABLES,'-t','mangle','-F',UNMETERED_RULE))
	run((IPTABLES,'-t','mangle','-I','PREROUTING','2','-j',UNMETERED_RULE))

	# define blacklist chain
	run((IPTABLES,'-t','mangle','-D','PREROUTING','-j',BLACKLIST_RULE))
	run((IPTABLES,'-t','mangle','-N',BLACKLIST_RULE))
	run((IPTABLES,'-t','mangle','-F',BLACKLIST_RULE))
	run((IPTABLES,'-t','mangle','-I','PREROUTING','3','-j',BLACKLIST_RULE))

	# define "captive" rule
	run((IPTABLES,'-t','mangle','-N',CAPTIVE_RULE))
	run((IPTABLES,'-t','mangle','-F',CAPTIVE_RULE))
	run((IPTABLES,'-t','mangle','-A',CAPTIVE_RULE,'-j','MARK','--set-mark','1'))
	run((IPTABLES,'-t','mangle','-A',CAPTIVE_RULE,'-m','socket','-j','ACCEPT'))
	
	# define the catch-all
	run((IPTABLES,'-t','mangle','-D','PREROUTING','-i',INTERN_IFACE,'-p','tcp','-j',CAPTIVE_RULE))
	run((IPTABLES,'-t','mangle','-A','PREROUTING','-i',INTERN_IFACE,'-p','tcp','-j',CAPTIVE_RULE))
	run((IPTABLES,'-t','mangle','-D','PREROUTING','-i',INTERN_IFACE,'-m','mark','--mark','1','-p','tcp','--dport','80','-j','TPROXY','--tproxy-mark','0x1/0x1','--on-port',str(CAPTIVE_PORT)))
	run((IPTABLES,'-t','mangle','-A','PREROUTING','-i',INTERN_IFACE,'-m','mark','--mark','1','-p','tcp','--dport','80','-j','TPROXY','--tproxy-mark','0x1/0x1','--on-port',str(CAPTIVE_PORT)))


def add_unmetered(ip,proto=None,port=None):
	cmd1 = [IPTABLES,'-A',UNMETERED_RULE,'-i',INTERN_IFACE,'-d',ip,'-j','ACCEPT']
	cmd2 = [IPTABLES,'-t','mangle','-A',UNMETERED_RULE,'-i',INTERN_IFACE,'-d',ip,'-j','ACCEPT']
	arg = []
	if proto != None and port == None:
		arg = ['-p', proto]
	elif proto == None and port != None:
		raise Exception, 'proto must be set if port is.'
	elif port != None:
		arg = ['-p', proto, '--dport', port]
	run(cmd1+arg)
	run(cmd2+arg)

	# now do reverse rule
	cmd = [IPTABLES,'-A',UNMETERED_RULE,'-o',INTERN_IFACE,'-s',ip,'-j','ACCEPT']
	if proto != None and port == None:
		cmd = cmd + ['-p', proto]
	elif proto != None and port != None:
		cmd = cmd + ['-p', proto, '--sport', port]
	run(cmd)

def add_blacklist(ip,proto=None,port=None):
	r = REJECT_MODE
	if proto == 'tcp' and REJECT_TCP_RESET:
		r = 'tcp-reset'
	cmd1 = [IPTABLES,'-A',BLACKLIST_RULE,'-i',INTERN_IFACE,'-d',ip,'-j','REJECT','--reject-with',r]
	cmd2 = [IPTABLES,'-t','mangle','-A',BLACKLIST_RULE,'-i',INTERN_IFACE,'-d',ip,'-j',CAPTIVE_RULE]
	arg = []
	if proto != None and port == None:
		arg = ['-p', proto]
	elif proto == None and port != None:
		raise Exception, 'proto must be set if port is.'
	elif port != None:
		arg = ['-p', proto, '--dport', port]
	else:
		# blocking all traffic, do tcp-reset for tcp packets first
		if REJECT_TCP_RESET:
			add_blacklist(ip, 'tcp')

	run(cmd1 + arg)
	run(cmd2 + arg)

	# now do reverse rule
	cmd = [IPTABLES,'-A',BLACKLIST_RULE,'-o',INTERN_IFACE,'-s',ip,'-j','REJECT','--reject-with',r]
	if proto != None and port == None:
		cmd = cmd + ['-p', proto]
	elif proto != None and port != None:
		cmd = cmd + ['-p', proto, '--sport', port]
	run(cmd)

def user_rule(uid):
	return USER_RULE_PREFIX + str(uid)

def limit_rule(uid):
	return LIMIT_RULE_PREFIX + str(uid)

def get_quota2_amount(label=str):
	"""Gets the named xt_quota2 quota label's value"""
	f = join(QUOTA2_PATH, label)
	if not exists(f):
		raise Exception, "label %s not found, perhaps it doesn't exist?" % label

	fh = open(f, 'r')
	d = fh.read().strip()
	fh.close()
	del fh

	return long(d)

def reset_quota2_amount(label=str):
	v = get_quota2_amount(label)
	set_quota2_amount(label, 0L)
	return v

def set_quota2_amount(label=str, value=long):
	"""Sets the named xt_quota2 quota label amount to a value"""
	f = join(QUOTA2_PATH, label)
	if not exists(f):
		raise Exception, "label %s not found, perhaps it doesn't exist?" % label
	
	write_file(f, value)
	
def write_file(filename, value):
	"Writes over a file with this content."
	fh = open(filename, 'w')
	fh.write(str(value))
	fh.close()

# backend api exposing
class PortalBackendAPI(dbus.service.Object):
	def __init__(self, bus, object_path=DBUS_PATH):
		dbus.service.Object.__init__(self, bus, object_path)

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='s', out_signature='')
	def create_user(self, uid):
		"""Creates a user in the firewall."""
		run((IPTABLES,'-N',user_rule(uid)))

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='s', out_signature='')
	def enable_user_unmetered(self, uid):
		"""Enableds a user and sets unmetered quota on a user."""
		self.enable_user(uid, None)

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='sx', out_signature='')
	def enable_user(self, uid, quota):
		"""Enables a user and sets a quota on a user."""
		# delete all rules on that user first
		run((IPTABLES,'-F',user_rule(uid)))

		# then make them allowed
		run((IPTABLES,'-A',user_rule(uid),'-m','quota2','--name',user_rule(uid),'--grow'))
		set_quota2_amount(user_rule(uid), 0L)
		if quota != None:
			run((IPTABLES,'-A',user_rule(uid),'-m','quota2','--name',limit_rule(uid),'--quota',str(quota),'-j',ALLOWED_RULE))
			set_quota2_amount(limit_rule(uid), long(quota))
		else:
			# cheat here to allow all traffic through, because later on there is
			# a "captivity check" which requires that it lets all of the first
			# packet through.  it's no-count mode so it'll never change
			#
			# however this has no effect if no rule exists that actually uses it
			run((IPTABLES,'-A',user_rule(uid),'-m','quota2','--name',limit_rule(uid),'--quota','999999','--no-change','-j',ALLOWED_RULE))
			set_quota2_amount(limit_rule(uid), 999999)

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='sss', out_signature='')
	def add_host(self, uid, mac, ip):
		"""Registers a host as belonging to a certain user id."""
		# filter outgoing packets by ip + mac
		run((IPTABLES,'-I','FORWARD','4','-i',INTERN_IFACE,'-s',ip,'-m','mac','--mac-source',mac,'-j',user_rule(uid)))

		# filter outgoing packets by ip only... after all you can't establish a connection without a correct MAC
		run((IPTABLES,'-I','FORWARD','4','-o',INTERN_IFACE,'-d',ip,'-j',user_rule(uid)))

		# take the host out of captivity
		start_at = '4'
		run((IPTABLES,'-t','mangle','-I','PREROUTING',start_at,'-i',INTERN_IFACE,'-s',ip,'-m','mac','--mac-source',mac,'-m','quota2','--name',limit_rule(uid),'--no-change','-j','ACCEPT'))

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='s', out_signature='')
	def flush_hosts(self, uid):
		"""Removes all hosts for a user."""
		# TODO: This is somewhat dangerous, really should prevent multiple actions occuring while this one is.
		d = run_capture_output((IPTABLES,'-L','FORWARD','-n','--line-numbers'))
		a = d.split('\n')

		rules_to_remove = []
		for line in a:
			r = PARSE_RULE.search(line)
			# debugging
			#if r != None:
			#	print "Parsed with user-rule %s and line %s" % (r.group('user'), r.group('rule_num'))
			#else:
			#	print "no match: %s" % (line,)

			if r != None and r.group('user') == user_rule(uid):
				try:
					rules_to_remove.append(long(r.group('rule_num')))

					if r.group('mac') != None:
						# take the host out of captive-exempt mode, we know it's mac address.
						run((IPTABLES,'-t','mangle','-D','PREROUTING','-i',INTERN_IFACE,'-s',r.group('ip'),'-m','mac','--mac-source',r.group('mac'),'-m','quota2','--name',limit_rule(uid),'--no-change','-j','ACCEPT'))
				except:
					# Non-match, we don't care.
					pass

		# sort out the list of rules, and put it in reverse order as otherwise the numbering shuffles
		rules_to_remove.sort()
		rules_to_remove.reverse()

		#print "Will delete: %s" % (rules_to_remove,)
		# now remove those rules
		for ln in rules_to_remove:
			run((IPTABLES,'-D','FORWARD',str(ln)))

		# doesn't work as you have to provide exact rule
		#run((IPTABLES,'-D','FORWARD','-j',user_rule(uid)))

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='s', out_signature='bt')
	def get_quota(self, uid):
		"""Gets the user's quota.

		Returns a tuple:
		 0: If the call suceeded, this is True.  Otherwise, it is false and the rest of the data should be ignored.
		 1: The amount of quota used since last query

		Returns False if it could not find the quota info."""

		try:
			return (True, reset_quota2_amount(user_rule(uid)))
		except:
			return (False, 0)
	
	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='', out_signature='a(si)')
	def get_all_users_quota_remaining(self):
		"""
		Gets all user's remaining quota.
		
		Returns an array of a tuple formed as follows:
		 0: The user ID.
		 1: The amount of quota remaining.
		"""
		
		o = []
		# list all items in the quota2 counter directory
		for f in listdir(QUOTA2_PATH):
			if not f.startswith(LIMIT_RULE_PREFIX):
				continue
			
			# add the counter
			try:
				quota = get_quota2_amount(f)
			except:
				# error reading, probably not a counter.
				continue
			
			# shove in the result
			
			o.append((f[len(LIMIT_RULE_PREFIX):], quota))
		
		return o
		
	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='s', out_signature='')
	def disable_user(self, uid):
		"""Disables a user's internet access by removing all their quota."""
		run((IPTABLES,'-F',USER_RULE_PREFIX + str(uid)))
		try:
			set_quota2_amount(user_rule(uid), 0)
		except:
			pass
		try:
			set_quota2_amount(limit_rule(uid), 0)
		except:
			pass

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='', out_signature='')
	def ip4pf_flush(self):
		"""Remove all IPv4 port forwarding rules."""
		run((
			IPTABLES,
			'-t', 'nat',
			'-F', IP4PF_RULE
		))

		run((
			IPTABLES,
			'-t', 'filter',
			'-F', IP4PF_RULE
		))

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='sxxx', out_signature='')
	def ip4pf_add(self, ip, protocol, port, external_port):
		"""Add a port forwarding entry"""
		if port != 0:
			# it's something with a port we need to handle.
			run((
				IPTABLES,
				'-t', 'nat',
				'-A', IP4PF_RULE,
				'-i', EXTERN_IFACE,
				'-p', str(protocol),
				'--dport', str(external_port),
				'-j', 'DNAT',
				'--to-destination', ('%s:%s' % (ip, port)),
			))

			# allow in forwarding
			run((
				IPTABLES,
				'-t', 'filter',
				'-A', IP4PF_RULE,
				'-i', EXTERN_IFACE,
				'-p', str(protocol),
				'--dport', str(external_port),
				'-m', 'state',
				'--state', 'NEW',
				'-j', 'ACCEPT',
			))
		else:
			# it doesn't have a port, it's just an ipv4 protocol number
			run((
				IPTABLES,
				'-t', 'nat',
				'-A', IP4PF_RULE,
				'-i', EXTERN_IFACE,
				'-p', str(protocol),
				'-j', 'DNAT',
				'--to-destination', ip,
			))

			# allow in forwarding
			run((
				IPTABLES,
				'-t', 'filter',
				'-A', IP4PF_RULE,
				'-i', EXTERN_IFACE,
				'-p', str(protocol),
				'-m', 'state',
				'--state', 'NEW',
				'-j', 'ACCEPT',
			))


def setup_dbus():
	system_bus = dbus.SystemBus()
	name = dbus.service.BusName(DBUS_SERVICE, bus=system_bus)
	object = PortalBackendAPI(name)
	return object

def boot_dbus():
	mainloop = gobject.MainLoop()
	mainloop.run()


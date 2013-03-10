#!/usr/bin/python
"""iptables support module for tollgate
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
from subprocess import call, Popen, PIPE
from os import system, listdir
from os.path import exists, join, isfile
from sys import exit
from re import compile as re_compile
import dbus, dbus.service, dbus.glib, glib, sys, gobject
from dbus.mainloop.glib import DBusGMainLoop
from threading import Thread
try:
	from scapy import all as scapy
except:
	scapy = None

DEBUG = False

DBUS_INTERFACE = 'au.org.tollgate.TollgateBackendInterface'
DBUS_SERVICE = 'au.org.tollgate.TollgateBackendService'
DBUS_PATH = '/TollgateBackendAPI'

QUOTA2_PATH = '/proc/net/xt_quota/'

GC_THRESH = None

# global level functions that aren't supposed to be exposed to the API
def run(*args):
	"""Wrapper function for executing commands in a blocking fashion.  This is
	a wrapper so we can replace things in future if needed, and implement
	security fixes, logging, and other features in all commands.

	Should return the errorcode from iptables."""
	if DEBUG:
		print "call(%r)" % (args,)
	return call(args)

def run_capture_output(*args):
	"""Runs a command and returns it's output in a string."""
	if DEBUG:
		print "capturing output from call(%s)" % str(args)

	p = Popen(args, stdout=PIPE)
	stdout = p.communicate()[0]
	return stdout
	
def iptables(*args):
	return run(IPTABLES, *args)

def ipset(*args):
	return run(IPSET, *args)
	
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
		run('modprobe', '-v', module)
	
def create_nat():
	# load kernel modules that may not have loaded.
	modules = set(('x_tables', 'xt_quota2', 'xt_TPROXY', 'nf_conntrack', 'nf_conntrack_ipv4', 'iptable_nat', 'ipt_MASQUERADE', 'iptable_filter', 'xt_state', 'ipt_REJECT', 'iptable_mangle', 'xt_mark', 'xt_set'))

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
		'xt_set_init', # xt_set
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
	iptables('-t','nat','-F','POSTROUTING')
	iptables('-t','nat','-A','POSTROUTING','-o',EXTERN_IFACE,'-j','MASQUERADE')

	# define allowed chain
	iptables('-N',ALLOWED_RULE)
	iptables('-F',ALLOWED_RULE)
	iptables('-A',ALLOWED_RULE,'-i',EXTERN_IFACE,'-o',INTERN_IFACE,'-m','state','--state','RELATED,ESTABLISHED','-j','ACCEPT')
	iptables('-A',ALLOWED_RULE,'-i',INTERN_IFACE,'-o',EXTERN_IFACE,'-j','ACCEPT')

	# define unmetered chain
	iptables('-D','FORWARD','-j',UNMETERED_RULE)
	iptables('-N',UNMETERED_RULE)
	iptables('-F',UNMETERED_RULE)
	iptables('-I','FORWARD','1','-j',UNMETERED_RULE)

	# define blacklist chain
	iptables('-D','FORWARD','-j',BLACKLIST_RULE)
	iptables('-N',BLACKLIST_RULE)
	iptables('-F',BLACKLIST_RULE)
	iptables('-I','FORWARD','2','-j',BLACKLIST_RULE)

	# delete existing rejection rule
	iptables('-D','FORWARD','-p','tcp','-m','state','--state','ESTABLISHED','-j','DROP')
	iptables('-D','FORWARD','-p','tcp','-j','REJECT','--reject-with','tcp-reset')
	iptables('-D','FORWARD','-j','REJECT','--reject-with',REJECT_MODE)
	
	# define port forwarding chain
	iptables('-t','nat','-D','PREROUTING','-j',IP4PF_RULE)
	iptables('-t','nat','-N',IP4PF_RULE)
	iptables('-t','nat','-F',IP4PF_RULE)
	iptables('-t','nat','-I','PREROUTING','1','-j',IP4PF_RULE)

	iptables('-t','filter','-D','FORWARD','-j',IP4PF_RULE)
	iptables('-t','filter','-N',IP4PF_RULE)
	iptables('-t','filter','-F',IP4PF_RULE)
	iptables('-t','filter','-I','FORWARD','1','-j',IP4PF_RULE)
	
	# handle captivity properly with tproxy
	iptables('-D','FORWARD','-m','mark','--mark','0x1','-i',INTERN_IFACE,'-j','ACCEPT')
	iptables('-D','FORWARD','-m','mark','--mark','0x1','-o',INTERN_IFACE,'-j','ACCEPT')
	iptables('-A','FORWARD','-m','mark','--mark','0x1','-i',INTERN_IFACE,'-j','ACCEPT')
	iptables('-A','FORWARD','-m','mark','--mark','0x1','-o',INTERN_IFACE,'-j','ACCEPT')
	
	# create new rejection rule
	# just drop traffic that has an open connection, that way it is just packet
	# loss when the firewall is resyncing
	iptables('-A','FORWARD','-p','tcp','-m','state','--state','ESTABLISHED','-j','DROP')
	if REJECT_TCP_RESET:
		iptables('-A','FORWARD','-p','tcp','-j','REJECT','--reject-with','tcp-reset')
	iptables('-A','FORWARD','-j','REJECT','--reject-with',REJECT_MODE)
	
	iptables('-P','FORWARD','DROP')

	# captivity related entries
	# define unmetered chain
	iptables('-t','mangle','-D','PREROUTING','-j',UNMETERED_RULE)
	iptables('-t','mangle','-N',UNMETERED_RULE)
	iptables('-t','mangle','-F',UNMETERED_RULE)
	iptables('-t','mangle','-I','PREROUTING','1','-j',UNMETERED_RULE)

	# define blacklist chain
	iptables('-t','mangle','-D','PREROUTING','-j',BLACKLIST_RULE)
	iptables('-t','mangle','-N',BLACKLIST_RULE)
	iptables('-t','mangle','-F',BLACKLIST_RULE)
	iptables('-t','mangle','-I','PREROUTING','2','-j',BLACKLIST_RULE)

	# define "captive" rule (DIVERT)
	iptables('-t','mangle','-N',CAPTIVE_RULE)
	iptables('-t','mangle','-F',CAPTIVE_RULE)
	iptables('-t','mangle','-A',CAPTIVE_RULE,'-j','MARK','--set-mark','1')
	iptables('-t','mangle','-A',CAPTIVE_RULE,'-j','ACCEPT')
	
	# define the catch-all
	# -m socket handles connections that have already been opened, and sends them to the "captive" rule above.
	iptables('-t','mangle','-D','PREROUTING','-i',INTERN_IFACE,'-p','tcp','--dport','80','-m','socket','-j',CAPTIVE_RULE)
	iptables('-t','mangle','-A','PREROUTING','-i',INTERN_IFACE,'-p','tcp','--dport','80','-m','socket','-j',CAPTIVE_RULE)
	
	# This handles traffic that is a new connection.  For that, we mark the socket, and send it down to the tproxy handler.
	iptables('-t','mangle','-D','PREROUTING','-i',INTERN_IFACE,'-p','tcp','--dport','80','-j','TPROXY','--tproxy-mark','0x1/0x1','--on-port',str(CAPTIVE_PORT))
	iptables('-t','mangle','-A','PREROUTING','-i',INTERN_IFACE,'-p','tcp','--dport','80','-j','TPROXY','--tproxy-mark','0x1/0x1','--on-port',str(CAPTIVE_PORT))


def add_unmetered(ip,proto=None,port=None):
	cmd1 = ['-A',UNMETERED_RULE,'-i',INTERN_IFACE,'-d',ip,'-j','ACCEPT']
	cmd2 = ['-t','mangle','-A',UNMETERED_RULE,'-i',INTERN_IFACE,'-d',ip,'-j','ACCEPT']
	arg = []
	if proto != None and port == None:
		arg = ['-p', proto]
	elif proto == None and port != None:
		raise Exception, 'proto must be set if port is.'
	elif port != None:
		arg = ['-p', proto, '--dport', port]
	iptables(*cmd1+arg)
	iptables(*cmd2+arg)

	# now do reverse rule
	cmd = ['-A',UNMETERED_RULE,'-o',INTERN_IFACE,'-s',ip,'-j','ACCEPT']
	if proto != None and port == None:
		cmd = cmd + ['-p', proto]
	elif proto != None and port != None:
		cmd = cmd + ['-p', proto, '--sport', port]
	iptables(*cmd)

def add_blacklist(ip,proto=None,port=None):
	r = REJECT_MODE
	if proto == 'tcp' and REJECT_TCP_RESET:
		r = 'tcp-reset'
	cmd1 = ['-A',BLACKLIST_RULE,'-i',INTERN_IFACE,'-d',ip,'-j','REJECT','--reject-with',r]
	cmd2 = ['-t','mangle','-A',BLACKLIST_RULE,'-i',INTERN_IFACE,'-d',ip,'-j',CAPTIVE_RULE]
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

	iptables(*cmd1 + arg)
	iptables(*cmd2 + arg)

	# now do reverse rule
	cmd = ['-A',BLACKLIST_RULE,'-o',INTERN_IFACE,'-s',ip,'-j','REJECT','--reject-with',r]
	if proto != None and port == None:
		cmd = cmd + ['-p', proto]
	elif proto != None and port != None:
		cmd = cmd + ['-p', proto, '--sport', port]
	iptables(*cmd)

def ipmac_set_name(uid):
	return IPMACSET_PREFIX + str(uid)

def ip_set_name(uid):
	return IPSET_PREFIX + str(uid)

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
		iptables('-N',user_rule(uid))

		# Create ipsets for the user if they don't already exist
		# match by ip+mac for outgoing, ip only for incoming
		ipset('create', ipmac_set_name(uid), 'bitmap:ip,mac', 'range', INTERN_SUBNET)
		ipset('create', ip_set_name(uid), 'bitmap:ip', 'range', INTERN_SUBNET)


	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='s', out_signature='')
	def enable_user_unmetered(self, uid):
		"""Enableds a user and sets unmetered quota on a user."""
		self.enable_user(uid, None)

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='sx', out_signature='')
	def enable_user(self, uid, quota):
		"""Enables a user and sets a quota on a user."""
		# delete all rules on that user first
		iptables('-F',user_rule(uid))
		
		# ipset bitmap:ip,mac strangeness from http://comments.gmane.org/gmane.linux.network/217806
		# "bitmap:ip,mac is a two dimensional set and therefore it requires two directional parameters" (src,src)
		# (why you would want to match based on ip on one way and mac from another is beyond me...)
		#
		# Also from the ipset man page:
		# "Please note, the set match and SET target netfilter kernel modules
		# always use the source MAC address from the packet to match, add or
		# delete entries from a bitmap:ip,mac type of set."
		iptables('-t','mangle','-D','PREROUTING','-i',INTERN_IFACE,'-m','set','--match-set',ipmac_set_name(uid),'src,src','-m','quota2','--name',limit_rule(uid),'--no-change','-j','ACCEPT')
		iptables('-D','FORWARD','-i',INTERN_IFACE,'-m','set','--match-set',ipmac_set_name(uid),'src,src','-j',user_rule(uid))
		iptables('-D','FORWARD','-o',INTERN_IFACE,'-m','set','--match-set',ip_set_name(uid),'dst','-j',user_rule(uid))


		# then make them allowed
		if quota != None:
			# enforce quota limits for user.
			# Allow the traffic through if there is quota available, record it's
			# use on the positive counter.
			iptables('-A',user_rule(uid),'-m','quota2','--name',limit_rule(uid),'--quota',str(quota),'-m','quota2','--name',user_rule(uid),'--grow','-j',ALLOWED_RULE)
			iptables('-t','mangle','-I','PREROUTING','3','-i',INTERN_IFACE,'-m','set','--match-set',ipmac_set_name(uid),'src,src','-m','quota2','--name',limit_rule(uid),'--quota',str(quota),'--no-change','-j','ACCEPT')
			set_quota2_amount(user_rule(uid), 0L)
			
			set_quota2_amount(limit_rule(uid), long(quota))
		else:
			# Unlimited quota.
			#
			# Cheat here to allow all traffic through, because later on there
			# is a "captivity check" which requires that it lets all of the 
			# first packet through.  It's no-count mode so it'll never change.
			#
			# However this has no effect if no rule exists that actually uses it.
			#
			# This will likely break with packets bigger than the amount
			# specified. It is set to stop at about 10 MiB, which is still
			# bigger than the MTU for most systems.
			iptables('-A',user_rule(uid),'-m','quota2','--name',limit_rule(uid),'--quota','10485760','--no-change','-m','quota2','--name',user_rule(uid),'--grow','-j',ALLOWED_RULE)
			iptables('-t','mangle','-I','PREROUTING','3','-i',INTERN_IFACE,'-m','set','--match-set',ipmac_set_name(uid),'src,src','-m','quota2','--name',limit_rule(uid),'--quota','10485860','--no-change','-j','ACCEPT')
			set_quota2_amount(user_rule(uid), 0L)
			set_quota2_amount(limit_rule(uid), 10485760)
				
		# add packet handlers for user
		iptables('-I','FORWARD','4','-i',INTERN_IFACE,'-m','set','--match-set',ipmac_set_name(uid),'src,src','-j',user_rule(uid))
		iptables('-I','FORWARD','4','-o',INTERN_IFACE,'-m','set','--match-set',ip_set_name(uid),'dst','-j',user_rule(uid))

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='sss', out_signature='')
	def add_host(self, uid, mac, ip):
		"""Registers a host as belonging to a certain user id."""
		# add ip+mac ipset entry
		ipset('add', ipmac_set_name(uid), ','.join([ip, mac]))
		
		# add ip ipset entry
		ipset('add', ip_set_name(uid), ip)

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='s', out_signature='')
	def flush_hosts(self, uid):
		"""Removes all hosts for a user."""
		ipset('flush', ipmac_set_name(uid))
		ipset('flush', ip_set_name(uid))

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
	
	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='', out_signature='a(sx)')
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
		iptables('-F',USER_RULE_PREFIX + str(uid))
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
		run(
			IPTABLES,
			'-t', 'nat',
			'-F', IP4PF_RULE
		)

		run(
			IPTABLES,
			'-t', 'filter',
			'-F', IP4PF_RULE
		)

	@dbus.service.method(dbus_interface=DBUS_INTERFACE, in_signature='sxxx', out_signature='')
	def ip4pf_add(self, ip, protocol, port, external_port):
		"""Add a port forwarding entry"""
		if port != 0:
			# it's something with a port we need to handle.
			run(
				IPTABLES,
				'-t', 'nat',
				'-A', IP4PF_RULE,
				'-i', EXTERN_IFACE,
				'-p', str(protocol),
				'--dport', str(external_port),
				'-j', 'DNAT',
				'--to-destination', ('%s:%s' % (ip, port)),
			)

			# allow in forwarding
			run(
				IPTABLES,
				'-t', 'filter',
				'-A', IP4PF_RULE,
				'-i', EXTERN_IFACE,
				'-p', str(protocol),
				'--dport', str(external_port),
				'-m', 'state',
				'--state', 'NEW',
				'-j', 'ACCEPT',
			)
		else:
			# it doesn't have a port, it's just an ipv4 protocol number
			run(
				IPTABLES,
				'-t', 'nat',
				'-A', IP4PF_RULE,
				'-i', EXTERN_IFACE,
				'-p', str(protocol),
				'-j', 'DNAT',
				'--to-destination', ip,
			)

			# allow in forwarding
			run(
				IPTABLES,
				'-t', 'filter',
				'-A', IP4PF_RULE,
				'-i', EXTERN_IFACE,
				'-p', str(protocol),
				'-m', 'state',
				'--state', 'NEW',
				'-j', 'ACCEPT',
			)
	
	@dbus.service.signal(dbus_interface=DBUS_INTERFACE, signature='ss')
	def on_arp_packet(self, mac, ip):
		pass


class ArpPacketSniffer(object):
	def __init__(self, dev, api):
		self.dev = dev
		self.api = api
		
	def start(self):
		#print 'sniffer: start on %r!' % self.dev
		# only sniff ARP packets
		scapy.sniff(iface=self.dev, prn=self.handle_packet, filter='arp', store=0)
	
	def handle_packet(self, packet):
		if scapy.ARP in packet and packet[scapy.ARP].op in (1, 2):
			# who-has or is-at
			# fire event on api for handling
			self.api.on_arp_packet(packet[scapy.ARP].hwsrc, packet[scapy.ARP].psrc)
			
			# source address
			#print 'sniffer: src=%r, ip=%r' % (packet[scapy.ARP].hwsrc, packet[scapy.ARP].psrc)


def setup_dbus():
	DBusGMainLoop(set_as_default=True)
	system_bus = dbus.SystemBus()
	name = dbus.service.BusName(DBUS_SERVICE, bus=system_bus)
	return name

def boot_dbus(daemonise, name, pid_file=None):
	# die early if scapy isn't available and arp events are requested
	assert (scapy or not GENERATE_ARP_EVENTS), 'scapy must be installed in order to capture arp events.'

	api = PortalBackendAPI(name)
	loop = glib.MainLoop()
	if daemonise:
		assert pid_file, 'Running in daemon mode means pid_file must be specified.'
		from daemon import daemonize

		# parent process drops here, child lives on
		daemonize(pid_file)
		
		
	if GENERATE_ARP_EVENTS:
		# fork off a loop to handle arp packets
		sniffer = ArpPacketSniffer(str(INTERN_IFACE), api)
		# this means it will be called again if it dies
		gobject.threads_init()
		Thread(target=sniffer.start).start()
		#glib.timeout_add(1000, sniffer.start)
		
		
	loop.run()
	

"""tollgate frontend models
Copyright 2008-2011 Michael Farrell <http://micolous.id.au>

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
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from tollgate.tollgate_controller_api import TollgateController
from os import popen
from django.core.exceptions import ObjectDoesNotExist
from socket import gethostbyaddr
try:
	from iplib import CIDR
except ImportError:
	CIDR = None
	import IPy

from django.utils.translation import ugettext as _
from tollgate.frontend import *
from django.core.exceptions import *

BYTES_MULTIPLIER = 1024.0
if CIDR:
	LAN_CIDR = CIDR(settings.LAN_SUBNET)
else:
	LAN_CIDR = IPy.IP(settings.LAN_SUBNET)

def bytes_str(v):
	if v >= pow(BYTES_MULTIPLIER, 4) * 2:
		return u'%.1f TB' % (v / pow(BYTES_MULTIPLIER, 4))
	elif v >= pow(BYTES_MULTIPLIER, 3) * 2:
		return u'%.1f GB' % (v / pow(BYTES_MULTIPLIER, 3))
	elif v >= pow(BYTES_MULTIPLIER, 2) * 2:
		return u'%.1f MB' % (v / pow(BYTES_MULTIPLIER, 2))
	elif v >= BYTES_MULTIPLIER * 2:
		return u'%.1f kB' % (v / BYTES_MULTIPLIER)
	else:
		return u'%.0f.0  B' % v

class UserProfile(Model):
	class Meta:
		ordering = ['user__username']

	user = ForeignKey(User, unique=True, related_name="user")
	internet_on = BooleanField(default=True)
	theme = CharField(default='cake', max_length=30, choices=THEME_CHOICES)

	def get_hosts(self):
		return NetworkHost.objects.filter(user_profile=self)

	def get_changes(self):
		return NetworkHostOwnerChangeEvent.objects.filter(
			Q(old_owner=self) | Q(new_owner=self)
		)

	def __unicode__(self):
		return u'%s' % (self.user,)



class NetworkHost(Model):
	class Meta:
		ordering = ['mac_address']
		permissions = (
			("can_view_ownership", "May see who owns a specific computer."),
		)
	mac_address = CharField(max_length=12)
	ip_address = IPAddressField()
	computer_name = CharField(max_length=128)
	first_connection = DateTimeField('first connection')
	user_profile = ForeignKey(UserProfile, blank=True, null=True)
	online = BooleanField(default=True)

	def get_console_oui(self):
		try:
			oui = Oui.objects.get(hex=self.mac_address[:6])
		except ObjectDoesNotExist:
			return None
		else:
			return oui
	
	def get_console_type(self):
		o = self.get_console_oui()
		if o == None:
			return 'pc'
		else:
			return o.slug

	def is_console(self):
		o = self.get_console_oui()
		return o != None and o.is_console

	def __unicode__(self):
		return u'%s (Name = %s, User = %s)' % (self.mac_address, self.computer_name, self.user_profile)

class Event(Model):
	class Meta:
		ordering = ['start']
	name = CharField(max_length=50)
	start = DateTimeField()
	end = DateTimeField()
	def is_active(self):
		current_time = datetime.now()
		return self.start < current_time < self.end
	is_active.boolean = True

	def __unicode__(self):
		return u'%s: %s to %s (Active = %s)' % (self.name, self.start, self.end, self.is_active())

class EventAttendance(Model):
	class Meta:
		ordering = ['event', 'user_profile']
		permissions = (
			("can_register_attendance", "May use the event attendance registration system."),
			("can_view_quota", "May view quota usage summaries."),
			("can_reset_quota", "May reset quota usage."),
			("can_change_coffee", "May change who has access to send coffee requests."), # this is a seperate ACL because of ravenge and dasman
		)
	event = ForeignKey(Event)
	user_profile = ForeignKey(UserProfile)
	quota_used = PositiveIntegerField(default=0)
	quota_multiplier = PositiveIntegerField(default=1)
	quota_amount = PositiveIntegerField(default=long(settings.DEFAULT_QUOTA_AMOUNT)*1048576L)
	quota_unmetered = BooleanField(default=False)

	# ALTER TABLE `tollgate`.`frontend_eventattendance` ADD COLUMN `coffee` TINYINT(1)  NOT NULL DEFAULT 0 AFTER `quota_unmetered`;
	coffee = BooleanField(default=False)

	registered_by = ForeignKey(UserProfile, null=True, blank=True, related_name="registered_by")
	registered_on = DateTimeField(auto_now_add=True)

	def is_unmetered(self):
		return self.quota_unmetered

	def quota_total(self):
		return self.quota_amount * self.quota_multiplier

	def quota_remaining(self):
		return self.quota_total() - self.quota_used

	def quota_remaining_str(self):
		return bytes_str(self.quota_remaining())

	def quota_amount_str(self):
		return bytes_str(self.quota_amount)

	def quota_used_str(self):
		return bytes_str(self.quota_used)

	def reset_count(self):
		return self.quota_multiplier - 1

	def is_quota_available(self):
		return self.quota_remaining > 0 or self.quota_unmetered

	def usage_fraction(self):
		if self.quota_unmetered:
			return 0.0
		elif self.quota_multiplier == 0:
			return 1.0
		else:
			return float(self.quota_used) / float(self.quota_total())

	def get_resets(self):
		return QuotaResetEvent.objects.filter(event_attendance=self)

	def last_datapoint(self):
		try:
			return NetworkUsageDataPoint.objects.filter(event_attendance=self).order_by('-when')[0]
		except:
			return None

	def last_datapoint_speed(self):
		try:
			return bytes_str(self.last_datapoint().average_speed())+u"/s"
		except:
			return u"0"

	def __unicode__(self):
		return u'(Event = %s) (User = %s) (Quota = %s/%s)' % (self.event, self.user_profile, bytes_str(self.quota_used), bytes_str(self.quota_amount * self.quota_multiplier))



class QuotaResetEvent(Model):
	class Meta:
		ordering = ['when']
	when = DateTimeField(auto_now_add=True)
	event_attendance = ForeignKey(EventAttendance)
	performer = ForeignKey(UserProfile, related_name='performer')
	excuse = CharField(max_length=256)

	def __unicode__(self):
		return u'(QRE: on %s by %s at %s)' % (self.event_attendance, self.performer, self.when)

class NetworkHostOwnerChangeEvent(Model):
	class Meta:
		ordering = ['when']
	when = DateTimeField(auto_now_add=True)
	old_owner = ForeignKey(UserProfile, blank=True, null=True, related_name="old_owner")
	new_owner = ForeignKey(UserProfile, blank=True, null=True, related_name="new_owner")
	network_host = ForeignKey(NetworkHost)


	def __unicode__(self):
		return u'(NHOCE: on %s from %s to %s at %s)' % (self.network_host, self.old_owner, self.new_owner, self.when)

def timedelta_to_seconds(td):
	"from <http://stackoverflow.com/questions/1083402/missing-datetime-timedelta-toseconds-float-in-python>.  This really should be in the standard library."
	return (td.days * 60 * 60 * 24) + td.seconds + td.microseconds / 1E6

class NetworkUsageDataPoint(Model):
	"""This allows us to track network usage over time."""
	class Meta:
		ordering = ['event_attendance', 'when']

	when = DateTimeField(auto_now_add=True)
	event_attendance = ForeignKey(EventAttendance)

	bytes = PositiveIntegerField()

	def previous_dp(self):
		# lookup the previous datapoint
		dps = NetworkUsageDataPoint.objects.filter(when__lt=self.when, event_attendance=self.event_attendance)

		if dps.count() > 1:
			return dps.latest('when')
		else:
			return None

	def average_speed(self):
		prev_dp = self.previous_dp()
		if prev_dp == None:
			return 0.
		else:
			delta = self.when - prev_dp.when
			bytes = self.bytes - prev_dp.bytes

			speed = (bytes / timedelta_to_seconds(delta))
			if speed < 0.:
				speed = 0.
			return speed
	def __unicode__(self):
		return u'(NUDP: when=%s, bytes=%s, ea=%s)' % (self.when, self.bytes, self.event_attendance)

class Oui(Model):
	"""
	Represents an entry in the IEEE OUI table.  This is used to lookup what the vendor of a device is, and whether or not it is a console device (for console-only mode).

	Shouldn't store foreign-key relations against this table - it gets destroyed whenever ouiscraper is run.  Instead we should relate using the .hex field manually.
	"""
	class Meta:
		ordering = ['hex', ]
		verbose_name = "OUI"
	hex = CharField(max_length=6, help_text="The first six characters of a MAC address for this vendor.", unique=True)
	full_name = CharField(max_length=100, help_text="The full name of the vendor.")
	slug = SlugField(help_text="A shortcode for the item.", unique=False)
	is_console = BooleanField(blank=True, help_text="Could this device be a console?")

	def __unicode__(self):
		return u'%s (%s)' % (self.hex, self.full_name)

def is_console(mac):
	try:
		oui = Oui.objects.get(hex=mac[:6])
	except ObjectDoesNotExist:
		return False
	else:
		return oui.is_console

class IP4Protocol(Model):
	class Meta:
		ordering = ['name', ]
		verbose_name = 'IP4 Protocol'
	name = CharField(max_length=16)
	description = CharField(max_length=128, blank=True)
	has_port = BooleanField(blank=True)
	def __unicode__(self):
		return u'%s (%s)' % (self.name, self.id)

class IP4PortForward(Model):
	class Meta:
		verbose_name = 'IP4 Port Forward'
		permissions = (
			('can_ip4portforward', 'Can manage IPv4 port forwarding'),
		)
	host = ForeignKey(NetworkHost)
	protocol = ForeignKey(IP4Protocol, help_text='The IPv4 protocol that this service uses.  If you don\'t know, try TCP or UDP.')
	port = PositiveIntegerField(default=0, help_text='The internal port that the service is running on.  This has no effect if the protocol does not have port numbers.')
	external_port = PositiveIntegerField(default=0, help_text='The external port that this service should show as running on.  This has no effect if the protocol does not have port numbers.')
	creator = ForeignKey(UserProfile)
	created = DateTimeField(auto_now_add=True)
	enabled = BooleanField(blank=True, default=True)

	def __unicode__(self):
		return u'%s %s/%s->%s' % (self.host, self.protocol.name, self.external_port, self.port)

	@permalink
	def get_absolute_url(self):
		return ('ip4portforward_list', (), {})

	def clean(self):
		# carry out basic validation
		super(IP4PortForward, self).clean()
		try:
			if self.protocol == None:
				raise ValidationError()
		except:
			raise ValidationError('You must specify a protocol.')

		# make sure external and internal port are the same
		if self.port != self.external_port:
			raise ValidationError('Internal and external port must be the same, due to a bug.  This will be fixed in a future release.')

		# make sure nothing else on the protocol is there
		qs = IP4PortForward.objects.filter(protocol=self.protocol)
		if self.id:
			qs = qs.exclude(id=self.id)

		if self.port != 0:
			# make sure that nothing else is using teh port too
			qs = qs.filter(port=self.port, external_port=self.external_port)

		if qs.exists():
			raise ValidationError('There exists another service using this protocol.')


def get_current_event():
	now = datetime.now()
	try:
		return Event.objects.get(start__lte=now, end__gte=now)
	except ObjectDoesNotExist:
		return None

def find_user(name):
	return User.objects.filter(username__icontains=name).order_by('username')

def get_user(userid):
	return User.objects.filter(id__exact=userid)[0]

def get_userprofile(user):
	try:
		return user.get_profile()
	except ObjectDoesNotExist:
		# profile doesn't exist, lets make it
		profile = UserProfile.objects.create(user=user)
		profile.save()
		return profile

def has_userprofile_attended(event, userprofile):
	return EventAttendance.objects.filter(event__exact=event, user_profile__exact=userprofile).exists()

def get_userprofile_attendance(event, userprofile):
	return EventAttendance.objects.get(event__exact=event, user_profile__exact=userprofile)

def get_attendance_currentevent(userprofile):
	return get_userprofile_attendance(get_current_event(), userprofile)

def has_attended_currentevent(userprofile):
	return has_userprofile_attended(get_current_event(), userprofile)

def user_exists(name):
	return User.objects.filter(username__iexact=name).exists()

def find_user_exact(name):
	return User.objects.filter(username__iexact=name)[0]

def get_signed_in_users(event):
	return EventAttendance.objects.filter(event__exact=event).order_by('user_profile')

def in_lan_subnet(ip):
	if CIDR:
		return LAN_CIDR.is_valid_ip(ip)
	else:
		return IPy.IP(ip) in LAN_CIDR

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
		if a[0] == ip and a[3] != '00:00:00:00:00:00' and a[5] == settings.LAN_IFACE and a[2] == "0x2":
			mac = a[3].replace(':','')
			if settings.ONLY_CONSOLE and not is_console(mac):
				return None
			else:
				return mac

	# now expired ones.
	for l in d:
		a = l.split()
		if a[0] == ip and a[3] != '00:00:00:00:00:00' and a[5] == settings.LAN_IFACE:
			mac = a[3].replace(':','')
			if settings.ONLY_CONSOLE and not is_console(mac):
				return None
			else:
				return mac

	return None

def get_ip_address(mac):
	if settings.ONLY_CONSOLE and not is_console(mac):
		return None
	fh = open('/proc/net/arp', 'r')
	# skip header
	fh.readline()
	d = fh.readlines()
	fh.close()

	# try active entries first
	for l in d:
		a = l.split()
		if a[3] == mac and a[5] == settings.LAN_IFACE and in_lan_subnet(a[0]) and a[2] == "0x2":
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
		if a[3] != '00:00:00:00:00:00' and a[5] == settings.LAN_IFACE and in_lan_subnet(a[0]) and a[2] == "0x0":
			mac = a[3].replace(":","")
			if settings.ONLY_CONSOLE and not is_console(mac):
				# skip this one, it's not a console.
				continue

			o[a[0]] = mac

	# active entries overwrite expired ones.
	for l in d:
		a = l.split()
		if a[3] != '00:00:00:00:00:00' and a[5] == settings.LAN_IFACE and in_lan_subnet(a[0]) and a[2] == "0x2":
			mac = a[3].replace(":","")
			if settings.ONLY_CONSOLE and not is_console(mac):
				# skip this one, it's not a console.
				continue

			o[a[0]] = mac
	return o

def get_portalapi():
	return TollgateController()

def enable_user_quota(event_attendance):
	portal = get_portalapi()
	refresh_quota_usage(event_attendance, portal)

	# we've had some success so far, mark their connection as on
	event_attendance.user_profile.internet_on = True
	event_attendance.user_profile.save()

	# add to firewall
	if event_attendance.quota_unmetered:
		# add unmetered connection
		portal.enable(event_attendance.user_profile.user.id)
	elif event_attendance.quota_remaining() > 0:
		# add quota
		portal.enable(event_attendance.user_profile.user.id, event_attendance.quota_remaining())

	sync_user_connections(event_attendance.user_profile)

def disable_user_quota(event_attendance):
	# lets read from the portal how much quota they have used
	portal = get_portalapi()
	# refresh usage
	refresh_quota_usage(event_attendance, portal)

	# make connection as disabled
	event_attendance.user_profile.internet_on = False
	event_attendance.user_profile.save()

	portal.disable(event_attendance.user_profile.user.id)

def sync_user_connections(profile, portal=None):
	"""Sync the database's copy of a user's connections with the portal"""
	user_id = profile.user.id
	if portal == None:
		portal = get_portalapi()

	portal.flush(user_id)

	# find all the user's computers.
	hosts = NetworkHost.objects.filter(user_profile__exact=profile, online__exact=True)

	for host in hosts:
		if in_lan_subnet(host.ip_address) and (not settings.ONLY_CONSOLE or host.is_console()):
			portal.connect(user_id, host.mac_address, host.ip_address)

def refresh_quota_usage(event_attendance, portal=None):
	if portal == None:
		portal = get_portalapi()

	r = portal.get_quota(event_attendance.user_profile.user.id)
	if r != None:
		# now set counters
		EventAttendance.objects.filter(id=event_attendance.id).update(quota_used=F('quota_used') + r)
		# get back new value
		event_attendance = EventAttendance.objects.get(id=event_attendance.id)
		# make datapoint
		NetworkUsageDataPoint.objects.create(
			event_attendance = event_attendance,
			bytes = event_attendance.quota_used
		)

def refresh_all_quota_usage(portal=None):
	if portal == None:
		portal = get_portalapi()
	event = get_current_event()

	r = EventAttendance.objects.filter(event__exact=event)
	for e in r:
		refresh_quota_usage(e, portal)


def refresh_networkhost(portal=None):
	if portal == None:
		portal = get_portalapi()
	# use nbtscan to scan the whole network.  it's pretty quick
	#fh = popen("nbtscan -qe " + settings.LAN_SUBNET)
	fh = popen("nmap -sP -n -T5 -oG - " + settings.LAN_SUBNET)
	hosts = fh.readlines()
	fh.close()

	arp_cache = get_arp_cache()
	netinfo = {}

	# updated to get information from DNS instead.
	for ip in arp_cache:
		hn = ''
		try: hn = gethostbyaddr(ip)[0]
		except: pass
		netinfo[ip] = [arp_cache[ip], hn]

	#for h in hosts:
	#	a = h.split("\t")
	#	if netinfo.has_key(a[0]):
	#		netinfo[a[0]].append(a[1].strip())

	# now we have all the network information
	# update the system
	users_needing_refresh = []
	offline_hosts = NetworkHost.objects.all()
	for ip in netinfo:
		mac = netinfo[ip][0]
		name = ''
		if len(netinfo[ip]) > 1:
			name = netinfo[ip][1]

		# find by mac
		try:
			hostinfo = NetworkHost.objects.get(mac_address__iexact=mac)
			offline_hosts = offline_hosts.exclude(mac_address__iexact=mac)

			# existing PC, run update...
			hostinfo.mac_address = mac
			if name != '':
				hostinfo.computer_name = name
			old_online_state = hostinfo.online
			hostinfo.online = True
			hostinfo.ip_address = ip

			if hostinfo.user_profile != None and old_online_state != hostinfo.online and not users_needing_refresh.__contains__(hostinfo.user_profile):
				users_needing_refresh.append(hostinfo.user_profile)
			hostinfo.save()
		except ObjectDoesNotExist:
			NetworkHost.objects.create(mac_address=mac, computer_name=name, first_connection=datetime.now(), online=True, ip_address=ip)

		try:
			recycled_ip_hosts = NetworkHost.objects.filter(ip_address__exact=ip).exclude(mac_address__iexact=mac)
			for hostinfo in recycled_ip_hosts:
				# we have an old host with a different MAC using that used that ip
				# mark it offline, and make a sync job for that user
				hostinfo.online = False
				hostinfo.save()

				if hostinfo.user_profile != None and not users_needing_refresh.__contains__(hostinfo.user_profile):
					users_needing_refresh.append(hostinfo.user_profile)
		except ObjectDoesNotExist:
			# no troubles
			pass

	# now hide offline hosts.
	for nh in offline_hosts:
		if nh.online:
			old_online_state = nh.online
			nh.online = False
			if nh.user_profile != None and old_online_state != nh.online and not users_needing_refresh.__contains__(nh.user_profile):
				users_needing_refresh.append(nh.user_profile)
			nh.save()

	# now refresh the specfic users
	for profile in users_needing_refresh:
		sync_user_connections(profile, portal)

def refresh_networkhost_quick():
	arp_cache = get_arp_cache()

	# now we have all the network information
	# update the system
	users_needing_refresh = []
	offline_hosts = NetworkHost.objects.all()
	for ip in arp_cache:
		mac = arp_cache[ip]

		# find by mac
		try:
			hostinfo = NetworkHost.objects.get(mac_address__iexact=mac)
			offline_hosts = offline_hosts.exclude(mac_address__iexact=mac)

			# existing PC, run update...
			hostinfo.mac_address = mac
			old_online_state = hostinfo.online
			hostinfo.online = True
			hostinfo.ip_address = ip
			if hostinfo.user_profile != None and old_online_state != hostinfo.online and not users_needing_refresh.__contains__(hostinfo.user_profile):
				users_needing_refresh.append(hostinfo.user_profile)
			hostinfo.save()
		except ObjectDoesNotExist:
			NetworkHost.objects.create(mac_address=mac, computer_name='', first_connection=datetime.now(), online=True, ip_address=ip)
		try:
			recycled_ip_hosts = NetworkHost.objects.filter(ip_address__exact=ip).exclude(mac_address__iexact=mac)
			for hostinfo in recycled_ip_hosts:
				# we have an old host with a different MAC using that used that ip
				# mark it offline, and make a sync job for that user
				hostinfo.online = False
				hostinfo.save()

				if hostinfo.user_profile != None and not users_needing_refresh.__contains__(hostinfo.user_profile):
					users_needing_refresh.append(hostinfo.user_profile)
		except ObjectDoesNotExist:
			# no troubles
			pass

	for profile in users_needing_refresh:
		sync_user_connections(profile)

def get_unclaimed_online_hosts():
	return NetworkHost.objects.filter(online__exact=True, user_profile__exact=None).order_by('-first_connection')

def get_unclaimed_offline_hosts():
	return NetworkHost.objects.filter(online__exact=False, user_profile__exact=None).order_by('-first_connection')

def apply_ip4portforwards():
	forwards = IP4PortForward.objects.filter(enabled=True, host__online=True, host__user_profile__internet_on=True).select_related(depth=1)

	portal = get_portalapi()
	portal.ip4pf_flush()

	for pf in forwards:
		# remove port number from things that shouldn't have one.
		if pf.protocol.has_port:
			port = pf.port
			external_port = pf.external_port
		else:
			port = 0
			external_port = 0

		portal.ip4pf_add(pf.host.ip_address, pf.protocol_id, port, external_port)


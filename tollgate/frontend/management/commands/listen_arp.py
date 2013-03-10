"""
tollgate management command: listen arp
Copyright 2008-2013 Michael Farrell

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

from django.core.management.base import BaseCommand, CommandError
from tollgate.frontend.tollgate_controller_api import TollgateController
from tollgate.frontend.models import apply_ip4portforwards, utcnow, NetworkHost
import dbus.glib, glib
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
	args = ''
	help = """\
Listens for ARP events from the tollgate backend and synchronises iptables 
appropriately.
"""
	
	def arp_handler(self, mac, ip):
		mac = mac.replace(':', '')
		
		assert len(mac) == 12, 'MAC address length must be 12'
		assert 7 <= len(ip) <= 15, 'IP address length must be between 7 and 15'
		
		#print 'arp: %s, %s' % (mac, ip)
		
		# check to see if this host exists
		try:
			host = NetworkHost.objects.get(mac_address__iexact=mac)
			
			if not host.online or host.ip_address != ip:
				# host was not marked as online, make it so.
				old_ip = host.ip_address
			
				# does exist, online the host
				host.online = True
				host.ip_address = ip
				host.save()
			
				if old_ip != ip:
					# ip change
					self.portal.disconnect(host.user_profile.user_id, mac, ip)

				# connect it in API
				self.portal.connect(host.user_profile.user_id, mac, ip)
			
				# connected!
				# FIXME: does not apply port forwards straight away.
		except ObjectDoesNotExist:
			host = NetworkHost.objects.create(
				mac_address=mac,
				computer_name='',
				first_connection=utcnow(),
				online=True,
				ip_address=ip
			)
		
		# check that nothing else is on that ip actively
		recycled_ip_hosts = NetworkHost.objects.filter(ip_address__exact=ip, online=True).exclude(mac_address__iexact=mac)
		
		# immediately mark as offline so nothing else touches these
		recycled_ip_hosts.update(online=False)
				
		# find user/macaddress combos to mark as offline
		users_to_refresh = set(recycled_ip_hosts.values_list('user_profile__user_id', 'mac_address'))
		
		# offline the hosts in the firewall
		for user_id, mac_address in users_to_refresh:
			self.portal.disconnect(user_id, mac_address, ip)
			
		# FIXME: does not remove port forwards for old hosts

	def handle(self, *args, **options):
		print 'ARP listener running...'
		self.portal = TollgateController(mainloop=True)
		self.portal.register_arp_packet(self.arp_handler)
		
		loop = glib.MainLoop()
		loop.run()


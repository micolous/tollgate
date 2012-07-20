"""
tollgate management command: refresh network hosts
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

from django.core.management.base import BaseCommand, CommandError
from tollgate.frontend.models import get_portalapi, refresh_networkhost, \
	apply_ip4portforwards, refresh_all_quota_usage


class Command(BaseCommand):
	args = ''
	help = 'Refreshes data about hosts on the network and accounting data.  ' +\
		'Run this from crontab every 10 minutes.'

	def handle(self, *args, **options):
		# refresh information about networkhosts and quota for crontab.
		portal = get_portalapi()
		try:
			refresh_networkhost(portal)
		except Exception, ex:
			print "Failed refreshing network hosts"
			print ex
		try:
			apply_ip4portforwards()
		except Exception, ex:
			print "Failed applying port forwards."
			print ex

		refresh_all_quota_usage(portal)


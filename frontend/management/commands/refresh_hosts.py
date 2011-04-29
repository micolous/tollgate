from django.core.management.base import BaseCommand, CommandError
from tollgate.frontend.models import get_portalapi, refresh_networkhost, apply_ip4portforwards, refresh_all_quota_usage

class Command(BaseCommand):
	args = ''
	help = 'Refreshes data about hosts on the network and accounting data.  Run this from crontab every 10 minutes.'
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


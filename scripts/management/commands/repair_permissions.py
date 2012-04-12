#!/usr/bin/env python
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os, stat

class Command(BaseCommand):
	args = ''
	help = 'Repairs the execute permissions of tollgate binaries.'
	
	def handle(self, *args, **kwargs):
		executable_files = [
			'manage.py',
			'scraper.py',
			os.path.join('backend', 'tollgate.py'),
			os.path.join('backend', 'tollgate.sh'),
		]
		
		for x in executable_files:
			# chmod the file such that all that have read access have execute as well.
			fp = os.path.join(settings.PROJECT_PATH, x)
			mode = os.stat(fp).st_mode
			
			if mode & stat.S_IRUSR:
				mode |= stat.S_IXUSR
				
			if mode & stat.S_IRGRP:
				mode |= stat.S_IXGRP
			
			if mode & stat.S_IROTH:
				mode |= stat.S_IXOTH
			
			os.chmod(fp, mode)
		
		print "Repaired execute permissions."
			
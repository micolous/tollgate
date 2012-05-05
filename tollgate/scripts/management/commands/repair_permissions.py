#!/usr/bin/env python
"""
tollgate management command: repair script permissions
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
from django.conf import settings
import os, stat

class Command(BaseCommand):
	args = ''
	help = 'Repairs the execute permissions of tollgate binaries.'
	
	def handle(self, *args, **kwargs):
		executable_files = [
			'manage.py',
			os.path.join('tollgate', 'backend', 'tollgate_backend.py'),
			os.path.join('platform', 'debian', 'init.d', 'tollgate-backend'),
			os.path.join('platform', 'debian', 'init.d', 'tollgate-captivity'),
			os.path.join('tollgate', 'captive_landing', 'tproxy.py'),
		]
		
		tollgate_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
		
		for x in executable_files:
			# chmod the file such that all that have read access have execute as well.
			fp = os.path.join(tollgate_path, x)
			print " %s" % fp
			mode = os.stat(fp).st_mode
			
			if mode & stat.S_IRUSR:
				mode |= stat.S_IXUSR
				
			if mode & stat.S_IRGRP:
				mode |= stat.S_IXGRP
			
			if mode & stat.S_IROTH:
				mode |= stat.S_IXOTH
			
			os.chmod(fp, mode)
		
		print "Repaired execute permissions."
			
#!/usr/bin/env python
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import string, random, os.path

class Command(BaseCommand):
	args = ''
	help = 'Sets up a settings/local.py with required elements.'
	
	def handle(self, *args, **kwargs):
		# take a copy of the original local.py
		local_py_location = os.path.join(settings.PROJECT_PATH, 'settings', 'local.py')
		if os.path.exists(local_py_location:
			fh = open(local_py_location, 'rb')
			local_py = fh.read()
			fh.close()
		else:
			local_py = ''
		
		fh = open(local_py_location, 'ab')
		
		# write out a SECRET_KEY if needed
		if not hasattr(settings, 'SECRET_KEY') or not settings.SECRET_KEY:
			fh.write("""
SECRET_KEY = %r

""" % "".join([random.choice(string.letters + string.digits + string.punctuation) for i in range(80)]))
		
		# write out the SOURCE_URL if needed.
		if 'SOURCE_URL' not in local_py:
			fh.write("""
# Please setup a location where the source code to your modifications to
# tollgate are stored.  This must be a publicly-accessible web (http/https)
# URL.  If your VCS does not provide access over HTTP, provide a link to a web
# page where instructions to configure access to your repository are.
#
# Tip: You can use the "fork" functionality in GitHub to do this.  Make sure
# you push back to your fork.
#
# A message will be inserted in all pages until you set this correctly.
#
# Please note this is a requirement of the Affero GPL license.
SOURCE_URL = None
""")
		fh.flush()
		fh.close()
		

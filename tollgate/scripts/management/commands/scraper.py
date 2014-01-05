#!/usr/bin/env python
"""
ouiscraper: A script to populate the OUI table of tollgate with vendor data.
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
from os.path import getmtime, exists, isfile, realpath, dirname, join
from time import gmtime, asctime, time
from urllib2 import Request, urlopen, HTTPError
from ConfigParser import ConfigParser
from sys import path
from os import environ

from lxml import objectify
from progressbar import ProgressBar, Percentage, Bar, ETA

# attempt use of better regex library.
try:
	from regex import compile as re_compile
	from regex import I
except ImportError:
	from re import compile as re_compile
	from re import I

from tollgate import __version__
from tollgate.frontend.models import Oui, IP4Protocol
from django.db import connection
from django.db.utils import DatabaseError, IntegrityError
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# other constants
OUI_LIST_URL = 'http://standards.ieee.org/develop/regauth/oui/oui.txt'
OUI_LIST_FILE = 'oui.txt'
OUI_RE = re_compile(r'^\s+([0-9A-F]{6})\s+\(base 16\)\s+(.*)\s*$')

IP4P_LIST_URL = \
	'http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xml'
IP4P_LIST_FILE = 'protocol-numbers.xml'

HELPER_DATA = join(realpath(dirname(__file__)), 'scraper.dat')

UA = 'tollgate/%s (scraper.py; Python)' % __version__
PBAR_WIDGET_STYLE = [Percentage(), Bar(), ETA()]


def download_file(filename, url):
	etag_filename = filename + '.etag'
	# check to see if there's an existing dump of the data
	mtime = None
	if exists(filename):
		if not isfile(filename):
			raise Exception((
				'ERROR: %s exists but is not a file.  Please check this, and' +
				'move it out of the way so I can run.'
			) % filename)

	# lets also check for an etag, and use it if it's there.
	etag = None
	if exists(etag_filename):
		etag = open(etag_filename, 'rb').read()
		mtime = asctime(gmtime(getmtime(filename))) + ' GMT'

	# connect to the IEEE website, and grab the current OUI data, if it is
	# older that the one currently on the system.

	print "Attempting to download data from %s..." % url
	request = Request(url, headers={
		'User-Agent': UA
	})

	if mtime != None:
		request.add_header('If-Modified-Since', mtime)
	if etag != None:
		request.add_header('If-None-Match', etag)

	response = None
	try:
		response = urlopen(request)
	except HTTPError, ex:
		if ex.code == 304:  # not modified
			print "Data that is present appears to be current."
		else:
			raise ex

	if response != None:
		try:
			length = long(response.info()['Content-Length'])
		except KeyError:
			# missing header, booo
			length = 0L
		# download the file to disk
		fp = open(filename, 'wb')
		
		if length > 0:
			print "Copying %s bytes..." % length
			progress = ProgressBar(widgets=PBAR_WIDGET_STYLE, maxval=length).start()
		else:
			print "Downloading..."
			progress = None

		for data in response:
			fp.write(data)
			if progress is not None:
				progress.update(fp.tell())

		if progress is not None:
			progress.finish()

		# write out etag
		try:
			open(etag_filename, 'wb').write(response.info()['ETag'])
		except:
			print "Warning: Couldn't write ETag data.  This will mean when"
			print "this script runs again, it will redownload all the content."

		print "File downloaded."

	# done


def parse_oui_data(filename, config):
	# open the oui file into memory
	fp = open(filename, 'rb')
	# get the size of the file
	fp.seek(0, 2)
	oui_bytes = fp.tell()
	fp.seek(0, 0)
	
	oui_regexps = {}
	for k, v in config.items('oui'):
		try:
			oui_regexps[k] = re_compile(v, I)
		except Exception, ex:
			print "There was a problem compiling the regular expression for %s." % k
			print "Expression: %s" % v
			raise ex

	# We're good.  Lets clear the existing Oui table because it's data is now
	# outdated.  Because we don't care about foreign relations, we should grab
	# the cursor and nuke the table directly.
	cursor = connection.cursor()

	# These sql queries don't work properly with "correct" escaping.  Maybe
	# vulnerable to sqli -- but doesn't accept data from user sources anyway.
	try:
		cursor.execute('TRUNCATE TABLE `%s`' % (Oui._meta.db_table,))
	except DatabaseError:
		# truncate may not be supported.  delete it the "slow" way.
		cursor.execute('DELETE FROM `%s`' % (Oui._meta.db_table,))
	print "Deleted existing OUI data."

	# now parse the new oui data with the regular expressions provided.
	print "Reading and populating OUI data..."
	progress = ProgressBar(widgets=PBAR_WIDGET_STYLE, maxval=oui_bytes).start()
	for line in fp:
		# oui database contains mixed encodings.
		try:
			# try to decode as utf-8 first
			line = unicode(line.decode('utf-8'))
		except UnicodeDecodeError:
			# try to decode as latin-1 second.
			line = unicode(line.decode('latin-1'))
		progress.update(fp.tell())
		m = OUI_RE.match(line)
		if m != None and m.group(2) != "":
			# try to match it
			matched = False
			hex, full_name = m.group(1), m.group(2).strip()
			try:
				for k, v in oui_regexps.iteritems():
					if v.match(full_name):
						# match it up with a particular group
						#print "%s = %s (%s)" % (k, m.group(1), m.group(2))

						# lets pump this into the database.
						Oui.objects.create(
							hex=hex,
							full_name=full_name,
							slug=k,
							is_console=(
								config.has_option('oui-console', k) and
								config.getboolean('oui-console', k)
							)
						)
						matched = True
				if not matched:
					Oui.objects.create(
						hex=hex,
						full_name=full_name,
						slug='pc',
						is_console=False
					)
			except IntegrityError:
				print "IntegrityError processing OUI: %s %s" % (m.group(1), m.group(2))
	progress.finish()
	print 'Added %d entries to Oui table.' % Oui.objects.count()


def parse_ip4p_data(filename, config):
	tree = objectify.parse(open(filename, 'rb'))
	root = tree.getroot()
	if root.registry.get('id') != 'protocol-numbers-1':
		raise Exception, 'This does not look like the protocol numbers XML'

	cursor = connection.cursor()

	# These sql queries don't work properly with "correct" escaping.  Maybe
	# vulnerable to sqli -- but doesn't accept data from user sources anyway.
	try:
		cursor.execute('TRUNCATE TABLE `%s`' % (IP4Protocol._meta.db_table,))
	except DatabaseError:
		# truncate may not be supported.  delete it the "slow" way.
		cursor.execute('DELETE FROM `%s`' % (IP4Protocol._meta.db_table,))
	print "Deleted existing IP4P data."

	# now walk
	print "Reading and populating IP4P data..."
	record_count = len(root.registry.record)
	progress = ProgressBar(widgets=PBAR_WIDGET_STYLE, maxval=record_count).start()
	for i, record in enumerate(root.registry.record):
		progress.update(i)
		#print objectify.dump(record)

		if '-' in str(record.value):
			continue

		# some items don't have proper names.  fix this.
		if config.has_option('ip4p-override-name', str(record.value)):
			name = config.get('ip4p-override-name', str(record.value))
		else:
			name = record.name

		try:
			description = record.description
		except:
			description = ''

		try:
			IP4Protocol.objects.create(
				id=record.value,
				name=name,
				description=description,
				has_port=(
					config.has_option('ip4p-has-port', str(record.value)) and
					config.getboolean('ip4p-has-port', str(record.value))
				)
			)
		except IntegrityError:
			# dupe PK
			print "Warning: duplicate protocol number %s." % (record.value)
			
	progress.finish()
	print 'Added %d entries to Protocol table.' % IP4Protocol.objects.count()


class Command(BaseCommand):
	args = ''
	help = """
		Populates the database with information about IPv4 protocol types and
		vendor OUIs.
	"""
	
	def handle(self, *args, **options):
		config = ConfigParser()
		config.read(HELPER_DATA)
		download_file(OUI_LIST_FILE, OUI_LIST_URL)
		download_file(IP4P_LIST_FILE, IP4P_LIST_URL)

		parse_oui_data(OUI_LIST_FILE, config)
		parse_ip4p_data(IP4P_LIST_FILE, config)

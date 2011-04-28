# tollgate Makefile
# Copyright 2008-2011 Michael Farrell <http://micolous.id.au/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

HASKEY = $(shell grep -P '^SECRET_KEY = ' settings_local.py)
HASSRC = $(shell grep -P '^SOURCE_URL = ' settings_local.py)

all:
	# repairing permissions...
	chmod a+x manage.py scraper.py backend/tollgate.py
	
ifeq ($(HASKEY),)
	# Create new secret key.
	python -c 'import string,random;print "\n\nSECRET_KEY = %s\n" % repr("".join([random.choice(string.letters + string.digits + string.punctuation) for i in range(80)]))' >> settings_local.py
endif

ifeq ($(HASSRC),)
	echo '# Please setup a location where the source code to your modifications to tollgate are stored.' >> settings_local.py
	echo '# This must be a publicly-accessible web (http/https) URL.  If your VCS does not provide access over HTTP, provide a link to a web page where instructions to configure access to your repository are.' >> settings_local.py
	echo '# Tip: You can use the "fork" functionality in GitHub to do this.  Make sure you push back to your fork.' >> settings_local.py
	echo '# A message will be inserted in all pages until you set this correctly.' >> settings_local.py
	echo 'SOURCE_URL = None' >> settings_local.py
endif
	
	# finished.  please see the README for further instructions.

export:
	rm -rf export
	svn export . export
	rm export/Makefile
	
tarball: export
	rm -f tollgate.tar.bz2
	tar -jcvf tollgate.tar.bz2 --owner=0 --group=0 -Cexport .
	
clean:
	rm -rf export 
	rm -f tollgate.tar.bz2

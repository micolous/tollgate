#!/usr/bin/env python
"""
Landing page for tollgate's captivity handler in apache2.
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
from os import environ
from os.path import join, dirname
from urllib import quote

try:
	tollgate_uri = open(join(dirname(__file__),'tollgate_uri'), 'rb').read().strip()
except IOError:
	raise IOError, 'Please create a file called "tollgate_uri" with the path to to tollgate\'s HTTPS site.'

LANDING_URI = "%s/captive_landing/?u=http://%s%s" % (tollgate_uri, quote(environ['HTTP_HOST']), quote(environ['REQUEST_URI']))

print """Last-Modified: Thu, 01 Jan 1970 03:13:37 GMT
Expires: Thu, 01 Jan 1970 03:13:37 GMT
Content-Type: text/html
Pragma: no-cache
Cache-Control: no-cache

<html>
  <head>
    <title>Captive Portal Logon Required</title>
    <meta http-equiv="refresh" content="0;URL=%s">
  </head>

  <body>
    <h1>Captive Portal Logon Required</h1>
    <p>A captive portal logon is required to access the requested site.  <a href="%s">Click here to login.</a></p>
  </body>
</html>
""" % (LANDING_URI, LANDING_URI)


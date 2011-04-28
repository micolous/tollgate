#!/usr/bin/env python
"""
Landing page for tollgate's captivity handler in apache2.
Copyright 2010 Michael Farrell <http://micolous.id.au/>
$Id: index.py 112 2010-11-10 12:42:16Z michael $


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
from urllib import quote

LANDING_URI = "https://portal.onadelaide.blackhats.net.au/captive_landing/?u=http://%s%s" % (quote(environ['HTTP_HOST']), quote(environ['REQUEST_URI']))
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

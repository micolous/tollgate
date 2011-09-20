#!/usr/bin/env python
"""
tollgate.wsgi: WSGI bootstrap for tollgate.
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
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'tollgate.settings'
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__),'..')))
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


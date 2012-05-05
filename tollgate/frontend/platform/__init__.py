#!/usr/bin/env python
"""
tollgate frontend platform-specific code distributor
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

from platform import system
import warnings
system = system().lower()
from tollgate.frontend.platform.common import *

if system == 'linux':
	from tollgate.frontend.platform.linux import *
else:
	warnings.warn('Platform %r is unsupported.  Some OS-specific functionality will not work.' % system, UserWarning)
	from tollgate.frontend.platform.dummy import *

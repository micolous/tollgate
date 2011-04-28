"""tollgate frontend urls
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

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',
	# Example:
	# (r'^frontend/', include('frontend.foo.urls')),

	# Uncomment the next line to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),

	# DEVELOPMENT ONLY: media path
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

	(r'^i18n/', include('django.conf.urls.i18n')),
	(r'^api/', include('tollgate.api.urls')),
	(r'^', include('tollgate.frontend.urls')),
)

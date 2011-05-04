"""tollgate frontend admin hooks
Copyright 2008-2010 Michael Farrell

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

from django.contrib import admin
from tollgate.frontend.models import *

class EventAttendanceAdmin(admin.ModelAdmin):
	list_display = ("event", "user_profile", "quota_used", "quota_multiplier", "quota_amount", "quota_unmetered", "coffee")

class EventAdmin(admin.ModelAdmin):
	list_display = ("name", "start", "end", "is_active")

class NetworkHostAdmin(admin.ModelAdmin):
	list_display = ("mac_address", "ip_address", "computer_name", "user_profile")

class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "internet_on")

class QuotaResetEventAdmin(admin.ModelAdmin):
	list_display = ("when", "event_attendance", "performer", "excuse")

class NetworkHostOwnerChangeEventAdmin(admin.ModelAdmin):
	list_display = ("when", "old_owner", "new_owner", "network_host")

class NetworkUsageDataPointAdmin(admin.ModelAdmin):
	list_display = ("when", "event_attendance", "bytes")

class OuiAdmin(admin.ModelAdmin):
	list_display = ("hex", "full_name", "slug", "is_console")
	list_filter = ('is_console', 'slug')

class IP4ProtocolAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'has_port')

class IP4PortForwardAdmin(admin.ModelAdmin):
	list_display = ('host', 'protocol', 'port', 'creator', 'created', 'enabled')
	list_filter = ('enabled', 'host')

mapairs = (
	(EventAttendance, EventAttendanceAdmin),
	(Event, EventAdmin),
	(NetworkHost, NetworkHostAdmin),
	(UserProfile, UserProfileAdmin),
	(QuotaResetEvent, QuotaResetEventAdmin),
	(NetworkHostOwnerChangeEvent, NetworkHostOwnerChangeEventAdmin),
	(NetworkUsageDataPoint, NetworkUsageDataPointAdmin),
	(Oui, OuiAdmin),
	(IP4Protocol, IP4ProtocolAdmin),
	(IP4PortForward, IP4PortForwardAdmin),
)

for x in mapairs:
	admin.site.register(*x)

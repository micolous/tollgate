#!/usr/bin/env python
"""tollgate frontend application
Copyright 2008-2012 Michael Farrell <http://micolous.id.au>

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

from django.utils.translation import ugettext as _
from south.signals import post_migrate

THEME_CHOICES = (
	('cake', _('cake: The new (white) theme, from v2.6.2')),
#	('platinum', 'platinum: A grey theme (in development)'),
	('terminal', _('terminal: The old (green) theme, in v2.6.1 and earlier')),
)


def update_permissions_after_migration(app, **kwargs):
	"""
	Update app permission just after every migration.
	This is based on app django_extensions update_permissions management command.
	
	"""
	
	from django.conf import settings
	from django.db.models import get_app, get_models
	from django.contrib.auth.management import create_permissions, \
		_get_all_permissions
	from django.contrib.auth import models as auth_app
	from django.contrib.contenttypes.models import ContentType

	app = get_app(app)
	create_permissions(app, get_models(), 2 if settings.DEBUG else 0)
	
	# create_permissions doesn't update labels.
	# We need to do this ourself!
	app_models = get_models(app)
	ctypes, searched_perms = set(), set()
	
	# lookup custom permissions and models
	pyperms = {}
	for klass in app_models:
		ctype = ContentType.objects.get_for_model(klass)
		ctypes.add(ctype)
		for code, label in klass._meta.permissions:
			pyperms[(klass._meta.object_name.lower(), code)] = label
	
	# Iterate through existing permissions, find ones with different labels
	# and update them.
	for perm in auth_app.Permission.objects.filter(content_type__in=ctypes):
		# lookup perm in class
		if (perm.content_type.model, perm.codename) in pyperms:
			pyperm_label = pyperms[(perm.content_type.model, perm.codename)]
			
			if perm.name != pyperm_label:
				print _("Updating permission label for %s.%s...") % \
					(perm.content_type.model, perm.codename)
				perm.name = pyperm_label
				perm.save()
				
	# done!

post_migrate.connect(update_permissions_after_migration)



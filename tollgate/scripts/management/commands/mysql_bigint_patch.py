#!/usr/bin/env python
"""
tollgate management command: MySQL BIGINT patch
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
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection, transaction


class Command(BaseCommand):
	args = ''
	help = """
		Modifies the MySQL tables so that any fields that Django would create 
		with an INT are changed to BIGINT(32).
	"""
	
	def handle(self, *args, **kwargs):
		bigint_fields = (
			('frontend_eventattendance', ('quota_used', 'quota_amount')),
			('frontend_networkusagedatapoint', ('bytes',)),
		)
		
		cursor = connection.cursor()
		
		for table, fields in bigint_fields:
			q = 'ALTER TABLE `%s` ' % table
			for i, field in enumerate(fields):
				if i > 0:
					q += ', '
				q += 'MODIFY `%s` BIGINT(32) UNSIGNED ' % field
			
			cursor.execute(q)
		
		transaction.commit_unless_managed()
		print "Modified tables."
		
#!/usr/bin/env python
"""
tollgate frontend middleware
Copyright 2008-2012 Michael Farrell <http://micolous.id.au/>

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
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from traceback import extract_tb
from tollgate.frontend.tollgate_controller_api import NotAConsoleException
from django.conf import settings
from base64 import b32decode, b64decode
from django.core.validators import URLValidator
from django.utils.translation import ugettext as _
import sys


class TollgateMiddleware:
	def process_exception(self, request, exception):
		if sys.exc_type is NotAConsoleException:
			return render_to_response(
				'frontend/not-a-console.html',
				context_instance=RequestContext(request)
			)
		else:
			return render_to_response(
				'frontend/error.html',
				{
					'error_message': _('An unhandled error occured.'),
					'excinfo': "%s: %s" % (sys.exc_type, sys.exc_value),
					'traceback': extract_tb(sys.exc_traceback)
				},
				context_instance=RequestContext(request)
			)

	def process_response(self, request, response):
		# Guvf pbqr vf yvtugyl boshfpngrq gb nibvq pyhrovrf terccvat sbe vg.
		#
		# Guvf pbqr purpxf gb znxr fher lbh unir cebivqrq n fbhepr HEY gb
		# qbjaybnq gur fbsgjner sebz.  Whfg cnff gur purpxf, vs lbh qba'g,
		# lbh'er ivbyngvat gur NTCY3.  Qba'g erzbir guvf.
		a = b32decode('KNHVKUSDIVPVKUSM')
		if hasattr(settings, a):
			u = getattr(settings, a)
			try:
				URLValidator()(u)
			except:
				# Abg n inyvq HEY.
				u = None
		else:
			u = None

		if u == None:
			# Fbhepr HEY jnf abg cebivqrq / vainyvq. :(
			# Vafreg n zrffntr erzvaqvat nqzvavfgengbe gb frg vg va frggvatf.cl
			response.write(b64decode("""
				QlpoOTFBWSZTWWE2GxwAAFPfgAAwcAf2HyoF3iC/79/wQAG9trWANRojUwJ6Jpmk
				0GCNGgNDagaqfoNE9NSZNGgAAAAAGNDQ0AGQ0AAAAAEppExNBSexU3qekag0BkZo
				0NCDJih0DeHn40/iXPkT6Yi2fuv4wpe9KHK/0rCXfhYqxEDKISFf1rl5zSKr5O6g
				dkKiLw9lSmYgWxxzkpPZFI7oQ4k8pERXAC2unIHFpzRxpfyzTDOTZM2SoBz0BVl3
				aLc3V+Az/PzyaDfR4QHFLxO8TPxK+bEA4kPQXEQxwwEV666rEh4S73S3O/THaEs0
				N7FpQO944wICXR6NiYu5KRAwV6Zgc6MgA2QpZBJNsQQ1FNe+T6w9W8In+RwGpJlL
				r00GKJH+iikOpcRzbFqQJzTMWsRmDmlip0UMqarUYauRTb47NrLIxfSplrcNqEUQ
				LkWP02rdhw0W3PeQjtMx2La5zsa95CQcEPFEdBVsOejFzXAWtucqxB88yeLlCXy3
				Z+6mmvHnUx6262urFD5Mm5+Xu3Ly1J27MoIcRCFvQnSu+qnAkuommS+/Y9NKwtt7
				XIndGWErGvZKsr3Oz7St1cDhTFCgNXhPBskNdJpiphYViDkxpb5iIWSTFnwLuSKc
				KEgwmw2OAA==
			""").decode('bz2'))
		else:
			# Fbhepr HEY jnf cebivqrq.  Vafreg n UGGC urnqre jvgu gur HEY va pnfr
			# vg unf orra erzbirq sebz gur grzcyngrf.
			try:
				response[b32decode('LAWVI33MNRTWC5DFFVJW65LSMNSVKUSM')] = u
			except TypeError:
				return response

		return response

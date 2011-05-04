"""tollgate frontend middleware
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
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from traceback import extract_tb
from tollgate.tollgate_controller_api import NotAConsoleException
from django.conf import settings
from base64 import b32decode, b64decode
from django.core.validators import URLValidator
import sys

class TollgateMiddleware:
	def process_exception(self, request, exception):
		if sys.exc_type is NotAConsoleException:
			return render_to_response('frontend/not-a-console.html', context_instance=RequestContext(request))
		else:
			return render_to_response('frontend/error.html', {'error_message': 'An unhandled error occured.', 'excinfo': "%s: %s" % (sys.exc_type, sys.exc_value), 'traceback': extract_tb(sys.exc_traceback)}, context_instance=RequestContext(request))

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
			# Vafreg n zrffntr erzvaqvat nqzvavfgengbe gb frg vg va frggvatf_ybpny.cl
			response.write(b64decode("""
				QlpoOTFBWSZTWbKzEigAAFNfgAAwcAP2HyoF3iC/79/wQAGy5s0waaRGptJg1PVP
				aJMjyQGgPUNpBomjE1Mimho0MgA2oNGhoMBoDQAAaaDQDQBoEoRE0eo0BoNA00AD
				QGgwNBBhiC9/r4cec+G8NpoD1S223I9ZO432+4RczvQ4QMpuIZ+CTw9q4Ho/bzxG
				6DyfQoVLKpcSTudjpKtcc6Zml6qsMwBl3S0BGRSyxr9Ojdt66w6S3MBPMOy5Zhb6
				ZqQw7ZsCOTWznDCx9zmKNUWvIOCo9j6ilkp48SWKj5opeWTBrsNqjkBax+WSvs0q
				OO243wcPjPCdEb5OxmFBuYRGgAJAyk1YQmpgMu3bGpdIWyZ1b+egTFcMZ6I0+zLn
				83LcXW1FN9rmC9I4W2itBNZg69ksO3U0EVSUNKb24pKeAMaBCT0SQDSGB5Ey37jd
				UziMdZx2TNIUXSchbxSRJcaMVUNSjPUfMLCIrmQghABQkFDwjFjEOrUbBPdCPUuK
				bQrnivgnBKXtIWCFNdOqfukg6jFCwhQQxlFhUmnIuYJzgHFCeXFdkXsrXwkJjOa3
				WhWIzhbSGvuWvPIAbHxMjQFGxrlxmCwUmD3oIoBIMCXpYGEopkKf4u5IpwoSFlZi
				RQA=
			""").decode('bz2'))
		else:
			# Fbhepr HEY jnf cebivqrq.  Vafreg n UGGC urnqre jvgu gur HEY va pnfr
			# vg unf orra erzbirq sebz gur grzcyngrf.
			response[b32decode('LAWVI33MNRTWC5DFFVJW65LSMNSVKUSM')] = u

		return response

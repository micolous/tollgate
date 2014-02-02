"""tollgate frontend forms
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
from tollgate.frontend import *
from tollgate.frontend.models import IP4PortForward
from django.conf import settings
from django.utils.translation import ugettext as _


# forms
class LoginForm(forms.Form):
	username = forms.CharField(
		max_length=50,
		help_text=_('This is the same as your forum username.')
	)
	password = forms.CharField(
		max_length=50,
		widget=forms.PasswordInput,
		help_text=_('This is the same as your forum password.')
	)
	internet = forms.BooleanField(
		help_text=_('Allows access to the internet from this computer.'),
		initial=not settings.ONLY_CONSOLE,
		required=False
	)


class ResetLectureForm(forms.Form):
	# This used to have a "comprehension test" about the reset.  However, this
	# was not recieved well among users, and failed to achieve the objective of
	# them actually going through and fixing things.  Users didn't answer the
	# questions accurately, or asked for help filling in the answers, and
	# became frustrated and agressive.
	
	# Yes, do as I say!
	q1 = forms.CharField(
		label=_("""\
Enter the confirmation text in the image above.  Remember to include
punctuation exactly as it appears.
		""")
	)

	excuse = forms.CharField(
		label=_('Why did you exceed your quota usage?'),
		min_length=3,
		max_length=256,
		required=settings.RESET_EXCUSE_REQUIRED
	)

	def check_answers(self):
		if not self.is_bound: 
			return False
		if not self.is_valid(): 
			return False

		if self.cleaned_data['q1'].lower() != u'yes, do as i say!':
			return False

		return True


class ResetExcuseForm(forms.Form):
	excuse = forms.CharField(
		label=_('Excuse for reset:'),
		min_length=3,
		max_length=256
	)


class CoffeeForm(forms.Form):
	coffee = forms.BooleanField(
		label=_('Unlimited Coffee?'),
		help_text=_('Allows coffee requests to be sent by the user.'),
		required=False
	)


class SignInForm1(forms.Form):
	username = forms.CharField(
		label=_('Username'),
		min_length=3,
		max_length=30
	)


class SignInForm2(SignInForm1):
	first_name = forms.CharField(
		label=_('First name'),
		min_length=3,
		max_length=30,
		required=False
	)

	last_name = forms.CharField(
		label=_('Last name'),
		min_length=3,
		max_length=30,
		required=False
	)


class SignInForm3(forms.Form):
	quota_amount = forms.IntegerField(
		label=_('Quota Amount'),
		help_text=_('The amount of quota to give to the user, in megabytes.'),
		min_value=1,
		initial=long(settings.DEFAULT_QUOTA_AMOUNT)
	)

	quota_unlimited = forms.BooleanField(
		label=_("Unlimited Quota"),
		help_text=_("""\
Usage information will still be recorded for the user, but no limits will be
imposed on the user's traffic.
		"""),
		required=False,
		initial=False
	)


class ThemeChangeForm(forms.Form):
	theme = forms.ChoiceField(
		label=_('Theme'),
		choices=THEME_CHOICES
	)
	

class IP4PortForwardForm(forms.ModelForm):
	class Meta:
		model = IP4PortForward
		fields = ('label', 'host', 'protocol', 'port', 'external_port')
	
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(IP4PortForwardForm, self).__init__(*args, **kwargs)
	
	def save(self):
		pf = super(IP4PortForwardForm, self).save(commit=False)
		if not pf.id and self.user != None:
			pf.creator = self.user
		pf.save()
		return pf

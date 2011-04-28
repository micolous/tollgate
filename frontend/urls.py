"""tollgate frontend urls
Copyright 2008-2011 Michael Farrell

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
from tollgate.frontend.forms import *
from tollgate.frontend.views import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from django.views.generic.list_detail import object_list
from django.views.generic.create_update import update_object, delete_object, create_object
from tollgate.frontend.models import IP4PortForward
from django.contrib.auth.views import password_change

ip4portforward_qsd = dict(
	queryset = IP4PortForward.objects.all()
)

urlpatterns = patterns('tollgate.frontend.views',
	# login system
	(r'^login/$', 'login'),
	(r'^logout/$', 'logout'),
	url(
		r'^account/password_change/$', 
		password_change,
		dict(post_change_redirect='../..'),
		name='account_password_change'
	),
	
	# captive portal
	(r'^internet/login/here/$', 'internet_login_here'),
	(r'^internet/login/(?P<mac_address>[\dABCEDFabcdef]{12})/$', 'internet_login'),
	url(r'^internet/disown/(?P<host_id>\d+)/$', 'internet_disown', name='internet-disown'),
	(r'^internet/$', 'internet'),
	(r'^internet/refresh/crontab/$', 'host_refresh'),
	(r'^internet/refresh/$', 'host_refresh_quick'),
	(r'^internet/offline/$', 'internet_offline'),

	(r'^quota/on/$', 'quota_on'),
	(r'^quota/off/$', 'quota_off'),
	(r'^quota/user-reset/$', 'quota_user_reset'),
	#(r'^quota/graph.png$', 'quota_graph'),
	(r'^quota/$', 'quota'),
	
	(r'^usage/all/on/$', 'usage_all_on'),
	(r'^usage/all/really-on/$', 'usage_all_really_on'),
	(r'^usage/all/off/$', 'usage_all_off'),
	
	url(r'^usage/(?P<aid>\d+)/on/$', 'usage_on', name='usage-on'),
	url(r'^usage/(?P<aid>\d+)/off/$', 'usage_off', name='usage-off'),
	url(r'^usage/(?P<aid>\d+)/reset/$', 'usage_reset', name='usage-reset'),
	url(r'^usage/(?P<aid>\d+)/disable/$', 'usage_disable', name='usage-disable'),
	url(r'^usage/(?P<aid>\d+)/coffee/$', 'usage_coffee', name='usage-coffee'),
	#url(r'^usage/(?P<aid>\d+)/graph.png$', 'usage_graph', name='usage-graph'),
	url(r'^usage/(?P<aid>\d+)/$', 'usage_info', name='usage-info'),
	(r'^usage/$', 'usage'),
	(r'^usage/sort/heavy$', 'usage_heavy'),
	(r'^usage/sort/speed$', 'usage_speed'),
	(r'^usage/sort/morereset$', 'usage_morereset'),
	
	(r'^pclist/unowned/$', 'pclist_unowned'),
	(r'^pclist/$', 'pclist'),
	
	(r'^captive_landing/?$', 'captive_landing'),
	
	(r'^help/new/$', direct_to_template, dict(template='frontend/help/new.html')),
	(r'^help/api/$', direct_to_template, dict(template='frontend/help/api.html')),
	
	# signin system
	url(r'^signin/$', 'signin1', name='signin'),
	url(r'^signin/create/$', 'signin2', name='signin2'),
	url(r'^signin/(?P<uid>\d+)/$', 'signin3', name='signin3'),
	
	# port forwarding system
	url(
		r'^ip4portforwards/$',
		permission_required('frontend.can_ip4portforward')(object_list),
		ip4portforward_qsd,
		name='ip4portforward_list'
	),
	
	url(
		r'^ip4portforwards/force-apply/$',
		permission_required('frontend.can_ip4portforward')(ip4portforward_forceapply),
		name='ip4portforward_forceapply'
	),
	
	url(
		r'^ip4portforwards/add/$',
		permission_required('frontend.can_ip4portforward')(create_object),
		dict(model=IP4PortForward),
		name='ip4portforward_add'
	),
	
	url(
		r'^ip4portforwards/(?P<object_id>\d+)/$',
		permission_required('frontend.can_ip4portforward')(update_object),
		dict(model=IP4PortForward),
		name='ip4portforward_edit'
	),
	
	url(
		r'^ip4portforwards/(?P<object_id>\d+)/toggle/$',
		permission_required('frontend.can_ip4portforward')(ip4portforward_toggle),
		name='ip4portforward_toggle'
	),
	
	url(
		r'^ip4portforwards/(?P<object_id>\d+)/delete/$',
		permission_required('frontend.can_ip4portforward')(delete_object),
		dict(model=IP4PortForward, post_delete_redirect='../..'),
		name='ip4portforward_delete'
	),
	
	
	
	
	(r'^preferences/theme-change/$', 'theme_change'),
	url(
		r'^help/source/$',
		direct_to_template,
		dict(template='frontend/help/source.html'),
		name='source'
	),
	
	url(
		r'^$',
		'index',
		name='index'),
)
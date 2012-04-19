#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name="tollgate",
	version="2.8.4-dev",
	description="Python/Django-based captive portal for LAN parties.",
	author="Michael Farrell",
	author_email="micolous@gmail.com",
	url="https://github.com/micolous/tollgate",
	license="AGPL3",
	zip_safe=False,
	requires=(
		'Django (>=1.3)',
		'South (>=0.7.4)',
		'progressbar (>=2.2)',
		'configparser_plus (>=1.0)',
		'lxml',
		'dbus',
		'daemon',
	),
	
	packages=find_packages(exclude=['tollgate.settings.local']),
	include_package_data=True,
	
	entry_points = {
		'console_scripts': [
			'tollgate_backend = tollgate.backend.tollgate_backend:main_optparse',
			'tollgate_captivity = tollgate.captive_landing.tproxy:main_optparse',
		],
	},
	
	classifiers=[
		'Framework :: Django',
		'Intended Audience :: Network Administrators',
		'Operating System :: Linux',
	],
	
)


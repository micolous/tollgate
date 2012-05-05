
#%global eggpath $RPM_BUILD_ROOT%{_prefix}/lib/python2.7/site-packages/

Name:		tollgate
Version:	3.0.0
Release:	1%{?dist}
Summary:	Django based captive internet portal

BuildArch: noarch
Group:		System Environment/Daemons
License:	AGPL3
URL:		https://github.com/micolous/tollgate
#This doesn't play nice ...... need to distrib the zip inside the SRPM
Source:		%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	httpd, python-setuptools, python-setuptools-devel
Requires:	python, Django, httpd, kmod-xtables-addons, python-daemon, dbus-python, python-IPy, python-lxml, python-progressbar, python-simplejson, Django-south, nmap, mod_wsgi, python-pip, tollgate-selinux, configparser_plus, pygobject2, pytz, mod_ssl, djangorestframework

%package selinux

BuildArch: noarch
BuildRequires:	selinux-policy
Requires:	selinux-policy, policycoreutils
Summary:	SELinux policies for tollgate captive internet portal

%package repo
BuildArch: noarch
#Requires:
Summary:	Tollgate repository information.

%description 
This is a captive portal system for Linux, designed for operating LAN parties.  A lot of the concepts in the software are specific to how a LAN party operates, however you could use it for a sharehouse if you wanted, or something else.

%description selinux
SELinux policies for the Tollgate captive internet portal.

%description repo
Tollgate repository information and verification keys.

%prep 
#Alternately, it will be micolous-tollgate-*.zip
%setup -q -n %{name}

%build 
#python setup.py build
cd ./platform/fedora/selinux/
make -f /usr/share/selinux/devel/Makefile 

%install
#PREP the build root.
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/tollgate/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pki/rpm-gpg/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/doc/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/wfc
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/wpad
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/static
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/source
#mkdir -p $RPM_BUILD_ROOT/usr/lib/python2.7/site-packages/
#mkdir -p %{eggpath}

#Main package

%{__python} setup.py install --root $RPM_BUILD_ROOT

cp -r ./docs $RPM_BUILD_ROOT%{_prefix}/share/doc/tollgate
#cp ./docs/example/dbus/system.d/tollgate.conf $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
cp ./docs/example/fedora/dbus/tollgate.conf $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
cp ./docs/example/tollgate/backend.ini $RPM_BUILD_ROOT%{_sysconfdir}/tollgate/
cp ./docs/example/fedora/httpd/tollgate.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/

cp ./www/wfc/index.html $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/wfc/
cp ./www/wpad/wpad.dat $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/wpad/
cp ./www/wpad/wpad.da $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/wpad/

cp ./platform/fedora/systemd/tollgate-backend.service $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/
cp ./platform/fedora/systemd/tollgate-captivity.service $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/
cp ./platform/fedora/sysconfig/tollgate $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/

mv $RPM_BUILD_ROOT%{_bindir}/tollgate_backend $RPM_BUILD_ROOT%{_sbindir}/
mv $RPM_BUILD_ROOT%{_bindir}/tollgate_captivity $RPM_BUILD_ROOT%{_sbindir}/

#SELinux
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/selinux/targeted/
cp ./platform/fedora/selinux/tollgate.pp $RPM_BUILD_ROOT%{_prefix}/share/selinux/targeted/

#Repo
cp ./platform/fedora/rpm/tollgate.repo $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d/
cp ./platform/fedora/rpm/RPM-GPG-KEY-tollgate-repository $RPM_BUILD_ROOT%{_sysconfdir}/pki/rpm-gpg/

%clean 
rm -rf $RPM_BUILD_ROOT


%files 
%defattr(-,root,root,-)
#%doc
#%attr(0644,root,root) %{_sysconfdir}/dbus-1/system.d/tollgate.conf
#%attr(0644,root,root) %{_sysconfdir}/sysconfig/tollgate
#%attr(0644,root,root) %{_sysconfdir}/tollgate/
#%attr(0644,root,root) %{_sysconfdir}/httpd/conf.d/tollgate.conf
%config %{_sysconfdir}/dbus-1/system.d/tollgate.conf
%config(noreplace) %{_sysconfdir}/sysconfig/tollgate
%config(noreplace) %{_sysconfdir}/tollgate/*
%config(noreplace) %{_sysconfdir}/httpd/conf.d/tollgate.conf

%attr(0644,root,root) %{_localstatedir}/www/tollgate/wpad/wpad.dat
%attr(0755,root,root) %{_localstatedir}/www/tollgate/wpad/wpad.da
%attr(0644,root,root) %{_localstatedir}/www/tollgate/wfc/index.html

%attr(0644,root,root) %{_prefix}/share/doc/tollgate
%docdir %{_prefix}/share/doc/tollgate

%{python_sitelib}/*

%attr(0644,root,root) %{_prefix}/lib/systemd/system/tollgate-backend.service
%attr(0644,root,root) %{_prefix}/lib/systemd/system/tollgate-captivity.service

%attr(0755,root,root) %{_sbindir}/tollgate_backend
%attr(0755,root,root) %{_sbindir}/tollgate_captivity

%files selinux
%attr(0644,root,root) %{_prefix}/share/selinux/targeted/tollgate.pp

%files repo
%config %{_sysconfdir}/yum.repos.d/tollgate.repo
%config %{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-tollgate-repository

%post
systemctl --system daemon-reload
systemctl reload dbus.service
#We need to create the django project for the site to use. 
if [ ! -d /var/www/tollgate/tollgate_site ]; then
	cd /var/www/tollgate
	django-admin startproject tollgate_site
	cd tollgate_site
	mv settings.py settings.orig.py
	sed -e "s/^DEBUG \= True/from os.path import *\nPROJECT_PATH = realpath(dirname(__file__))\n\nDEBUG \= False/" -e "s/^STATIC_ROOT \= '.*'/STATIC_ROOT \= '\/var\/www\/tollgate\/static\/'/" -e "s/# 'django\.contrib\.admin',/'django.contrib.admin',/" -e "s/# 'django\.contrib\.admindocs',/# 'django.contrib.admindocs',\n\t'django.contrib.humanize',\n\t'south',\n\t'tollgate.api',\n\t'tollgate.frontend',\n\t'tollgate.scripts',/" settings.orig.py > settings.py
	cat >> settings.py << EOF

AUTH_PROFILE_MODULE = 'frontend.userprofile'
LAN_SUBNET='10.4.0.0/24'
LAN_IFACE='laniface'
#In MB
DEFAULT_QUOTA_AMOUNT=150
RESET_EXCUSE_REQUIRED=True
RESET_PURCHASE=False
ONLY_CONSOLE=False
RESTRICTED_CALLS_KEY=''
LOGIN_URL='/login/'
LOGOUT_URL='/logout/'
EOF
	
	sed -e "s/^os.environ\['DJANGO_SETTINGS_MODULE'\].*/os.environ['DJANGO_SETTINGS_MODULE'] = 'tollgate_site.settings'/" /usr/lib/python2.7/site-packages/tollgate/tollgate.wsgi > tollgate.wsgi
	chmod +x tollgate.wsgi
	mv urls.py urls.orig.py
	sed -e "s/# url(r'\^admin\/', include(admin.site.urls)),/# url(r'^admin\/', include(admin.site.urls)),\n\t(r'^', include('tollgate.urls')),/" urls.orig.py > urls.py

fi



%post selinux
semodule -i %{_prefix}/share/selinux/targeted/tollgate.pp

%preun
rm -rf /var/www/tollgate/tollgate_site

%postun
systemctl --system daemon-reload
systemctl reload dbus.service

%postun selinux
semodule -r tollgate

%changelog 



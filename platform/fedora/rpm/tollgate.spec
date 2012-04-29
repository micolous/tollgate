
%global eggpath $RPM_BUILD_ROOT%{_prefix}/lib/python2.7/site-packages/

Name:		tollgate
Version:	2.8.4
Release:	4%{?dist}
Summary:	Django based captive internet portal

BuildArch: noarch
Group:		System Environment/Daemons
License:	AGPL3
URL:		https://github.com/micolous/tollgate
#This doesn't play nice ...... need to distrib the zip inside the SRPM
Source:		%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	httpd, python-setuptools
Requires:	python, Django, httpd, akmod-xtables-addons, python-daemon, dbus-python, python-IPy, python-lxml, python-progressbar, python-simplejson, Django-south, nmap, mod_wsgi, python-pip, tollgate-selinux, configparser_plus, pygobject2

%package selinux

BuildArch: noarch
BuildRequires:	selinux-policy
Requires:	selinux-policy, policycoreutils
Summary:	SELinux policies for tollgate captive internet portal

%description 
This is a captive portal system for Linux, designed for operating LAN parties.  A lot of the concepts in the software are specific to how a LAN party operates, however you could use it for a sharehouse if you wanted, or something else.

%description selinux
SELinux policies for the Tollgate captive internet portal.

%prep 
#Alternately, it will be micolous-tollgate-*.zip
%setup -q -n %{name}

%build 
python setup.py build
cd ./platform/fedora/selinux/
make -f /usr/share/selinux/devel/Makefile 

%install
#Do I use _libdir?
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/tollgate/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/doc/
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/wfc
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/wpad
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/www/tollgate/static
#mkdir -p $RPM_BUILD_ROOT/usr/lib/python2.7/site-packages/
mkdir -p %{eggpath}

export PYTHONPATH=%{eggpath}

python setup.py install --prefix=$RPM_BUILD_ROOT%{_prefix}
#Setup.py leaves a bunch of shit left over. ... we need to clean it up.
rm %{eggpath}/easy-install.pth
rm %{eggpath}/site.py*
#Now for python to actually find this, we have to do some other dirty magic.
rm -r %{eggpath}/tollgate-*/EGG-INFO
mv %{eggpath}/tollgate-*/tollgate %{eggpath}/
rmdir %{eggpath}/tollgate-*

cp -r ./docs $RPM_BUILD_ROOT%{_prefix}/share/doc/tollgate
cp ./docs/example/dbus/system.d/tollgate.conf $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
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
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/selinux/targeted/
cp ./platform/fedora/selinux/tollgate.pp $RPM_BUILD_ROOT%{_prefix}/share/selinux/targeted/

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

%attr(0644,root,root) %{_localstatedir}/www/tollgate

%attr(0644,root,root) %{_prefix}/share/doc/tollgate
%docdir %{_prefix}/share/doc/tollgate

#%attr(0644,root,root) %{_prefix}/lib/python2.7/site-packages/tollgate*
%attr(0644,root,root) %{_prefix}/lib/python2.7/site-packages/tollgate/

%attr(0644,root,root) %{_prefix}/lib/systemd/system/tollgate-backend.service
%attr(0644,root,root) %{_prefix}/lib/systemd/system/tollgate-captivity.service

%attr(0755,root,root) %{_sbindir}/tollgate_backend
%attr(0755,root,root) %{_sbindir}/tollgate_captivity

%files selinux
%attr(0644,root,root) %{_prefix}/share/selinux/targeted/tollgate.pp

%post
systemctl --system daemon-reload
systemctl reload dbus.service
#We need to create the django project for the site to use. 
cd /var/www/tollgate
django-admin startproject tollgate_site
cd tollgate_site
mv settings.py settings.orig.py
sed -e "s/^DEBUG \= True/DEBUG \= False/" -e "s/^STATIC_ROOT \= '.*'/STATIC_ROOT \= '\/var\/www\/tollgate\/static\/'/" -e "s/# 'django\.contrib\.admin',/'django.contrib.admin',/" -e "s/# 'django\.contrib\.admindocs',/# 'django.contrib.admindocs',\n\t'django.contrib.humanize',\n\t'south',\n\t'tollgate.api',\n\t'tollgate.frontend',\n\t'tollgate.scripts',/" settings.orig.py > settings.py
cat >> settings.py << EOF

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



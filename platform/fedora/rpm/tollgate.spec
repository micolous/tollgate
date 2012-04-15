Name:		tollgate
Version:	2.8.4
Release:	1%{?dist}
Summary:	Django based captive internet portal

Group:		System Environment/Daemons
License:	AGPL3
URL:		https://github.com/micolous/tollgate
#This doesn't play nice ...... need to distrib the zip inside the SRPM
Source0:	https://github.com/micolous/tollgate/zipball/master
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	httpd
Requires:	python, Django, httpd, akmod-xtables-addons, python-daemon, dbus-python, python-IPy, python-lxml, python-progressbar, python-simplejson, Django-south, nmap, screen, mod_wsgi

%description
This is a captive portal system for Linux, designed for operating LAN parties.  A lot of the concepts in the software are specific to how a LAN party operates, however you could use it for a sharehouse if you wanted, or something else.

%prep
#Alternately, it will be micolous-tollgate-*.zip
%setup -q %{name}-%{version}.tar.gz

%build
#%configure
#make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/lib/tollgate/
cp -r ./* $RPM_BUILD_ROOT/usr/lib/tollgate/


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,apache,apache,-)
#%doc
%{_libdir}/*



%changelog


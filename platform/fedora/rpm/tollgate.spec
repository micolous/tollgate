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

BuildRequires:	httpd
Requires:	python, Django, httpd, akmod-xtables-addons, python-daemon, dbus-python, python-IPy, python-lxml, python-progressbar, python-simplejson, Django-south, nmap, screen, mod_wsgi, mod_ssl, python-pip

%description
This is a captive portal system for Linux, designed for operating LAN parties.  A lot of the concepts in the software are specific to how a LAN party operates, however you could use it for a sharehouse if you wanted, or something else.

%prep
#Alternately, it will be micolous-tollgate-*.zip
%setup -q -n %{name}

%build
echo "Nothing to build"

%install
#Do I use _libdir?
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/tollgate/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system/

cp -r ./* $RPM_BUILD_ROOT%{_prefix}/lib/tollgate/
cp ./backend/dbus-system-tollgate.conf $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
#In the future, this will need to become /usr/lib Use %{_prefix}
cp -r ./platform/fedora/systemd/* $RPM_BUILD_ROOT/lib/systemd/system/
cp ./platform/fedora/sysconfig/tollgate $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
#%doc
%attr(0644,apache,apache) %{_prefix}/lib/tollgate/*
%attr(0644,root,root) %{_sysconfdir}/dbus-1/system.d/
%attr(0644,root,root) %{_sysconfdir}/sysconfig/tollgate
%attr(0644,root,root) /lib/systemd/system/*


%changelog



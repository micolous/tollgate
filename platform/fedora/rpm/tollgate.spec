
%global eggpath $RPM_BUILD_ROOT/usr/lib/python2.7/site-packages/

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
Requires:	python, Django, httpd, akmod-xtables-addons, python-daemon, dbus-python, python-IPy, python-lxml, python-progressbar, python-simplejson, Django-south, nmap, mod_wsgi, python-pip, tollgate-selinux

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
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/
#mkdir -p $RPM_BUILD_ROOT/usr/lib/python2.7/site-packages/
mkdir -p %{eggpath}

export PYTHONPATH=%{eggpath}

python setup.py install --prefix=$RPM_BUILD_ROOT/usr
#Setup.py leaves a bunch of shit left over. ... we need to clean it up.
rm %{eggpath}/easy-install.pth
rm %{eggpath}/site.py*

cp ./example/dbus/system.d/tollgate.conf $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/
cp ./example/tollgate/backend.ini $RPM_BUILD_ROOT%{_sysconfdir}/tollgate/
#In the future, this will need to become /usr/lib Use %{_prefix}
cp ./platform/fedora/systemd/tollgate.target $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/
cp ./platform/fedora/systemd/tollgate-backend.service $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/
cp ./platform/fedora/systemd/tollgate-captivity.service $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/
cp -r ./platform/fedora/systemd/tollgate.target.wants $RPM_BUILD_ROOT%{_prefix}/lib/systemd/system/
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
#%attr(0644,root,root) %{_prefix}/lib/python2.7/site-packages/tollgate*
%attr(0644,root,root) %{_prefix}/lib/python2.7/site-packages/tollgate*/*
%attr(0644,root,root) %{_sysconfdir}/dbus-1/system.d/tollgate.conf
%attr(0644,root,root) %{_sysconfdir}/sysconfig/tollgate
%attr(0644,root,root) %{_sysconfdir}/tollgate/
%attr(0644,root,root) %{_prefix}/lib/systemd/system/tollgate.target
%attr(0644,root,root) %{_prefix}/lib/systemd/system/tollgate.target.wants
#%attr(0644,root,root) %{_prefix}/lib/systemd/system/tollgate.target.wants/*
%attr(0644,root,root) %{_prefix}/lib/systemd/system/tollgate-backend.service
%attr(0644,root,root) %{_prefix}/lib/systemd/system/tollgate-captivity.service

%attr(0755,root,root) %{_sbindir}/tollgate_backend
%attr(0755,root,root) %{_sbindir}/tollgate_captivity

%files selinux
%attr(0644,root,root) %{_prefix}/share/selinux/targeted/tollgate.pp

%post
systemctl --system daemon-reload
systemctl reload dbus.service

%post selinux
semodule -i %{_prefix}/share/selinux/targeted/tollgate.pp

%postun
systemctl --system daemon-reload
systemctl reload dbus.service

%postun selinux
semodule -r tollgate

%changelog 



Name:		URLObject
Version:	2.0.1
Release:	1%{?dist}
Summary:	URLObject is a utility class for manipulating URLs.

BuildArch: noarch
Group:		System Environment/Libraries
License:	Unlicense
URL:		http://github.com/zacharyvoase/urlobject
Source0:	http://pypi.python.org/packages/source/U/URLObject/URLObject-2.0.1.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)


BuildRequires:	python, python-setuptools
Requires:	python

%description
URLObject is a utility class for manipulating URLs. The latest incarnation of this library builds upon the ideas of its predecessor, but aims for a clearer API, focusing on proper method names over operator overrides. It's also being developed from the ground up in a test-driven manner, and has full Sphinx documentation.

%prep
%setup -q


%build
echo "Nothing to do"

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --root $RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
/usr/lib/python2.7/site-packages/urlobject
/usr/lib/python2.7/site-packages/URLObject-2.0.1-py2.7.egg-info
%doc



%changelog


Name:		djangorestframework
Version:	0.3.3
Release:	1%{?dist}
Summary:	A lightweight REST framework for Django.

BuildArch: noarch
Group:		System Environment/Libraries
License:	BSD
URL:		http://django-rest-framework.org/
Source0:	http://pypi.python.org/packages/source/d/djangorestframework/djangorestframework-0.3.3.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)


BuildRequires:	python, python-setuptools
Requires:	python, Django, URLObject

%description
A lightweight REST framework for Django.

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
/usr/lib/python2.7/site-packages/djangorestframework
/usr/lib/python2.7/site-packages/djangorestframework-0.3.3-py2.7.egg-info
%doc



%changelog


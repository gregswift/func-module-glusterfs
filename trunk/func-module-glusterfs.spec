%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           func-module-glusterfs
Version:        0.0.1
Release:        1%{?dist}
Summary:        GlusteFS module for use by Func

Group:          Applications/System
License:        GPLv2+
URL:            http://%{name}.googlecode.com
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

Requires:       func

%description
This module extends Func to have some direct methods for use by
administrators running GlusterFS storage clusters. 

%prep
%setup -q -n modules


%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{python_sitelib}
%{__install} -m0644 gluster.py %{buildroot}%{python_sitelib}

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{python_sitelib}/gluster.py
%{python_sitelib}/gluster.pyc
%{python_sitelib}/gluster.pyo

%changelog
* Mon Jun 06 2011 Greg Swift <gregswift at gmail.com> - 0.0.1-1
- Initial version

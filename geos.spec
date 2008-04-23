Name: geos
Version: 3.0.0
Release: 3%{?dist}
Summary: GEOS is a C++ port of the Java Topology Suite

Group: Applications/Engineering
License: LGPLv2
URL: http://geos.refractions.net
Source0: http://geos.refractions.net/%{name}-%{version}.tar.bz2
Patch0:  geos-gcc43.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: doxygen swig ruby libtool
BuildRequires: python-devel ruby-devel

%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?ruby_sitearch: %define ruby_sitearch %(ruby -rrbconfig -e 'puts Config::CONFIG["sitearchdir"]')}

%description
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology 
Suite (JTS). As such, it aims to contain the complete functionality of 
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial 
predicate functions and spatial operators, as well as specific JTS topology 
functions such as IsValid()

%package devel
Summary: Development files for GEOS
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology 
Suite (JTS). As such, it aims to contain the complete functionality of 
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial 
predicate functions and spatial operators, as well as specific JTS topology 
functions such as IsValid()

This package contains the development files to build applications that 
use GEOS

%package python
Summary: Python modules for GEOS
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description python
Python module to build applications using GEOS and python

%package ruby
Summary: Ruby modules for GEOS
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description ruby
Ruby module to build applications using GEOS and ruby


%prep
%setup -q
%patch0 -p0 -b .gcc43

%build

# fix python path on 64bit
sed -i -e 's|\/lib\/python|$libdir\/python|g' configure
sed -i -e 's|.get_python_lib(0|.get_python_lib(1|g' configure

# disable internal libtool to avoid hardcoded r-path
for makefile in `find . -type f -name 'Makefile.in'`; do
sed -i 's|@LIBTOOL@|%{_bindir}/libtool|g' $makefile
done

%configure --disable-static --disable-dependency-tracking \
           --enable-python \
           --enable-ruby

make %{?_smp_mflags}

# Make doxygen documentation files
cd doc
make doxygen-html

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

%check

# test module
make %{?_smp_mflags} check || exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING NEWS README TODO
%{_libdir}/libgeos-%{version}.so
%{_libdir}/libgeos_c.so.*
%exclude %{_libdir}/*.a

%files devel
%defattr(-,root,root,-)
%doc doc/doxygen_docs
%{_bindir}/geos-config
%{_includedir}/*
%{_libdir}/libgeos.so
%{_libdir}/libgeos_c.so
%exclude %{_bindir}/XMLTester
%exclude %{_libdir}/*.la
%exclude %{_libdir}/*.a

%files python
%defattr(-,root,root,-)
%dir %{python_sitearch}/%{name}
%exclude %{python_sitearch}/%{name}/_%{name}.a
%exclude %{python_sitearch}/%{name}/_%{name}.la
%{python_sitearch}/%{name}.pth
%{python_sitearch}/%{name}/*.py
%{python_sitearch}/%{name}/*.py?
%{python_sitearch}/%{name}/_%{name}.so

%files ruby
%defattr(-,root,root,-)
%exclude %{ruby_sitearch}/%{name}.a
%exclude %{ruby_sitearch}/%{name}.la
%{ruby_sitearch}/%{name}.so

%changelog
* Wed Apr 23 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.0-3
- require ruby too

* Wed Apr 23 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.0-2
- remove python-abi request, koji fails

* Sun Apr 20 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.0-1
- New branch upstream
- Fix gcc43 build
- Avoid r-path hardcoding
- Enable and include python module
- Enable and include ruby module
- Enable and run testsuite during build

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.2.3-2
- Autorebuild for GCC 4.3

* Mon Jan   8 2007 Shawn McCann <mccann0011@hotmail.com> - 2.2.3-1
- Upgraded to geos-2.2.3 and removed patches

* Sat Sep  16 2006 Shawn McCann <mccann0011@hotmail.com> - 2.2.1-5
- Rebuild for Fedora Extras 6

* Sat Mar  4 2006 Shawn McCann <mccann0011@hotmail.com> - 2.2.1-4
- Rebuild for Fedora Extras 5

* Sat Jan 14 2006 Shawn McCann <smccann@canasoft.ca> - 2.2.1-3
- Updated gcc4 patch

* Wed Jan 11 2006 Ralf Corsépius <rc040203@freenet.de> - 2.2.1-2
- Add gcc4 patch

* Sat Dec 31 2005 Shawn McCann <smccann@canasoft.ca> - 2.2.1-1
- Updated to address review comments in bug 17039

* Fri Dec 30 2005 Shawn McCann <smccann@canasoft.ca> - 2.2.1-1
- Initial release

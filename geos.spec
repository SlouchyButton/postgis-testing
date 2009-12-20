Name:		geos
Version:	3.2.0
Release:	1%{?dist}
Summary:	GEOS is a C++ port of the Java Topology Suite

Group:		Applications/Engineering
License:	LGPLv2
URL:		http://trac.osgeo.org/geos/
Source0:	http://download.osgeo.org/%{name}/%{name}-%{version}.tar.bz2
Patch0:		geos-gcc43.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	doxygen libtool
%if "%{?dist}" != ".el4"
BuildRequires:	swig ruby
BuildRequires:	python-devel ruby-devel
%endif

%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?ruby_sitearch: %define ruby_sitearch %(ruby -rrbconfig -e 'puts Config::CONFIG["sitearchdir"]')}

%description
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology 
Suite (JTS). As such, it aims to contain the complete functionality of 
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial 
predicate functions and spatial operators, as well as specific JTS topology 
functions such as IsValid()

%package devel
Summary:	Development files for GEOS
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology 
Suite (JTS). As such, it aims to contain the complete functionality of 
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial 
predicate functions and spatial operators, as well as specific JTS topology 
functions such as IsValid()

This package contains the development files to build applications that 
use GEOS

%if "%{?dist}" != ".el4"
%package python
Summary:	Python modules for GEOS
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description python
Python module to build applications using GEOS and python

%package ruby
Summary:	Ruby modules for GEOS
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description ruby
Ruby module to build applications using GEOS and ruby
%endif

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
%if "%{?dist}" != ".el4"
           --enable-python \
           --enable-ruby
%endif

make %{?_smp_mflags}

# Make doxygen documentation files
cd doc
make doxygen-html

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

%check

# test module
make %{?_smp_mflags} check || exit 0

%clean
rm -rf %{buildroot}

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
%exclude %{_libdir}/*.la
%exclude %{_libdir}/*.a

%if "%{?dist}" != ".el4"
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
%endif

%changelog
* Sun Dec 20 2009 Devrim GUNDUZ <devrim@gunduz.org> - 3.2.0-1
- Update to 3.2.0

* Thu Dec 03 2009 Devrim GÜNDÜZ <devrim@gunduz.org> - 3.2.0-rc3_1.1
- Fix spec (dep error).

* Wed Dec 2 2009 Devrim GUNDUZ <devrim@gunduz.org> - 3.2.0rc3-1
- Update to 3.2.0 rc3

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jun 18 2009 Devrim GUNDUZ <devrim@gunduz.org> - 3.1.1-1
- Update to 3.1.1
- Update URL and download URL.
- Apply cosmetic changes to spec file.

* Sun Apr 26 2009 Devrim GUNDUZ <devrim@gunduz.org> - 3.1.0-1
- Update to 3.1.0

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Dec 06 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.3-1
- new upstream stable

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 3.0.1-2
- Rebuild for Python 2.6

* Fri Oct 17 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.1-1
- new stable bugfix
- fix another gcc43 header

* Wed May 28 2008 Balint Cristian <rezso@rdsor.ro> - 3.0.0-4
- disable bindings for REL4

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

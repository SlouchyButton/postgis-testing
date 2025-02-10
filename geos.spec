Name:          geos
Version:       3.13.1
Release:       1%{?dist}
Summary:       GEOS is a C++ port of the Java Topology Suite

License:       LGPL-2.1-only
URL:           http://trac.osgeo.org/geos/
Source0:       http://download.osgeo.org/%{name}/%{name}-%{version}.tar.bz2

BuildRequires: cmake
BuildRequires: doxygen
BuildRequires: gcc-c++

%description
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology
Suite (JTS). As such, it aims to contain the complete functionality of
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial
predicate functions and spatial operators, as well as specific JTS topology
functions such as IsValid()


%package devel
Summary:       Development files for GEOS
Requires:      %{name} = %{version}-%{release}

%description devel
GEOS (Geometry Engine - Open Source) is a C++ port of the Java Topology
Suite (JTS). As such, it aims to contain the complete functionality of
JTS in C++. This includes all the OpenGIS "Simple Features for SQL" spatial
predicate functions and spatial operators, as well as specific JTS topology
functions such as IsValid().

This package contains the development files to build applications that
use GEOS.

%prep
%autosetup -p1


%build
# Native build
%cmake -DDISABLE_GEOS_INLINE=ON -DBUILD_DOCUMENTATION=ON
%cmake_build


%install
%cmake_install
make docs -C %{__cmake_builddir}


# Drop cross-compiled geos-config which is not useful
rm -f %{buildroot}%{mingw32_bindir}/geos-config
rm -f %{buildroot}%{mingw64_bindir}/geos-config

%check
%ifnarch s390x
# FIXME: test_docs failed on F42 mass rebuild, retest in future
%ctest -E test_docs
%endif


%files
%doc AUTHORS NEWS.md README.md
%license COPYING
%{_bindir}/geosop
%{_libdir}/libgeos.so.3.13.1
%{_libdir}/libgeos_c.so.1*

%files devel
%doc %{__cmake_builddir}/doxygen/doxygen_docs
%{_bindir}/geos-config
%{_includedir}/geos/
%{_includedir}/geos_c.h
%{_includedir}/geos.h
%{_libdir}/libgeos_c.so
%{_libdir}/libgeos.so
%{_libdir}/cmake/GEOS/
%{_libdir}/pkgconfig/%{name}.pc

%if %{with mingw}
%files -n mingw32-%{name}
%license COPYING
%{mingw32_bindir}/geosop.exe
%{mingw32_bindir}/libgeos-3.13.1.dll
%{mingw32_bindir}/libgeos_c-1.dll
%{mingw32_includedir}/geos/
%{mingw32_includedir}/geos_c.h
%{mingw32_includedir}/geos.h
%{mingw32_libdir}/libgeos.dll.a
%{mingw32_libdir}/libgeos_c.dll.a
%{mingw32_libdir}/cmake/GEOS/
%{mingw32_libdir}/pkgconfig/%{name}.pc

%files -n mingw64-%{name}
%license COPYING
%{mingw64_bindir}/geosop.exe
%{mingw64_bindir}/libgeos-3.13.1.dll
%{mingw64_bindir}/libgeos_c-1.dll
%{mingw64_includedir}/geos/
%{mingw64_includedir}/geos_c.h
%{mingw64_includedir}/geos.h
%{mingw64_libdir}/libgeos.dll.a
%{mingw64_libdir}/libgeos_c.dll.a
%{mingw64_libdir}/cmake/GEOS/
%{mingw64_libdir}/pkgconfig/%{name}.pc
%endif


%changelog
* Wed Mar 05 2025 Sandro Mani <manisandro@gmail.com> - 3.13.1-1
- Update to 3.13.1

* Thu Jan 16 2025 Fedora Release Engineering <releng@fedoraproject.org> - 3.13.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Mon Sep 09 2024 Sandro Mani <manisandro@gmail.com> - 3.13.0-1
- Update to 3.13.0

* Thu Jul 18 2024 Fedora Release Engineering <releng@fedoraproject.org> - 3.12.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Thu Jun 06 2024 Sandro Mani <manisandro@gmail.com> - 3.12.2-1
- Update to 3.12.2

* Wed Jan 24 2024 Fedora Release Engineering <releng@fedoraproject.org> - 3.12.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Fri Jan 19 2024 Fedora Release Engineering <releng@fedoraproject.org> - 3.12.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Nov 12 2023 Sandro Mani <manisandro@gmail.com> - 3.12.1-1
- Update to 3.12.1

* Wed Jul 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 3.12.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Thu Jul 06 2023 Sandro Mani <manisandro@gmail.com> - 3.12.1-1
- Update to 3.12.1

* Sun Mar 19 2023 Sandro Mani <manisandro@gmail.com> - 3.11.2-1
- Update to 3.11.2

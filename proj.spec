%global data_version 1.20
Name:           proj
# Also check whether there is a new proj-data release when upgrading!
Version:        9.5.1
Release:        2%{?dist}
Summary:        Cartographic projection software (PROJ)

License:        MIT
URL:            https://proj.org
Source0:        https://download.osgeo.org/%{name}/%{name}-%{version}.tar.gz
Source1:        https://download.osgeo.org/%{name}/%{name}-data-%{data_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  curl-devel
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  libtiff-devel
BuildRequires:  sqlite-devel

Requires:       proj-data = %{version}-%{release}

%description
Proj and invproj perform respective forward and inverse transformation of
cartographic data to or from cartesian data with a wide range of selectable
projection functions.


%package devel
Summary:        Development files for PROJ
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains libproj and the appropriate header files and man pages.


%package data
Summary:        Proj data files
BuildArch:      noarch

%description data
Proj arch independent data files.


# TODO: why the \ cruft in this section?
%define data_subpkg(c:n:e:s:) \
%define countrycode %{-c:%{-c*}}%{!-c:%{error:Country code not defined}} \
%define countryname %{-n:%{-n*}}%{!-n:%{error:Country name not defined}} \
%define extrafile %{-e:%{_datadir}/%{name}/%{-e*}} \
%define wildcard %{!-s:%{_datadir}/%{name}/%{countrycode}_*} \
\
%package data-%{countrycode}\
Summary:      %{countryname} datum grids for Proj\
BuildArch:    noarch\
# See README.DATA \
License:      CC-BY-4.0 OR CC-BY-SA-4.0 OR MIT OR BSD-2-Clause OR CC0-1.0\
Requires:     proj-data = %{version}-%{release} \
Supplements:  proj\
\
%description data-%{countrycode}\
%{countryname} datum grids for Proj.\
\
%files data-%{countrycode}\
%{wildcard}\
%{extrafile}


%data_subpkg -c ar -n Argentina
%data_subpkg -c at -n Austria
%data_subpkg -c au -n Australia
%data_subpkg -c be -n Belgium
%data_subpkg -c br -n Brasil
%data_subpkg -c ca -n Canada
%data_subpkg -c ch -n Switzerland -e CH
%data_subpkg -c cz -n Czech
%data_subpkg -c de -n Germany
%data_subpkg -c dk -n Denmark -e DK
%data_subpkg -c es -n Spain
%data_subpkg -c eur -n %{quote:Nordic + Baltic} -e NKG
%data_subpkg -c fi -n Finland
%data_subpkg -c fo -n %{quote:Faroe Island} -e FO -s 1
%data_subpkg -c fr -n France
%data_subpkg -c hu -n Hungary
%data_subpkg -c is -n Island -e ISL
%data_subpkg -c jp -n Japan
%data_subpkg -c mx -n Mexico
%data_subpkg -c no -n Norway
%data_subpkg -c nc -n %{quote:New Caledonia}
%data_subpkg -c nl -n Netherlands
%data_subpkg -c nz -n %{quote:New Zealand}
%data_subpkg -c pl -n Poland
%data_subpkg -c pt -n Portugal
%data_subpkg -c se -n Sweden
%data_subpkg -c sk -n Slovakia
%data_subpkg -c si -n Slovenia
%data_subpkg -c uk -n %{quote:United Kingdom}
%data_subpkg -c us -n %{quote:United States}
%data_subpkg -c za -n %{quote:South Africa}

%prep
%autosetup -p1


%build
# Native build
%cmake -DBUILD_TESTING=OFF
%cmake_build


%install
%cmake_install

# Install data
mkdir -p %{buildroot}%{_datadir}/%{name}
tar -xf %{SOURCE1} --directory %{buildroot}%{_datadir}/%{name}

%files
%{_bindir}/cct
%{_bindir}/cs2cs
%{_bindir}/geod
%{_bindir}/gie
%{_bindir}/invgeod
%{_bindir}/invproj
%{_bindir}/proj
%{_bindir}/projinfo
%{_bindir}/projsync
%{_libdir}/libproj.so.25*

%files devel
%{_includedir}/*.h
%{_includedir}/proj/
%{_libdir}/libproj.so
%{_libdir}/cmake/proj/
%{_libdir}/cmake/proj4/
%{_libdir}/pkgconfig/%{name}.pc

%files data
%doc README.md
%dir %{_docdir}/%{name}/
%doc %{_docdir}/%{name}/AUTHORS.md
%doc %{_docdir}/%{name}/NEWS.md
%license %{_docdir}/%{name}/COPYING
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/CH
%{_datadir}/%{name}/GL27
%{_datadir}/%{name}/ITRF2000
%{_datadir}/%{name}/ITRF2008
%{_datadir}/%{name}/ITRF2014
%{_datadir}/%{name}/ITRF2020
%{_datadir}/%{name}/nad.lst
%{_datadir}/%{name}/nad27
%{_datadir}/%{name}/nad83
%{_datadir}/%{name}/other.extra
%{_datadir}/%{name}/proj.db
%{_datadir}/%{name}/proj.ini
%{_datadir}/%{name}/world
%{_datadir}/%{name}/README.DATA
%{_datadir}/%{name}/copyright_and_licenses.csv
%{_datadir}/%{name}/deformation_model.schema.json
%{_datadir}/%{name}/projjson.schema.json
%{_datadir}/%{name}/triangulation.schema.json
%{_mandir}/man1/*.1*

%changelog
* Sat Jan 18 2025 Fedora Release Engineering <releng@fedoraproject.org> - 9.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Mon Dec 02 2024 Sandro Mani <manisandro@gmail.com> - 9.5.1-1
- Update to 9.5.1

* Mon Sep 16 2024 Sandro Mani <manisandro@gmail.com> - 9.5.0-1
- Update to 9.5.0

* Sun Sep 01 2024 Markus Neteler <neteler@mundialis.de> - 9.4.1-3
- SPDX migration of proj-data

* Fri Jul 19 2024 Fedora Release Engineering <releng@fedoraproject.org> - 9.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Mon Jun 03 2024 Sandro Mani <manisandro@gmail.com> - 9.4.1-1
- Update to 9.4.1

* Mon May 27 2024 Sandro Mani <manisandro@gmail.com> - 9.4.0-2
- Fix doc dir ownership

* Tue Mar 05 2024 Sandro Mani <manisandro@gmail.com> - 9.4.0-1
- Update to 9.4.0

* Fri Jan 26 2024 Fedora Release Engineering <releng@fedoraproject.org> - 9.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Jan 21 2024 Fedora Release Engineering <releng@fedoraproject.org> - 9.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Dec 03 2023 Sandro Mani <manisandro@gmail.com> - 9.3.1-1
- Update to 9.3.1

* Sat Sep 02 2023 Sandro Mani <manisandro@gmail.com> - 9.3.0-1
- Update to 9.3.0


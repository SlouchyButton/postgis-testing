%global run_tests 1

%global bashcompletiondir %(pkg-config --variable=compatdir bash-completion)

%global cpuarch 64


%bcond_without python3
# No complete java yet in EL8
%if 0%{?rhel} == 8
%bcond_with java
%else
%ifarch %{java_arches}
%bcond_without java
%else
%bcond_with java
%endif
%endif


#global pre rc1


Name:          gdal
Version:       3.10.2
Release:       5%{?dist}
Summary:       GIS file format library
License:       MIT
URL:           http://www.gdal.org
# Source0:   http://download.osgeo.org/gdal/%%{version}/gdal-%%{version}.tar.xz
# See PROVENANCE.TXT-fedora and the cleaner script for details!

Source0:       %{name}-%{version}%{?pre:%pre}-fedora.tar.xz
Source1:       http://download.osgeo.org/%{name}/%{version}/%{name}autotest-%{version}%{?pre:%pre}.tar.gz
# Multilib compatible cpl-config.h header
Source2:       cpl-config.h
# Multilib compatible gdal-config script
Source3:       gdal-config
Source4:       PROVENANCE.TXT-fedora

# Cleaner script for the tarball
Source5:       %{name}-cleaner.sh

# Add some utils to the default install target
Patch0:        gdal_utils.patch
# Fix passing incompatible pointer type
Patch1:        gdal_incompatible-pointer-types.patch
# Add definitions of missing int16_t and int32_t
Patch2:        gdal-3.10.2-integer-types.patch

BuildRequires: cmake
BuildRequires: gcc-c++

BuildRequires: bison
BuildRequires: blosc-devel
BuildRequires: cfitsio-devel
BuildRequires: CharLS-devel
BuildRequires: curl-devel
BuildRequires: expat-devel
BuildRequires: geos-devel
BuildRequires: json-c-devel
BuildRequires: libarchive-devel
BuildRequires: libpng-devel
BuildRequires: libpq-devel
BuildRequires: libjpeg-turbo-devel
BuildRequires: libtiff-devel
BuildRequires: libtirpc-devel
BuildRequires: mariadb-connector-c-devel
BuildRequires: openjpeg2-devel
BuildRequires: openssl-devel
BuildRequires: pcre2-devel
BuildRequires: proj-devel >= 5.2.0
BuildRequires: sqlite-devel
BuildRequires: swig
BuildRequires: unixODBC-devel
BuildRequires: xz-devel
BuildRequires: zlib-devel

BuildRequires: python3-setuptools
BuildRequires: python3-numpy
BuildRequires: python3-devel


%description
Geospatial Data Abstraction Library (GDAL/OGR) is a cross platform
C++ translator library for raster and vector geospatial data formats.
As a library, it presents a single abstract data model to the calling
application for all supported formats. It also comes with a variety of
useful commandline utilities for data translation and processing.

It provides the primary data access engine for many applications.
GDAL/OGR is the most widely used geospatial data access library.


%package devel
Summary:       Development files for the GDAL file format library
Requires:      %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
This package contains development files for GDAL.


%package libs
Summary:       GDAL file format library
# See frmts/grib/degrib/README.TXT
Provides:      bundled(g2lib) = 1.6.0
Provides:      bundled(degrib) = 2.14

%description libs
This package contains the GDAL file format library.


%prep
%autosetup -N -p1 -n %{name}-%{version}-fedora

# Delete bundled libraries
rm -rf frmts/zlib
rm -rf frmts/png/libpng
rm -rf frmts/gif/giflib
rm -rf frmts/jpeg/libjpeg
rm -rf frmts/jpeg/libjpeg12
rm -rf frmts/gtiff/libgeotiff
rm -rf frmts/gtiff/libtiff
rm -rf mrf/LERCV1
rm -rf third_party/LercLib

# Setup autotest directory
tar xf %{SOURCE1}
mv %{name}autotest-%{version} autotest

# Need to patch autotest
%autopatch -p1

# Copy in PROVENANCE.TXT-fedora
cp -a %{SOURCE4} .


%build
%cmake \
  -DCMAKE_INSTALL_INCLUDEDIR=include/gdal \
  -DGDAL_BUILD_OPTIONAL_DRIVERS=OFF \
  -DOGR_BUILD_OPTIONAL_DRIVERS=OFF \
  -DGDAL_USE_JPEG=ON \
  -DGDAL_USE_JPEG_INTERNAL=OFF \
  -DGDAL_USE_JPEG12_INTERNAL=OFF \
  -DGDAL_USE_GOOGLETEST=OFF \
  -DGDAL_USE_LERC=OFF \
  -DGDAL_USE_LERC_INTERNAL=OFF \
  -DGDAL_USE_GEOTIFF=OFF \
  -DGDAL_USE_GEOTIFF_INTERNAL=OFF \
  -DBUILD_TESTING=OFF \
  -DENABLE_DEFLATE64=OFF \

%cmake_build

%install
%cmake_install


# List of manpages for python scripts
for file in %{buildroot}%{_bindir}/*.py; do
  if [ -f %{buildroot}%{_mandir}/man1/`basename ${file/.py/.1*}` ]; then
    echo "%{_mandir}/man1/`basename ${file/.py/.1*}`" >> gdal_python_manpages.txt
    echo "%exclude %{_mandir}/man1/`basename ${file/.py/.1*}`" >> gdal_python_manpages_excludes.txt
  fi
done

# Multilib
# - cpl_config.h is arch-dependent (contains various SIZEOF defines)
# - gdal-config stores arch-specific information
mv %{buildroot}%{_includedir}/%{name}/cpl_config.h %{buildroot}%{_includedir}/%{name}/cpl_config-%{cpuarch}.h
cp -a %{SOURCE2} %{buildroot}%{_includedir}/%{name}/cpl_config.h
mv %{buildroot}%{_bindir}/%{name}-config %{buildroot}%{_bindir}/%{name}-config-%{cpuarch}
cp -a %{SOURCE3} %{buildroot}%{_bindir}/%{name}-config



%if 0%{run_tests}
%check
%ctest || :
%endif


%files -f gdal_python_manpages_excludes.txt
%{_bindir}/8211*
%{_bindir}/gdal2tiles
%{_bindir}/gdal2xyz
%{_bindir}/gdaladdo
%{_bindir}/gdalattachpct
%{_bindir}/gdalbuildvrt
%{_bindir}/gdal_calc
%{_bindir}/gdalcompare
%{_bindir}/gdal_contour
%{_bindir}/gdal_create
%{_bindir}/gdaldem
%{_bindir}/gdal_edit
%{_bindir}/gdalenhance
%{_bindir}/gdal_fillnodata
%{_bindir}/gdal_footprint
%{_bindir}/gdal_grid
%{_bindir}/gdalinfo
%{_bindir}/gdallocationinfo
%{_bindir}/gdalmanage
%{_bindir}/gdalmdiminfo
%{_bindir}/gdalmdimtranslate
%{_bindir}/gdal_merge
%{_bindir}/gdalmove
%{_bindir}/gdal_pansharpen
%{_bindir}/gdal_polygonize
%{_bindir}/gdal_proximity
%{_bindir}/gdal_rasterize
%{_bindir}/gdal_retile
%{_bindir}/gdal_sieve
%{_bindir}/gdalsrsinfo
%{_bindir}/gdaltindex
%{_bindir}/gdaltransform
%{_bindir}/gdal_translate
%{_bindir}/gdal_viewshed
%{_bindir}/gdalwarp
%{_bindir}/gnmanalyse
%{_bindir}/gnmmanage
%{_bindir}/nearblack
%{_bindir}/ogr2ogr
%{_bindir}/ogrinfo
%{_bindir}/ogr_layer_algebra
%{_bindir}/ogrlineref
%{_bindir}/ogrmerge
%{_bindir}/ogrtindex
%{_bindir}/pct2rgb
%{_bindir}/rgb2pct
%{_bindir}/s57dump
%{_bindir}/sozip
%{_datadir}/bash-completion/completions/*
%exclude %{_datadir}/bash-completion/completions/*.py
%{_mandir}/man1/*
%exclude %{_mandir}/man1/gdal-config.1*
# Python manpages excluded in -f gdal_python_manpages_excludes.txt

%files libs
%license LICENSE.TXT
%doc NEWS.md PROVENANCE.TXT COMMITTERS PROVENANCE.TXT-fedora
%{_libdir}/libgdal.so.36
%{_libdir}/libgdal.so.36.*
%{_datadir}/%{name}/
%{_libdir}/gdalplugins/

%files devel
%{_bindir}/%{name}-config
%{_bindir}/%{name}-config-%{cpuarch}
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/cmake/gdal/
%{_libdir}/pkgconfig/%{name}.pc
%{_mandir}/man1/gdal-config.1*



%changelog
* Thu Feb 27 2025 Laurențiu Nicola <lnicola@dend.ro> - 3.10.2-5
- Enable blosc

* Wed Feb 26 2025 Sandro Mani <manisandro@gmail.com> - 3.10.2-4
- Rebuild (poppler)

* Thu Feb 20 2025 Marek Kasik <mkasik@redhat.com> - 3.10.2-3
- Add definitions of missing int16_t and int32_t

* Thu Feb 20 2025 Marek Kasik <mkasik@redhat.com> - 3.10.2-2
- Rebuild for libarrow 19 in poppler's sidetag

* Sat Feb 15 2025 Sandro Mani <manisandro@gmail.com> - 3.10.2-1
- Update to 3.10.2

* Fri Feb 14 2025 Benjamin A. Beasley <code@musicinmybrain.net> - 3.10.1-4
- Rebuilt for libarrow 19

* Tue Feb 11 2025 Sandro Mani <manisandro@gmail.com> - 3.10.1-3
- Rebuild (poppler)

* Thu Jan 16 2025 Fedora Release Engineering <releng@fedoraproject.org> - 3.10.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Tue Jan 14 2025 Sandro Mani <manisandro@gmail.com> - 3.10.1-1
- Update to 3.10.1

* Wed Nov 27 2024 Richard W.M. Jones <rjones@redhat.com> - 3.10.0-4
- Rebuild for libarrow 18

* Wed Nov 20 2024 Sandro Mani <manisandro@gmail.com> - 3.10.0-3
- Drop fedora conditional for gpsbabel requires

* Tue Nov 19 2024 Sandro Mani <manisandro@gmail.com> - 3.10.0-2
- Require gpsbabel only on Fedora

* Wed Nov 06 2024 Sandro Mani <manisandro@gmail.com> - 3.10.0-1
- Update to 3.10.0

* Fri Oct 25 2024 Orion Poplawski <orion@nwra.com> - 3.9.3-5
- Rebuild for hdf5 1.14.5

* Tue Oct 22 2024 Sandro Mani <manisandro@gmail.com> - 3.9.3-4
- Rebuild (mingw-xerces-c)

* Mon Oct 21 2024 Pete Walter <pwalter@fedoraproject.org> - 3.9.3-3
- Rebuild for xerces-c 3.3

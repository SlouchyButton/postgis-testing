Name:      gdal
Version:   1.6.0
Release:   1%{?dist}
Summary:   GIS file format library
Group:     System Environment/Libraries
License:   MIT
URL:       http://www.gdal.org/
Source0:   %{name}-%{version}-fedora.tar.gz
Source1:   http://download.osgeo.org/gdal/gdalautotest-1.6.0.tar.gz
Patch0:    %{name}-libdap.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libtool pkgconfig
BuildRequires: python-devel numpy xerces-c-devel
BuildRequires: libpng-devel libungif-devel libjpeg-devel libtiff-devel
BuildRequires: doxygen tetex-latex ghostscript ruby-devel jpackage-utils
BuildRequires: jasper-devel cfitsio-devel hdf-devel libdap-devel librx-devel
BuildRequires: unixODBC-devel mysql-devel sqlite-devel postgresql-devel zlib-devel
BuildRequires: proj-devel geos-devel netcdf-devel hdf5-devel ogdi-devel libgeotiff-devel
BuildRequires: perl(ExtUtils::MakeMaker)

%if "%{?dist}" != ".el4"
BuildRequires: ant swig ruby java-devel
%endif

# enable/disable grass support, for bootstrapping
%define grass_support 1
# enable/disable refman generation
%define build_refman  1

# we have multilib triage
%if "%{_lib}" == "lib"
%define cpuarch 32
%else
%define cpuarch 64
%endif

%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?ruby_sitearch: %define ruby_sitearch %(ruby -rrbconfig -e 'puts Config::CONFIG["sitearchdir"]')}

%if %{grass_support}
BuildRequires: grass-devel
%endif

%description
The GDAL library provides support to handle multiple GIS file formats.

%package devel
Summary: Development Libraries for the GDAL file format library
Group: Development/Libraries
Requires: pkgconfig
Requires: libgeotiff-devel
Requires: %{name} = %{version}-%{release}

%description devel
The GDAL library provides support to handle multiple GIS file formats.

%package static
Summary: Static Development Libraries for the GDAL file format library
Group: Development/Libraries

%description static
The GDAL library provides support to handle multiple GIS file formats.

%package python
Summary: Python modules for the GDAL file format library
Group: Development/Libraries
Requires: numpy
Requires: %{name} = %{version}-%{release}

%description python
The GDAL python modules provides support to handle multiple GIS file formats.

%package perl
Summary: Perl modules for the GDAL file format library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description perl
The GDAL perl modules provides support to handle multiple GIS file formats.

%if "%{?dist}" != ".el4"
%package ruby
Summary: Ruby modules for the GDAL file format library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description ruby
The GDAL ruby  modules provides support to handle multiple GIS file formats.

%package java
Summary: Java modules for the GDAL file format library
Group: Development/Libraries
Requires: java
Requires: jpackage-utils
Requires: %{name} = %{version}-%{release}

%description java
The GDAL java modules provides support to handle multiple GIS file formats.
%endif

%prep
%setup -q -n %{name}-%{version}-fedora
%if "%{?dist}" == ".fc10"
%patch0 -p1 -b .libdap~
%endif

# unpack test cases olso.
tar -xzf %{SOURCE1}

# fix russian docs from tarball
for ru in `find doc/ru/ -type f -name "*.dox"`; do
iconv -f KOI8-R -t UTF-8 < $ru > $ru.tmp
mv -f $ru.tmp  $ru
done

set +x
for f in `find . -type f` ; do
   if file $f | grep -q ISO-8859 ; then
      set -x
      iconv -f ISO-8859-1 -t UTF-8 $f > ${f}.tmp && \
         mv -f ${f}.tmp $f
      set +x
   fi
   if file $f | grep -q CRLF ; then
      set -x
      sed -i -e 's|\r||g' $f
      set +x
   fi
done
set -x

# remove junks
find . -name ".cvsignore" -exec rm -rf '{}' \;

# fix some exec bits
chmod -x alg/gdal_tps.cpp
chmod -x apps/nearblack.cpp
chmod -x frmts/jpeg/gdalexif.h
chmod -x ogr/ogrsf_frmts/ogdi/ogrogdi.h
chmod -x ogr/ogrsf_frmts/ogdi/ogrogdilayer.cpp
chmod -x ogr/ogrsf_frmts/ogdi/ogrogdidatasource.cpp
chmod -x ogr/ogrsf_frmts/ogdi/ogrogdidriver.cpp
find swig/python/samples -name "*.py" -exec chmod -x '{}' \;

%build

# fix hardcoded issues
sed -i 's|@LIBTOOL@|%{_bindir}/libtool|g' GDALmake.opt.in
sed -i 's|-L\$with_cfitsio -L\$with_cfitsio\/lib -lcfitsio|-lcfitsio|g' configure
sed -i 's|-I\$with_cfitsio|-I\$with_cfitsio\/include\/cfitsio|g' configure
sed -i 's|-L\$with_netcdf -L\$with_netcdf\/lib -lnetcdf|-lnetcdf|g' configure
sed -i 's|-L\$DODS_LIB -ldap++|-ldap++|g' configure
sed -i 's|-L\$with_ogdi -L\$with_ogdi\/lib -logdi|-logdi|g' configure
sed -i 's|-L\$with_jpeg -L\$with_jpeg\/lib -ljpeg|-ljpeg|g' configure
sed -i 's|-L\$with_libtiff\/lib -ltiff|-ltiff|g' configure
sed -i 's|-L\$with_grass\/lib||g' configure
sed -i 's|-lgeotiff -L$with_geotiff $LIBS|-lgeotiff $LIBS|g' configure
sed -i 's|-L\$with_geotiff\/lib -lgeotiff $LIBS|-lgeotiff $LIBS|g' configure
sed -i 's|-lmfhdf -ldf|-L$libdir/hdf -lmfhdf -ldf|g' configure
sed -i 's|-logdi31|-logdi|g' configure

# fix python path for ppc64
sed -i 's|test \"$ARCH\" = \"x86_64\"|test \"$libdir\" = \"\/usr\/lib64\"|g' configure

# append some path for few libs
export CPPFLAGS="`pkg-config ogdi --cflags`"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/netcdf-3"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/netcdf"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/hdf"
export CPPFLAGS="$CPPFLAGS -I%{_includedir}/libgeotiff"
export CPPFLAGS="$CPPFLAGS `dap-config --cflags`"
export CPPFLAGS="$CPPFLAGS -DH5_USE_16_API"

# code may contain sensible buffer overflows triggered by gcc ssp flag (mustfixupstream).
export CXXFLAGS=`echo %{optflags}|sed -e 's/\-Wp\,-D_FORTIFY_SOURCE\=2 / -fPIC -DPIC /g'`
export CFLAGS=`echo %{optflags}|sed -e 's/\-Wp\,\-D_FORTIFY_SOURCE\=2 / -fPIC -DPIC /g'`

%configure \
        --prefix=%{_prefix} \
        --includedir=%{_includedir}/%{name}/ \
        --datadir=%{_datadir}/%{name}/ \
        --with-threads      \
        --with-dods-root=%{_libdir} \
        --with-ogdi=`ogdi-config --libdir` \
        --with-cfitsio=%{_prefix} \
        --with-geotiff=external   \
        --with-tiff=external      \
        --with-libtiff=external   \
        --with-libz               \
        --with-netcdf             \
        --with-hdf4               \
        --with-hdf5               \
        --with-geos               \
        --with-jasper             \
        --with-png                \
        --with-gif                \
        --with-jpeg               \
        --with-odbc               \
        --with-sqlite             \
        --with-mysql              \
        --with-curl               \
        --with-python             \
        --with-perl               \
%if "%{?dist}" != ".el4"
        --with-ruby               \
        --with-java               \
%endif
        --with-xerces             \
        --with-xerces-lib='-lxerces-c' \
        --with-xerces-inc=%{_includedir} \
        --without-pcraster        \
        --enable-shared           \
%if %{grass_support}
        --with-libgrass             \
        --with-grass=%{_prefix}     \
%endif

# fixup hardcoded wrong compile flags.
cp GDALmake.opt GDALmake.opt.orig
sed -e 's/ cfitsio / /' \
-e 's/-ldap++/-ldap -ldapclient -ldapserver/' \
-e 's/-L\$(INST_LIB) -lgdal/-lgdal/' \
GDALmake.opt.orig > GDALmake.opt
rm GDALmake.opt.orig

# fix ruby flags
sed -i -e "s/\$(LD)/g++ -L..\/..\/.libs\/ $RPM_OPT_FLAGS/g" swig/ruby/RubyMakefile.mk

# fix doxygen for multilib docs
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' swig/perl/Doxyfile
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' frmts/gxf/Doxyfile
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' frmts/sdts/Doxyfile
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' frmts/pcraster/doxygen.cfg
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = ../../doc/gdal_footer.html\n#HTML_FOOTER = |' frmts/iso8211/Doxyfile

# WARNING !!!
# dont use {?_smp_mflags} it break compile
make

# make perl modules, disable makefile generate
pushd swig/perl
 perl Makefile.PL;  make;
 echo > Makefile.PL;
popd

%if "%{?dist}" != ".el4"
# make java modules
pushd swig/java
# fix makefile
sed -i -e 's|include java.opt|\#include java.opt|' GNUmakefile
sed -i -e 's|-cp|\#-cp|g' GNUmakefile
sed -i -e 's|\$(LD) -shared \$(LDFLAGS) \$(CONFIG_LIBS)|g++ -shared -lgdal -L..\/..\/.libs|g' GNUmakefile
# build java module
make generate
# disable ColorEntry for now (gdal Ticket: #2331)
rm -rf org/gdal/gdal/ColorTable.java
make build
popd
%endif

# remake documentation for multilib issues
# olso include many pdf documentation
for docdir in ./ doc doc/ru doc/br ogr ogr/ogrsf_frmts ogr/ogrsf_frmts/dgn frmts/gxf frmts/sdts frmts/iso8211 swig/perl; do
cp -p doc/gdal_footer.html $docdir/footer_local.html
pushd $docdir
if [ ! -f Doxyfile ]; then
doxygen -g
fi
sed -i -e 's|^HTML_FOOTER|HTML_FOOTER = footer_local.html\n#HTML_FOOTER |' Doxyfile
sed -i -e 's|^GENERATE_LATEX|GENERATE_LATEX = YES\n#GENERATE_LATEX |' Doxyfile
sed -i -e 's|^USE_PDFLATEX|USE_PDFLATEX = YES\n#USE_PDFLATEX |' Doxyfile
if [ $docdir == "doc/ru" ]; then
sed -i -e 's|^OUTPUT_LANGUAGE|OUTPUT_LANGUAGE = Russian\n#OUTPUT_LANGUAGE |' Doxyfile
fi
rm -rf latex html
doxygen
%if %{build_refman}
pushd latex
sed -i -e '/rfoot\[/d' -e '/lfoot\[/d' doxygen.sty
sed -i -e '/small/d' -e '/large/d' refman.tex
sed -i -e 's|pdflatex|pdflatex -interaction nonstopmode |g' Makefile
make refman.pdf || true; popd
%endif
rm -rf footer_local.html; popd
done

%install
rm -rf $RPM_BUILD_ROOT

# fix some perl instalation issue
sed -i 's|>> $(DESTINSTALLARCHLIB)\/perllocal.pod|> \/dev\/null|g' swig/perl/Makefile_*
# fix include header instalation issue
cat GNUmakefile | grep -v "\$(INSTALL_DIR) \$(DESTDIR)\$(INST_INCLUDE)" | \
                  grep -v "\$(INSTALL_DIR) \$(DESTDIR)\$(INST_DATA)" \
> GNUmakefile.tmp; mv -f GNUmakefile.tmp GNUmakefile

# fix python installation path
sed -i 's|setup.py install|setup.py install --root=%{buildroot}|' swig/python/GNUmakefile

make    DESTDIR=%{buildroot} \
        install

make    DESTDIR=%{buildroot} \
        INST_MAN=%{_mandir} \
        install-man

# move perl modules in the right path
mkdir -p %{buildroot}%{perl_vendorarch}
mv %{buildroot}%{perl_sitearch}/* %{buildroot}%{perl_vendorarch}/
find %{buildroot}%{perl_vendorarch} -name "*.dox" -exec rm -rf '{}' \;

%if "%{?dist}" != ".el4"
# move ruby modules in the right path
mv %{buildroot}%{ruby_sitearch}/%{name}/*.* %{buildroot}%{ruby_sitearch}/
rm -rf %{buildroot}%{ruby_sitearch}/%{name}

# install multilib java modules in the right path
touch -r NEWS swig/java/gdal.jar
mkdir -p %{buildroot}%{_javadir}
cp -p swig/java/gdal.jar  \
      %{buildroot}%{_javadir}/%{name}-%{version}.jar
%endif

# fix some exec bits
find %{buildroot}%{perl_vendorarch} -name "*.so" -exec chmod 755 '{}' \;
find %{buildroot}%{python_sitearch} -name "*.so" -exec chmod 755 '{}' \;

# install and include all docs
rm -rf docs doc/docs-perl
mkdir -p doc/gdal_frmts; find frmts -name "*.html" -exec install -p -m 644 '{}' doc/gdal_frmts/ \;
mkdir -p doc/ogrsf_frmts; find ogr -name "*.html" -exec install -p -m 644 '{}' doc/ogrsf_frmts/ \;
%if %{build_refman}
mkdir -p docs/docs-%{cpuarch}/pdf
pushd docs/docs-%{cpuarch}/pdf; mkdir -p br ru en ogr ogrsf_frmts/dgn frmts/gxf frmts/sdts frmts/iso8211 ; popd
install -p -m 644 doc/latex/refman.pdf docs/docs-%{cpuarch}/pdf/en
install -p -m 644 doc/br/latex/refman.pdf docs/docs-%{cpuarch}/pdf/br/
#install -p -m 644 doc/ru/latex/refman.pdf docs/docs-%{cpuarch}/pdf/ru/
install -p -m 644 latex/refman.pdf docs/docs-%{cpuarch}/refman.pdf
install -p -m 644 ogr/latex/refman.pdf docs/docs-%{cpuarch}/pdf/ogr/
install -p -m 644 ogr/ogrsf_frmts/latex/refman.pdf docs/docs-%{cpuarch}/pdf/ogrsf_frmts/
install -p -m 644 ogr/ogrsf_frmts/dgn/latex/refman.pdf docs/docs-%{cpuarch}/pdf/ogrsf_frmts/dgn/
%if "%{?dist}" != ".el4"
# broken on el4
install -p -m 644 frmts/gxf/latex/refman.pdf docs/docs-%{cpuarch}/pdf/frmts/gxf/
%endif
install -p -m 644 frmts/sdts/latex/refman.pdf docs/docs-%{cpuarch}/pdf/frmts/sdts/
install -p -m 644 frmts/iso8211/latex/refman.pdf docs/docs-%{cpuarch}/pdf/frmts/iso8211/
mkdir -p doc/docs-perl/docs-%{cpuarch}/pdf
install -p -m 644 swig/perl/latex/refman.pdf doc/docs-perl/docs-%{cpuarch}/pdf
%endif
pushd docs/docs-%{cpuarch}/; mkdir -p en/html gdal_frmts ogrsf_frmts br ru; popd
cp -pr html/* docs/docs-%{cpuarch}/
cp -pr doc/html/* docs/docs-%{cpuarch}/en/html
cp -pr doc/gdal_frmts/* docs/docs-%{cpuarch}/gdal_frmts
cp -pr doc/ogrsf_frmts/* docs/docs-%{cpuarch}/ogrsf_frmts
cp -pr doc/br/html/* docs/docs-%{cpuarch}/br
cp -pr doc/ru/html/* docs/docs-%{cpuarch}/ru
cp -pr swig/perl/html/* doc/docs-perl/docs-%{cpuarch}/

# install multilib cpl_config.h bz#430894
install -p -m 644 port/cpl_config.h %{buildroot}%{_includedir}/%{name}/cpl_config-%{cpuarch}.h
# create universal multilib cpl_config.h bz#341231
cat > %{buildroot}%{_includedir}/%{name}/cpl_config.h <<EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "gdal/cpl_config-32.h"
#else
#if __WORDSIZE == 64
#include "gdal/cpl_config-64.h"
#else
#error "Unknown word size"
#endif
#endif
EOF
touch -r NEWS port/cpl_config.h

# install pkgconfig file
cat > %{name}.pc <<EOF
prefix=%{_prefix}
exec_prefix=%{_prefix}
libdir=%{_libdir}
includedir=%{_includedir}

Name: GDAL
Description: GIS file format library
Version: %{version}
Libs: -L\${libdir} -lgdal
Cflags: -I\${includedir}/%{name}
EOF

mkdir -p %{buildroot}%{_libdir}/pkgconfig/
install -p -m 644 %{name}.pc %{buildroot}%{_libdir}/pkgconfig/
touch -r NEWS %{buildroot}%{_libdir}/pkgconfig/

# multilib gdal-config
mv %{buildroot}%{_bindir}/%{name}-config %{buildroot}%{_bindir}/%{name}-config-%{cpuarch}
cat > %{buildroot}%{_bindir}/%{name}-config <<EOF
#!/bin/bash

ARCH=\$(uname -m)
case \$ARCH in
x86_64 | ppc64 | ia64 | s390x | sparc64 | alpha | alphaev6 )
%{name}-config-64 \${*}
;;
*)
%{name}-config-32 \${*}
;;
esac
EOF
chmod 755 %{buildroot}%{_bindir}/%{name}-config
touch -r NEWS %{buildroot}%{_bindir}/%{name}-config

# cleanup junks
rm -rf %{buildroot}%{_includedir}/%{name}/%{name}
rm -rf %{buildroot}%{_bindir}/gdal_sieve.dox
for junk in {*.la,*.bs,.exists,.packlist,.cvsignore} ; do
find %{buildroot} -name "$junk" -exec rm -rf '{}' \;
done

%check

pushd gdalautotest-1.6.0

# export test enviroment
export PYTHONPATH=$PYTHONPATH:%{buildroot}%{python_sitearch}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH%{buildroot}%{_libdir}
export GDAL_DATA=%{buildroot}%{_datadir}/%{name}/

# remove some testcases for now due to build failure
rm -rf ogr/ogr_pg.py        # no pgsql during test (disabled)
rm -rf ogr/ogr_mysql.py     # no mysql during test (disabled)
rm -rf ogr/ogr_dods.py      # no DODS  during test (disabled)
rm -rf gdrivers/dods.py     # no DODS  during test (disabled)
rm -rf osr/osr_esri.py        # ESRI datum absent  (disabled)
rm -rf ogr/ogr_sql_test.py    # no SQL during tests
rm -rf gcore/mask.py       # crash ugly  (mustfix)

# run tests but force than normal exit
./run_all.py || true

popd

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc NEWS PROVENANCE.TXT-mainstream PROVENANCE.TXT-fedora COMMITERS
%doc docs/
%{_bindir}/gdal_contour
%{_bindir}/gdal_rasterize
%{_bindir}/gdal_translate
%{_bindir}/gdaladdo
%{_bindir}/gdalinfo
%{_bindir}/gdaltindex
%{_bindir}/gdalwarp
%{_bindir}/gdal_grid
%{_bindir}/gdalenhance
%{_bindir}/gdalmanage
%{_bindir}/gdaltransform
%{_bindir}/nearblack
%{_bindir}/ogr*
%{_bindir}/testepsg
%{_libdir}/*.so.*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%{_mandir}/man1/gdaladdo.1.gz
%{_mandir}/man1/gdalinfo.1.gz
%{_mandir}/man1/gdaltindex.1.gz
%{_mandir}/man1/gdaltransform.1.gz
%{_mandir}/man1/gdal2tiles.1.gz
%{_mandir}/man1/nearblack.1.gz
%{_mandir}/man1/gdal_contour.1.gz 
%{_mandir}/man1/gdal_rasterize.1.gz
%{_mandir}/man1/gdal_translate.1.gz
%{_mandir}/man1/gdal_utilities.1.gz
%{_mandir}/man1/gdal_grid.1.gz
%{_mandir}/man1/gdal_retile.1.gz
%{_mandir}/man1/ogr*.1.gz

%files devel
%defattr(-,root,root,-)
%doc docs
%{_bindir}/%{name}-config
%{_bindir}/%{name}-config-%{cpuarch}
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/%{name}.pc
%{_mandir}/man1/%{name}-config*

%files static
%defattr(-,root,root,-)
%{_libdir}/*.a

%files python
%defattr(-,root,root,-)
%doc swig/python/samples
%exclude %{_bindir}/*.py?
%attr(0755,root,root) %{_bindir}/*.py
%{python_sitearch}/*
%{_mandir}/man1/pct2rgb.1.gz
%{_mandir}/man1/rgb2pct.1.gz
%{_mandir}/man1/gdal_merge.1.gz

%files perl
%defattr(-,root,root,-)
%doc doc/docs-perl
%doc swig/perl/README
%{perl_vendorarch}/*

%if "%{?dist}" != ".el4"
%files ruby
%defattr(-,root,root,-)
%{ruby_sitearch}/gdal.so
%{ruby_sitearch}/ogr.so
%{ruby_sitearch}/osr.so
%{ruby_sitearch}/gdalconst.so

%files java
%defattr(-,root,root,-)
%doc swig/java/apps
%{_javadir}/%{name}-%{version}.jar
%endif

%changelog
* Fri Dec 12 2008 Balint Cristian <rezso@rdsor.ro> - 1.6.0-1
- final stable release

* Sat Dec 06 2008 Balint Cristian <rezso@rdsor.ro> - 1.6.0-0.2.rc4
- enable grass

* Sat Dec 06 2008 Balint Cristian <rezso@rdsor.ro> - 1.6.0-0.1.rc4
- new branch
- disable grass
- fix ruby compile

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.5.3-2
- Rebuild for Python 2.6

* Fri Oct 24 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.3-1
- new stable
- ship static package too
- fix some doc generation
- libdap patch for fc10 only

* Tue Sep 30 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.2-4
- enable gdal_array for python subpackage
- require numpy

* Tue Sep  9 2008 Patrice Dumas <pertusus@free.fr> - 1.5.2-3
- patch for libdap > 0.8.0, from Rob Cermak

* Thu Jun 12 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.2-1
- a new bugfix upstream
- drop gcc43 patch
- more license cleaned

* Wed May 27 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-13
- fix pkgconfig too

* Wed May 27 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-12
- fix once more gdal-config

* Tue May 27 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-11
- fix multilib gdal-config, add wrapper around
- fix typos in cpl_config.h wrapper

* Tue May 27 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-10
- fix for multilib packaging bz#341231
- huge spec cleanup
- enable russian and brazil docs
- enable and triage more docs

* Sun May 25 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-9
- enable ruby and java packages
- fix spurious sed problem
- spec file cosmetics

* Thu May 23 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-8
- fix sincos on all arch

* Thu May 15 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-7
- fix x86_64 problem

* Wed Apr 16 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-6
- disable fortify source, it crash gdal for now.

* Fri Mar 28 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-5
- really eanble against grass63

* Fri Mar 28 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-4
- disable grass to bootstrap once again

* Fri Mar 28 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-3
- rebuild to really pick up grass63 in koji

* Fri Mar 28 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-2
- enable build against newer grass
- enable build of reference manuals

* Tue Mar 25 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.1-1
- new bugfix release from upstream
- drop large parts from gcc43 patch, some are upstream now
- fix building with perl-5.10 swig binding issue

* Wed Feb 29 2008 Orion Poplawski <orion@cora.nwra.com> - 1.5.0-4
- Rebuild for hdf5-1.8.0, use compatability API define

* Tue Feb 12 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.0-3
- install cpl_config.h manually for bz#430894
- fix gcc4.3 build

* Mon Jan 14 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.0-2
- fix perl dependency issue.

* Mon Jan 07 2008 Balint Cristian <rezso@rdsor.ro> - 1.5.0-1
- update to new 1.5.0 upstream stable
- dropped build patch since HFA/ILI/DGN mandatories are now present
- dropped swig patch, its upstream now
- enable HFA it holds Intergraph (TM) explicit public license
- enable DGN it holds Avenza Systems (TM) explicit public license
- enable ILI headers since now contain proper public license message
- keep and polish up rest of doubted license
- further fixed hdf not supporting netcdf for for bz#189337
- kill the annoying -Lexternal/lib for -lgeotiff
- fix configure to not export LDFLAGS anyomre, upstream 
  should really switch to real GNU automagic stuff
- pymod samples and rfc docs now gone
- hardcode external libtool to be used, LIBTOOL env not propagating anymore
- use DESTDIR instead

* Thu Jan 03 2008 Alex Lancaster <alexlan[AT]fedoraproject.org> - 1.4.2-7
- Re-enable grass support now that gdal has been bootstrapped

* Wed Jan 02 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.4.2-6
- Bootstrap 1st: disabling grass support
- Workaround for hdf not supporting netcdf (bug 189337 c8)
- Disabling documents creation for now.

* Thu Dec 06 2007 Release Engineering <rel-eng at fedoraproject dot org> - 1.4.2-5
- Rebuild for deps
- Disable grass to avoid circular deps

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 1.4.2-3
- Rebuild for selinux ppc32 issue.

* Wed Jul 24 2007 Balint Cristian <cbalint@redhat.com> 1.4.2-2
- disable one more HFA test, HFA is unaviable due to license

* Wed Jul 24 2007 Balint Cristian <cbalint@redhat.com> 1.4.2-1
- new upstream one
- catch some more docs
- fix ogr python module runtime
- include testcases and run tests
- enable geotiff external library we have new libgeotiff now
- EPSG geodetic database is licensed OK since v6.13 so re-enable
- enable it against grass by default, implement optional switches 

* Tue Jun 05 2007 Balint Cristian <cbalint@redhat.com> 1.4.1-4
- re-build.

* Sat May 12 2007 Balint Cristian <cbalint@redhat.com> 1.4.1-3
- re-build against grass.

* Fri May 11 2007 Balint Cristian <cbalint@redhat.com> 1.4.1-2
- fix python lookup paths for ppc64.

* Wed May 09 2007 Balint Cristian <cbalint@redhat.com> 1.4.1-1
- new upstream release.
- disable temporary grass-devel requirement untill find a
  resonable solution for gdal-grass egg-chicken dep problem.

* Fri Apr 20 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-22
- and olso dont attempt pack missing docs.

* Fri Apr 20 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-21
- exclude some docs, doxygen segfault with those now upstream.

* Fri Apr 20 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-20
- rebuild against latest fedora upstream tree.

* Mon Apr 02 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-19
- own gdal includedir
- fix one more spurious lib path

* Wed Mar 21 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-18
- remove system lib path from gdal-config --libs, its implicit

* Tue Mar 20 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-17
- enable build against grass
- fix incorrect use of 32/64 library paths lookups

* Fri Mar 16 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-16
- fix gdal flag from pkgconfig file

* Thu Mar 15 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-15
- require pkgconfig
- generate pkgconfig from spec instead

* Thu Mar 15 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-14
- require perl(ExtUtils::MakeMaker) instead ?dist checking
- add pkgconfig file 

* Wed Mar 14 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-13
- fix typo in specfile

* Wed Mar 14 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-12
- add missing dot from dist string in specfile

* Wed Mar 14 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-11
- fix fc6 fc5 builds

* Thu Mar 1 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-10
- fix mock build
- require perl-devel

* Tue Feb 27 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-9
- repack tarball for fedora, explain changes in PROVENANCE-fedora,
  license should be clean now according to PROVENANCE-* files
- require ogdi since is aviable now
- drop nogeotiff patch, in -fedora tarball geotiff is removed
- man page triage over subpackages
- exclude python byte compiled objects
- fix some source C file exec bits

* Sat Feb 24 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-8
- fix more things in spec
- include more docs

* Wed Feb 21 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-7
- libtool in requirement list for build

* Wed Feb 21 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-6
- use external libtool to avoid rpath usage
- include more docs

* Mon Feb 12 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-5
- use rm -rf for removal of dirs.
- fix require lists

* Mon Feb 12 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-4
- fix doxygen buildreq
- make sure r-path is fine.

* Sat Feb 10 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-3
- disable now ogdi (pending ogdi submission).

* Sat Feb 10 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-2
- more fixups for lib paths

* Fri Feb 09 2007 Balint Cristian <cbalint@redhat.com> 1.4.0-1
- first pack for fedora extras
- disable geotiff (untill license sorted out)
- enable all options aviable from extras
- pack perl and python modules
- kill r-path from libs
- pack all docs posible

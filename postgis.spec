%{!?javabuild:%define	javabuild 0}
%{!?utils:%define	utils 1}
%{!?gcj_support:%define	gcj_support 0}

%global majorversion 2.1
%global prevmajorversion 2.0
%global prevversion %{prevmajorversion}.7

%global pg_version_minimum 9.2
%global pg_version_built  %(if [ -x %{_bindir}/pg_config ]; then %{_bindir}/pg_config --version | /bin/sed 's,^PostgreSQL *,,gi'; else echo %{pg_version_minimum}; fi)

Summary:	Geographic Information Systems Extensions to PostgreSQL
Name:		postgis
Version:	2.1.7
Release:	2%{?dist}
License:	GPLv2+
Group:		Applications/Databases
Source0:	http://download.osgeo.org/%{name}/source/%{name}-%{version}.tar.gz
Source2:	http://download.osgeo.org/%{name}/docs/%{name}-%{version}.pdf
Source3:        http://download.osgeo.org/%{name}/source/%{name}-%{prevversion}.tar.gz
Source4:	filter-requires-perl-Pg.sh
Patch0:		postgis-1.5.1-pgsql9.patch
# CFLAGS are reset before AC_CHECK_LIBRARY, but -fPIC is necessary to link against gdal
Patch1:		postgis-configureac21.patch
URL:		http://www.postgis.org
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	postgresql-devel >= %{pg_version_minimum}, proj-devel, geos-devel >= 3.4.2 byacc, proj-devel, flex, java, java-devel, ant
BuildRequires:	gtk2-devel, libxml2-devel, gdal-devel >= 1.10.0
BuildRequires:	autoconf, automake, libtool
Requires:	postgresql >= %{pg_version_built}, geos >= 3.4.2, proj, gdal >= 1.10.0, json-c

%description
PostGIS adds support for geographic objects to the PostgreSQL object-relational
database. In effect, PostGIS "spatially enables" the PostgreSQL server,
allowing it to be used as a backend spatial database for geographic information
systems (GIS), much like ESRI's SDE or Oracle's Spatial extension. PostGIS
follows the OpenGIS "Simple Features Specification for SQL" and has been
certified as compliant with the "Types and Functions" profile.

%package docs
Summary:	Extra documentation for PostGIS
Group:		Applications/Databases
%description docs
The postgis-docs package includes PDF documentation of PostGIS.

%if %javabuild
%package jdbc
Summary:	The JDBC driver for PostGIS
Group:		Applications/Databases
License:	LGPLv2+
Requires:	%{name} = %{version}-%{release}, postgresql-jdbc
BuildRequires:	ant >= 0:1.6.2, junit >= 0:3.7, postgresql-jdbc

%if %{gcj_support}
BuildRequires:		gcc-java
BuildRequires:		java-1.5.0-gcj-devel
Requires(post):		%{_bindir}/rebuild-gcj-db
Requires(postun):	%{_bindir}/rebuild-gcj-db
%endif

%description jdbc
The postgis-jdbc package provides the essential jdbc driver for PostGIS.
%endif

%if %utils
%package utils
Summary:	The utils for PostGIS
Group:		Applications/Databases
Requires:	%{name} = %{version}-%{release}, perl-DBD-Pg

%description utils
The postgis-utils package provides the utilities for PostGIS.
%endif

%define __perl_requires %{SOURCE4}

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1 -b .pgsql9
%patch1 -p0 -b .configureac21
# Copy .pdf file to top directory before installing.
cp -p %{SOURCE2} .

%build
./autogen.sh
%configure --with-gui --enable-raster
make %{?_smp_mflags} LPATH=`pg_config --pkglibdir` shlib="%{name}.so"

%if %javabuild
export BUILDXML_DIR=%{_builddir}/%{name}-%{version}/java/jdbc
JDBC_VERSION_RPM=`rpm -ql postgresql-jdbc| grep 'jdbc2.jar$'|awk -F '/' '{print $5}'`
sed 's/postgresql.jar/'${JDBC_VERSION_RPM}'/g' $BUILDXML_DIR/build.xml > $BUILDXML_DIR/build.xml.new
mv -f $BUILDXML_DIR/build.xml.new $BUILDXML_DIR/build.xml
pushd java/jdbc
ant
popd
%endif

%if %utils
 make %{?_smp_mflags}  -C utils
%endif

# PostGIS 2.1 breaks compatibility with 2.0, and we need to ship
# postgis-2.0.so file along with 2.1 package, so that we can upgrade:
tar zxf %{SOURCE3}
cd %{name}-%{prevversion}
%configure --without-raster --disable-rpath --without-json

make %{?_smp_mflags} LPATH=`%[_bindir}/pg_config --pkglibdir` shlib="%{name}-%{prevmajorversion}.so"

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
make %{?_smp_mflags}  -C utils install DESTDIR=%{buildroot}
make %{?_smp_mflags}  -C extensions install DESTDIR=%{buildroot}

rm -f  %{buildroot}%{_libdir}/liblwgeom.{a,la}

# (moved into install section:
# Install postgis-2.0.so file manually:
%{__mkdir} -p %{buildroot}/%{_libdir}/pgsql
%{__install} -m 644 %{name}-%{prevversion}/postgis/postgis-%{prevmajorversion}.so %{buildroot}/%{_libdir}/pgsql/postgis-%{prevmajorversion}.so

rm -f  %{buildroot}%{_datadir}/*.sql

#if [ "%{_lib}" = "lib64" ] ; then
#	mv %{buildroot}%{_datadir}/pgsql/contrib/%{name}-%{majorversion}/postgis.sql %{buildroot}%{_datadir}/pgsql/contrib/postgis-64.sql
#fi

%if %javabuild
install -d %{buildroot}%{_javadir}
install -m 755 java/jdbc/%{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}.jar
%if %{gcj_support}
aot-compile-rpm
%endif
strip %{buildroot}/%{_libdir}/gcj/%{name}/*.jar.so
%endif

%if %utils
install -d %{buildroot}%{_datadir}/%{name}
install -m 755 utils/*.pl %{buildroot}%{_datadir}/%{name}
%endif

%clean
rm -rf %{buildroot}

%if %javabuild
%if %gcj_support
%post -p %{_bindir}/rebuild-gcj-db
%postun -p %{_bindir}/rebuild-gcj-db
%endif
%endif

%files
%defattr(-,root,root)
%doc COPYING CREDITS NEWS TODO README.%{name} doc/html loader/README.* doc/%{name}.xml doc/ZMSgeoms.txt 
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/pgsql/%{name}-%{prevmajorversion}.so
%attr(755,root,root) %{_libdir}/pgsql/%{name}-%{majorversion}.so
%{_datadir}/pgsql/contrib/postgis-%{majorversion}/*.sql
#if {_lib} == lib64
#{_datadir}/pgsql/contrib/postgis*.sql
#endif
%{_datadir}/pgsql/extension/postgis-*.sql
%{_datadir}/pgsql/extension/postgis_topology*.sql
%{_datadir}/pgsql/extension/postgis.control
%{_datadir}/pgsql/extension/postgis_topology.control
%{_datadir}/pgsql/extension/postgis_tiger_geocoder*.sql
%{_datadir}/pgsql/extension/postgis_tiger_geocoder.control
%{_datadir}/postgis/svn_repo_revision.pl
%{_includedir}/liblwgeom.h
%{_libdir}/liblwgeom*
%{_libdir}/pgsql/rtpostgis-%{majorversion}.so

%if %javabuild
%files jdbc
%defattr(-,root,root)
%doc java/jdbc/COPYING_LGPL java/jdbc/README
%attr(755,root,root) %{_javadir}/%{name}.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%{_libdir}/gcj/%{name}/*.jar.so
%{_libdir}/gcj/%{name}/*.jar.db
%endif
%endif

%if %utils
%files utils
%defattr(755,root,root)
%doc utils/README
%dir %{_datadir}/%{name}/
%{_datadir}/%{name}/test_estimation.pl
%{_datadir}/%{name}/profile_intersects.pl
%{_datadir}/%{name}/test_joinestimation.pl
%{_datadir}/%{name}/create_undef.pl
%{_datadir}/%{name}/%{name}_proc_upgrade.pl
%{_datadir}/%{name}/%{name}_restore.pl
%{_datadir}/pgsql/contrib/postgis-%{majorversion}/postgis_restore.pl
%{_datadir}/%{name}/read_scripts_version.pl
%{_datadir}/%{name}/test_geography_estimation.pl
%{_datadir}/%{name}/test_geography_joinestimation.pl
%endif

%files docs
%defattr(-,root,root)
%doc postgis*.pdf

%changelog
* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Apr 1 2015 Devrim Gündüz <devrim@gunduz.org> - 2.1.7-1
- Update to 2.1.7, per changes described at:
  http://svn.osgeo.org/postgis/tags/2.1.7/NEWS

* Fri Mar 27 2015 Devrim Gündüz <devrim@gunduz.org> - 2.1.6-1
- Update to 2.1.6, per changes described at:
  http://postgis.net/2015/03/20/postgis-2.1.6

* Wed Mar 11 2015 Devrim Gündüz <devrim@gunduz.org> - 2.1.5-3
- Rebuild for Proj 4.9.1
- Add patch to fix FTBFS -- patch by Sandro Mani <manisandro@gmail.com>

* Thu Jan 08 2015 Jozef Mlich <jmlich@redhat.com> - 2.1.5-2
- disable json-c/geojson just for upgrade part of postgis

* Mon Dec 22 2014 Devrim Gündüz <devrim@gunduz.org> - 2.1.5-1
- Update to 2.1.5, per changes described at:
  http://postgis.net/2014/12/18/postgis-2.1.5 and
  http://postgis.net/2014/09/10/postgis-2.1.4

* Mon Aug 18 2014 Jozef Mlich <jmlich@redhat.com> - 2.1.3-5
- Dropped json-c because it is not building anymore
  Resolves: #1129292

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 26 2014 Jozef Mlich <jmlich@redhat.com> - 2.1.3-3
- Removing static libraries
  Resolves: #979179

* Mon Jun 09 2014 Jozef Mlich <jmlich@redhat.com> - 2.1.3-2
- removing sinjdoc from BuildRequires as it is not available
  in rawhide anymore

* Mon Jun 09 2014 Jozef Mlich <jmlich@redhat.com> - 2.1.3-1
- Rebase to 2.1.3 and 2.0.6 (security bugfixes, feature bugfixes)
  see http://svn.osgeo.org/postgis/tags/2.1.3/NEWS
- json_c turned on
- installation of .so file of previous version moved into install section

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Jan 23 2014 Devrim Gündüz <devrim@gunduz.org> - 2.1.1-2
- Install postgis-2.0.so file, by compiling it from 2.0 sources
  Fixes bz #1055293.

* Thu Dec 12 2013 Devrim Gündüz <devrim@gunduz.org> - 2.1.1-1
- Update to 2.1.1

* Fri Oct 25 2013 Dan Horák <dan[at]danny.cz> - 2.1.0-2
- fix build on non-x86 64-bit arches

* Thu Sep 12 2013 Devrim Gündüz <devrim@gunduz.org> - 2.1.0-1
- Update to 2.1.0, per changes described at:
  http://svn.osgeo.org/postgis/tags/2.1.0/NEWS

* Tue Aug 27 2013 Orion Poplawski <orion@cora.nwra.com> - 2.0.3-4
- Rebuild for gdal 1.10.0

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 2.0.3-2
- Perl 5.18 rebuild

* Wed Mar 6 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.0.3-1
- Update to 2.0.3, and build against GeOS 3.3.8.
- Update all URLs.

* Fri Jan 25 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.0.2-2
- Rebuilt against geos 3.3.7.
- Apply changes for PostgreSQL 9.2 and extensions.

* Wed Jan 16 2013 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.0.2-1
- Update to 2.0.2, for various changes described at:
  http://www.postgis.org/news/20121203/

* Tue Nov 13 2012 Devrim GÜNDÜZ <devrim@gunduz.org> - 2.0.1-1
- Update to 2.0.1, so it works against PostgreSQL 9.2,
  which also fixes #872710.
- Add deps for gdal.
- Don't build JDBC portions. I have already disabled it in
  upstream packaging 8 months ago.

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Oct 4 2011 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.5.3-2
- Provide postgis.jar instead of provide postgis-1.5.2.jar,
  per #714856

* Tue Oct 4 2011 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.5.3-1
- Update to 1.5.3

* Tue Apr 19 2011 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.5.2-1
- Update to 1.5.2

* Sun Apr 03 2011 Nils Philippsen <nils@redhat.com> - 1.5.1-3
- cope with PostgreSQL 9.0 build environment
- require pgsql version used for building

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Mar 11 2010 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.5.1-1
- Update to 1.5.1

* Tue Jan 12 2010 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.5.0-1
- Update to 1.5.0
- Trim changelog a bit.

* Wed Jan 6 2010 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.4.1-2
- Add shp2pgsql-{cli-gui} among installed files.

* Sun Dec 20 2009 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.4.1-1
- Update to 1.4.1

* Thu Dec 03 2009 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.4.1-rc2_1.2
- Fix spec per rawhide report.

* Tue Dec 01 2009 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.4.1-rc2_1.1
- Update spec for rc2 changes.

* Mon Nov 30 2009 Devrim GUNDUZ <devrim@gunduz.org> - 1.4.1rc2-1
- Update to 1.4.1rc2

* Mon Nov 23 2009 Devrim GUNDUZ <devrim@gunduz.org> - 1.4.1rc1-1
- Update to 1.4.1rc1

* Sun Nov 22 2009 Devrim GÜNDÜZ <devrim@gunduz.org> - 1.4.0-2
- Fix spec, per bz #536860

* Mon Jul 27 2009 Devrim GUNDUZ <devrim@gunduz.org> - 1.4.0-1
- Update to 1.4.0

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.0rc1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 6 2009 Devrim GUNDUZ <devrim@gunduz.org> - 1.4.0rc1-1
- Update to 1.4.0rc1
- Fix spec for 1.4

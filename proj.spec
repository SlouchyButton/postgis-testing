Name: proj
Version: 4.5.0
Release: 2%{?dist}
Summary: Cartographic projection software (PROJ.4)

Group: Applications/Engineering
License: MIT
URL: http://www.remotesensing.org/proj/
Source0: ftp://ftp.remotesensing.org/pub/proj/proj-%{version}.tar.gz
Source1: ftp://ftp.remotesensing.org/pub/proj/proj-datumgrid-1.3.zip
Source2: http://packages.debian.org/changelogs/pool/main/p/proj/proj_4.4.8-3/proj.copyright
Patch0: proj.copyright.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%package devel
Summary: Development files for PROJ.4
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%package nad
Summary: US and Canadian datum shift grids for PROJ.4
Group: Applications/Engineering
Requires: %{name} = %{version}-%{release}

%description
Proj and invproj perform respective forward and inverse transformation of
cartographic data to or from cartesian data with a wide range of selectable
projection functions. Proj docs: http://www.remotesensing.org/dl/new_docs/

%description devel
This package contains libproj and the appropriate header files and man pages.

%description nad
This package contains additional US and Canadian datum shift grids.

%prep
%setup -q

# Prepare copyright
cp %{SOURCE2} ./
%patch0 -p0 -b .buildroot
cp proj.copyright COPYING

# Prepare nad
cd nad
unzip %{SOURCE1}
cd ..

%build
%configure
make OPTIMIZE="$RPM_OPT_FLAGS" %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall
install -p -m 0644 nad/pj_out27.dist nad/pj_out83.dist nad/td_out.dist $RPM_BUILD_ROOT%{_datadir}/%{name}
install -p -m 0755 nad/test27 nad/test83 nad/testvarious $RPM_BUILD_ROOT%{_datadir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc NEWS AUTHORS COPYING README ChangeLog
%{_bindir}/*
%{_mandir}/man1/*.1*
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root,-)
%{_mandir}/man3/*.3*
%{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%exclude %{_libdir}/libproj.la

%files nad
%defattr(-,root,root,-)
%doc nad/README
%attr(0755,root,root) %{_datadir}/%{name}/test27
%attr(0755,root,root) %{_datadir}/%{name}/test83
%attr(0755,root,root) %{_datadir}/%{name}/testvarious
%{_datadir}/%{name}

%changelog
* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 4.5.0-2
- Autorebuild for GCC 4.3

* Tue Jan   2 2007 Shawn McCann <mccann0011@hotmail.com> - 4.5.0-1
- Updated to proj-4.5.0 and datumgrid-1.3

* Sat Sep  16 2006 Shawn McCann <mccann0011@hotmail.com> - 4.4.9-4
- Rebuild for Fedora Extras 6

* Sat Mar  4 2006 Shawn McCann <mccann0011@hotmail.com> - 4.4.9-3
- Rebuild for Fedora Extras 5

* Sat Mar  4 2006 Shawn McCann <mccann0011@hotmail.com> - 4.4.9-2
- Rebuild for Fedora Extras 5

* Thu Jul  7 2005 Shawn McCann <mccann0011@hotmail.com> - 4.4.9-1
- Updated to proj-4.4.9 and to fix bugzilla reports 150013 and 161726. Patch2 can be removed once this package is upgraded to the next release of the source.

* Sun May 22 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 4.4.8-6
- rebuilt

* Thu Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 4.4.8-5
- rebuilt

* Wed Dec 29 2004 David Kaplan <dmk@erizo.ucdavis.edu> - 0:4.4.8-4
- Added testvarious to nad distribution

* Wed Dec 29 2004 David Kaplan <dmk@erizo.ucdavis.edu> - 0:4.4.8-0.fdr.3
- Added patch for test scripts so that they will work in installed rpm

* Wed Dec 29 2004 David Kaplan <dmk@erizo.ucdavis.edu> - 0:4.4.8-0.fdr.2
- Fixed permissions on nad27 and nad83
- Included test27 and test83 in the nad rpm and made them executable

* Fri Aug 13 2004 David M. Kaplan <dmk@erizo.ucdavis.edu> 0:4.4.8-0.fdr.1
- Updated to version 4.4.8 of library.
- Changed license file so that it agrees with Debian version.
- Updated web addresses of packages.

* Wed Aug 11 2004 David M. Kaplan <dmk@erizo.ucdavis.edu> 0:4.4.7-0.fdr.3
- Removed the "Requires(post,postun)"

* Tue Dec 30 2003 David M. Kaplan <dmk@erizo.ucdavis.edu> 0:4.4.7-0.fdr.2
- proj-nad now owns %{_datadir}/%{name}

* Wed Oct 29 2003 Steve Arnold <sarnold@arnolds.dhs.org>
- Basically re-wrote previous spec file from scratch so as
- to comply with both Fedora and RedHat 9 packaging guidelines.
- Split files into proj, proj-devel, and proj-nad (additional grids)
- and adjusted the EXE path in the test scripts.

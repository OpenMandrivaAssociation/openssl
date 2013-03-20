%define major 1.0.0
%define engines_name %mklibname openssl-engines %{major}
%define libname %mklibname openssl %{major}
%define develname %mklibname openssl -d
%define staticname %mklibname openssl -s -d

%define conflict2 %mklibname openssl 0.9.8

# Number of threads to spawn when testing some threading fixes.
#define thread_test_threads %{?threads:%{threads}}%{!?threads:1}

%define with_krb5 %{?_with_krb5:1}%{!?_with_krb5:0}

Summary:	Secure Sockets Layer communications libs & utils
Name:		openssl
Version:	1.0.1e
Release:	1
License:	BSD-like
Group:		System/Libraries
URL:		http://www.openssl.org/
Source0:	ftp://ftp.openssl.org/source/%{name}-%{version}.tar.gz
Source1:	ftp://ftp.openssl.org/source/%{name}-%{version}.tar.gz.asc
Source2:	Makefile.certificate
Source3:	make-dummy-cert
Source4:	openssl-thread-test.c
# (gb) 0.9.7b-4mdk: Handle RPM_OPT_FLAGS in Configure
Patch2:		openssl-optflags.diff
# (oe) support Brazilian Government OTHERNAME X509v3 field (#14158)
# http://www.iti.gov.br/resolucoes/RESOLU__O_13_DE_26_04_2002.PDF
Patch6:		openssl-0.9.8-beta6-icpbrasil.diff
Patch7:		openssl-1.0.0-defaults.patch
Patch8:		openssl-0.9.8a-link-krb5.patch
Patch10:	openssl-0.9.7-beta6-ia64.patch
Patch12:	openssl-0.9.6-x509.patch
Patch13:	openssl-0.9.7-beta5-version-add-engines.patch
# http://qa.mandriva.com/show_bug.cgi?id=32621
Patch15:	openssl-0.9.8e-crt.patch
Patch16:	openssl-1.0.1c-fix-perlpath.pl
# MIPS and ARM support
Patch300:	openssl-1.0.0-mips.patch
Patch301:	openssl-1.0.0-arm.patch
Patch302:	openssl-1.0.0-enginesdir.patch
Patch303:	openssl-0.9.8a-no-rpath.patch
Patch304:	openssl-1.0.1-test-use-localhost.diff
Patch305:	openssl-aarch64.patch
Requires:	%{engines_name} = %{version}-%{release}
Requires:	perl-base
Requires:	rootcerts
Provides:	/usr/bin/openssl
%{?_with_krb5:BuildRequires:	krb5-devel}
BuildRequires:	zlib-devel
# (tv) for test suite:
BuildRequires:	bc
BuildRequires:	sctp-devel

%description
The openssl certificate management tool and the shared libraries that provide
various encryption and decription algorithms and protocols, including DES, RC4,
RSA and SSL.

%package -n %{engines_name}
Summary:	Engines for openssl
Group:		System/Libraries
Obsoletes:	openssl-engines < 1.0.0a-5
Provides:	openssl-engines = %{version}-%{release}

%description -n	%{engines_name}
This package provides engines for openssl.

%package -n %{libname}
Summary:	Secure Sockets Layer communications libs
Group:		System/Libraries
Provides:	%{libname} = %{version}-%{release}

%description -n	%{libname}
The libraries files are needed for various cryptographic algorithms
and protocols, including DES, RC4, RSA and SSL.

%package -n %{develname}
Summary:	Secure Sockets Layer communications libs & headers & utils
Group:		Development/Other
Requires:	%{libname} = %{version}-%{release}
Provides:	libopenssl-devel = %{version}-%{release}
Provides:	openssl-devel = %{version}-%{release}
Obsoletes:	openssl-devel < %{version}-%{release}
Obsoletes:	%{conflict2}-devel
Obsoletes:	%{mklibname openssl 1.0.0}-devel
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{develname}
The libraries and include files needed to compile apps with support
for various cryptographic algorithms and protocols, including DES, RC4, RSA
and SSL.

%package -n %{staticname}
Summary:	Secure Sockets Layer communications static libs
Group:		Development/Other
Requires:	%{develname} = %{version}-%{release}
Provides:	libopenssl-static-devel
Provides:	openssl-static-devel = %{version}-%{release}
Obsoletes:	%{conflict2}-static-devel
Obsoletes:	%{mklibname openssl 1.0.0}-static-devel
Provides:	%{name}-static-devel = %{version}-%{release}

%description -n	%{staticname}
The static libraries needed to compile apps with support for various
cryptographic algorithms and protocols, including DES, RC4, RSA and SSL.

%prep

%setup -q -n %{name}-%{version}
%patch2 -p0 -b .optflags
%patch6 -p0 -b .icpbrasil
%patch7 -p1 -b .defaults
%{?_with_krb5:%patch8 -p1 -b .krb5}
#patch10 -p0 -b .ia64
%patch12 -p1 -b .x509
%patch13 -p1 -b .version-add-engines
%patch15 -p1 -b .crt
%patch16 -p1 -b .perlfind~

%patch300 -p0 -b .mips
%patch301 -p0 -b .arm
%patch302 -p1 -b .engines
%patch303 -p1 -b .no-rpath
%patch304 -p0 -b .test-use-localhost
%patch305 -p1 -b .aarch64

perl -pi -e "s,^(OPENSSL_LIBNAME=).+$,\1%{_lib}," Makefile.org engines/Makefile

# fix perl path
perl util/perlpath.pl %{_bindir}/perl

cp %{SOURCE2} Makefile.certificate
cp %{SOURCE3} make-dummy-cert
cp %{SOURCE4} openssl-thread-test.c

%build
%serverbuild

# Figure out which flags we want to use.
# default
sslarch=%{_os}-%{_arch}
%ifarch %ix86
sslarch=linux-elf
if ! echo %{_target} | grep -q i[56]86 ; then
    sslflags="no-asm"
fi
%endif
%ifarch sparcv9
sslarch=linux-sparcv9
%endif
%ifarch alpha
sslarch=linux-alpha-gcc
%endif
%ifarch s390
sslarch="linux-generic32 -DB_ENDIAN -DNO_ASM"
%endif
%ifarch s390x
sslarch="linux-generic64 -DB_ENDIAN -DNO_ASM"
%endif
%ifarch %{arm}
sslarch=linux-generic32
%endif
%ifarch aarch64
sslarch=linux-generic32
%endif


# ia64, x86_64, ppc, ppc64 are OK by default
# Configure the build tree.  Override OpenSSL defaults with known-good defaults
# usable on all platforms.  The Configure script already knows to use -fPIC and
# RPM_OPT_FLAGS, so we can skip specifiying them here.
./Configure \
    --openssldir=%{_sysconfdir}/pki/tls ${sslflags} \
    --enginesdir=%{_libdir}/openssl-%{version}/engines \
    --prefix=%{_prefix} --libdir=%{_lib}/ %{?_with_krb5:--with-krb5-flavor=MIT -I%{_prefix}/kerberos/include -L%{_prefix}/kerberos/%{_lib}} \
    zlib no-idea no-rc5 enable-camellia enable-seed enable-tlsext enable-rfc3779 enable-cms sctp shared ${sslarch}

# Add -Wa,--noexecstack here so that libcrypto's assembler modules will be
# marked as not requiring an executable stack.
RPM_OPT_FLAGS="%{optflags} -Wa,--noexecstack"

make depend
make all build-shared

# Generate hashes for the included certs.
make rehash build-shared

%check
# Verify that what was compiled actually works.
export LD_LIBRARY_PATH=`pwd`${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

make -C test apps tests

gcc -o openssl-thread-test \
    %{?_with_krb5:`krb5-config --cflags`} \
    -I./include \
    %{optflags} \
    openssl-thread-test.c \
    -L. -lssl -lcrypto \
    %{?_with_krb5:`krb5-config --libs`} \
    -lpthread -lz -ldl

./openssl-thread-test --threads %{thread_test_threads}

%install

%makeinstall \
    INSTALL_PREFIX=%{buildroot} \
    MANDIR=%{_mandir} \
    build-shared

mkdir %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/libcrypto.so.%{major} %{buildroot}/%{_lib}
ln -srf %{buildroot}/%{_lib}/libcrypto.so.%{major} %{buildroot}%{_libdir}/libcrypto.so
mv %{buildroot}%{_libdir}/libssl.so.%{major} %{buildroot}/%{_lib}
ln -srf %{buildroot}/%{_lib}/libssl.so.%{major} %{buildroot}%{_libdir}/libssl.so

# the makefiles is too borked...
install -d %{buildroot}%{_libdir}/openssl-%{version}
mv %{buildroot}%{_libdir}/engines %{buildroot}%{_libdir}/openssl-%{version}/engines

# make the rootcerts dir
install -d %{buildroot}%{_sysconfdir}/pki/tls/rootcerts

# Install a makefile for generating keys and self-signed certs, and a script
# for generating them on the fly.
install -d %{buildroot}%{_sysconfdir}/pki/tls/certs
install -m0644 Makefile.certificate %{buildroot}%{_sysconfdir}/pki/tls/certs/Makefile
install -m0755 make-dummy-cert %{buildroot}%{_sysconfdir}/pki/tls/certs/make-dummy-cert

# Pick a CA script.
mv %{buildroot}%{_sysconfdir}/pki/tls/misc/CA.sh %{buildroot}%{_sysconfdir}/pki/tls/misc/CA

install -d %{buildroot}%{_sysconfdir}/pki/CA
install -d %{buildroot}%{_sysconfdir}/pki/CA/private

# openssl was named ssleay in "ancient" times.
ln -snf openssl %{buildroot}%{_bindir}/ssleay

# The man pages rand.3 and passwd.1 conflict with other packages
# Rename them to ssl-* and also make a symlink from openssl-* to ssl-*
mv %{buildroot}%{_mandir}/man1/passwd.1 %{buildroot}%{_mandir}/man1/ssl-passwd.1
ln -sf ssl-passwd.1%{_extension} %{buildroot}%{_mandir}/man1/openssl-passwd.1%{_extension}

for i in rand err; do
    mv %{buildroot}%{_mandir}/man3/$i.3 %{buildroot}%{_mandir}/man3/ssl-$i.3
    ln -snf ssl-$i.3%{_extension} %{buildroot}%{_mandir}/man3/openssl-$i.3%{_extension}
done

rm -rf {main,devel}-doc-info
mkdir -p {main,devel}-doc-info
cat - << EOF > main-doc-info/README.Mandriva-manpage
Warning:
The man page of passwd, passwd.1, has been renamed to ssl-passwd.1
to avoid a conflict with passwd.1 man page from the package passwd.
EOF

cat - << EOF > devel-doc-info/README.Mandriva-manpage
Warning:
The man page of rand, rand.3, has been renamed to ssl-rand.3
to avoid a conflict with rand.3 from the package man-pages
The man page of err, err.3, has been renamed to ssl-err.3
to avoid a conflict with err.3 from the package man-pages
EOF

chmod 755 %{buildroot}%{_libdir}/pkgconfig

%multiarch_includes %{buildroot}%{_includedir}/openssl/opensslconf.h

# strip cannot touch these unless 755
chmod 755 %{buildroot}%{_libdir}/openssl-%{version}/engines/*.so*
chmod 755 %{buildroot}%{_bindir}/*

# nuke a mistake
rm -f %{buildroot}%{_mandir}/man3/.3

# Fix libdir.
pushd %{buildroot}%{_libdir}/pkgconfig
    for i in *.pc ; do
	sed 's,^libdir=${exec_prefix}/lib$,libdir=${exec_prefix}/%{_lib},g' \
	    $i >$i.tmp && \
	    cat $i.tmp >$i && \
	    rm -f $i.tmp
    done
popd

# adjust ssldir
perl -pi -e "s|^CATOP=.*|CATOP=%{_sysconfdir}/pki/tls|g" %{buildroot}%{_sysconfdir}/pki/tls/misc/CA
perl -pi -e "s|^\\\$CATOP\=\".*|\\\$CATOP\=\"%{_sysconfdir}/pki/tls\";|g" %{buildroot}%{_sysconfdir}/pki/tls/misc/CA.pl
perl -pi -e "s|\./demoCA|%{_sysconfdir}/pki/tls|g" %{buildroot}%{_sysconfdir}/pki/tls/openssl.cnf

%files
%doc FAQ INSTALL LICENSE NEWS PROBLEMS main-doc-info/README*
%doc README README.ASN1 README.ENGINE
%dir %{_libdir}/%{name}-%{version}
%dir %{_sysconfdir}/pki
%dir %{_sysconfdir}/pki/CA
%dir %{_sysconfdir}/pki/CA/private
%dir %{_sysconfdir}/pki/tls
%dir %{_sysconfdir}/pki/tls/certs
%dir %{_sysconfdir}/pki/tls/misc
%dir %{_sysconfdir}/pki/tls/private
%dir %{_sysconfdir}/pki/tls/rootcerts
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/pki/tls/openssl.cnf
%attr(0755,root,root) %{_sysconfdir}/pki/tls/certs/make-dummy-cert
%attr(0644,root,root) %{_sysconfdir}/pki/tls/certs/Makefile
%attr(0755,root,root) %{_sysconfdir}/pki/tls/misc/*
%attr(0755,root,root) %{_bindir}/*
%attr(0644,root,root) %{_mandir}/man[157]/*

%files -n %{libname}
%attr(0755,root,root) /%{_lib}/lib*.so.%{major}*

%files -n %{engines_name}
%attr(0755,root,root) %dir %{_libdir}/openssl-%{version}/engines
%attr(0755,root,root) %{_libdir}/openssl-%{version}/engines/*.so

%files -n %{develname}
%doc CHANGES doc/* devel-doc-info/README*
%doc FAQ INSTALL LICENSE NEWS PROBLEMS README*
%attr(0755,root,root) %dir %{_includedir}/openssl
%{multiarch_includedir}/openssl/opensslconf.h
%attr(0644,root,root) %{_includedir}/openssl/*
%attr(0755,root,root) %{_libdir}/lib*.so
%attr(0644,root,root) %{_mandir}/man3/*
%attr(0644,root,root) %{_libdir}/pkgconfig/*

%files -n %{staticname}
%attr(0644,root,root) %{_libdir}/lib*.a

%changelog
* Thu Jan 17 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.0.1c-2
- move libraries under /%%{_lib} as /bin/rpm links against it

* Fri May 11 2012 Oden Eriksson <oeriksson@mandriva.com> 1.0.1c-1
+ Revision: 798177
- 1.0.1c

* Thu Apr 26 2012 Oden Eriksson <oeriksson@mandriva.com> 1.0.1b-1
+ Revision: 793590
- 1.0.1b

* Thu Apr 19 2012 Oden Eriksson <oeriksson@mandriva.com> 1.0.1a-1
+ Revision: 792130
- 1.0.1a

* Fri Mar 16 2012 Oden Eriksson <oeriksson@mandriva.com> 1.0.1-1
+ Revision: 785271
- fix deps; sctp-devel for the new SCTP support in openssl
- 1.0.1
- drop the pkcs11_engine patch by sun (now oracle), it's nowhere to be found...
- rediffed some patches
- added 2 patches from fedora

* Tue Mar 13 2012 Oden Eriksson <oeriksson@mandriva.com> 1.0.0h-1
+ Revision: 784664
- 1.0.0h

* Thu Jan 19 2012 Oden Eriksson <oeriksson@mandriva.com> 1.0.0g-1
+ Revision: 762530
- 1.0.0g

* Mon Jan 09 2012 Oden Eriksson <oeriksson@mandriva.com> 1.0.0f-1
+ Revision: 758821
- 1.0.0f
- enable some new'ish features per default (enable-seed enable-rfc3779 enable-cms)

* Thu Dec 01 2011 Matthew Dawkins <mattydaw@mandriva.org> 1.0.0e-3
+ Revision: 735862
- rebuild for openssl
- solves dep LOOP problems
- removed clean section, mkrel

* Tue Nov 29 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.0e-2
+ Revision: 735413
- bump release
- more fixes to make sure rpm -Fvh works better
- drop the french fixes patch, it has never been used
- applied some fixes by Matthew Dawkins

* Tue Sep 06 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.0e-1
+ Revision: 698456
- 1.0.0e (fixes CVE-2011-3207, CVE-2011-3210)

  + Matthew Dawkins <mattydaw@mandriva.org>
    - fix arm build

* Mon May 02 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.0d-2
+ Revision: 661710
- multiarch fixes

* Wed Feb 09 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.0d-1
+ Revision: 636986
- 1.0.0d

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.0c-1mdv2011.0
+ Revision: 606171
- 1.0.0b

* Wed Nov 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.0b-1mdv2011.0
+ Revision: 598376
- 1.0.0b (fixes CVE-2010-3864)
- P17: post 1.0.0b fix to make the test suite work after upstream CVE-2010-3864 fixes
- fix small borkiness

* Sat Oct 02 2010 Anssi Hannula <anssi@mandriva.org> 1.0.0a-7mdv2011.0
+ Revision: 582540
- fix versioned obsoletes of openssl-engines (the package was renamed
  in 1.0.0a-5, not 1.0.0a-1.4)

* Mon Sep 20 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.0a-6mdv2011.0
+ Revision: 579973
- bump release
- fix a dep problem which prevented openssl-engines to be upgraded if both
  x86_64 and i586 urpmi repos were configured.

* Tue Sep 14 2010 Eugeni Dodonov <eugeni@mandriva.com> 1.0.0a-4mdv2011.0
+ Revision: 578251
- Fixed typo in openssl.cnf (#61019)

* Sat Sep 04 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.0a-3mdv2011.0
+ Revision: 575832
- sync with MDVSA-2010:168

* Wed Jul 14 2010 Matthew Dawkins <mattydaw@mandriva.org> 1.0.0a-2mdv2011.0
+ Revision: 553412
- dropped major for devel & static packages

* Wed Jun 02 2010 Eugeni Dodonov <eugeni@mandriva.com> 1.0.0a-1mdv2010.1
+ Revision: 546943
- Updated to 1.0.0a.

* Tue Apr 06 2010 Eugeni Dodonov <eugeni@mandriva.com> 1.0.0-4mdv2010.1
+ Revision: 532146
- Disable md2 again because it really should not have been enabled.

* Tue Apr 06 2010 Funda Wang <fwang@mandriva.org> 1.0.0-3mdv2010.1
+ Revision: 532115
- enable md2

* Tue Apr 06 2010 Funda Wang <fwang@mandriva.org> 1.0.0-2mdv2010.1
+ Revision: 531959
- obsoletes 0.9.8-static-devel

* Mon Apr 05 2010 Eugeni Dodonov <eugeni@mandriva.com> 1.0.0-1mdv2010.1
+ Revision: 531697
- Updated optflags patches.
- Updated to 1.0.0.
  Rediffed patches.
  Updated pkcs11 patch.

* Fri Mar 26 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.9.8n-1mdv2010.1
+ Revision: 527842
- Updated to 0.9.8n.

* Thu Feb 25 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.9.8m-1mdv2010.1
+ Revision: 511325
- Drop P3 and P9 (no longer needed).
- Updated to 0.9.8m.
  Drop P3, P17-24 (merged upstream).
  Rediff P2, P9, P16.

* Thu Jan 21 2010 Oden Eriksson <oeriksson@mandriva.com> 0.9.8l-2mdv2010.1
+ Revision: 494502
- P24: fix build with binutils-2.20.51.0.x
- P23: security fix for CVE-2009-4355 (upstream)

* Fri Nov 06 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.9.8l-1mdv2010.1
+ Revision: 461230
- Updated to 0.9.8l.
  Fixed static package summary.

* Wed Oct 07 2009 Oden Eriksson <oeriksson@mandriva.com> 0.9.8k-5mdv2010.0
+ Revision: 455585
- P22: fixes a regression with CVE-2009-2409 (#54349)

* Sun Sep 27 2009 Olivier Blin <blino@mandriva.org> 0.9.8k-4mdv2010.0
+ Revision: 450189
- mips and arm support (from Arnaud Patard)

* Tue Sep 22 2009 Oden Eriksson <oeriksson@mandriva.com> 0.9.8k-3mdv2010.0
+ Revision: 447234
- P19: security fix for CVE-2009-1379
- P20: security fix for CVE-2009-1387
- P21: security fix for CVE-2009-2409

* Thu May 21 2009 Oden Eriksson <oeriksson@mandriva.com> 0.9.8k-2mdv2010.0
+ Revision: 378365
- P17: security fix for CVE-2009-1377
- P18: security fix for CVE-2009-1378

* Thu Mar 26 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.9.8k-1mdv2009.1
+ Revision: 361433
- Updated to 0.9.8k.
  Rediffed P9, P13, P16.
  Dropped P17 (no longer needed) and P18 (merged upstream).

* Tue Feb 03 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.9.8i-5mdv2009.1
+ Revision: 337119
- keep bash completion in its own package

* Mon Jan 12 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.9.8i-4mdv2009.1
+ Revision: 328609
- no need to rename man page, we don't ship rsbac anymore
- uncompress additional sources
- bash completion

* Thu Jan 08 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.9.8i-3mdv2009.1
+ Revision: 327021
- P18: security fix for CVE-2008-5077

* Tue Dec 16 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8i-2mdv2009.1
+ Revision: 314928
- rediffed fuzzy patches
- fix build with P17 (-Werror=format-security)

* Fri Oct 10 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8i-1mdv2009.1
+ Revision: 291331
- 0.9.8i
- dropped the mbstring_flag patch (P4), it's implemented upstream
- added pkcs11 engine support P16

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 0.9.8h-3mdv2009.0
+ Revision: 265275
- rebuild early 2009.0 package (before pixel changes)

* Wed Jun 11 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8h-2mdv2009.0
+ Revision: 217952
- fix "#%%define is forbidden"
- added P4 to fix borkiness in the apache test suites

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Fri May 30 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8h-1mdv2009.0
+ Revision: 213381
- 0.9.8h (fixes CVE-2008-1672, CVE-2008-0891)
- rediffed P2

* Thu May 29 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8g-9mdv2009.0
+ Revision: 212968
- P16: security fix for CVE-2008-0891
- P17: security fix for CVE-2008-1672

* Tue May 27 2008 Thierry Vignaud <tv@mandriva.org> 0.9.8g-8mdv2009.0
+ Revision: 211562
- fix duplicated descriptions between devel packages (as showed by latest commits)
- descriptions are not license tags
- remove URLs & emails from descriptions

* Sat May 24 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8g-7mdv2009.0
+ Revision: 210856
- rebuild

* Tue May 20 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8g-6mdv2009.0
+ Revision: 209328
- rebuilt with gcc43

* Mon Apr 14 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8g-5mdv2009.0
+ Revision: 192694
- rebuild
- fix #39792 (openssl-thread-test does not use proper .so file)

* Thu Feb 28 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8g-4mdv2008.1
+ Revision: 176382
- rebuild (take 2)

* Thu Feb 28 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8g-3mdv2008.1
+ Revision: 176250
- rebuild

* Thu Feb 28 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9.8g-2mdv2008.1
+ Revision: 176044
- fix #38237 (Please include SNI support patch)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Dec 06 2007 Oden Eriksson <oeriksson@mandriva.com> 0.9.8g-1mdv2008.1
+ Revision: 115942
- bump release
- 0.9.8g

* Fri Oct 19 2007 Oden Eriksson <oeriksson@mandriva.com> 0.9.8f-1mdv2008.1
+ Revision: 100300
- 0.9.8f
- rediffed P2
- drop upstream implemented fixes for CVE-2007-3108, CVE-2007-5135
- drop upstream implemented fixes; P4, P14, P16, P17, P18

* Fri Oct 05 2007 Anne Nicolas <ennael@mandriva.org> 0.9.8e-8mdv2008.0
+ Revision: 95537
- bump release

* Thu Oct 04 2007 Andreas Hasenack <andreas@mandriva.com> 0.9.8e-7mdv2008.0
+ Revision: 95496
- patch to fix security issues CVE-2007-5135 and
  CVE-2007-3108 (#34405 and #32376 respectively)

* Fri Sep 21 2007 Andreas Hasenack <andreas@mandriva.com> 0.9.8e-6mdv2008.0
+ Revision: 91695
- fix sigill during make test (#32769)
- make c_rehash handle .crt extensions (#32621)

  + Thierry Vignaud <tv@mandriva.org>
    - add missing buildrequires for test suite
    - kill file require on perl-base

* Tue Jun 26 2007 Thierry Vignaud <tv@mandriva.org> 0.9.8e-4mdv2008.0
+ Revision: 44488
- rebuild with -fstack-protector

* Tue Apr 24 2007 Andreas Hasenack <andreas@mandriva.com> 0.9.8e-3mdv2008.0
+ Revision: 17927
- fixed 3des cipher bug in openssl (#30431)


* Mon Mar 19 2007 Thierry Vignaud <tvignaud@mandriva.com> 0.9.8e-2mdv2007.1
+ Revision: 146607
- move big doc in -devel

* Mon Feb 26 2007 Andreas Hasenack <andreas@mandriva.com> 0.9.8e-1mdv2007.1
+ Revision: 125816
- updated to version 0.9.8e

* Wed Dec 20 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 0.9.8d-3mdv2007.1
+ Revision: 100705
- bump re?\195?\184lease
- fix sparcv9 build
  do not disable asm on sparc
  move checks to %%check

* Mon Dec 11 2006 Gwenole Beauchesne <gbeauchesne@mandriva.com> 0.9.8d-2mdv2007.1
+ Revision: 94733
- 0.9.8d-2mdv
- merge from 2007.0-branch: fix build on ppc64

* Mon Nov 06 2006 Andreas Hasenack <andreas@mandriva.com> 0.9.8d-1mdv2007.1
+ Revision: 77025
- updated to version 0.9.8d
- dropped poll patch, it's already being used upstream
- added new cipher: camellia
- dropped security patches that were already applied

* Tue Oct 31 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.8b-4mdv2007.1
+ Revision: 74810
- add another patch, phew!
- commit one more patch (duh!)
- commit the patches too...
- bunzip patches

  + Andreas Hasenack <andreas@mandriva.com>
    - added security patches for CVE-2006-2940 (two patches),
      CVE-2006-4343, CVE-2006-3738 and CVE-2006-2937 (#26197)
    - Import openssl

* Thu Sep 07 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.8b-2
- plug CVE-2006-4339 (#25234)

* Fri May 05 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.8b-1mdk
- 0.9.8a
- rediffed P3

* Mon Jan 30 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.8a-10mdk
- fix one conflicting manpage (buffer.3) with rsbac-admin (#20875)

* Fri Jan 27 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.8a-9mdk
- fix deps (rootcerts)

* Wed Jan 04 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.8a-8mdk
- fix the /usr/lib6464 error (duh!)

* Wed Jan 04 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.8a-7mdk
- fix deps

* Mon Dec 05 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.8a-6mdk
- fix file attribs on certain files in /etc/pki/tls/ (thanks ahasenack)
- fix one missing ";" in the /etc/pki/tls/misc/CA.pl file (thanks ahasenack)
- for the record, 0.9.8a-4mdk fixed #19882

* Wed Nov 23 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 0.9.8a-5mdk
- add BuildRequires: chrpath

* Mon Nov 21 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.8a-4mdk
- don't ship a crippled package

* Sat Nov 12 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.8a-3mdk
- rebuilt due package loss

* Fri Nov 11 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.8a-2mdk
- added patches and changes from fedora
- OPENSSLDIR is now %%{_sysconfdir}/pki/tls

* Thu Nov 10 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.8a-1mdk
- merge with the openssl0.9.8 package:
  - 0.9.8a
  - new major
  - rediff P2, P3 and P6

* Mon Oct 17 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.7i-1mdk
- 0.9.7i (compatibility fix)

* Fri Oct 14 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.7h-2mdk
- security update for CAN-2005-2946 (P7)

* Wed Oct 12 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.7h-1mdk
- 0.9.7h (addresses CAN-2005-2969)
- rediff P2,P3

* Fri May 06 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.7g-2mdk
- rebuilt with gcc4

* Sat Apr 16 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.9.7g-1mdk
- 0.9.7g
- rediffed P2

* Fri Apr 01 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.9.7f-1mdk
- 0.9.7f
- use the %%mkrel macro
- drop the libfips patch (P5), it's implemented upstream
- drop the CAN-2004-0975 patch (P4) as the code is gone
- rediffed P2

* Wed Mar 02 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.9.7e-5mdk
- added P6 to support Brazilian Government OTHERNAME X509v3 field (#14158)

* Mon Jan 31 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.9.7e-4mdk
- fix deps and conditional %%multiarch
- added P5 as there's no libfips

* Mon Jan 10 2005 Frederic Lepied <flepied@mandrakesoft.com> 0.9.7e-3mdk
- build in parallel

* Tue Dec 07 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 0.9.7e-2mdk
- apply the CAN-2004-0975 patch (P4) from 0.9.7d-1.1.101mdk

* Mon Nov 08 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 0.9.7e-1mdk
- 0.9.7e
- rediffed P2 & P3
- misc spec file fixes

* Sat Jun 19 2004 Jean-Michel Dault <jmdault@mandrakesoft.com> 0.9.7d-1mdk
- new version
- rediff P3
- remove P4/P5 since they're included in the release


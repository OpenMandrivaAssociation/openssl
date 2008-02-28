%define maj 0.9.8
%define libname %mklibname openssl %{maj}
%define conflict1 %mklibname openssl 0.9.7

# Number of threads to spawn when testing some threading fixes.
#%define thread_test_threads %{?threads:%{threads}}%{!?threads:1}

# French policy is to not use ciphers stronger than 128 bits
%define french_policy 0

%define with_krb5 %{?_with_krb5:1}%{!?_with_krb5:0}

Summary:	Secure Sockets Layer communications libs & utils
Name:		openssl
Version:	%{maj}g
Release:	%mkrel 2
License:	BSD-like
Group:		System/Libraries
URL:		http://www.openssl.org/
Source0:	ftp://ftp.openssl.org/source/%{name}-%{version}.tar.gz
Source1:	ftp://ftp.openssl.org/source/%{name}-%{version}.tar.gz.asc
Source2:	Makefile.certificate.bz2
Source3:	make-dummy-cert.bz2
Source4:	openssl-thread-test.c.bz2
# (gb) 0.9.6b-5mdk: Limit available SSL ciphers to 128 bits
Patch0:		openssl-0.9.6b-mdkconfig.patch
# (fg) 20010202 Patch from RH: some funcs now implemented with ia64 asm
Patch1:		openssl-0.9.7-ia64-asm.patch
# (gb) 0.9.7b-4mdk: Handle RPM_OPT_FLAGS in Configure
Patch2:		openssl-optflags.diff
# (gb) 0.9.7b-4mdk: Make it lib64 aware. TODO: detect in Configure
Patch3:		openssl-0.9.8b-lib64.diff
# (oe) support Brazilian Government OTHERNAME X509v3 field (#14158)
# http://www.iti.gov.br/resolucoes/RESOLU__O_13_DE_26_04_2002.PDF
Patch6:		openssl-0.9.8-beta6-icpbrasil.diff
Patch7:		openssl-0.9.8a-defaults.patch
Patch8:		openssl-0.9.8a-link-krb5.patch
Patch9:		openssl-0.9.8a-enginesdir.patch
Patch10:	openssl-0.9.7-beta6-ia64.patch
Patch12:	openssl-0.9.6-x509.patch
Patch13:	openssl-0.9.7-beta5-version-add-engines.patch
# http://qa.mandriva.com/show_bug.cgi?id=32621
Patch15:        openssl-0.9.8e-crt.patch
Requires:	%{libname} = %{version}-%{release}
Requires:	perl-base
Requires:	rootcerts
%{?_with_krb5:BuildRequires: krb5-devel}
%if %mdkversion >= 1020
BuildRequires:	multiarch-utils >= 1.0.3
%endif
BuildRequires:	chrpath
BuildRequires:	zlib-devel
# (tv) for test suite:
BuildRequires:	bc
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
The openssl certificate management tool and the shared libraries that provide
various encryption and decription algorithms and protocols, including DES, RC4,
RSA and SSL.
This product includes software developed by the OpenSSL Project for use in the
OpenSSL Toolkit (http://www.openssl.org/).
This product includes cryptographic software written by Eric Young
(eay@cryptsoft.com).
This product includes software written by Tim Hudson (tjh@cryptsoft.com).

%package -n	%{libname}
Summary:	Secure Sockets Layer communications libs
Group:		System/Libraries
Conflicts:	openssh < 3.5p1-4mdk

%description -n	%{libname}
The libraries files are needed for various cryptographic algorithms
and protocols, including DES, RC4, RSA and SSL.
This product includes software developed by the OpenSSL Project for use in
the OpenSSL Toolkit (http://www.openssl.org/).
This product includes cryptographic software written by Eric Young
(eay@cryptsoft.com).
This product includes software written by Tim Hudson (tjh@cryptsoft.com).
Patches for many networking apps can be found at: 
	ftp://ftp.psy.uq.oz.au/pub/Crypto/SSLapps/

%package -n	%{libname}-devel
Summary:	Secure Sockets Layer communications static libs & headers & utils
Group:		Development/Other
Requires:	%{libname} = %{version}-%{release}
Provides:	libopenssl-devel
Provides:	openssl-devel = %{version}-%{release}
Obsoletes:	openssl-devel
# temporary opsolete, will be a conflict later. a compat package
# with openssl-0.9.7 devel libs will be provided soon
Obsoletes:	%{conflict1}-devel
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{libname}-devel
The static libraries and include files needed to compile apps with support
for various cryptographic algorithms and protocols, including DES, RC4, RSA
and SSL.
This product includes software developed by the OpenSSL Project for use in
the OpenSSL Toolkit (http://www.openssl.org/).
This product includes cryptographic software written by Eric Young
(eay@cryptsoft.com).
This product includes software written by Tim Hudson (tjh@cryptsoft.com).
Patches for many networking apps can be found at: 
	ftp://ftp.psy.uq.oz.au/pub/Crypto/SSLapps/

%package -n	%{libname}-static-devel
Summary:	Secure Sockets Layer communications static libs & headers & utils
Group:		Development/Other
Requires:	%{libname}-devel = %{version}-%{release}
Provides:	libopenssl-static-devel
Provides:	openssl-static-devel = %{version}-%{release}
# temporary opsolete, will be a conflict later. a compat package
# with openssl-0.9.7 static-devel libs will be provided soon
Obsoletes:	%{conflict1}-static-devel
Provides:	%{name}-static-devel = %{version}-%{release}

%description -n	%{libname}-static-devel
The static libraries and include files needed to compile apps with support
for various cryptographic algorithms and protocols, including DES, RC4, RSA
and SSL.
This product includes software developed by the OpenSSL Project for use in
the OpenSSL Toolkit (http://www.openssl.org/).
This product includes cryptographic software written by Eric Young
(eay@cryptsoft.com).
This product includes software written by Tim Hudson (tjh@cryptsoft.com).
Patches for many networking apps can be found at: 
	ftp://ftp.psy.uq.oz.au/pub/Crypto/SSLapps/

%prep

%setup -q -n %{name}-%{version}
%if %{french_policy}
%patch0 -p1 -b .frenchpolicy
%endif
%patch1 -p1 -b .ia64-asm
%patch2 -p0 -b .optflags
%patch3 -p1 -b .lib64
%patch6 -p0 -b .icpbrasil
%patch7 -p1 -b .defaults
%{?_with_krb5:%patch8 -p1 -b .krb5}
%patch9 -p1 -b .enginesdir
%patch10 -p1 -b .ia64
%patch12 -p1 -b .x509
%patch13 -p1 -b .version-add-engines
%patch15 -p1 -b .crt

perl -pi -e "s,^(OPENSSL_LIBNAME=).+$,\1%{_lib}," Makefile.org engines/Makefile

# fix perl path
perl util/perlpath.pl %{_bindir}/perl

bzcat %{SOURCE2} > Makefile.certificate
bzcat %{SOURCE3} > make-dummy-cert
bzcat %{SOURCE4} > openssl-thread-test.c

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

# ia64, x86_64, ppc, ppc64 are OK by default
# Configure the build tree.  Override OpenSSL defaults with known-good defaults
# usable on all platforms.  The Configure script already knows to use -fPIC and
# RPM_OPT_FLAGS, so we can skip specifiying them here.
./Configure \
    --prefix=%{_prefix} --openssldir=%{_sysconfdir}/pki/tls ${sslflags} \
    --enginesdir=%{_libdir}/openssl/engines %{?_with_krb5:--with-krb5-flavor=MIT-I%{_prefix}/kerberos/include -L%{_prefix}/kerberos/%{_lib}} \
     no-idea no-rc5 enable-camellia shared enable-tlsext ${sslarch}

#    zlib no-idea no-mdc2 no-rc5 no-ec no-ecdh no-ecdsa shared ${sslarch}

# antibork stuff...
perl -pi -e "s|^#define ENGINESDIR .*|#define ENGINESDIR \"%{_libdir}/openssl/engines\"|g" crypto/opensslconf.h

# Add -Wa,--noexecstack here so that libcrypto's assembler modules will be
# marked as not requiring an executable stack.
RPM_OPT_FLAGS="%{optflags} -Wa,--noexecstack"
make depend
make all build-shared

# Generate hashes for the included certs.
make rehash build-shared

# Verify that what was compiled actually works.
export LD_LIBRARY_PATH=`pwd`${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

%check
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
rm -fr %{buildroot}

%makeinstall \
    INSTALL_PREFIX=%{buildroot} \
    MANDIR=%{_mandir} \
    build-shared

# the makefiles is too borked...
install -d %{buildroot}%{_libdir}/openssl
mv %{buildroot}%{_libdir}/engines %{buildroot}%{_libdir}/openssl/

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
ln -sf ssl-passwd.1.bz2 %{buildroot}%{_mandir}/man1/openssl-passwd.1.bz2

for i in rand err; do
    mv %{buildroot}%{_mandir}/man3/$i.3 %{buildroot}%{_mandir}/man3/ssl-$i.3
    ln -snf ssl-$i.3.bz2 %{buildroot}%{_mandir}/man3/openssl-$i.3.bz2
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

%if %mdkversion >= 1020
%multiarch_includes %{buildroot}%{_includedir}/openssl/opensslconf.h
%endif

# strip cannot touch these unless 755
chmod 755 %{buildroot}%{_libdir}/openssl/engines/*.so*
chmod 755 %{buildroot}%{_libdir}/*.so*
chmod 755 %{buildroot}%{_bindir}/*

# nuke a mistake
rm -f %{buildroot}%{_mandir}/man3/.3

# nuke rpath
chrpath -d %{buildroot}%{_bindir}/openssl

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

# fix one conflicting manpage with rsbac-admin
mv %{buildroot}%{_mandir}/man3/buffer.3 %{buildroot}%{_mandir}/man3/openssl_buffer.3

cat > README.urpmi << EOF

The most significant changes made and starting from the 
openssl-0.9.8a-2mdk package is these:

 o The OPENSSLDIR has moved from %{_libdir}/ssl to %{_sysconfdir}/pki/tls

The most significant changes made and starting from the 
%{libname}-devel-0.9.8a-10mdk package is these:

 o The static development libraries (*.a) has been packaged in the
  %{libname}-static-devel sub package.
 o %{_mandir}/man3/buffer.3 has been renamed to %{_mandir}/man3/openssl_buffer.3
   to solve a file conflict with rsbac-admin.

EOF

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%clean
rm -fr %{buildroot}

%files 
%defattr(-,root,root)
%doc FAQ INSTALL LICENSE NEWS PROBLEMS README* main-doc-info/README* README.urpmi 
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
%defattr(-,root,root)
%doc FAQ INSTALL LICENSE NEWS PROBLEMS README*
%attr(0755,root,root) %{_libdir}/lib*.so.*
%attr(0755,root,root) %dir %{_libdir}/openssl/engines
%attr(0755,root,root) %{_libdir}/openssl/engines/*.so

%files -n %{libname}-devel
%defattr(-,root,root)
%doc CHANGES doc/* devel-doc-info/README*
%attr(0755,root,root) %dir %{_includedir}/openssl
%if %mdkversion >= 1020
%multiarch %{multiarch_includedir}/openssl/opensslconf.h
%endif
%attr(0644,root,root) %{_includedir}/openssl/*
%attr(0755,root,root) %{_libdir}/lib*.so
%attr(0644,root,root) %{_mandir}/man3/*
%attr(0644,root,root) %{_libdir}/pkgconfig/*

%files -n %{libname}-static-devel
%defattr(-,root,root)
%attr(0644,root,root) %{_libdir}/lib*.a

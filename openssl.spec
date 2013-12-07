%define major 1.0.0
%define engines_name %mklibname openssl-engines %{major}
%define libcrypto %mklibname crypto %{major}
%define libssl %mklibname ssl %{major}
%define devname %mklibname openssl -d
%define staticname %mklibname openssl -s -d

%define with_krb5 %{?_with_krb5:1}%{!?_with_krb5:0}

Summary:	Secure Sockets Layer communications libs & utils
Name:		openssl
Version:	1.0.1e
Release:	7
License:	BSD-like
Group:		System/Libraries
Url:		http://www.openssl.org/
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
# (tv) for test suite:
BuildRequires:	bc
BuildRequires:	makedepend
%{?_with_krb5:BuildRequires:	krb5-devel}
BuildRequires:	sctp-devel
BuildRequires:	pkgconfig(zlib)
Requires:	%{engines_name} = %{version}-%{release}
Requires:	rootcerts
Provides:	/usr/bin/openssl

%description
The openssl certificate management tool and the shared libraries that provide
various encryption and decription algorithms and protocols, including DES, RC4,
RSA and SSL.

%package -n %{engines_name}
Summary:	Engines for openssl
Group:		System/Libraries
Provides:	openssl-engines = %{version}-%{release}

%description -n	%{engines_name}
This package provides engines for openssl.

%package -n %{libcrypto}
Summary:	Secure Sockets Layer communications libs
Group:		System/Libraries
Conflicts:	%{_lib}openssl1.0.0 < 1.0.1e-3

%description -n	%{libcrypto}
The libraries files are needed for various cryptographic algorithms
and protocols, including DES, RC4, RSA and SSL.

%package -n %{libssl}
Summary:	Secure Sockets Layer communications libs
Group:		System/Libraries
Obsoletes:	%{_lib}openssl1.0.0 < 1.0.1e-3

%description -n	%{libssl}
The libraries files are needed for various cryptographic algorithms
and protocols, including DES, RC4, RSA and SSL.

%package -n %{devname}
Summary:	Secure Sockets Layer communications libs & headers & utils
Group:		Development/Other
Requires:	%{libcrypto} = %{version}-%{release}
Requires:	%{libssl} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
The libraries and include files needed to compile apps with support
for various cryptographic algorithms and protocols, including DES, RC4, RSA
and SSL.

%package -n %{staticname}
Summary:	Secure Sockets Layer communications static libs
Group:		Development/Other
Requires:	%{devname} = %{version}-%{release}
Provides:	%{name}-static-devel = %{version}-%{release}

%description -n	%{staticname}
The static libraries needed to compile apps with support for various
cryptographic algorithms and protocols, including DES, RC4, RSA and SSL.

%package	perl
Summary:	Perl scripts provided with OpenSSL
Group:		System/Libraries
Requires:	%{name} = %{version}-%{release}
Conflicts:	%{name} < 1.0.1e-3

%description perl
The openssl-perl package provides Perl scripts for converting certificates and
keys from other formats to the formats used by the OpenSSL toolkit.

%prep
%setup -q
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
export CC=%{__cc}
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
	--prefix=%{_prefix} \
	--libdir=%{_lib}/ \
	%{?_with_krb5:--with-krb5-flavor=MIT -I%{_prefix}/kerberos/include -L%{_prefix}/kerberos/%{_lib}} \
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
%attr(0755,root,root) %{_sysconfdir}/pki/tls/misc/CA
%attr(0755,root,root) %{_sysconfdir}/pki/tls/misc/c_*
%{_bindir}/openssl
%{_bindir}/ssleay
%{_mandir}/man[157]/*
%exclude %{_mandir}/man1/CA.pl*

%files perl
%{_bindir}/c_rehash
%{_mandir}/man1/CA.pl*
%{_sysconfdir}/pki/tls/misc/CA.pl
%{_sysconfdir}/pki/tls/misc/tsget

%files -n %{libcrypto}
/%{_lib}/libcrypto.so.%{major}*

%files -n %{libssl}
/%{_lib}/libssl.so.%{major}*

%files -n %{engines_name}
%dir %{_libdir}/openssl-%{version}/engines
%{_libdir}/openssl-%{version}/engines/*.so

%files -n %{devname}
%doc CHANGES doc/* devel-doc-info/README*
%doc FAQ INSTALL LICENSE NEWS PROBLEMS README*
%dir %{_includedir}/openssl
%{multiarch_includedir}/openssl/opensslconf.h
%{_includedir}/openssl/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_mandir}/man3/*

%files -n %{staticname}
%{_libdir}/lib*.a


%define maj 1.0.0
%define libname %mklibname openssl %{maj}
%define conflict1 %mklibname openssl 0.9.7
%define conflict2 %mklibname openssl 0.9.8

# Number of threads to spawn when testing some threading fixes.
#define thread_test_threads %{?threads:%{threads}}%{!?threads:1}

# French policy is to not use ciphers stronger than 128 bits
%define french_policy 0

%define with_krb5 %{?_with_krb5:1}%{!?_with_krb5:0}

Summary:	Secure Sockets Layer communications libs & utils
Name:		openssl
Version:	%{maj}
Release:	%mkrel 3
License:	BSD-like
Group:		System/Libraries
URL:		http://www.openssl.org/
Source0:	ftp://ftp.openssl.org/source/%{name}-%{version}.tar.gz
Source1:	ftp://ftp.openssl.org/source/%{name}-%{version}.tar.gz.asc
Source2:	Makefile.certificate
Source3:	make-dummy-cert
Source4:	openssl-thread-test.c
Source5:	README.pkcs11
# (gb) 0.9.6b-5mdk: Limit available SSL ciphers to 128 bits
Patch0:		openssl-0.9.6b-mdkconfig.patch
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
Patch15:        openssl-0.9.8e-crt.patch
# http://blogs.sun.com/janp/
Patch16:	pkcs11_engine-1.0.0.diff
# MIPS and ARM support
Patch30:	openssl-1.0.0-mips.patch
Patch31:	openssl-1.0.0-arm.patch
Patch32:	openssl-1.0.0-enginesdir.patch
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
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The openssl certificate management tool and the shared libraries that provide
various encryption and decription algorithms and protocols, including DES, RC4,
RSA and SSL.

%package -n	openssl-engines
Summary:	Engines for openssl
Group:		System/Libraries

%description -n	openssl-engines
This package provides engines for openssl.

%package -n	%{libname}
Summary:	Secure Sockets Layer communications libs
Group:		System/Libraries
Requires:	openssl-engines = %{version}-%{release}
Conflicts:	openssh < 3.5p1-4mdk

%description -n	%{libname}
The libraries files are needed for various cryptographic algorithms
and protocols, including DES, RC4, RSA and SSL.

%package -n	%{libname}-devel
Summary:	Secure Sockets Layer communications libs & headers & utils
Group:		Development/Other
Requires:	%{libname} = %{version}-%{release}
Provides:	libopenssl-devel
Provides:	openssl-devel = %{version}-%{release}
Obsoletes:	openssl-devel
# temporary opsolete, will be a conflict later. a compat package
# with openssl-0.9.7 devel libs will be provided soon
Obsoletes:	%{conflict1}-devel
Obsoletes:	%{conflict2}-devel
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{libname}-devel
The libraries and include files needed to compile apps with support
for various cryptographic algorithms and protocols, including DES, RC4, RSA
and SSL.

%package -n	%{libname}-static-devel
Summary:	Secure Sockets Layer communications static libs
Group:		Development/Other
Requires:	%{libname}-devel = %{version}-%{release}
Provides:	libopenssl-static-devel
Provides:	openssl-static-devel = %{version}-%{release}
# temporary opsolete, will be a conflict later. a compat package
# with openssl-0.9.7 static-devel libs will be provided soon
Obsoletes:	%{conflict1}-static-devel
Obsoletes:	%{conflict2}-static-devel
Provides:	%{name}-static-devel = %{version}-%{release}

%description -n	%{libname}-static-devel
The static libraries needed to compile apps with support for various
cryptographic algorithms and protocols, including DES, RC4, RSA and SSL.

%prep

%setup -q -n %{name}-%{version}
%if %{french_policy}
%patch0 -p1 -b .frenchpolicy
%endif
%patch2 -p1 -b .optflags
%patch6 -p0 -b .icpbrasil
%patch7 -p1 -b .defaults
%{?_with_krb5:%patch8 -p1 -b .krb5}
%patch10 -p0 -b .ia64
%patch12 -p1 -b .x509
%patch13 -p1 -b .version-add-engines
%patch15 -p1 -b .crt
%patch16 -p1 -b .pkcs11_engine
%patch30 -p1 -b .mips
%patch31 -p1 -b .arm
%patch32 -p1 -b .engines

perl -pi -e "s,^(OPENSSL_LIBNAME=).+$,\1%{_lib}," Makefile.org engines/Makefile

# fix perl path
perl util/perlpath.pl %{_bindir}/perl

cp %{SOURCE2} Makefile.certificate
cp %{SOURCE3} make-dummy-cert
cp %{SOURCE4} openssl-thread-test.c
cp %{SOURCE5} README.pkcs11

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
    --openssldir=%{_sysconfdir}/pki/tls ${sslflags} \
    --enginesdir=%{_libdir}/openssl-%{version}/engines \
    --prefix=%{_prefix} --libdir=%{_lib}/ %{?_with_krb5:--with-krb5-flavor=MIT -I%{_prefix}/kerberos/include -L%{_prefix}/kerberos/%{_lib}} \
     enable-md2 no-idea no-rc5 enable-camellia shared enable-tlsext ${sslarch} --pk11-libname=%{_libdir}/pkcs11/PKCS11_API.so

#    zlib no-idea no-mdc2 no-rc5 no-ec no-ecdh no-ecdsa shared ${sslarch}

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

LD_LIBRARY_PATH=. ./openssl-thread-test --threads %{thread_test_threads}

%install
rm -fr %{buildroot}

%makeinstall \
    INSTALL_PREFIX=%{buildroot} \
    MANDIR=%{_mandir} \
    build-shared

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
chmod 755 %{buildroot}%{_libdir}/openssl-%{version}/engines/*.so*
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

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -fr %{buildroot}

%files 
%defattr(-,root,root)
%doc FAQ INSTALL LICENSE NEWS PROBLEMS main-doc-info/README*
%doc README README.ASN1 README.ENGINE README.pkcs11
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

%files -n openssl-engines
%defattr(-,root,root)
%attr(0755,root,root) %dir %{_libdir}/openssl-%{version}/engines
%attr(0755,root,root) %{_libdir}/openssl-%{version}/engines/*.so

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

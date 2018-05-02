# For the curious:
# 0.9.5a soversion = 0
# 0.9.6  soversion = 1
# 0.9.6a soversion = 2
# 0.9.6c soversion = 3
# 0.9.7a soversion = 4
# 0.9.7ef soversion = 5
# 0.9.8ab soversion = 6
# 0.9.8g soversion = 7
# 0.9.8jk + EAP-FAST soversion = 8
# 1.0.0 soversion = 10
# 1.1.0 soversion = 1.1 (same as upstream although presence of some symbols
#                        depends on build configuration options)
%define soversion 1.1
%define libcrypto %mklibname crypto %{soversion}
%define libssl %mklibname ssl %{soversion}
%define engines_name %mklibname openssl-engines %{soversion}
%define devname %mklibname openssl -d
%define staticname %mklibname openssl -s -d

# Number of threads to spawn when testing some threading fixes.
%define thread_test_threads %{?threads:%{threads}}%{!?threads:1}

# Arches on which we need to prevent arch conflicts on opensslconf.h, must
# also be handled in opensslconf-new.h.
%define multilib_arches %{ix86} ia64 %{mips} ppc %{power64} s390 s390x sparcv9 sparc64 x86_64

%global optflags %{optflags} -O3

# Disables krb5 support to avoid circular dependency
# (tpg) 2018-04-18 why do we need krb5 here ?
%bcond_with bootstrap

Summary: Utilities from the general purpose cryptography library with TLS implementation
Name: openssl
Version: 1.1.0h
Release: 2
# We have to remove certain patented algorithms from the openssl source
# tarball with the hobble-openssl script which is included below.
# The original openssl upstream tarball cannot be shipped in the .src.rpm.
Source0: https://www.openssl.org/source/openssl-%{version}.tar.gz
Source1: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/hobble-openssl
Source2: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/Makefile.certificate
Source6: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/make-dummy-cert
Source7: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/renew-dummy-cert
Source9: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/opensslconf-new.h
Source10: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/opensslconf-new-warning.h
Source11: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/README.FIPS
Source12: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/ec_curve.c
Source13: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/ectest.c
# Build changes
Patch1: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-build.patch
Patch2: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-defaults.patch
Patch3: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-no-html.patch
# Bug fixes
Patch21: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-issuer-hash.patch
Patch22: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-algo-doc.patch
Patch23: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-manfix.patch
# Functionality changes
Patch31: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-ca-dir.patch
Patch32: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-version-add-engines.patch
Patch33: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-apps-dgst.patch
Patch34: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-starttls-xmpp.patch
Patch35: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-chil-fixes.patch
Patch36: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-secure-getenv.patch
Patch38: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-no-md5-verify.patch
Patch39: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-cc-reqs.patch
Patch40: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-disable-ssl3.patch
Patch41: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-fips.patch
#Patch47: openssl-1.0.2a-readme-warning.patch FIPS
#Patch70: openssl-1.0.2a-fips-ec.patch
#Patch72: openssl-1.0.2a-fips-ctor.patch
#Patch76: openssl-1.0.2f-new-fips-reqs.patch
Patch92: http://pkgs.fedoraproject.org/cgit/rpms/openssl.git/plain/openssl-1.1.0-system-cipherlist.patch
# Backported fixes including security fixes
### OpenMandriva specific patches
Patch100: openssl-0.9.8-beta6-icpbrasil.diff
#Patch102: openssl-1.1.0c-fips-linkerscript.patch
Patch103: openssl-1.1.0d-clang-asm-buildfix.patch

License: OpenSSL
Group: System/Libraries
URL: http://www.openssl.org/
BuildRequires: coreutils
%if ! %{with bootstrap}
BuildRequires: krb5-devel
%endif
BuildRequires: perl
BuildRequires: sed
BuildRequires: zlib-devel
BuildRequires: pkgconfig(libsctp)
BuildRequires: /usr/bin/cmp
BuildRequires: /usr/bin/rename
BuildRequires: /usr/bin/pod2man
BuildRequires: perl(Test::Harness)
BuildRequires: perl(Test::More) => 0.96
BuildRequires: perl(Math::BigInt)
BuildRequires: perl(Module::Load::Conditional)
BuildRequires: perl(Timer::HiRes)
Requires: coreutils
Requires: make

%description
The OpenSSL toolkit provides support for secure communications between
machines. OpenSSL includes a certificate management tool and shared
libraries which provide various cryptographic algorithms and
protocols.

%package -n %{engines_name}
Summary: Engines for openssl
Group: System/Libraries
Provides: openssl-engines = %{version}-%{release}

%description -n	%{engines_name}
This package provides engines for openssl.

%package -n %{devname}
Summary: Files for development of applications which will use OpenSSL
Group: Development/Other
Requires: %{libcrypto} = %{EVRD}
Requires: %{libssl} = %{EVRD}
Provides: %{name}-devel = %{EVRD}

%description -n %{devname}
OpenSSL is a toolkit for supporting cryptography. The openssl-devel
package contains include files needed to develop applications which
support various cryptographic algorithms and protocols.

%package -n %{staticname}
Summary:  Libraries for static linking of applications which will use OpenSSL
Group: Development/Other
Requires: %{devname} = %{EVRD}

%description -n %{staticname}
OpenSSL is a toolkit for supporting cryptography. The openssl-static
package contains static libraries needed for static linking of
applications which support various cryptographic algorithms and
protocols.

%package perl
Summary: Perl scripts provided with OpenSSL
Group: System/Libraries
Requires: perl
Requires: %{name} = %{EVRD}

%description perl
OpenSSL is a toolkit for supporting cryptography. The openssl-perl
package provides Perl scripts for converting certificates and keys
from other formats to the formats used by the OpenSSL toolkit.

%package doc
Summary: OpenSSL documentation
Group: Books/Other
Requires: %{name} = %{EVRD}

%description doc
OpenSSL documentation.

%prep
%setup -q
cp %{SOURCE12} crypto/ec/
cp %{SOURCE13} test/

%apply_patches

sed -i -e 's|-O3 -fomit-frame-pointer|%{optflags}|g' Configurations/10-main.conf

%build
%serverbuild
# Figure out which flags we want to use.
# default
sslarch=%{_os}-%{_target_cpu}
%ifarch %ix86
sslarch=linux-elf
if ! echo %{_target} | grep -q i686 ; then
    sslflags="no-asm 386"
fi
%endif
%ifarch x86_64
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch sparcv9
sslarch=linux-sparcv9
sslflags=no-asm
%endif
%ifarch sparc64
sslarch=linux64-sparcv9
sslflags=no-asm
%endif
%ifarch alpha alphaev56 alphaev6 alphaev67
sslarch=linux-alpha-gcc
%endif
%ifarch s390 sh3eb sh4eb
sslarch="linux-generic32 -DB_ENDIAN"
%endif
%ifarch s390x
sslarch="linux64-s390x"
%endif
%ifarch %{arm}
sslarch=linux-armv4
%endif
%ifarch aarch64
sslarch=linux-aarch64
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch sh3 sh4
sslarch=linux-generic32
%endif
%ifarch ppc64 ppc64p7
sslarch=linux-ppc64
%endif
%ifarch ppc64le
sslarch="linux-ppc64le"
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch mips mipsel
sslarch="linux-mips32 -mips32r2"
%endif
%ifarch mips64 mips64el
sslarch="linux64-mips64 -mips64r2"
%endif
%ifarch mips64el
sslflags=enable-ec_nistp_64_gcc_128
%endif

# Add -Wa,--noexecstack here so that libcrypto's assembler modules will be
# marked as not requiring an executable stack.
# Also add -DPURIFY to make using valgrind with openssl easier as we do not
# want to depend on the uninitialized memory as a source of entropy anyway.
RPM_OPT_FLAGS="%{optflags} -Wa,--noexecstack -DPURIFY %{ldflags}"

%ifarch %{arm}
# For Thumb2-isms in ecp_nistz256-armv4
sed -i -e 's,-march=armv7-a,-march=armv7-a -fno-integrated-as,g' config
%endif

# ia64, x86_64, ppc are OK by default
# Configure the build tree.  Override OpenSSL defaults with known-good defaults
# usable on all platforms.  The Configure script already knows to use -fPIC and
# RPM_OPT_FLAGS, so we can skip specifiying them here.
./Configure \
	--prefix=%{_prefix} --libdir=%{_lib} \
	--system-ciphers-file=%{_sysconfdir}/crypto-policies/back-ends/openssl.config \
	--openssldir=%{_sysconfdir}/pki/tls ${sslflags} \
	zlib enable-camellia enable-seed enable-rfc3779 enable-sctp \
	enable-cms enable-md2 enable-rc5 enable-ssl3 enable-ssl3-method \
	no-mdc2 no-ec2m no-gost no-srp \
	shared  ${sslarch} $RPM_OPT_FLAGS

#	 %{?!nofips:fips}
util/mkdef.pl crypto update
%make all

# Overwrite FIPS README
cp -f %{SOURCE11} .

# Clean up the .pc files
for i in libcrypto.pc libssl.pc openssl.pc ; do
    sed -i '/^Libs.private:/{s/-L[^ ]* //;s/-Wl[^ ]* //}' $i
done

%check
# Verify that what was compiled actually works.

# We must revert patch31 before tests otherwise they will fail
patch -p1 -R < %{PATCH31}

# This seems to fail because of a problem with the test
rm test/recipes/30-test_evp.t

LD_LIBRARY_PATH=`pwd`${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
export LD_LIBRARY_PATH
OPENSSL_ENABLE_MD5_VERIFY=
export OPENSSL_ENABLE_MD5_VERIFY
make test

# Add generation of HMAC checksum of the final stripped library
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    crypto/fips/fips_standalone_hmac %{buildroot}%{_libdir}/libcrypto.so.%{version} >%{buildroot}%{_libdir}/.libcrypto.so.%{version}.hmac \
    ln -sf .libcrypto.so.%{version}.hmac %{buildroot}%{_libdir}/.libcrypto.so.%{soversion}.hmac \
    crypto/fips/fips_standalone_hmac %{buildroot}%{_libdir}/libssl.so.%{version} >%{buildroot}%{_libdir}/.libssl.so.%{version}.hmac \
    ln -sf .libssl.so.%{version}.hmac %{buildroot}%{_libdir}/.libssl.so.%{soversion}.hmac \
%{nil}

%define __provides_exclude_from %{_libdir}/openssl

%install
# Install OpenSSL.
install -d %{buildroot}{%{_bindir},%{_includedir},%{_libdir},%{_mandir},%{_libdir}/openssl}
make DESTDIR=%{buildroot} install
rename so.%{soversion} so.%{version} %{buildroot}%{_libdir}/*.so.%{soversion}
mkdir %{buildroot}/%{_lib}
for lib in %{buildroot}%{_libdir}/*.so.%{version} ; do
    chmod 755 ${lib}
    ln -s -f `basename ${lib}` %{buildroot}%{_libdir}/`basename ${lib} .%{version}`
    ln -s -f `basename ${lib}` %{buildroot}%{_libdir}/`basename ${lib} .%{version}`.%{soversion}
done

# Install a makefile for generating keys and self-signed certs, and a script
# for generating them on the fly.
mkdir -p %{buildroot}%{_sysconfdir}/pki/tls/certs
install -m644 %{SOURCE2} %{buildroot}%{_sysconfdir}/pki/tls/certs/Makefile
install -m755 %{SOURCE6} %{buildroot}%{_bindir}/make-dummy-cert
install -m755 %{SOURCE7} %{buildroot}%{_bindir}/renew-dummy-cert

# Move runable perl scripts to bindir
mv %{buildroot}%{_sysconfdir}/pki/tls/misc/*.pl %{buildroot}%{_bindir}
mv %{buildroot}%{_sysconfdir}/pki/tls/misc/tsget %{buildroot}%{_bindir}

# Make sure we actually include the headers we built against.
for header in %{buildroot}%{_includedir}/openssl/* ; do
    if [ -f ${header} -a -f include/openssl/$(basename ${header}) ] ; then
	install -m644 include/openssl/`basename ${header}` ${header}
    fi
done

# Rename man pages so that they don't conflict with other system man pages.
pushd %{buildroot}%{_mandir}
ln -s -f config.5 man5/openssl.cnf.5
for manpage in man*/* ; do
    if [ -L ${manpage} ]; then
	TARGET=`ls -l ${manpage} | awk '{ print $NF }'`
	ln -snf ${TARGET}ssl ${manpage}ssl
	rm -f ${manpage}
    else
	mv ${manpage} ${manpage}ssl
    fi
done
for conflict in passwd rand ; do
    rename ${conflict} ssl${conflict} man*/${conflict}*
done
popd

mkdir -m755 %{buildroot}%{_sysconfdir}/pki/CA
mkdir -m700 %{buildroot}%{_sysconfdir}/pki/CA/private
mkdir -m755 %{buildroot}%{_sysconfdir}/pki/CA/certs
mkdir -m755 %{buildroot}%{_sysconfdir}/pki/CA/crl
mkdir -m755 %{buildroot}%{_sysconfdir}/pki/CA/newcerts

# Ensure the openssl.cnf timestamp is identical across builds to avoid
# mulitlib conflicts and unnecessary renames on upgrade
touch -r %{SOURCE2} %{buildroot}%{_sysconfdir}/pki/tls/openssl.cnf

rm -f %{buildroot}%{_sysconfdir}/pki/tls/openssl.cnf.dist

# Determine which arch opensslconf.h is going to try to #include.
basearch=%{_arch}
%ifarch %{ix86}
basearch=i386
%endif
%ifarch sparcv9
basearch=sparc
%endif
%ifarch sparc64
basearch=sparc64
%endif

%ifarch %{multilib_arches}
# Do an opensslconf.h switcheroo to avoid file conflicts on systems where you
# can have both a 32- and 64-bit version of the library, and they each need
# their own correct-but-different versions of opensslconf.h to be usable.
install -m644 %{SOURCE10} \
	%{buildroot}/%{_includedir}/openssl/opensslconf-${basearch}.h
cat %{buildroot}/%{_includedir}/openssl/opensslconf.h >> \
	%{buildroot}/%{_includedir}/openssl/opensslconf-${basearch}.h
install -m644 %{SOURCE9} \
	%{buildroot}/%{_includedir}/openssl/opensslconf.h
%endif

# For spec_install_post script
export LD_LIBRARY_PATH=`pwd`${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

%libpackage crypto %{soversion}
%{_libdir}/.libcrypto*.hmac

%libpackage ssl %{soversion}
%{_libdir}/.libssl*.hmac

%files
%{!?_licensedir:%global license %%doc}
%license LICENSE
%{_bindir}/make-dummy-cert
%{_bindir}/renew-dummy-cert
%{_sysconfdir}/pki/tls/certs/Makefile
%dir %{_sysconfdir}/pki/tls
%dir %{_sysconfdir}/pki/tls/certs
%dir %{_sysconfdir}/pki/tls/misc
%dir %{_sysconfdir}/pki/tls/private
%config(noreplace) %{_sysconfdir}/pki/tls/openssl.cnf
%attr(0755,root,root) %{_bindir}/openssl
%attr(0644,root,root) %{_mandir}/man1*/[ABD-Zabcd-z]*
%attr(0644,root,root) %{_mandir}/man5*/*
%attr(0644,root,root) %{_mandir}/man7*/*

%files -n %{engines_name}
%dir %{_libdir}/engines-%{soversion}
%{_libdir}/engines-%{soversion}/*.so

%files -n %{devname}
%{_includedir}/openssl
%attr(0755,root,root) %{_libdir}/*.so
%attr(0644,root,root) %{_mandir}/man3*/*
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%files -n %{staticname}
%attr(0644,root,root) %{_libdir}/*.a

%files perl
%attr(0755,root,root) %{_bindir}/c_rehash
%attr(0755,root,root) %{_bindir}/*.pl
%attr(0755,root,root) %{_bindir}/tsget
%attr(0644,root,root) %{_mandir}/man1*/*.pl*
%dir %{_sysconfdir}/pki/CA
%dir %{_sysconfdir}/pki/CA/private
%dir %{_sysconfdir}/pki/CA/certs
%dir %{_sysconfdir}/pki/CA/crl
%dir %{_sysconfdir}/pki/CA/newcerts

%files doc
%doc CHANGES doc/dir-locals.example.el doc/openssl-c-indent.el
%doc FAQ NEWS README README.FIPS

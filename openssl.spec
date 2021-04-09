# openssl is used by systemd, libsystemd is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

# (tpg) enable PGO build
%ifnarch riscv64
%bcond_without pgo
%endif

%global optflags %{optflags} -O3

%define beta alpha14
%define major 3
%define libssl %mklibname ssl %{major}
%define libcrypto %mklibname crypto %{major}
%define devel %mklibname openssl -d
%define static %mklibname openssl -s -d
%define lib32ssl libssl%{major}
%define lib32crypto libcrypto%{major}
%define devel32 libopenssl-devel
%define static32 libopenssl-static-devel

Name:		openssl
Version:	3.0.0
Release:	%{?beta:0.%{beta}.}1
Group:		System/Libraries
Summary:	The OpenSSL cryptography and TLS library
Source0:	https://www.openssl.org/source/openssl-%{version}%{?beta:-%{beta}}.tar.gz
Patch0:		openssl-3.0-additional-clang-targets.patch
License:	Apache 2.0
BuildRequires:	perl
BuildRequires:	perl(Pod::Man)
BuildRequires:	perl(Pod::Html)
BuildRequires:	pkgconfig(libsctp)
BuildRequires:	pkgconfig(zlib)

%description
The OpenSSL cryptography and TLS library.

%files
%dir %{_sysconfdir}/pki
%dir %{_sysconfdir}/pki/tls
%dir %{_sysconfdir}/pki/tls/misc
%{_sysconfdir}/pki/tls/ct_log_list.cnf
%{_sysconfdir}/pki/tls/ct_log_list.cnf.dist
%{_sysconfdir}/pki/tls/openssl.cnf
%{_sysconfdir}/pki/tls/openssl.cnf.dist
%{_bindir}/c_rehash
%{_bindir}/openssl
%dir %{_libdir}/engines-3
%{_libdir}/engines-3/afalg.so
%{_libdir}/engines-3/capi.so
%{_libdir}/engines-3/padlock.so
%dir %{_libdir}/ossl-modules
%{_libdir}/ossl-modules/legacy.so
%{_libdir}/ossl-modules/fips.so
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man7/*

%package perl
Summary:	Perl based tools for working with OpenSSL
Group:		System/Libraries
Requires:	%{name} = %{EVRD}

%description perl
Perl based tools for working with OpenSSL.

%files perl
%dir %{_sysconfdir}/pki/tls/misc
%{_sysconfdir}/pki/tls/misc/CA.pl
%{_sysconfdir}/pki/tls/misc/tsget.pl
%{_sysconfdir}/pki/tls/misc/tsget

%package -n %{libssl}
Summary:	The OpenSSL SSL/TLS library
Group:		System/Libraries

%description -n %{libssl}
The OpenSSL SSL/TLS library.

%files -n %{libssl}
%{_libdir}/libssl.so.%{major}*

%package -n %{libcrypto}
Summary:	The OpenSSL cryptography library
Group:		System/Libraries

%description -n %{libcrypto}
The OpenSSL cryptography library.

%files -n %{libcrypto}
%{_libdir}/libcrypto.so.%{major}*

%package -n %{devel}
Summary:	Development files for OpenSSL
Group:		Development/C
Requires:	%{libssl} = %{EVRD}
Requires:	%{libcrypto} = %{EVRD}

%description -n %{devel}
Development files for OpenSSL.

%files -n %{devel}
%{_includedir}/openssl
%{_libdir}/libcrypto.so
%{_libdir}/libssl.so
%{_mandir}/man3/*
%{_libdir}/pkgconfig/libcrypto.pc
%{_libdir}/pkgconfig/libssl.pc
%{_libdir}/pkgconfig/openssl.pc
%doc %{_docdir}/openssl

%package -n %{static}
Summary:	Static libraries for OpenSSL
Group:		Development/C
Requires:	%{devel} = %{EVRD}

%description -n %{static}
Static libraries for OpenSSL.

%files -n %{static}
%{_libdir}/libssl.a
%{_libdir}/libcrypto.a

%if %{with compat32}
%package -n %{lib32ssl}
Summary:	The OpenSSL SSL/TLS library (32-bit)
Group:		System/Libraries
BuildRequires:	cross-i686-openmandriva-linux-gnu-gcc

%description -n %{lib32ssl}
The OpenSSL SSL/TLS library.

%files -n %{lib32ssl}
%{_prefix}/lib/libssl.so.%{major}*

%package -n %{lib32crypto}
Summary:	The OpenSSL cryptography library (32-bit)
Group:		System/Libraries

%description -n %{lib32crypto}
The OpenSSL cryptography library.

%files -n %{lib32crypto}
%{_prefix}/lib/libcrypto.so.%{major}*

%package -n %{devel32}
Summary:	Development files for OpenSSL (32-bit)
Group:		Development/C
Requires:	%{devel} = %{EVRD}
Requires:	%{lib32ssl} = %{EVRD}
Requires:	%{lib32crypto} = %{EVRD}

%description -n %{devel32}
Development files for OpenSSL.

%files -n %{devel32}
%{_prefix}/lib/libcrypto.so
%{_prefix}/lib/libssl.so
%{_prefix}/lib/pkgconfig/libcrypto.pc
%{_prefix}/lib/pkgconfig/libssl.pc
%{_prefix}/lib/pkgconfig/openssl.pc

%package -n %{static32}
Summary:	Static libraries for OpenSSL (32-bit)
Group:		Development/C
Requires:	%{devel32} = %{EVRD}

%description -n %{static32}
Static libraries for OpenSSL.

%files -n %{static32}
%{_prefix}/lib/libssl.a
%{_prefix}/lib/libcrypto.a

%package 32
Summary:	Plugins for the 32-bit version of OpenSSL
Group:		System/Libraries
Requires:	%{lib32ssl} = %{EVRD}
Requires:	%{lib32crypto} = %{EVRD}

%description 32
Plugins for the 32-bit version of OpenSSL.

%files 32
%dir %{_prefix}/lib/engines-3
%{_prefix}/lib/engines-3/capi.so
%{_prefix}/lib/engines-3/padlock.so
%dir %{_prefix}/lib/ossl-modules
%{_prefix}/lib/ossl-modules/legacy.so
%{_prefix}/lib/ossl-modules/fips.so
%endif

%prep
%autosetup -p1 -n %{name}-%{version}%{?beta:-%{beta}}

%build
case %{_arch} in
arm*)
	TARGET=%{_target_os}-armv4
	;;
riscv32)
	TARGET=%{_target_os}-generic32
	;;
riscv64)
	TARGET=%{_target_os}-generic64
	;;
i*86|pentium*|athlon*)
	TARGET=%{_target_os}-x86
	;;
*)
	TARGET=%{_target_os}-%{_arch}
	;;
esac
echo %{__cc} |grep -q clang && TARGET="${TARGET}-clang"

%if %{with compat32}
export CFLAGS="%(echo %{optflags} |sed -e 's,-mx32,,g;s,-m64,,g;s,-flto,,g') -fno-strict-aliasing -isystem %{_includedir}"
export LDFLAGS="%(echo %{optflags} |sed -e 's,-mx32,,g;s,-m64,,g;s,-flto,,g') -fno-strict-aliasing"

mkdir build32
cd build32
CROSS_COMPILE=i686-openmandriva-linux-gnu- \
../Configure \
	linux-x86 \
	--prefix=%{_prefix} \
	--libdir=%{_prefix}/lib \
	--openssldir=%{_sysconfdir}/pki/tls \
	threads shared zlib-dynamic sctp 386

%make_build
cd ..
%endif

export CFLAGS="%{optflags} -fno-strict-aliasing"
export LDFLAGS="%{optflags} -fno-strict-aliasing"
%ifarch %{ix86}
export CFLAGS="${CFLAGS} -fPIC"
export LDFLAGS="${LDFLAGS} -fPIC -Wl,-z,notext"
%endif
mkdir build
cd build

%if %{with pgo}
export LLVM_PROFILE_FILE=%{name}-%p.profile.d
export LD_LIBRARY_PATH="$(pwd)"
CFLAGS="$CFLAGS -fprofile-instr-generate" \
CXXFLAGS="%{optflags} -fprofile-instr-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{build_ldflags} -fprofile-instr-generate" \
../Configure ${TARGET} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--openssldir=%{_sysconfdir}/pki/tls \
	threads shared zlib-dynamic sctp \
%ifarch %{x86_64} %{ix86}
	386
%endif

make depend
make

#apps/openssl speed
LD_PRELOAD="./libcrypto.so ./libssl.so" apps/openssl speed rsa

unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=%{name}.profile *.profile.d

make clean
CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif
../Configure ${TARGET} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--openssldir=%{_sysconfdir}/pki/tls \
	threads shared zlib-dynamic sctp \
%ifarch %{x86_64} %{ix86}
	386
%endif

%make_build

%install
%if %{with compat32}
%make_install -C build32
%endif
%make_install -C build

# openssl is used by systemd, libsystemd is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

# (tpg) enable PGO build
%if %{cross_compiling}
%bcond_with pgo
%else
%ifarch %{aarch64}
# FIXME as of 3.4.0, clang 19.1.4, `openssl speed`
# crashes at runtime, causing PGO to fail
%bcond_with pgo
%else
%bcond_without pgo
%endif
%endif

%global optflags %{optflags} -O3

# (tpg) use LLVM/polly for polyhedra optimization and automatic vector code generation
%define pollyflags -mllvm -polly -mllvm -polly-position=early -mllvm -polly-parallel=true -fopenmp -fopenmp-version=50 -mllvm -polly-dependences-computeout=5000000 -mllvm -polly-detect-profitability-min-per-loop-insts=40 -mllvm -polly-tiling=true -mllvm -polly-prevect-width=256 -mllvm -polly-vectorizer=stripmine -mllvm -polly-omp-backend=LLVM -mllvm -polly-num-threads=0 -mllvm -polly-enable-delicm=true -mllvm -extra-vectorizer-passes -mllvm -enable-cond-stores-vec -mllvm -slp-vectorize-hor-store -mllvm -enable-loopinterchange -mllvm -enable-loop-distribute -mllvm -enable-unroll-and-jam -mllvm -enable-loop-flatten -mllvm -unroll-runtime-multi-exit -mllvm -aggressive-ext-opt -mllvm -polly-scheduling=dynamic -mllvm -polly-scheduling-chunksize=1 -mllvm -polly-invariant-load-hoisting -mllvm -polly-loopfusion-greedy -mllvm -polly-run-inliner
# (tpg) 2022-11-21 this -mllvm -polly-run-dce causes segfault on aarch64

#define beta beta1
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
Version:	3.5.1
Release:	%{?beta:0.%{beta}.}1
Group:		System/Libraries
Summary:	The OpenSSL cryptography and TLS library
Source0:	https://www.openssl.org/source/openssl-%{version}%{?beta:-%{beta}}.tar.gz
Patch0:		openssl-3.0-additional-clang-targets.patch
# QUIC support patches from https://github.com/quictls/openssl
# Currently none required
License:	Apache 2.0
BuildRequires:	perl
BuildRequires:	perl(Pod::Man)
BuildRequires:	perl(Pod::Html)
BuildRequires:	pkgconfig(libsctp)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	atomic-devel
BuildRequires:	llvm-polly

%description
The OpenSSL cryptography and TLS library.

%files
%dir %{_sysconfdir}/pki/tls
%dir %{_sysconfdir}/pki/tls/misc
%dir %{_sysconfdir}/pki/tls/private
%{_sysconfdir}/pki/tls/ct_log_list.cnf
%{_sysconfdir}/pki/tls/ct_log_list.cnf.dist
%{_sysconfdir}/pki/tls/openssl.cnf
%{_sysconfdir}/pki/tls/openssl.cnf.dist
%{_sysconfdir}/pki/tls/fipsmodule.cnf
%{_bindir}/c_rehash
%{_bindir}/openssl
%dir %{_libdir}/engines-3
%{_libdir}/engines-3/afalg.so
%{_libdir}/engines-3/capi.so
%{_libdir}/engines-3/loader_attic.so
%{_libdir}/engines-3/padlock.so
%dir %{_libdir}/ossl-modules
%{_libdir}/ossl-modules/legacy.so
%{_libdir}/ossl-modules/fips.so
%doc %{_mandir}/man1/*
%doc %{_mandir}/man5/*
%doc %{_mandir}/man7/*

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
%{_modulesloaddir}/openssl-tls.conf
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
%doc %{_mandir}/man3/*
%{_libdir}/pkgconfig/libcrypto.pc
%{_libdir}/pkgconfig/libssl.pc
%{_libdir}/pkgconfig/openssl.pc
%doc %{_docdir}/openssl
%{_libdir}/cmake/OpenSSL

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
BuildRequires:	libc6
BuildRequires:	devel(libz)
Requires:	libc6

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
%{_prefix}/lib/cmake/OpenSSL

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
%{_prefix}/lib/engines-3/afalg.so
%{_prefix}/lib/engines-3/capi.so
%{_prefix}/lib/engines-3/loader_attic.so
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
	TARGET=%{_target_os}32-riscv32
	;;
riscv64)
	TARGET=%{_target_os}64-riscv64
	;;
i*86|pentium*|athlon*)
	TARGET=%{_target_os}-x86
	;;
*)
	TARGET=%{_target_os}-%{_arch}
	;;
esac
# There's no separate linux64-riscv64-clang target, but
# linux64-riscv64 works with clang
%ifnarch %{riscv64}
echo %{__cc} |grep -q clang && TARGET="${TARGET}-clang"
%endif

%if %{with compat32}
export CFLAGS="%(echo %{optflags} |sed -e 's,-mx32,,g;s,-m64,,g;s,-flto,,g') -fno-strict-aliasing -m32 -isystem %{_includedir}"
export LDFLAGS="%(echo %{optflags} |sed -e 's,-mx32,,g;s,-m64,,g;s,-flto,,g') -fno-strict-aliasing -m32"

cp build.info build.info.orig
sed -i -e 's,LIBDIR=,LIBDIR=lib,g' build.info
mkdir build32
cd build32
../Configure \
	linux-x86 \
	--prefix=%{_prefix} \
	--libdir=%{_prefix}/lib \
	--openssldir=%{_sysconfdir}/pki/tls \
	threads shared zlib sctp 386 enable-fips enable-ktls no-tests
sed -i -e 's,^LIBDIR=$,LIBDIR=lib,' Makefile

%make_build
cd ..
mv build.info build.info.32
mv build.info.orig build.info
%endif

sed -i -e 's,LIBDIR=,LIBDIR=%{_lib},g' build.info
export CFLAGS="%{optflags} -fno-strict-aliasing"
export LDFLAGS="%{optflags} -fno-strict-aliasing"
%ifarch %{ix86}
export CFLAGS="${CFLAGS} -fPIC"
export LDFLAGS="${LDFLAGS} -fPIC -Wl,-z,notext"
%endif
mkdir build
cd build

%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)"

CC="%{__cc}" \
CXX="%{__cxx}" \
CFLAGS="$CFLAGS -fprofile-generate %{pollyflags}" \
CXXFLAGS="%{optflags} -fprofile-generate %{pollyflags}" \
LDFLAGS="$LDFLAGS -fprofile-generate" \
../Configure ${TARGET} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--openssldir=%{_sysconfdir}/pki/tls \
%ifarch %{x86_64} %{aarch64}
	enable-ec_nistp_64_gcc_128 \
%endif
%ifarch %{x86_64} %{ix86}
	386 \
%endif
	threads shared zlib sctp enable-fips enable-ktls no-tests

%make_build

# Run benchmarks on all algorithms to generate profile data.
LD_PRELOAD="./libcrypto.so ./libssl.so" apps/openssl speed

unset LD_LIBRARY_PATH
llvm-profdata merge --output=%{name}-llvm.profdata $(find . -name "*.profraw" -type f)
PROFDATA="$(realpath %{name}-llvm.profdata)"
rm -f *.profraw

make clean

CFLAGS="$CFLAGS -fprofile-use=$PROFDATA %{pollyflags}" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA %{pollyflags}" \
LDFLAGS="$LDFLAGS -fprofile-use=$PROFDATA" \
%endif
CC="%{__cc}" \
CXX="%{__cxx}" \
../Configure ${TARGET} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--openssldir=%{_sysconfdir}/pki/tls \
%ifarch %{x86_64} %{aarch64}
	enable-ec_nistp_64_gcc_128 \
%endif
%ifarch %{x86_64} %{ix86}
	386 \
%endif
	threads shared zlib sctp enable-fips enable-ktls no-tests
sed -i -e 's,^LIBDIR=$,LIBDIR=%{_lib},' Makefile

%make_build

%install
%if %{with compat32}
mv build.info build.info.64
mv build.info.32 build.info
%make_install install_sw -C build32
mv build.info build.info.32
mv build.info.64 build.info
%endif
%make_install install_sw install_fips install_man_docs -C build

# Replace bogus absolute symlinks pointing to the buildroot
cd %{buildroot}%{_mandir}
for i in *; do
    cd "$i"
	for j in *; do
	    [ -L "$j" ] && ln -sf "$(basename $(ls -l "$j" |cut -d'>' -f2-))" "$j"
	done
    cd ..
done

# Used by e.g. %_create_ssl_certificate (rpm-helper)
mkdir -p %{buildroot}%{_sysconfdir}/pki/tls/private

# enable kernel TLS offload support
mkdir -p %{buildroot}%{_modulesloaddir}
cat > %{buildroot}%{_modulesloaddir}/openssl-tls.conf << EOF
tls
EOF

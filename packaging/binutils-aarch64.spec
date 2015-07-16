%define cross aarch64
%define aarch64 1

%ifarch armv7l
%define ARCH armv7l
%define ABI eabi
%endif
%ifarch %ix86
%define ARCH i586
%endif
%ifarch x86_64
%define ARCH x86_64
%endif
%ifarch aarch64
%define ARCH aarch64
%endif

%define host_arch %{ARCH}-tizen-linux-gnu%{?ABI}

%define target_cpu %{?cross}%{!?cross:%{ARCH}}
%define target_abi %{?cross:%{?armv7l:eabi}}%{!?cross:%{?ABI}}

%define target_arch %{target_cpu}-tizen-linux-gnu%{?target_abi}

Name:           binutils%{?cross:-%{cross}}
BuildRequires:  makeinfo
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  ncurses-devel
BuildRequires:  zlib-devel
BuildRequires:  gcc-c++
Version:        2.25
Release:        0
Url:            http://www.gnu.org/software/binutils/
Summary:        GNU Binutils
License:        GFDL-1.3 and GPL-3.0+
Group:          Development/Building
%{?cross:ExcludeArch: %{cross}}
Source:         binutils-%{version}.tar.bz2
Source1001:     binutils.manifest

%description
C compiler utilities: ar, as, gprof, ld, nm, objcopy, objdump, ranlib,
size, strings, and strip. These utilities are needed whenever you want
to compile a program or kernel.


%package gold
Summary:        The gold linker
License:        GPL-3.0+
Group:          Development/Building

%description gold
gold is an ELF linker.	It is intended to have complete support for ELF
and to run as fast as possible on modern systems.  For normal use it is
a drop-in replacement for the older GNU linker.


%package devel
Summary:        GNU binutils (BFD development files)
License:        GPL-3.0+
Group:          Development/Building

%description devel
This package includes header files and static libraries necessary to
build programs which use the GNU BFD library, which is part of
binutils.


%prep
%setup -q -n binutils-%{version}
cp %{SOURCE1001} .


%build
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -Wno-error %{?cross:-DIGNORE_MISSING_PLUGINS}"
export CFLAGS="${RPM_OPT_FLAGS}"
export CXXFLAGS="${RPM_OPT_FLAGS}"

mkdir build-dir
cd build-dir

../configure \
	--prefix=%{_prefix} --libdir=%{_libdir} \
	--infodir=%{_infodir} --mandir=%{_mandir} \
	--with-bugurl=http://bugs.tizen.org/ \
	--with-sysroot=/ \
	--disable-nls \
	--with-separate-debug-dir=%{_prefix}/lib/debug \
	--with-pic \
	--build=%{host_arch} --target=%{target_arch} \
	--host=%{host_arch} \
%{?cross: \
	--enable-targets=%{target_arch} \
} \
%{!?cross: \
	--enable-targets=aarch64-tizen-linux,armv7l-tizen-linux,armv8l-tizen-linux,i686-tizen-linux,x86_64-tizen-linux \
} \
	--enable-plugins \
	--enable-gold \
	--enable-shared

make %{?_smp_mflags}

%install
cd build-dir
make DESTDIR=$RPM_BUILD_ROOT install

# Copy instead of hardlinks
for binary in ar as ld{,.bfd,.gold} nm obj{dump,copy} ranlib strip
do
  rm %{buildroot}%{_prefix}/%{target_arch}/bin/$binary
%{!?cross:
  cp %{buildroot}%{_bindir}/$binary %{buildroot}%{_prefix}/%{target_arch}/bin/$binary
}
%{?cross:
  cp %{buildroot}%{_bindir}/%{target_arch}-$binary %{buildroot}%{_prefix}/%{target_arch}/bin/$binary
}
done

# Remove unwanted files to shut up rpm
%{remove_docs}
rm -rf %{buildroot}%{_bindir}/gcore
rm -rf %{buildroot}%{_bindir}/gdb*
rm -rf %{buildroot}%{_datadir}/gdb
rm -rf %{buildroot}%{_libdir}/lib{bfd,opcodes,inproctrace}.{so,la}
%{?cross:
rm -rf %{buildroot}%{_prefix}/%{target_arch}/lib/ldscripts
rm -rf %{buildroot}%{_prefix}/%{host_arch}
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_prefix}/lib*
rm -rf %{buildroot}%{_datadir}
}

%files 
%manifest binutils.manifest
%defattr(-,root,root)
%{_bindir}/*
%{_prefix}/%{target_arch}/bin/*
%{!?cross:
%exclude %{_bindir}/ld.gold
%exclude %{_prefix}/%{target_arch}/bin/ld.gold
%{_libdir}/*.so
%{_prefix}/%{host_arch}/lib/ldscripts

%files devel
%manifest binutils.manifest
%defattr(-,root,root)
%{_includedir}/*.h
%{_includedir}/gdb/*.h
%{_libdir}/*.a

%files gold
%manifest binutils.manifest
%defattr(-,root,root)
%{_bindir}/ld.gold
%{_prefix}/%{target_arch}/bin/ld.gold
}

%changelog

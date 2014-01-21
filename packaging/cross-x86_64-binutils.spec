Name:         cross-x86_64-binutils
ExcludeArch: x86_64
%define cross 1
%define TARGET x86_64
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  gcc-c++
# for the testsuite
BuildRequires:  glibc-devel-static
# for some gold tests
BuildRequires:  bc
BuildRequires:  makeinfo
BuildRequires:  zlib-devel-static
Requires(pre):  update-alternatives
Version:        2.23.1
Release:        0
#
# RUN_TESTS
%define run_tests %(test ! -f %_sourcedir/RUN_TESTS ; echo $?)
# check the vanilla binutils, with no patches applied
# TEST_VANILLA
%define test_vanilla %(test ! -f %_sourcedir/TEST_VANILLA ; echo $?)
#
# handle test suite failures
#
%ifarch alpha %arm aarch64 hppa mips sh4 %sparc
%define	make_check_handling	true
%else
# XXX check again
# XXX disabled because gold is seriously broken for now
%define	make_check_handling	true
%endif
# let make check fail anyway if RUN_TESTS was requested
%if %{run_tests}
%define	make_check_handling	false
%endif
# handle all binary object formats supported by SuSE (and a few more)
%ifarch %ix86 %arm aarch64 ia64 ppc ppc64 s390 s390x x86_64
%define build_multitarget 1
%else
%define build_multitarget 0
%endif
%define target_list aarch64 alpha armv5l armv7l armv8l hppa hppa64 i686 ia64 m68k mips powerpc powerpc64 s390 s390x sh4 sparc sparc64 x86_64
#
#
#
Url:            http://www.gnu.org/software/binutils/
#%define binutils_version %(echo %version | sed 's/\\.[0-9]\\{8\\}$//')
Summary:        GNU Binutils
License:        GFDL-1.3 and GPL-3.0+
Group:          Development/Tools/Building
Source:         binutils-%{version}.tar.bz2
Source1:        pre_checkin.sh
Source3:        baselibs.conf

%description
C compiler utilities: ar, as, gprof, ld, nm, objcopy, objdump, ranlib,
size, strings, and strip. These utilities are needed whenever you want
to compile a program or kernel.


%package gold
Summary:        The gold linker
License:        GPL-3.0+
Group:          Development/Tools/Building
Requires:       binutils = %{version}-%{release}
%if 0%{!?cross:1}
%define gold_archs %ix86 %arm aarch64 x86_64 ppc ppc64 %sparc
%endif

%description gold
gold is an ELF linker.	It is intended to have complete support for ELF
and to run as fast as possible on modern systems.  For normal use it is
a drop-in replacement for the older GNU linker.


%package devel
Summary:        GNU binutils (BFD development files)
License:        GPL-3.0+
Group:          Development/Libraries/C and C++
Requires:       binutils = %{version}-%{release}
Requires:       zlib-devel
Provides:       binutils:/usr/include/bfd.h

%description devel
This package includes header files and static libraries necessary to
build programs which use the GNU BFD library, which is part of
binutils.


%ifarch %arm
%define HOST %{_target_cpu}-tizen-linux-gnueabi
%else
%define HOST %(echo %{_target_cpu} | sed -e "s/parisc/hppa/" -e "s/i.86/i586/" -e "s/ppc/powerpc/" -e "s/sparc64v.*/sparc64/" -e "s/sparcv.*/sparc/")-tizen-linux
%endif 
%define DIST %(echo '%distribution' | sed 's/ (.*)//')

%prep
echo "make check will return with %{make_check_handling} in case of testsuite failures."
%setup -q -n binutils-%{version}

sed -i -e '/BFD_VERSION_DATE/s/$/-%(echo %release | sed 's/\.[0-9]*$//')/' bfd/version.h
%build
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -Wno-error"
RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS |sed -e 's/atom/i686/g'`
%if 0%{!?cross:1}
# Building native binutils
echo "Building native binutils." 
%if %build_multitarget
EXTRA_TARGETS="%(printf ,%%s-tizen-linux %target_list)"
EXTRA_TARGETS="$EXTRA_TARGETS,powerpc-macos,powerpc-macos10,spu-elf,x86_64-pep"
%else
EXTRA_TARGETS=
%ifarch sparc
EXTRA_TARGETS="$EXTRA_TARGETS,sparc64-tizen-linux"
%endif
%ifarch ppc
EXTRA_TARGETS="$EXTRA_TARGETS,powerpc64-tizen-linux"
%endif
%ifarch s390
EXTRA_TARGETS="$EXTRA_TARGETS,s390x-tizen-linux"
%endif
%ifarch s390x
EXTRA_TARGETS="$EXTRA_TARGETS,s390-tizen-linux"
%endif
%ifarch %ix86
EXTRA_TARGETS="$EXTRA_TARGETS,x86_64-tizen-linux"
%endif
%ifarch ppc ppc64
EXTRA_TARGETS="$EXTRA_TARGETS,spu-elf"
%endif
%ifarch %arm
EXTRA_TARGETS="$EXTRA_TARGETS,arm-tizen-linux-gnueabi"
%endif
%ifarch aarch64
EXTRA_TARGETS="$EXTRA_TARGETS,aarch64-tizen-linux"
%endif
%endif
%define common_flags CFLAGS="${RPM_OPT_FLAGS}" CXXFLAGS="${RPM_OPT_FLAGS}" \\\
	--prefix=%{_prefix} --libdir=%{_libdir} \\\
	--infodir=%{_infodir} --mandir=%{_mandir} \\\
	--with-bugurl=http://bugs.opensuse.org/ \\\
	--with-pkgversion="GNU Binutils; %{DIST}" \\\
	--disable-nls \\\
	--with-separate-debug-dir=%{_prefix}/lib/debug \\\
	--with-pic --build=%{HOST} 
mkdir build-dir
cd build-dir
../configure %common_flags \
	${EXTRA_TARGETS:+--enable-targets="${EXTRA_TARGETS#,}"} \
	--enable-plugins \
%ifarch %gold_archs
	--enable-gold \
%endif
	--enable-shared
make %{?_smp_mflags} all-bfd TARGET-bfd=headers
# force reconfiguring (???)
rm bfd/Makefile
make %{?_smp_mflags}

%else
# building cross-TARGET-binutils
echo "Building cross binutils." 
mkdir build-dir
cd build-dir
EXTRA_TARGETS=
%if "%{TARGET}" == "sparc"
EXTRA_TARGETS="$EXTRA_TARGETS,sparc64-tizen-linux"
%endif
%if "%{TARGET}" == "powerpc"
EXTRA_TARGETS="$EXTRA_TARGETS,powerpc64-tizen-linux"
%endif
%if "%{TARGET}" == "s390"
EXTRA_TARGETS="$EXTRA_TARGETS,s390x-tizen-linux"
%endif
%if "%{TARGET}" == "s390x"
EXTRA_TARGETS="$EXTRA_TARGETS,s390-tizen-linux"
%endif
%if "%{TARGET}" == "i586"
EXTRA_TARGETS="$EXTRA_TARGETS,x86_64-tizen-linux"
%endif
%if "%{TARGET}" == "hppa"
EXTRA_TARGETS="$EXTRA_TARGETS,hppa64-tizen-linux"
%endif
%if "%{TARGET}" == "arm"
EXTRA_TARGETS="$EXTRA_TARGETS,arm-tizen-linux-gnueabi"
%endif
%if "%{TARGET}" == "aarch64"
EXTRA_TARGETS="$EXTRA_TARGETS,aarch64-tizen-linux"
%endif
%if "%{TARGET}" == "avr" || "%{TARGET}" == "spu"
TARGET_OS=%{TARGET}
%else
%if "%{TARGET}" == "arm"
TARGET_OS=%{TARGET}-tizen-linux-gnueabi
%else
TARGET_OS=%{TARGET}-tizen-linux
%endif
%endif
../configure CFLAGS="${RPM_OPT_FLAGS}" \
  --prefix=%{_prefix} \
  --with-bugurl=http://bugs.opensuse.org/ \
  --with-pkgversion="GNU Binutils; %{DIST}" \
  --disable-nls \
  --build=%{HOST} --target=$TARGET_OS \
%if "%{TARGET}" == "spu"
  --with-sysroot=/usr/spu \
%else
  --with-sysroot=%{_prefix}/$TARGET_OS/sys-root \
%endif
  ${EXTRA_TARGETS:+--enable-targets="${EXTRA_TARGETS#,}"}
make %{?_smp_mflags} all-bfd TARGET-bfd=headers
# force reconfiguring
rm bfd/Makefile
make %{?_smp_mflags}
%if "%{TARGET}" == "avr"
# build an extra nesC version because nesC requires $'s in identifiers
cp -a gas gas-nesc
echo '#include "tc-%{TARGET}-nesc.h"' > gas-nesc/targ-cpu.h
make -C gas-nesc clean
make -C gas-nesc %{?_smp_mflags}
%endif
%endif

%check
unset LD_AS_NEEDED
cd build-dir
%if 0%{?cross:1}
make -k check CFLAGS="-O2 -g" CXXFLAGS="-O2 -g" || %{make_check_handling}
%else
make -k check CFLAGS="$RPM_OPT_FLAGS -Wno-unused -Wno-unprototyped-calls" || :
%endif

%install
cd build-dir
%if 0%{!?cross:1}
# installing native binutils
%ifarch %gold_archs
make DESTDIR=$RPM_BUILD_ROOT install-gold
ln -sf ld.gold $RPM_BUILD_ROOT%{_bindir}/gold
%endif
make DESTDIR=$RPM_BUILD_ROOT install-info install
make -C gas/doc DESTDIR=$RPM_BUILD_ROOT install-info-am install-am
make DESTDIR=$RPM_BUILD_ROOT install-bfd install-opcodes

if [ ! -f "%buildroot/%_bindir/ld.bfd" ]; then
  mv "%buildroot/%_bindir"/{ld,ld.bfd};
else
  rm -f "%buildroot/%_bindir/ld";
fi
mkdir -p "%buildroot/%_sysconfdir/alternatives";
ln -s "%_bindir/ld" "%buildroot/%_sysconfdir/alternatives/ld";
ln -s "%_sysconfdir/alternatives/ld" "%buildroot/%_bindir/ld";
rm -rf $RPM_BUILD_ROOT%{_prefix}/%{HOST}/bin
mkdir -p $RPM_BUILD_ROOT%{_prefix}/%{HOST}/bin
ln -sf ../../bin/{ar,as,ld,nm,ranlib,strip} $RPM_BUILD_ROOT%{_prefix}/%{HOST}/bin

mv $RPM_BUILD_ROOT%{_prefix}/%{HOST}/lib/ldscripts $RPM_BUILD_ROOT%{_libdir}
ln -sf ../../%{_lib}/ldscripts $RPM_BUILD_ROOT%{_prefix}/%{HOST}/lib/ldscripts

# Install header files
make -C libiberty install_to_libdir target_header_dir=/usr/include DESTDIR=$RPM_BUILD_ROOT
# We want the PIC libiberty.a
install -m 644 libiberty/pic/libiberty.a $RPM_BUILD_ROOT%{_libdir}
#
chmod a+x $RPM_BUILD_ROOT%{_libdir}/libbfd-*
chmod a+x $RPM_BUILD_ROOT%{_libdir}/libopcodes-*
# No shared linking outside binutils
rm $RPM_BUILD_ROOT%{_libdir}/lib{bfd,opcodes}.so
rm $RPM_BUILD_ROOT%{_libdir}/lib{bfd,opcodes}.la
# Remove unwanted files to shut up rpm
rm $RPM_BUILD_ROOT%{_infodir}/configure* $RPM_BUILD_ROOT%{_infodir}/standards.info*
rm $RPM_BUILD_ROOT%{_mandir}/man1/dlltool.1 $RPM_BUILD_ROOT%{_mandir}/man1/windres.1 $RPM_BUILD_ROOT%{_mandir}/man1/windmc.1
cd ..
#%find_lang binutils
#%find_lang bfd binutils.lang
#%find_lang gas binutils.lang
#%find_lang ld binutils.lang
#%find_lang opcodes binutils.lang
#%find_lang gprof binutils.lang
%ifarch %gold_archs
#%find_lang gold binutils-gold.lang
%endif
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}
install -m 644 binutils/NEWS $RPM_BUILD_ROOT%{_docdir}/%{name}/NEWS-binutils
install -m 644 gas/NEWS $RPM_BUILD_ROOT%{_docdir}/%{name}/NEWS-gas
install -m 644 ld/NEWS $RPM_BUILD_ROOT%{_docdir}/%{name}/NEWS-ld
%else
# installing cross-TARGET-binutils and TARGET-binutils
make DESTDIR=$RPM_BUILD_ROOT install
# Replace hard links by symlinks, so that rpmlint doesn't complain
T=$(basename %buildroot/usr/%{TARGET}*)
for f in %buildroot/usr/$T/bin/* ; do
   ln -sf /usr/bin/$T-$(basename $f) $f
done
%if "%{TARGET}" == "avr"
install -c gas-nesc/as-new $RPM_BUILD_ROOT%{_prefix}/bin/%{TARGET}-nesc-as
ln -sf ../../bin/%{TARGET}-nesc-as $RPM_BUILD_ROOT%{_prefix}/%{TARGET}/bin/nesc-as
%endif
rm -rf $RPM_BUILD_ROOT%{_mandir}
rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -rf $RPM_BUILD_ROOT%{_prefix}/lib*
rm -rf $RPM_BUILD_ROOT%{_prefix}/include
rm -f $RPM_BUILD_ROOT%{_prefix}/bin/*-c++filt
> ../binutils.lang
%endif
cd $RPM_BUILD_DIR/binutils-%version


%if 0%{!?cross:1}
%docs_package
%post
"%_sbindir/update-alternatives" --install \
    "%_bindir/ld" ld "%_bindir/ld.bfd" 1

%post gold
"%_sbindir/update-alternatives" --install \
    "%_bindir/ld" ld "%_bindir/ld.gold" 2


%preun
if [ "$1" = 0 ]; then
    "%_sbindir/update-alternatives" --remove ld "%_bindir/ld.bfd";
fi;

%preun gold
if [ "$1" = 0 ]; then
    "%_sbindir/update-alternatives" --remove ld "%_bindir/ld.gold";
fi;

%endif

%files 
%defattr(-,root,root)
%if 0%{!?cross:1}
%{_docdir}/%{name}
%{_prefix}/%{HOST}/bin/*
%{_prefix}/%{HOST}/lib/ldscripts
%ghost %_sysconfdir/alternatives/ld
%{_libdir}/ldscripts
%{_bindir}/*
%ifarch %gold_archs
%exclude %{_bindir}/gold
%exclude %{_bindir}/ld.gold
%endif
%doc %{_infodir}/*.gz
%{_libdir}/lib*-%{version}*.so
%else
%{_prefix}/%{TARGET}*
%{_prefix}/bin/*
%endif

%ifarch %gold_archs
%files gold 
%defattr(-,root,root)
%{_bindir}/gold
%{_bindir}/ld.gold
%endif

%if 0%{!?cross:1}
%files devel
%defattr(-,root,root)
%{_prefix}/include/*.h
%{_libdir}/lib*.*a
%endif

%changelog

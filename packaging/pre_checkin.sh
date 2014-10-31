#!/bin/bash

# the script takes binutils* and creates the cross-* packages
# sh4 is stuck in the testsuite
for arch in arm aarch64 i386 x86_64; do

   echo -n "Building package for $arch --> cross-$arch-binutils ..."

   #ln -f binutils.changes cross-$arch-binutils.changes
   targetarch=`echo $arch | sed -e "s/parisc/hppa/;s/i.86/i586/;s/ppc/powerpc/"`
   sed -e "s/^Name:.*binutils\$/Name:\t\tcross-$arch-binutils\nExclusiveArch: %{ix86} x86_64\n%define cross 1\n%define TARGET $targetarch/;" \
       binutils.spec | sed '/manifest/d' |sed '/1001/d' > cross-$arch-binutils.spec
   echo " done."
done


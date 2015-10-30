#!/bin/bash

# the script takes binutils* and creates the cross-* packages
# sh4 is stuck in the testsuite
for arch in armv7l aarch64; do

   echo -n "Building package for $arch --> binutils-$arch ..."

   echo "%define cross $arch" > binutils-${arch}.spec
   echo "%define $arch 1" >> binutils-${arch}.spec
   echo "" >> binutils-${arch}.spec
   cat binutils.spec >> binutils-${arch}.spec
   echo " done."
done


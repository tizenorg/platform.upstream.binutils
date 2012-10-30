.*: Assembler messages:
.*:3: Error: .*
.*:5: Error: .*
GAS LISTING .*


[ 	]*1[ 	]+\.text
[ 	]*2[ 	]+\.globl  bar1
[ 	]*3[ 	]+\.equ    bar1,%eax
[ 	]*4[ 	]+\.equ    bar2,%eax
[ 	]*5[ 	]+\.globl  bar2
[ 	]*6[ 	]+.*[ 	]+mov bar1,%eax
[ 	]*6[ 	]+.*
[ 	]*7[ 	]+.*[ 	]+mov bar2,%eax

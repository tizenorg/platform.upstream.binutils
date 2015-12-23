	.syntax unified
	.text
	.global _start
	.type _start, %function
_start:
	.fnstart
	.save {r4, lr}
	.vsave {d0}
	.vsave {d4}
	bx lr
	.fnend

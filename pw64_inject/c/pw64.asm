.include "functions.asm"
.n64
.open "PW64.z64", "PW64_MOD_C.z64", 0
.align 4

; This section will load code from ROM to RAM and place it @ 0x8037CCC8
.orga 0xCAFD8 ; Offset in ROM, code we want to replace in Intro (func @ 0x80343aa8 == "draw shaded box")
lui a0, 0x8038; Copy to RAM @ 0x8037CCC8 (to be 8-byte aligned), address mostly randomly chosen.
addiu a0, a0, 0xccc8
lui t0, 0x0070 ; ROM address copy from (0x700000)
ori a1, t0, 0x0000
jal 0x8022ed30 ; Call uvDMA() to copy the bytes
li a2,0x1000 ; copy 0x1000 bytes of code (way more than we need for now)
jal runonce ; jump to the code below 
nop

; This section will "inject" our compiled C code in the Padding section of the ROM @ 0x700000
.headersize 0x7FC7CCC8 ; I'm not really sure how I calculated this. checking $a0 a lot.
                       ; ^ this (0x8037CCD4) is where our string lives in RAM after copy.
                       ; 0x8037CCD4 (string in RAM) - 0x70000C (string in ROM) = 0x7FC7CCC8
                       ; But this is fine! Adding code before the Print "moves" the String data address! IHNIWID.

.orga 0x700000 ; Where our code will be stored in ROM (in the padding bytes, lots of room)
runonce:
.importobj "injection_test.o" ; armips just sucks in the binary code, no headers. awesome.
.Close

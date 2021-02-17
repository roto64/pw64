; armips PW64 code injection PoC
;
; Get: https://github.com/Kingcom/armips
; Build: ./armips injection_test.asm
;

; Original ROM file will be untouched, instead you'll get a modified file out.
.Open "PW64.z64", "PW64_MOD_ASM.z64",0
.n64
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

; This section will write our chunk of code in the Padding section of the ROM @ 0x700000
.headersize 0x7FC7CCC8 ; More on this later. I don't remember how I locked in on this.
.orga 0x700000 ; Where our code will be stored in ROM
runonce:
jal 0x8022217c; this is uvGfxEnd(), needed because we're overwriting some code that alread called uvGfxBegin()
nop
lui a0, hi(mystring) ; High-half of 32bit value of addr of our custom string (below).
jal 0x802e81bc ; printFatalMessage() (deduced from diassembly)
addiu a0,a0, lo(mystring) ; Lower-half
mystring: .asciiz "TESTING ASM INJECTION" ; Must be placed here to be addressed properly. 
.Close

; ToDo: fix ROM checksum

.include "functions.asm"
.n64
.open "PW64.z64", "PW64_MOD_C.z64", 0
.align 4

;;; X / Y / Z Coordinates HUD Injection PoC by roto
;
; In this patch we'll be printing the player's world coordinates while in-flight.
; We replace some code in the function used to print "Start!" when the mission begins.
; This section will load our code from ROM to RAM.
;
; We also replace a small chunk of code normally used to check whether or not to
; display the N64 pad (as seen during demo flights) to instead run our code continuously.
;
; *** Notes ***:
; * The memory address I chose _mostly_ works OK...
;       but if you select Ibis and play "Metropolis Dance" (UPWT = A_RP_1) there
;       are some graphical artifacts (in emu and HW). Memory viewer confirms we're
;       overwriting some RAM that is used in that combo of player+mission.
;
; A good to-do would be to rewrite the "Start!" display func in our code as it's now gone.
; Ugh, I'll clean this up and make it clearer later.
;;;

;;; This section will load code from ROM to RAM and store it @ 0x8038CCC8.
;
;;;;;;
; Go to 0xA5190 offset in ROM (program code)
.orga 0xA5190 ; Function that draws "Start!" when mission starts (func @ 0x8031DC60)
.importobj "memload.o"

; Go to the function that draws the on-screen demo controller and fully overwrite it.
; Here we load our "hook" code that will run continuously and decide whether to
; display stuff on screen or not depending on the code above (that loads our ROM code into RAM).
.orga 0xA3404 ; Offset in ROM for start of demoControllerShow() (func @ 0x8031BED4)
.importobj "hook.o"

; This section will "inject" our compiled C code in the Padding section of the ROM @ 0x700000
.headersize 0x7FC8CCC8 ; The "headersize" is calculated as such:
                       ; 0x8038CCC8 (Our code in RAM) - 0x700000 (code in ROM) = 0x7FC8CCC8

.orga 0x700000 ; Where our code will be stored in ROM
runonce:
.importobj "injection_test.o" ; armips just sucks in the binary code, no headers. awesome.
.Close

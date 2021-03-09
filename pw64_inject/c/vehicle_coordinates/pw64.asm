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
; A good to-do would be to rewrite the "Start!" display func in our code as it's now gone.
; Also demo flights are now broken because of this! (lulz, will fix later?).
; Ok a LOT of stuff is broken because of this patch as the game keeps clearing 0x8038CCC8. Oh well, PoC.
; Should probably find another location to store this? Or find another function for injection.
; Ugh, I'll clean this up and make it clearer later.
;;;

;;; This section will load code from ROM to RAM and store it @ 0x8038CCC8.
;
; Go to 0xA5190 offset in ROM (program code)
.orga 0xA5190 ; Function that draws "Start!" when mission starts (func @ 0x8031DC60)
lui a0, 0x8039; Copy to RAM @ 0x8038CCC8 (to be 8-byte aligned), address was chosen mostly arbitrarily..
              ; Note: Had to bump this up another 0x10000 because of collision with game data in RAM.
              ; Previously was @ 0x8037CCC8
addiu a0, a0, 0xccc8
lui t0, 0x0070 ; ROM address copy from (0x700000)
ori a1, t0, 0x0000
jal 0x8022ed30 ; Call uvDMA() to do the copy operation
li a2,0x1000 ; copy 0x1000 bytes of code (way more than we need, for now)
nop ; just in case
jal demoControllerShowToggle ; Uhh... a hack because I couldn't quickly find a better way
                             ; to continuously run the injected printing code.
                             ; Since we replaced the "show demo controller" call
                             ; (and that check is done in an infinite loop...)
                             ; Set this bit to 1 (on) and we'll trigger our function to print stuff.
li a0, 0x1 ; Yes, "show the contoller" as if we're in demo flight mode.

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

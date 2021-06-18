; Map some functions that we are going to use later
.definelabel drawBoxSetup, 0x802DF988
.definelabel drawBox, 0x802DED44
.definelabel PrintFatalError, 0x802E81BC ; This prints "FILE 1 WRITE FAILED" in case of EEPROM failure.
.definelabel uvDMA, 0x8022ED30 ; Obvious.
.definelabel uvGfxEnd, 0x8022217C ; Opposite of uvGfxBegin(). Obvious.....yeah.
.definelabel uvGfxStatePop, 0x8022394C
.definelabel uvGfxStatePush, 0x802238EC
.definelabel uvFontSet, 0x802194D8
.definelabel uvFontSetScale, 0x80219550
.definelabel uvFontSetColor, 0x8021956C
.definelabel printOnscreenText, 0x80219ACC
.definelabel textBringToFront, 0x80219EA8
.definelabel _sprintf, 0x8022DA9C
.definelabel _debug_printf, 0x8022ED14
.definelabel uvMemAlloc, 0x8022AC48
.definelabel demoControllerShowToggle, 0x8031EABC
;
; Some RAM addresses with data we'll be working with/on
;
.definelabel vehicleX, 0x80362788
.definelabel vehicleY, 0x80362790
.definelabel vehicleZ, 0x8036278C
.definelabel ourcode, 0x8038CCC8

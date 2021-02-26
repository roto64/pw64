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

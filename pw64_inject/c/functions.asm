; Map some functions that we are going to use later
.definelabel PrintFatalError, 0x802E81BC ; This prints "FILE 1 WRITE FAILED" in case of EEPROM failure.
.definelabel uvDMA, 0x8022ED30 ; Obvious.
.definelabel uvGfxEnd, 0x8022217C ; Opposite of uvGfxBegin(). Obvious.....yeah.

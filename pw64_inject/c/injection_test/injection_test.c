#include "pw64.h"

// Fills the screen with black and prints your text in yellow.
// Normally a "fatal error" screen in case of EEPROM failure.
void test_inject(void)
{
	uvGfxEnd();				// Needed to appease the GFX gods.
	PrintFatalError("TESTING C INJECTION");	// requires ".headersize" directive in ASM to work...
						// Can also call in-ROM static strings such as @ 0x80352014
}

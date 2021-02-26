#include "pw64.h"

void test_inject(void)
{
	// Lets try to continue the code we overwrote...
	drawBoxSetup();
	drawBox(0x1e, 0x12, 0x11d, 0x22, 0, 0, 0, 0x50);
	drawBox(0x61, 0x4c, 0xca, 0x76, 0, 0, 0, 0x50);

	// Now our code to draw some text on the title screen...
	uvFontSet(0);
	//uvFontSetScale(1, 1); // Don't use this... breaks things...
	uvFontSetColor(255, 0, 0, 255);
	printOnscreenText(90, 215, "25TH ANNIVERSARY EDITION");
	return;
}

#include "pw64.h"

// by roto
void hud_inject(void)
{
	// Use a thin font with black as the text color.
	uvFontSet(6);
	uvFontSetColor(0, 0, 0, 255);

	// Where we'll hold our formatted string coordinates.
	char final_string_x[10];
	char final_string_y[10];
	char final_string_z[10];

	// Take the float @ vehicleX/Y/Z (addr in RAM), prepend some stuff (format it)
	// Store the final string in our buffer var. Then print that string to screen.
	_sprintf(final_string_x, "X: %4.2f", vehicleX);
	printOnscreenText(25, 80, final_string_x);

        _sprintf(final_string_y, "Y: %4.2f", vehicleY);
        printOnscreenText(25, 100, final_string_y);

        _sprintf(final_string_z, "Z: %4.2f", vehicleZ);
        printOnscreenText(25, 120, final_string_z);
	return;
}

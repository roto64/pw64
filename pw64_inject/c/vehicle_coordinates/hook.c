#include "pw64.h"

// by roto
void hook(void)
{
	// The demoControllerShow() function is referenced in a lot of contexts...
	// but we load our code into 0x8038CCC8 only ONCE (during flight start)...
	// Make a "no-op" of this whole thing if 0x8038CCC8 is "empty" (our code wasn't loaded).
	// This way Demo flights and other parts of the game don't crash! This our "hook".
	if (ourcode == 0) {
                return;
        } else {
                hud_inject();
                return;
        }

        return;
}

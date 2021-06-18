#include "pw64.h"

/* The call to uvDMA() creates some kind of infinite 'jr ra' loop
 * that we can never get out of, so make this function one that
 * doesn't return.
*/
void memload () __attribute__ ((noreturn));

void memload(void)
{
	/////////////////
	// This was supposed to be a rewrite to use uvMemAlloc to "allocate" some memory to store our code.
	// After we got the chunk of memory (500 bytes, 8-byte aligned) we were supposed to "jump"
	// to this code via our hook....
	// But I can't figure out how to pass the hook address that we got allocated to us. So...
	// Now we just use uvDMA to load memory and jumo to our static address :(
	// WIP... maybe.
	//
	//
        // BROKEN: Somehow need to tell 'ourcode' (in functions.asm) this new address we get from uvMemAlloc
	//int hook_addr = uvMemAlloc(0x500, 8); // hook_addr is almost always 0x8015D3E8 ? (for E_RP_1)
	//uvDMA(hook_addr, 0x700000, 0x500);
	////////////////

	// DMA copy 0x500 bytes from ROM address 0x700000 to RAM @ 0x8038CCC8
	uvDMA(0x8038CCC8, 0x700000, 0x500);

	// Toggle Demo Controller display which now holds our "hook" check which
	// either jumps to our code or does nothing if the code is not in memory (0x0's @ 0x8038CCC8)
	demoControllerShowToggle(1); // func @ 0x8031EABC

	/* This next op is required because using 'noreturn' messes with the Stack Pointer (?).
	 * Since we have no more 'jr ra', the 2nd instruction the function's ASM is
	 * now "addiu $sp, $sp, -0x18" which, if not remediated with this next call,
	 * will mess up our SP and eventually RA will become 0x00000000 -> crash.
	 * I don't really know enough MIPS ASM to fully explain this. But this works. */
	asm volatile ("addiu $sp, $sp, 0x18");
	asm volatile ("nop");
	// I should probably NOP out the rest of the code past here (where we injected this code),
	// but it doesn't seem to be a problem...

	/////////////////////////////////////////////////////////////////////////////////////////
	/* *** OLD CODE ***
	 * This whole function (now shown above in C-ish) used to be in 'pw64.asm' as such:
	 * ;;;;;;
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
	;;;;;; */
}

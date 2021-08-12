#!/usr/bin/env python

# Stupid little script to find all matches of a byte pattern in a file and modify if necessary.
# This whole thing could probably be done with a good hex editor.
# Was used in the UPWT Mod PoC script to find hits of hardcoded addresses/offsets.

import binascii
import os
import sys

target_offsets = []

# FS Size Modifiers (printf and other calls)
# Old = 0x00618b70
# New = 0x00618be0
#target_old = b'\x8B\x70' #32
#target_new = b'\x8B\x71'   #49
#target_new = b'\x8B\xE0'
# Confirmed offsets need changing:
# 0x49ba
# 0x4a06
# 0x4a1e 
# 0x2f1ae
#############################################

# Audio System init offsets
# Old = 0x0062d460
# New = 0x0062d4d0
# Confirmed offset need changing:
# 0x5512
target_old = b'\xD4\x60' # 33
#target_new = b'\xD4\x61' # 36, for incremental
target_new = b'\xD4\xD0'
#############################################


# Something else after Start menu <-- don't worry about this, its an offset (0x618B70 + 0xF28) ^-- see above FS section
# Old = 0x00619A98
# New = 0x00619B08
#target_old = b'\x9A\x98' # 132
#target_new = b'\x9B\x08' #
#target_new = b'\x9A\x99' # 526, for incremental
#############################################

# Hitting start on intro <-- not needed either? since if we only do FS+Audio patches it "mostly" works (other than Audio)?
# Old = 0x0060B8E6
# New = 0x0060B956
#target_old = b'\xB8\xE6' # 25
#target_new = b'\xB8\xE7' # 35, for incremetnal
#target_new = b'\xB9\x56'
#############################################


# Audio data (.CTL / .TBL) TESTING
# Old = 0x004bbf84
# New = 0x004bbff4
#target_old = b'\xBF\x84'
#target_new = b'\xBF\xF4'

# UPWT E_GC_1 Append testing
#target_old = b'\xDE\xDC'
#target_new = b'\xDE\xDD'

### DMA audio stream addresses
#target_old = b'\x03\x2C\xC4'
#target_new = b'\x03\x2C\xC5'

# Number of bytes to move over (depends on size of bytes to seek)
num_byte = 2

PW64_ROM = "PW64_MOD_EDITOR.z64"

with open (PW64_ROM, "r+b") as pw64_rom:
	data = pw64_rom.read()

	location = 0
	counter = 0
	while True:
		finder = data.find(target_old, location)
		if finder == -1:
                        break
		else:
			#print("match: %s" % (hex(finder)))
			target_offsets.append(hex(finder))
			counter += 1
		location = finder + num_byte
pw64_rom.close()

with open (PW64_ROM, "r+b") as pw64_rom:
	for item in range(0,len(target_offsets)):
        #if item >= 28 and item <= 31: # Here we can modify only select matches
			pw64_rom.seek(int(target_offsets[item], 16), 0)
		
			# If one of these is uncommented every match will be modified
			#pw64_rom.write(binascii.unhexlify(hex(int(binascii.hexlify(target_new), 16)).lstrip("0x")))
        	#pw64_rom.write(binascii.unhexlify(hex(int(binascii.hexlify(target_new), 16)+item).lstrip("0x"))) # This is the incremental change
        	pw64_rom.seek(int(target_offsets[item], 16), 0)
			new_read = pw64_rom.read(4)
        	if int(target_offsets[item], 16) > 0xDF5B0 and int(target_offsets[item], 16) < 0x618BE0:
        	    infs = True # In Filesystem (not code or Audio area)
        	else:
        	    infs = False
        	print("Modified: %s (%s) | %s -> %s | %s" % (target_offsets[item], item, binascii.hexlify(target_old), binascii.hexlify(new_read), infs))
pw64_rom.close()	
print("Total Matches: %s" % counter)

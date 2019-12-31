#!/usr/bin/env python3

# Pilotwings 64 Mission Editor: Millenial Edition
#    by roto
# 
# Q: What is it?
# A: A PoC script that injects an objective from the Beginner class Rocket Pack level (a poppable Balloon on top of the castle in E_RP_1)
#    into the Beginner Class GyroCopter level (E_GC_1). There's only supposed to be 3 rings in this mission.
#    You never see objectives being mixed in missions (e.g. rings+balloons) so this proves its possible to create "custom" tasks.
#
# Q: Why?
# A: To see if Missions (Tasks/Tests) can be modified and to also check if we can combine objectives (rings/balloons/targets/etc).
#    To see if this type of hardpatching will work on hardware (it does).
#    To get a jump start on other reversing work. Still lots to do but this is my main interest at this point.
#
# Q: How?
# A: All the testing/work was done in PJ64 with the debugger (duh),  DMA logs, Symbols and Scripts (thanks again queueRAM for the debug printf script and r2 syms)

# Requirements:
# Needs 'mio0' and 'n64cksum' binaries in same dir as the script. Built from https://github.com/queueRAM/sm64tools
# make mio0
#   gcc -Wall -Wextra -Wno-format-overflow -O2 -ffunction-sections -fdata-sections -I./ext  -MMD -DMIO0_STANDALONE -s -Wl,--gc-sections -o mio0 libmio0.c
# make n64cksum
#   gcc -s -Wl,--gc-sections -o n64cksum obj/n64cksum.o libsm64.a

# ToDo:
# * args (./pw64meme.py E_GC_1 0x666)
#   - More args.
#   - User proper argparse (or some other arg parsing module) instead of this quick jank.
# * ADAT encoder
# * Extract files (UVMD/UVBT/etc)?
# * Make sure we don't re-modify already modified data...
#   - Right now this keeps increasing specified code offsets without error checking and inserts junk data if the ROM is already modified/resized/injected/etc.
# * Lessen the amount of open()'s on the ROM.
# * Combine with pw64_upwt_parser.py (or make that into a library).

# Notes to self:
# The USA PW64 ROM (that I totally dumped myself!) has 0x103420 (1,061,920 / ~1MB) bytes of padding (0xFF) at the end of the ROM.
# The full ROM file size is 8,388,608 bytes
# Most of this was written while repeatedly listening to "Jel - Late Pass"

import binascii
import itertools
import os
import struct
from subprocess import call
import sys

import pw64_lib

# Fill me in
PW64_ROM = ""

def main():
    pw64_lib.build_fs_table(PW64_ROM)

    # Print full FS Table
    if len(sys.argv) == 2 and sys.argv[1] == "-l":
        pw64_lib.show_fs_table()
        sys.exit(0)
    # We probably want some other file.
    elif len(sys.argv) == 3 and sys.argv[1] == "-l":
        pw64_lib.show_fs_table(sys.argv[2])
        sys.exit(0)

    # If we continue here then do all the things. 
    pw64_lib.update_task_size_in_tabl("E_GC_1", 0x728) # Update specified Task ID with new size in TABL. 0x728 is entire FORM chunk (with marker and size)
    rebuild_TABL() # Does what it says.
    inject_TABL() # Inject our updated and compressed TABL back into the ROM.

    modify_e_gc_1() # In this early script we hardcode a lot of things (specifically in this function) and we only modify the first Gyro mission.
    pw64_lib.fix_rom_checksum(PW64_ROM) # Does what it says on the label.

    pw64_lib.show_fs_table("UPWT") # Show the listing of UPWT's at the end for whatever reason

def modify_e_gc_1():
    # Dedicated function for editing E_GC_1 to add a Balloon to the task.
    # These operations will be automated and not centered on this one task, in the future, obviously.
    fs_size_increase = 0x70 # BALS is 0x68 for data + 0x8 for header (marker+size)

    # FS Size / Audio System code manipulation addresses.
    # Hard-patches are needed in the program code to account for the +0x70 bytes we inserted in the FS
    fs_size_mod_locs = [0x49ba, # 0x80203A08: ADDIU A1, A1, 0x8B70  -  FS end/size (0x00618b70)
                        0x4a06, # 0x80203A54: ADDIU A1, A1, 0x8B70  -  FS end
                        0x4a1e, # 0x80203A6C: ADDIU A1, A1, 0x8B70  -  FS end
                        0x2f1ae,# 0x8022E1FC: ADDIU A3, A3, 0x8B70  -  FS end  - Debug stuff  -  0x802C1C34 = Debug Print data of FS size
                        0x5512, # 0x80204560: ADDIU S3, S3, 0xD460  -  Audio system data offsets - Put Debug Exec BP here for Audio Sys calcs.
                        0x551a, # 0x80204568: ADDIU T7, T7, 0x14D0  -  The calculated "read size of B1 (Audio Bank?)". 4000 -> 4070
                        0x5556] # 0x802045A4: ADDIU A1, A1, 0x14D0  -  Related to above "length calculation". Found by pure dumb luck
    # ToDo: Add some error checking for pre/post-mod, maybe "expected post-patch bytes" (?) along with the above addresses.

    level_form_size = 0x0720 # E_GC_1 was previously 0x6b0 (0x6b8 - 0x8). 0x720 is the length of data of the FORM chunk (minus FORM marker and size / 0x8)
    level_form_size_offset = 0x34d492 # Location in ROM where we need to modify the above.
    level_bals_counter_offset =  0x34d936 # Offset where we modify the Number of Balloons
    level_bals_counter = 1
    level_bals_data = b'' # Populated below. For this PoC I'm just copying the BALS chunk from E_RP_1.
    level_bals_data_offset = 0x34db44 # At first I was using 0x34db14 (offset pre-LSTP) but it seems appending to the end of the chunk is fine too?

    # Read the BALS chunk from the beginner Rocket Pack stage (E_RP_1) @ 0x3538DC
    with open(PW64_ROM, 'rb') as pw64_rom:
        pw64_rom.seek(0x3538DC, 0) # Bad hardcoding. 
        level_bals_data = pw64_rom.read(0x70) # 0x70 bytes == full BALS chunk with marker and chunk size
    pw64_rom.close()

    # Yeah I need to stop opening/closing files so frequently.
    with open(PW64_ROM, 'r+b') as pw64_rom:
        # Loop through and hard patch our game code at various offsets.
        # These need to be modified for the game to know we've added 0x70 of data and moved FS/Audio offsets by +0x70
        # I learned the hard way there are explicit expectations about locations of various data at specific ROM addresses that are calculated in code.
        for addr in fs_size_mod_locs:
            pw64_rom.seek(addr, 0)
            data = int(binascii.hexlify(pw64_rom.read(2)), 16) + fs_size_increase # Read the bytes and convert to int + increase size
            pw64_rom.seek(addr, 0)
            #pw64_rom.write(binascii.unhexlify(hex(data).lstrip('0x'))) # stupid bytes() function doesn't do what I expected.
            pw64_rom.write(binascii.unhexlify(b'%x' % (data))) # This is still silly but better than ^
 
        # Modify E_GC_1's FORM size (does not include marker + size)
        pw64_rom.seek(level_form_size_offset)
        pw64_rom.write(level_form_size.to_bytes(2, 'big'))

        # Add 1 ball by overwriting the byte in COMM that defines # of BALS in this mission (task)
        pw64_rom.seek(level_bals_counter_offset)
        pw64_rom.write(level_bals_counter.to_bytes(1, 'big'))
    pw64_rom.close()

    # Insert our BALS chunk.
    # We open the ROM in read-only mode, read in the original data from the ROM up to where we want to insert our new data.
    # Open a temp file and then insert the BALS bytes we read in before.
    # Then read in and write the rest of the ROM to the 2nd temp file.
    # When doen writing out this newly munged crap into a temp file, remove the original and rename our temp file back to the OG ROM name.
    # There's probably a better way to do this.
    with open(PW64_ROM, 'rb') as pw64_rom_first, open("PW64_ROM_TMP.z64", 'wb') as pw64_rom_second:
        pw64_rom_second.write(pw64_rom_first.read(level_bals_data_offset)) # Read all teh bytes up to where we need to insert our data
        pw64_rom_second.write(level_bals_data) # Add our BALS data
        pw64_rom_second.write(pw64_rom_first.read()) # Read in the rest of the data from original ROM and write to temp file
        
        # Truncate 0x70 bytes of padding at end of ROM
        pw64_rom_second.flush()
        pw64_rom_second.seek(-fs_size_increase, os.SEEK_END)
        pw64_rom_second.truncate()
    pw64_rom_second.close()
    pw64_rom_first.close()

    # Switch our files ... ooh scary.
    os.remove(PW64_ROM)
    os.rename('PW64_ROM_TMP.z64', PW64_ROM)

    # Yay one more file open/write operation!
    # Let's modify the Mission Objective text!
    with open(PW64_ROM, 'r+b') as pw64_rom:
        pw64_rom.seek(0x36A61C, 0) # Eww another hardcoded address
        data = pw64_lib.encode_adat("Fly through 3 rings and...\nooh look a balloon!", 0x70)
        pw64_rom.write(data)
    pw64_rom.close()

def rebuild_TABL():
# Once we've read in our mods and modified the TABL data,
# rebuild and write out the entire TABL back to binary format for later MIO0 compression
# Note: 'filesys' size Debug output is at 0x802C1C34
#       0x802B6CC8 = E_GC_1's size as read from TABL
    with open("TABL_NEW.bin", 'wb') as TABL_OUT:
        for f in range(len(pw64_lib.fs_table)):
            file_type = pw64_lib.fs_table[f][pw64_lib.FS_FILE_TYPE].encode()
            file_size = binascii.unhexlify(hex(pw64_lib.fs_table[f][pw64_lib.FS_FILE_SIZE]).lstrip("0x").zfill(8).encode()) # HAHA WAT

            TABL_OUT.write(file_type)
            TABL_OUT.write(file_size)
    TABL_OUT.close()

    # Use the external 'mio0' tool to re-compress this data.
    # If I had a Python sample of MIO0 compression code this would not be needed...
    call(['./mio0', 'TABL_NEW.bin', 'TABL_NEW.mio0'])


def inject_TABL():
    # Take our newly built and compressed TABL and shove it into the PW64 ROM

    # Make sure the MIO0 is padded. For some reason the `mio0` tool doesn't re-compress to original size?
    # To be more clear the MIO0 data in the PW64 ROM is 3676 bytes but after all the 
    # other work is done it compresses back to only 3409 bytes.
    mio0_file_size = os.path.getsize('TABL_NEW.mio0')
    if mio0_file_size < 3676:
        bytes_to_pad = 3676 - mio0_file_size
        with open ("TABL_NEW.mio0", 'ab') as m: # Open the ROM in append mode.
            m.write(binascii.unhexlify('00')*bytes_to_pad) # Seems to work fine? :shrug:
        m.close()

    # We will add/remove these padding bytes as needed here when we start to inject bigger UPWTasks.
    #rom_file_size = os.path.getsize(PW64_ROM)

    # Write our newly compressed MIO0 TABL data back into the ROM.
    with open (PW64_ROM, 'r+b') as pw64_rom: #F'ing was using the wrong mode (wb) and it was zeroing all data
        pw64_rom.seek(int(0xDE754), 0)
        with open ("TABL_NEW.mio0", 'rb') as mio0:
            pw64_rom.write(mio0.read()) # File read/write inception.
        mio0.close()
    pw64_rom.close()

if __name__== "__main__":
  main()

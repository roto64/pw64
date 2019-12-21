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
# * unpack_full_tabl() and build_file_map() can probably be combined. Feels redundant.
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
import sys
from subprocess import call

# Fill me in
PW64_ROM = "PW64_MOD_EDITOR.z64"

pw64_fs_start = 0xDF5B0 # Offset of first file in "File System" (UVSY)
pw64_tabl_mio0_data_start = 0xDE758 # Never changes
pw64_tabl_uncompressed_size = 0 # Filled in later

# This list will hold some data about specific files of interest(right now UPWT)
upwt_map = [] # [FS ID (index in list), offset/location in ROM, task ID (for UPWT).] A dictionary won't work because of dupe keys for Task IDs.
upwt_fs_id = 0
upwt_offset = 1
upwt_task_id = 2

# This dictionary will hold our parsed list of files and their attributes: file type, offset in ROM, file size
fs_layout = {}
# Shortcuts for the above dict
fs_file_type = 0
fs_file_offset = 1
fs_file_size = 2

def main():
    unpack_full_tabl()

    # Only print TABL contents
    if len(sys.argv) > 1 and sys.argv[1] == "-t":
        show_unpacked_tabl()
        sys.exit(0)
    # Only print UPWT file info
    if len(sys.argv) == 2 and sys.argv[1] == "-l":
        build_file_map()
        show_file_map()
        sys.exit(0)
    # We probably want some other file, but default back to UPWT.
    elif len(sys.argv) == 3 and sys.argv[1] == "-l":
        build_file_map(sys.argv[2].upper())
        show_file_map(sys.argv[2].upper())
        sys.exit(0)

    # If we continue here then do all the things. 
    build_file_map("UPWT") # Build a list of all the UPWT files in the ROM FS.
    update_task_size_in_tabl("E_GC_1", 0x728) # Update specified Task ID with new size in TABL. 0x728 is entire FORM chunk (with marker and size)
    rebuild_TABL() # Does what it says.
    inject_TABL() # Inject our updated and compressed TABL back into the ROM.

    modify_e_gc_1() # In this early script we hardcode a lot of things (specifically in this function) and we only modify the first Gyro mission.
    fix_rom_checksum() # Does what it says on the label.

    show_file_map() # Show the map at the end for whatever reason

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
        data = encode_adat("Fly through 3 rings and...\nooh look a balloon!", 0x70)
        pw64_rom.write(data)
    pw64_rom.close()

def encode_adat(message, expected_string_length):
    # 'FE': Newline
    # 'FD': Tab?
    # 'FF': EOF/EOS
    char_map_combined = { # // Normal Font //
						'00': '0', '01': '1', '02': '2', '03': '3', '04': '4',
						'05': '5', '06': '6', '07': '7', '08': '8', '09': '9',
						'0A': 'A', '0B': 'B', '0C': 'C', '0D': 'D', '0E': 'E',
						'0F': 'F', '10': 'G', '11': 'H', '12': 'I', '13': 'J',
						'14': 'K', '15': 'L', '16': 'M', '17': 'N', '18': 'O',
						'19': 'P', '1A': 'Q', '1B': 'R', '1C': 'S', '1D': 'T',
						'1E': 'U', '1F': 'V', '20': 'W', '21': 'X', '22': 'Y',
						'23': 'Z', '24': 'a', '25': 'b', '26': 'c', '27': 'd',
						'28': 'e', '29': 'f', '2A': 'g', '2B': 'h', '2C': 'i',
						'2D': 'j', '2E': 'k', '2F': 'l', '30': 'm', '31': 'n',
						'32': 'o', '33': 'p', '34': 'q', '35': 'r', '36': 's',
						'37': 't', '38': 'u', '39': 'v', '3A': 'w', '3B': 'x',
						'3C': 'y', '3D': 'z', '3E': '-', '3F': '#', '40': '<',
						'41': '>', '42': ' ', '43': '\"', '44': '(', '45': ')',
						'46': '*', '47': '&', '48': ',', '49': '.', '4A': '/',
						'4B': '!', '4C': '?', '4D': '\'', '4E': '#', '4F': ':',
						'50': '0', '51': '1', '52': '2', '53': '3', '54': '4',
						'55': '5', '56': '6', '57': '7', '58': '8', '59': '9',
						'5A': '\\', '5B': '\\', '5C': '\\', '5D': '\\',
						'5E': '\\', '5F': '\\',
						# // Bold Font //
						# This obviously doesn't show up in this code.
						# But it is bold in the game. Trust me.
						'60': '0', '61': '1', '62': '2', '63': '3', '64': '4',
						'65': '5', '66': '6', '67': '7', '68': '8', '69': '9',
						'6A': 'A', '6B': 'B', '6C': 'C', '6D': 'D', '6E': 'E',
						'6F': 'F', '70': 'G', '71': 'H', '72': 'I', '73': 'J',
						'74': 'K', '75': 'L', '76': 'M', '77': 'N', '78': 'O',
						'79': 'P', '7A': 'Q', '7B': 'R', '7C': 'S', '7D': 'T',
						'7E': 'U', '7F': 'V', '80': 'W', '81': 'X', '82': 'Y',
						'83': 'Z', '84': 'a', '85': 'b', '86': 'c', '87': 'd',
						'88': 'e', '89': 'f', '8A': 'g', '8B': 'h', '8C': 'i',
						'8D': 'j', '8E': 'k', '8F': 'l', '90': 'm', '91': 'n',
						'92': 'o', '93': 'p', '94': 'q', '95': 'r', '96': 's',
						'97': 't', '98': 'u', '99': 'v', '9A': 'w', '9B': 'x',
						'9C': 'y', '9D': 'z', '9E': '-', '9F': '#', 'A0': '<',
						'A1': '>', 'A2': ' ', 'A3': '\"', 'A4': '(', 'A5': ')',
						'A6': '*', 'A7': '&', 'A8': ',', 'A9': '.', 'AA': '/',
						'AB': '!', 'AC': '?', 'AD': '\'', 'AE': '}', 'AF': ':',
						'B0': '0', 'B1': '1', 'B2': '2', 'B3': '3', 'B4': '4',
						'B5': '5', 'B6': '6', 'B7': '7', 'B8': '8', 'B9': '9',
						'BA': '\\', 'BB': '\\', 'BC': '\\', 'BD': '\\',
						'BE': '\\', 'BF': '\\' }

    encoded_string_hex = []

    for c in message:
        encoded_string_hex.append("00")
        if c == '\n':
            encoded_string_hex.append("FE")
        for k, v in char_map_combined.items():
            if v == c:
                encoded_string_hex.append(k)
                break

    # Newline, EOF/EOS and padding, to be automated later
    end1 = ["00", "FE","00","FF","00", "00", "00", "00"]
    for bla in end1:
        encoded_string_hex.append(bla)

    # Early PoC. Until I work out offsets and ADAT format/parsing I'll limit to 0x70 (original message's size).
    if len(encoded_string_hex) < expected_string_length:
        pad = expected_string_length - len(encoded_string_hex)
        for i in range(0, pad):
            encoded_string_hex.append("00")
    elif len(encoded_string_hex) > expected_string_length:
        print("String too long! %s" % hex(len(encoded_string_hex)))
        sys.exit(1)

    return(binascii.unhexlify(''.join(encoded_string_hex)))

def fix_rom_checksum():
    # Fix ROM checksum
    call(['./n64cksum', PW64_ROM])

def build_file_map(pw_file_type="UPWT"):
    # Loop through our FS, find the XXXX files and build a look-up table
    # This function is probably reduntant because of unpack_full_tabl(), it was previously only meant for UPWT.
    # Maybe redo that other function to find UPWT's instead of here.

    # Find our first instance of the file type. Files are grouped together. This is fine. Probably.
    for file_index in fs_layout:
        if fs_layout[file_index][0] == pw_file_type:
            file_first_hit = int(fs_layout[file_index][1], 16)
            break

    # This is an unnecessary ROM read. Only pulls mission ID for UPWT. But for all other files reads junk into "task_ID".
    with open(PW64_ROM, 'rb') as pw64_rom:
        location = file_first_hit
        for fs_index in range(len(fs_layout)):
            file_type = fs_layout[fs_index][fs_file_type]
            if  file_type == pw_file_type: 
                file_size = fs_layout[fs_index][2]

                # This is the only reason we read the ROM yet again...
                if file_type == "UPWT":
                    pw64_rom.seek(location + 0x20, 0) # Skip 0x20 bytes to go straight to the test/task name/ID
                    task_ID = pw64_rom.read(6)
                else:
                    task_ID = "" # We don't _really_ needs this since we never read out the Task ID for non-UPWT.
                
                upwt_map.append([fs_index, hex(location), task_ID])
                location = location + file_size # Very critical this is updated last. 
            
    pw64_rom.close()

def show_file_map(pw_file_type="UPWT"):
    #upwt_task_header = ""
    #if pw_file_type == "UPWT": upwt_task_header = "|\tTask ID\t"
    upwt_task_header = ("|\tTask ID\t" if pw_file_type == "UPWT" else "")

    print("%s FS ID\t|\tOffset in ROM\t%s|\tFS Size" % (pw_file_type, upwt_task_header))
    print("-"*72)

    for task in upwt_map:
        if pw_file_type == "UPWT":
            print("\t%s\t|\t%s\t|\t%s\t|\t%s" % (task[0], task[1], task[2].decode(), hex(fs_layout[task[0]][fs_file_size])))#raw_fs_layout[task[0]][1].zfill(8)))
        else:
            print("\t%s\t|\t%s\t|\t%s" % (task[0], task[1], hex(fs_layout[task[0]][fs_file_size])))

# Write new size for UPWT task to the FS table for later TABL build and compression
def update_task_size_in_tabl(task_id, new_size):
    for task in upwt_map:
        #print(task[2])
        if task[upwt_task_id].decode() == task_id:
            print("Task Name: %s (FS ID: %s) resized to: %s" % (task_id, task[upwt_fs_id], new_size))
            fs_layout[task[upwt_fs_id]][fs_file_size] = new_size
            
# Reads, unpacks TABL (FS layout)
def unpack_full_tabl():
    with open (PW64_ROM, 'rb') as pw64_rom:
        global pw64_tabl_uncompressed_size

        # Get expected MIO0 uncompressed size
        pw64_rom.seek(int(pw64_tabl_mio0_data_start), 0)
        pw64_tabl_uncompressed_size = int(binascii.b2a_hex(pw64_rom.read(4)),16)

        # Go back 8 bytes to start of MIO0 compressed TABL data (skip futzing with FORM/GZIP/TABL/etc "chunks")
        pw64_rom.seek(-8, 1)

        # MIO0 data length == 0xe58 + MIO0 (marker) = 0xe5c
        # Read in the whole block, decompress MIO0 and convert to hex stream
        uncompressed_data = decompress_mio0(pw64_rom.read(int(0xe5c))).hex()

        # Build a list of 16-character "groups" which denote "files" (file type + file size)
        file_count = len(list(grouper(uncompressed_data, 16, '?')))

        fs_index = 0
        location = pw64_fs_start
        for filenum in range(0, file_count):
            # 16-character groups will hold our File Type and File Size to be later translated to Hex.
            data = ''.join(list(grouper(uncompressed_data, 16, '?'))[filenum])

            # Decoded File Type and File Size for printing
            file_type = binascii.unhexlify(data[0:8]).decode()
            file_size = int(data[9:16], 16)

            fs_layout.update( {fs_index: [file_type, hex(location), file_size]})

            fs_index += 1
            location = location + file_size
            
    pw64_rom.close()

def show_unpacked_tabl():
    print("TABL MIO0 Block Uncompressed Size: %s bytes" % pw64_tabl_uncompressed_size)
    print("-"*40)
    print("Number of files in TABL: %s\n" % len(fs_layout))

    total_fs_size = 0
    print("Index\t\tFile\t\tOffset in ROM\t\tLength\t(Hex)")
    print("-"*72)
    for fs_file in fs_layout:
        print("%s\t\t%s\t\t%s\t\t\t%s\t(0x%x)" % (fs_file, fs_layout[fs_file][fs_file_type], fs_layout[fs_file][fs_file_offset], fs_layout[fs_file][fs_file_size], fs_layout[fs_file][fs_file_size]))
        total_fs_size += fs_layout[fs_file][fs_file_size]
    print("Total FS Size: %s" % total_fs_size)

def rebuild_TABL():
# Once we've read in our mods and modified the TABL data,
# rebuild and write out the entire TABL back to binary format for later MIO0 compression
# Note: 'filesys' size Debug output is at 0x802C1C34
#       0x802B6CC8 = E_GC_1's size as read from TABL
    with open("TABL_NEW.bin", 'wb') as TABL_OUT:
        for f in range(len(fs_layout)):
            file_type = fs_layout[f][fs_file_type].encode()
            file_size = binascii.unhexlify(hex(fs_layout[f][fs_file_size]).lstrip("0x").zfill(8).encode()) # HAHA WAT

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
        with open ("TABL_NEW.mio0", 'ab') as m:
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

def grouper(iterable, n, fillvalue=None):
	# For grouping n number of characters together for display
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)

# Copied from, and credit to, queueRAM: https://github.com/queueRAM/pilotwings_64/blob/master/pw64_filesys_dump.py
def decompress_mio0(raw_bytes):
    magic = raw_bytes[:4]
    assert magic == b'MIO0'

    uncompressed_size, lengths_offs, data_offs = struct.unpack('>LLL', raw_bytes[4:16])
    flags_offs = 0x10

    output = b""
    while True:
        command_byte = raw_bytes[flags_offs]
        flags_offs += 1

        for i in reversed(range(8)):
            if command_byte & (1 << i):
                # Literal
                uncompressed_size -= 1
                output += bytes([raw_bytes[data_offs]])
                data_offs += 1
            else:
                # LZSS
                tmp, = struct.unpack('>H', raw_bytes[lengths_offs:lengths_offs+2])
                lengths_offs += 2

                window_offset = (tmp & 0x0FFF) + 1
                window_length = (tmp >> 12) + 3
                uncompressed_size -= window_length
                for j in range(window_length):
                    output += bytes([output[-window_offset]])

            if uncompressed_size <= 0:
                return output

if __name__== "__main__":
  main()

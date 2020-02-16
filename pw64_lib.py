import binascii
import itertools
import os
import struct
from subprocess import call

# Will hold our table of files: File Type, File Offset, and File Size
fs_table = {}
# Shortcuts for the above dict
FS_FILE_TYPE = 0
FS_FILE_OFFSET = 1
FS_FILE_SIZE = 2
FS_FILE_UPWT_TASK_ID = 3

# Will hold all the strings in the game.
adat_layout = {}

pw64_tabl_uncompressed_size = 0
COMM_data_start = 0

# COMM Data and Offsets. There's quite a lot of COMM data that varies between tasks but these are the ones I was able to decipher for now.
COMM_layout = {
    "pilot_class" : 0x0, # Test Class # '00': 'Beginner', '01': 'Class A', '02': 'Class B', '03': 'Pilot Class'
    "vehicle": 0x1, # Vehicle # '00': 'Hang Glider', '01': 'Rocket Pack', '02': 'Gyro Copter', '03': 'Cannon', '06': 'Birdman'
    "test_number": 0x2, # Test Number # 00 = Test 1, 01 = Test 2, etc
    "level": 0x3, # Level # '00': 'Holiday Island', '01': 'Crescent Island', '02': 'Little States', '03': 'Ever-Frost Island'
    "skybox": 0x8, # Weather / Time of Day # '00': 'Sunny', '01': 'Sunny Part 2', '02': 'Cloudy', '03': 'Snowing?', '04': 'Evening', '05': 'Starry Night'
    "snow": 0x9, #  Snow
    "wind_WE": 0x10,
    "wind_SN": 0x14,
    "wind_UD": 0x18,
    "THER": 0x41C, # Hang Glider Thermals
    "LWND": 0x41D, # Local Winds
    "TPAD": 0x41E, # Takeoff Pads/Strips
    "LPAD": 0x41F, # Landing Pads
    "LSTP": 0x420, # Landing Strips
    "RNGS": 0x421, # Rings
    "BALS": 0x422, # Balloons
    "TARG": 0x423, # Rocket Targets
    "HPAD": 0x424, # Floating Pads
    "BTGT": 0x425, # Ball Targets
    "PHTS": 0x426, # Photo Targets
    "FALC": 0x427, # "Falcos Domains"
    "UNKN": 0x428, # Unknown
    "CNTG": 0x429, # Canon Targets
    "HOPD": 0x42A, # Jumble Hopper Goals
}

# RNGS layout past Marker+Size
RNGS_layout = {
    "x": 0x0,
    "z": 0x4,
    "y": 0x8,
    "yaw": 0xc,
    "pitch": 0x10,
    "roll": 0x14,
    "size": 0x54,
    "state": 0x55,
    "motion_axis": 0x60,
    "motion_rad_start": 0x58,
    "motion_rad_end": 0x5c,
    "rotation": 0x70,
    "rotation_speed": 0x64,
    "ring_special": 0x72,
    "next_ring_unknown": 0x1c,
    "next_ring_order_count": 0x1d,
    "next_ring_index": [0x20, 0x24, 0x28, 0x2c]
}

TPAD_layout = {
    "x": 0x0,
    "y": 0x4,
    "z": 0x8,
    "yaw": 0xc,
    "pitch": 0x10,
    "roll": 0x14
}

LSTP_layout = {
    "x": 0x0,
    "y": 0x4,
    "z": 0x8,
    "yaw": 0xc,
    "pitch": 0x10,
    "roll": 0x14
}

BALS_layout = {
    "x": 0x0,
    "z": 0x4,
    "y": 0x8,
    "scale": 0x30,
    "color": 0x20,
    "type": 0x21,
    "solidity": 0x24,
    "weight": 0x28,
    "popforce": 0x2c
}

# The DATA blocks in the ADAT container appear to be "coded" ASCII strings.
# The strings use a sort of look-up table as seen below.
# This was probably done for easier localization (Kanji font textures?)
# The Font Sprite/Texture maps are in the "STRG" container/blocks.
# This table was extrapolated from the FS dump and PJ64 memory searches.
adat_char_map_combined = { # // Normal Font //
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

def dsplit(data, convert=False):
	# Doubleword Split with base 16 conversion if needed
	if convert == True:
		return int(data[0:2],16), int(data[2:4],16), int(data[4:6],16), int(data[6:8],16)
	else:
		return data[0:2], data[2:4], data[4:6], data[6:8]

# Assumes "n64cksum" is in same directory. Bad.
def fix_rom_checksum(rom):
    # Fix ROM checksum
    call(['./n64cksum', rom])

def grouper(iterable, n, fillvalue=None):
	# For grouping n number of characters together for display
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)

def decode_adat(hex_data):
	# This is the same code as what I added to queueRAM's PW64 FS dumper
	#
	hex_split = [(hex_data[i:i+2]) for i in range(0, len(hex_data), 2)]

   # Empty list for storing final string
	adat_final_string = []

	# Read a pair of hex bytes
	for i in range(0, len(hex_split), 2):
		hex_pair = hex_split[i:i+2]

		char_byte1 = hex_pair[0].upper()
		char_byte2 = hex_pair[1].upper()

		if char_byte1 == '00':
		  if char_byte2 == 'CA':
			  # slash? '\' ?
			  pass
		  elif char_byte2 == 'D4':
			  # Unknown char
			  pass
		  elif char_byte2 == 'FE':
			  # Newline
			  adat_final_string.append('\n')
		  elif char_byte2 == 'FD':
			  # Tab?
			  pass
		  elif char_byte2 == 'FF':
			  # EOF/EOS
			  break
		  else:
			  adat_final_string.append(adat_char_map_combined[char_byte2])
		else:
		  # We found some weird control char in our pair?
		  adat_final_string.append('?0')

	return adat_final_string

# This is a PoC and is not complete. Only works for E_GC_1 and 0x70 bytes in length
def encode_adat(message, expected_string_length):
    # 'FE': Newline
    # 'FD': Tab?
    # 'FF': EOF/EOS
    encoded_string_hex = []

    for c in message:
        encoded_string_hex.append("00")
        if c == '\n':
            encoded_string_hex.append("FE")
        for k, v in adat_char_map_combined.items():
            if v == c:
                encoded_string_hex.append(k)
                break

    # Newline, EOF/EOS and padding, to be automated later
    end1 = ["00", "FE","00","FF","00", "00", "00", "00"]
    for bla in end1:
        encoded_string_hex.append(bla)

    # Early PoC. Until I work out offsets and ADAT format/parsing I'll limit the string DATA chunk to 0x70 bytes (original message's size).
    if len(encoded_string_hex) < expected_string_length:
        pad = expected_string_length - len(encoded_string_hex)
        for i in range(0, pad):
            encoded_string_hex.append("00")
    elif len(encoded_string_hex) > expected_string_length:
        print("String too long! %s" % hex(len(encoded_string_hex)))
        sys.exit(1)

    return(binascii.unhexlify(''.join(encoded_string_hex)))

def build_adat_layout(PW64_Rom):
    # Builds a table of game strings with size and offset in ROM:
    # adat_layout[STRING_ID_ASCII][SIZE, OFFSET]
    # There is no index because the strings seem to be all over the place.
    # Size/Offset are returned as int for easier manipulation upstack (e.g. convert to hex for display or whatever)
    # So the lookup has to be done by a string as such:
    #
    # offset_of_EGC1_message = adat_layout["E_GC_1_M"][1]
    #
    # Again, "_N" is the name of a test/task and "_M" is the mission message/instruction as show in the mission start screen.

    # Find our ADAT chunk in the FS
    for fs_index, fs_attrs in fs_table.items():
        if fs_attrs[FS_FILE_TYPE] == "ADAT":
            adat_offset = fs_attrs[FS_FILE_OFFSET]
            adat_index = fs_index

    #print("ADAT (Index: %s) Addr: %s" % (adat_index, adat_offset))

    with open(PW64_Rom, 'rb') as pw64_rom:
        pw64_rom.seek(int(adat_offset, 16), 0)

        pw64_rom.seek(0x28, 1) # Move 0x28 bytes forward to the first NAME chunk

        while True:
            location = pw64_rom.tell()
            marker = pw64_rom.read(0x4)

            if marker.decode() == "NAME":
                name_marker_size = int.from_bytes(pw64_rom.read(0x4), 'big')
                name_marker_id = pw64_rom.read(name_marker_size)
                name_marker_id = name_marker_id.decode().rstrip('\0')
                #print("%s Marker Size: %s" % (marker.decode(), name_marker_size))
                #print("%s Marker ID: %s" % (marker.decode(), name_marker_id))

            elif marker.decode() == "DATA":
                data_marker_size = int.from_bytes(pw64_rom.read(0x4), 'big')
                data_marker_offset_start = pw64_rom.tell()
                #print("\t%s Marker Offset: %s" % (marker.decode(), data_marker_offset_start))
                #print("\t%s Marker Size: %s" % (marker.decode(), hex(data_marker_size)))

                data_marker_data = pw64_rom.read(data_marker_size)

                adat_layout.update({name_marker_id: [data_marker_size, data_marker_offset_start]})

            # If we start reading past the ADAT file, break out
            if location >= int(fs_table[adat_index+1][FS_FILE_OFFSET], 16):
                break

# Does what it says on the tin
def float_to_hex(float_in):
    return struct.pack('>f', float_in)

# Combined unpack_tabl and build_fs_map
# We can specify a game here because we can now parse AeroFighters Assault! Defaults to PW64.
def build_fs_table(ROM, game="PW64"):
    global fs_table
    global pw64_tabl_uncompressed_size

    fs_table.clear()

    with open (ROM, 'rb') as pw64_rom:
        # AeroFighters Assault is also made by Paradigm Entertainment (previously part of Paradigm Simulation).
        # Has a similar TABL chunk we can process, if so inclined... example:
        #   !/usr/bin/env python3
        #   import pw64_lib
        #   def main():
        #       ROM = "<AFA_ROM>"
        #       pw64_lib.fs_table = pw64_lib.build_fs_table(ROM, "AFA")
        #       pw64_lib.show_fs_table() # or e.g. ("UVMD")
        #   if __name__== "__main__":
        #   main()
        if game == "AFA":
            tabl_form_start = 0x118690
            afa_tabl_mio0_data_start = 0x1186C8 # Never changes
            afa_fs_start = 0x119530 # Offset of first file in "File System" (UVSY)
            pw64_tabl_mio0_data_start = afa_tabl_mio0_data_start
            pw64_fs_start = afa_fs_start
        elif game == "PW64":
            tabl_form_start = 0xDE720
            pw64_tabl_mio0_data_start = 0xDE758 # Never changes
            pw64_fs_start = 0xDF5B0 # Offset of first file in "File System" (UVSY)

        # Get MIO0 Data chunk size
        pw64_rom.seek(tabl_form_start + 0x28, 0) # Move 0x28 forward to skip other markers/etc
        mio0_data_chunk_size = pw64_rom.read(4)

        # Get expected MIO0 uncompressed size
        pw64_rom.seek(tabl_form_start + 0x38, 0) # MIO0 data starts at FORM + 0x38
        pw64_tabl_uncompressed_size = int(binascii.b2a_hex(pw64_rom.read(4)),16)

        # Go back 8 bytes to start of MIO0 compressed TABL data (skip futzing with FORM/GZIP/TABL/etc "chunks")
        pw64_rom.seek(-8, 1)

        # Read in the whole block, decompress MIO0 and convert to hex stream
        uncompressed_data = decompress_mio0(pw64_rom.read(int.from_bytes(mio0_data_chunk_size, 'big'))).hex()

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

            # If we have a UPWT, read it's Task ID
            if file_type == "UPWT":
                pw64_rom.seek(location + 0x20, 0) # Skip 0x20 bytes to go straight to the test/task name/ID
                task_ID = pw64_rom.read(6)
                task_ID = task_ID.decode() # if we error out here, we're reading (choking on) a modified ROM!
            else:
                task_ID = "" # We don't _really_ needs this since we never read out the Task ID for non-UPWT.

            fs_table.update( {fs_index: [file_type, hex(location), file_size, task_ID]})

            fs_index += 1
            location = location + file_size

    pw64_rom.close()
    return fs_table

# Shows either full FS table or only specific files.
# Needs cleaning up for DRY
def show_fs_table(filter_file_type=""):
    upwt_task_header = ("Task ID\t" if filter_file_type == "UPWT" else "")

    print("{: ^10}\t|\t{: ^10}\t|\t{: ^10}\t|\t{: ^10}\t|\t{: ^10}".format("FS ID", "File Type", "Offset in ROM", "File Size", upwt_task_header))
    print("-"*110)

    # We must have been passed a file to filter
    if filter_file_type != "":
        for file_id in fs_table:
            if filter_file_type == fs_table[file_id][FS_FILE_TYPE]:
                # ID, FileType, Offset, Size, UPWT Task ID (if needed)
                if fs_table[file_id][0] == "UPWT":
                    print("{: ^10}\t|\t{: ^10}\t|\t{: ^10}\t|\t{: <10}\t|\t{: ^10}".format(file_id, fs_table[file_id][FS_FILE_TYPE], fs_table[file_id][FS_FILE_OFFSET], hex(fs_table[file_id][FS_FILE_SIZE]), fs_table[file_id][FS_FILE_UPWT_TASK_ID]))
                else:
                    print("{: ^10}\t|\t{: ^10}\t|\t{: ^10}\t|\t{: <10}".format(file_id, fs_table[file_id][FS_FILE_TYPE], fs_table[file_id][FS_FILE_OFFSET], hex(fs_table[file_id][FS_FILE_SIZE])))
    else:
        total_fs_size = 0
        for file_id in fs_table:
                # ID, FileType, Offset, Size, UPWT Task ID (if needed)
                if fs_table[file_id][0] == "UPWT":
                    print("{: ^10}\t|\t{: ^10}\t|\t{: ^10}\t|\t{: <10}\t|\t{: ^10}".format(file_id, fs_table[file_id][FS_FILE_TYPE], fs_table[file_id][FS_FILE_OFFSET], hex(fs_table[file_id][FS_FILE_SIZE]), fs_table[file_id][FS_FILE_UPWT_TASK_ID]))
                else:
                    print("{: ^10}\t|\t{: ^10}\t|\t{: ^10}\t|\t{: <10}".format(file_id, fs_table[file_id][FS_FILE_TYPE], fs_table[file_id][FS_FILE_OFFSET], hex(fs_table[file_id][FS_FILE_SIZE])))
                total_fs_size += fs_table[file_id][FS_FILE_SIZE]
        print("\nTABL MIO0 Block Uncompressed Size: %s bytes" % pw64_tabl_uncompressed_size)
        print("Number of files in TABL: %s" % len(fs_table))
        print("Total FS Size: %s" % total_fs_size)

# Read the COMM chunk (data only, no marker/size header)
def read_comm_from_rom(test_ID, rom_file):
    global COMM_data_start

    # Find our offset in teh FS of the Test ID
    for file_index in fs_table:
        if fs_table[file_index][FS_FILE_TYPE] == "UPWT":
            if fs_table[file_index][FS_FILE_UPWT_TASK_ID] == test_ID:
                test_offset = fs_table[file_index][FS_FILE_OFFSET]

    COMM_data_start = int(test_offset,16) + 0x88 # Skip 0x80 bytes (and 0x8 bytes past COMM header/size) to get to start of COMM data

    with open(rom_file, 'rb') as pw64_rom:
        pw64_rom.seek(COMM_data_start, 0)
        comm_data = pw64_rom.read(0x430) # Assumption but whatevs.
    pw64_rom.close()

    return comm_data, COMM_data_start

# Write new size for UPWT task to the FS table for later TABL build and compression
# TODO: Rewrite this to be "update file size" for all files
def update_task_size_in_tabl(task_id, new_size):
    for file_index in fs_table:
        if fs_table[file_index][FS_FILE_UPWT_TASK_ID] == task_id:
            print("Task Name: %s (FS ID: %s) resized to: %s" % (task_id, file_index, new_size))
            fs_table[file_index][FS_FILE_SIZE] = new_size

# See above... don't do this.
def update_file_size_in_tabl(file_index, new_size):
    print("File ID: %s resized to: %s" % (file_index, new_size))
    fs_table[file_index][FS_FILE_SIZE] = new_size

# Test ID -> FS Index
def get_fs_index_and_size_of_task(task_name):
    for file_index in fs_table:
        if fs_table[file_index][FS_FILE_UPWT_TASK_ID] == task_name:
            return file_index, fs_table[file_index][FS_FILE_SIZE]


# Patch all addresses that deal with File System size
def patch_fs_addrs(patch_size, rom_file):
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

    with open(rom_file, 'r+b') as pw64_rom:
        # Loop through and hard patch our game code at various offsets.
        # These need to be modified for the game to know we've added 0x70 of data and moved FS/Audio offsets by +0x70
        # I learned the hard way there are explicit expectations about locations of various data at specific ROM addresses that are calculated in code.
        for addr in fs_size_mod_locs:
            pw64_rom.seek(addr, 0)
            data = int(binascii.hexlify(pw64_rom.read(2)), 16) + patch_size # Read the bytes and convert to int + increase size
            pw64_rom.seek(addr, 0)
            #pw64_rom.write(binascii.unhexlify(hex(data).lstrip('0x'))) # stupid bytes() function doesn't do what I expected.
            pw64_rom.write(binascii.unhexlify(b'%x' % (data))) # This is still silly but better than ^
    pw64_rom.close()

def update_upwt_size(upwt_addr, new_size, output_rom):
    # Update the actual size of the UPWT FORM
    with open(output_rom, 'r+b') as pw64_rom:
        pw64_rom.seek(upwt_addr, 0)
        pw64_rom.write(new_size.to_bytes(2, 'big'))
    pw64_rom.close()

# ^ and \/ -- basically identical? merge+rewrite

def overwrite_in_rom(output_rom, offset, data):
    # Overwrites data without adding anything (no need to update TABL)

    with open(output_rom, 'r+b') as pw64_rom:
        pw64_rom.seek(offset)
        pw64_rom.write(bytes.fromhex(data))
    pw64_rom.close()

# Inject data into offset
def inject_data(offset, data, trim_rom=True):
    # TODO: Things
    # use write_final_upwt() from JSON PoC for base
    pass

def rebuild_TABL():
# Once we've done our mods and modified the TABL data (i.e. UPWT "file" size),
# rebuild and write out the entire TABL back to binary format for later MIO0 compression
# Note: 'filesys' size Debug output is at 0x802C1C34
#       0x802B6CC8 = E_GC_1's size as read from TABL
    with open("TABL_NEW.bin", 'wb') as TABL_OUT:
        for f in range(len(fs_table)):
            file_type = fs_table[f][FS_FILE_TYPE].encode()
            file_size = binascii.unhexlify(hex(fs_table[f][FS_FILE_SIZE]).lstrip("0x").zfill(8).encode()) # HAHA WAT

            TABL_OUT.write(file_type)
            TABL_OUT.write(file_size)
    TABL_OUT.close()

    # Use the external 'mio0' tool to re-compress this data.
    # If I had a Python sample of MIO0 compression code this would not be needed...
    call(['./mio0', 'TABL_NEW.bin', 'TABL_NEW.mio0'])

    print("* TABL updated, rebuilt, written out to tempfile, MIO0 re-compressed.")

def inject_TABL(rom):
    # This goes hand-in-hand with rebuild_TABL()... should probably be combined into one function.
    # Take our newly built and compressed TABL and shove it back into the ROM.
    # Make sure the MIO0 is padded. For some reason the `mio0` tool doesn't re-compress to original size? I don't know how these things work.
    # To be more clear the MIO0 data in the PW64 ROM is 3676 bytes but after all the
    # other work is done it compresses back to only 3409 bytes.
    mio0_file_size = os.path.getsize('TABL_NEW.mio0')
    if mio0_file_size < 3676:
        bytes_to_pad = 3676 - mio0_file_size
        with open ("TABL_NEW.mio0", 'ab') as m: # Open the ROM in append mode.
            m.write(binascii.unhexlify('00')*bytes_to_pad) # Seems to work fine? :shrug:
        m.close()

    # Get the rom size. We will add/remove these padding bytes here as needed when we start to inject bigger UPWTasks.
    #rom_file_size = os.path.getsize(PW64_ROM)

    # Write our newly compressed MIO0 TABL data back into the ROM.
    with open (rom, 'r+b') as pw64_rom: #F'ing was using the wrong mode (wb) and it was zeroing all data
        pw64_rom.seek(int(0xDE754), 0)
        with open ("TABL_NEW.mio0", 'rb') as mio0:
            pw64_rom.write(mio0.read()) # File read/write inception.
        mio0.close()
    pw64_rom.close()

    # Remove the files (or comment out for debugging... but why? it works! trust me!)
    os.remove("TABL_NEW.bin")
    os.remove("TABL_NEW.mio0")

    print("* New TABL chunk injected into ROM.")

def inject_data_into_rom(rom, data, addr):
    # We open the ROM in read-only mode, read in the original data from the ROM up to where we want to insert our new data.
    # Open a temp file in write mode, read the ROM up to the insertion address and then insert the BALS bytes we read in previously.
    # Then read in (from old ROM) and write (to temp file) the rest of the ROM.
    # This is a form of "injecting" data into a binary file. Python doesn't have an "insert" mode for writing files...
    # When done writing out this newly munged crap into a temp file, remove the original and rename our temp file back to the OG ROM name.
    # There's probably a better way to do this.

    rom_size_expected = 8388608

    with open(rom, 'rb') as pw64_rom_first, open("PW64_ROM_TMP.z64", 'wb') as pw64_rom_second:
        pw64_rom_second.write(pw64_rom_first.read(addr)) # Read all the bytes up to where we need to insert our data
        pw64_rom_second.write(data) # Add our newly recompiled UPWT container

        pw64_rom_second.write(pw64_rom_first.read()) # Read in the rest of the data from original ROM and write to temp file

        #fs_size_change = len(final_upwt_data) - old_upwt_size
        #if fs_size_change > 0:
        #    pw64_rom_second.flush()
        #    pw64_rom_second.seek(-fs_size_change, os.SEEK_END)
        #    pw64_rom_second.truncate()
        pw64_rom_second.seek(os.SEEK_END, 1)
        rom_end = pw64_rom_second.tell()

        if rom_size_expected < rom_end:
            pw64_rom_second.flush()
            pw64_rom_second.seek(rom_size_expected, 0)
            pw64_rom_second.truncate()

    pw64_rom_second.close()
    pw64_rom_first.close()

    # Switch our files ... ooh scary.
    os.remove(rom)
    os.rename('PW64_ROM_TMP.z64', rom)
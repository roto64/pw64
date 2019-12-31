import binascii
import itertools
import struct
from subprocess import call

# Will hold our table of files: File Type, File Offset, and File Size
fs_table = {}
# Shortcuts for the above dict
FS_FILE_TYPE = 0
FS_FILE_OFFSET = 1
FS_FILE_SIZE = 2
FS_FILE_UPWT_TASK_ID = 3

pw64_tabl_uncompressed_size = 0

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

    # Early PoC. Until I work out offsets and ADAT format/parsing I'll limit to 0x70 (original message's size).
    if len(encoded_string_hex) < expected_string_length:
        pad = expected_string_length - len(encoded_string_hex)
        for i in range(0, pad):
            encoded_string_hex.append("00")
    elif len(encoded_string_hex) > expected_string_length:
        print("String too long! %s" % hex(len(encoded_string_hex)))
        sys.exit(1)

    return(binascii.unhexlify(''.join(encoded_string_hex)))

# Does what it says on the tin
def float_to_hex(float_in):
    return struct.pack('>f', float_in)

# Combined unpack_tabl and build_fs_map
def build_fs_table(PW64_Rom):
    with open (PW64_Rom, 'rb') as pw64_rom:
        global fs_table
        global pw64_tabl_uncompressed_size
        pw64_tabl_mio0_data_start = 0xDE758 # Never changes
        pw64_fs_start = 0xDF5B0 # Offset of first file in "File System" (UVSY)

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

# Write new size for UPWT task to the FS table for later TABL build and compression
def update_task_size_in_tabl(task_id, new_size):
    for file_index in fs_table:
        if fs_table[file_index][FS_FILE_UPWT_TASK_ID] == task_id:
            print("Task Name: %s (FS ID: %s) resized to: %s" % (task_id, file_index, new_size))
            fs_table[file_index][FS_FILE_SIZE] = new_size

# Inject data into offset
def inject_data(offset, data, trim_rom=True):
    # TODO: Things
    pass

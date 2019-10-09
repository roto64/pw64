#!/usr/bin/env python
import binascii
import sys

# Just dumps all the strings straight from the PW64 ROM
# NOT the latest version. Check queueRAM's FS Dumper.
# Just keeping this around for historical purposes.

def print_adat_decoded(hex_data, printer=True):
		# The DATA blocks in the ADAT container appear to be "coded" ASCII strings.
		# The strings use a sort of look-up table as seen below.
		# This was probably done for easier localization (Kanji font textures?)
		# The Font Sprite/Texture maps are in the "STRG" container/blocks.
		# This table was extrapolated from the FS dump and PJ64 memory searches.
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

		# Take the raw binary data and convert to Hex
		#hex_data = str(binascii.b2a_hex(hex_data),'ascii')

		# Split input stream of characters into hex bytes
		#hex_split = [(hex_data[i:i+4]) for i in range(0, len(hex_data), 4)]
		hex_split = [(hex_data[i:i+2]) for i in range(0, len(hex_data), 2)]
		#print(hex_split)
		#print("Len: %s" % len(hex_split))

		""" 
	 for i in xrange(0, len(hex_split), 2):
				hex_pair = hex_split[i:i+2]
				if hex_pair[0] == '00':
					print (hex_pair[1]),
				elif hex_pair[0] == '00' and hex_pair[1] == '00':
					print (hex_pair[1]),
				else:
					print("WTF: %s" % hex_pair[0])
		"""
 
		# Empty list for storing final string
		adat_final_string = []

		# Go through each byte
		for char_byte in hex_split:
#				char_byte = char_byte[2:]
				char_byte = char_byte.upper()
				if char_byte == 'CA':
						# slash? '\' ?
						adat_final_string.append('\t') #'?1')
				elif char_byte == 'D4':
						# Unknown char
						adat_final_string.append(' ') #'?2')
				elif char_byte == 'FE':
						# Newline
						adat_final_string.append('\n')
				elif char_byte == 'FD':
						# Tab?
						adat_final_string.append('\t')
				elif char_byte == 'FF':
						# EOF/EOS
						break
				elif char_byte == '00':
						pass
				else:
						adat_final_string.append(char_map_combined[char_byte])

		if printer:
			print('		--------- Decoded String ---------')
			for line in "".join(adat_final_string).splitlines():
				print ('		%s' % line)
			print('		----------------------------------')
		else:
			return adat_final_string


def main():
	in_data = """
		00 1d 00 24 00 2e 00 28 00 42 00 24 00 42 00 33 
		00 2b 00 32 00 37 00 32 00 42 00 32 00 29 00 42 
		00 37 00 2b 00 28 00 42 00 29 00 2f 00 24 00 30 
		00 28 00 fe 00 26 00 32 00 30 00 2c 00 31 00 2a 
		00 42 00 29 00 35 00 32 00 30 00 42 00 37 00 2b 
		00 28 00 42 00 32 00 2c 00 2f 00 42 00 33 00 2f 
		00 24 00 31 00 37 00 4d 00 36 00 fe 00 36 00 30 
		00 32 00 2e 00 28 00 42 00 36 00 37 00 24 00 26 
		00 2e 00 48 00 42 00 37 00 2b 00 28 00 31 00 42 
		00 2f 00 24 00 31 00 27 00 42 00 32 00 31 00 fe 
		00 37 00 2b 00 28 00 42 00 2f 00 24 00 31 00 27 
		00 2c 00 31 00 2a 00 42 00 33 00 32 00 2c 00 31 
		00 37 00 49 00 fe 00 ff 
"""

	#in_data = in_data.replace("\n","")
	#in_data = in_data.replace(" ","")

	#print_adat_decoded(in_data)

	tests = {}

		

	# Open the ROM and find the ADAT chunk @ 0x35C08C
	with open(sys.argv[1], 'rb') as pw64_rom:
		pw64_rom.seek(int(0x35C08C), 0)
		
		FORM_block_marker = pw64_rom.read(4)
		FORM_block_length = binascii.b2a_hex(pw64_rom.read(4))
		print(FORM_block_marker)
		print(FORM_block_length)
		
		# Hardcode skip 0x20 bytes from current position to get to the first NAME:
		#		ADAT marker (name 0x4 bytes, no length), 
		#		PAD (name 0x4 bytes + length 0x4 bytes + data 0x4 bytes)
		#		SIZE (name 0x4 bytes + length 0x4 bytes + data 0x8 bytes)
		pw64_rom.seek(0x20, 1)
		
		
		while True:
			NAME_chunk_marker = pw64_rom.read(4)
			NAME_chunk_length = binascii.b2a_hex(pw64_rom.read(4))
			#print(NAME_chunk_marker)
			#print(NAME_chunk_length)
		
			if NAME_chunk_marker == "NAME":
				data = pw64_rom.read(int(NAME_chunk_length, 16)).rstrip('\0')
				print("%s (%s)" % (data.rstrip('\0'), binascii.b2a_hex(data)))
		
				DATA_chunk_marker = pw64_rom.read(4)
				DATA_chunk_length = binascii.b2a_hex(pw64_rom.read(4))
				data_text = pw64_rom.read(int(DATA_chunk_length, 16))
				
				print(DATA_chunk_marker)
				print(DATA_chunk_length)
				tests.update({data: data_text})
		
				# Dump all the text?
				print_adat_decoded(binascii.b2a_hex(tests[data]), True)
		
				

					# If we're reading past START+END_OF_FORM 
			if pw64_rom.tell() >= int(FORM_block_length, 16)+0x35C08C:
				print("We're done")
				#print tests
				break
			
			#for k,v in tests.iteritems():
			#	print k

		if len(sys.argv) > 2:
			test_name = sys.argv[2]
		else:
			test_name = 'E_GC_1'
		test_title = "".join(print_adat_decoded(binascii.b2a_hex(tests[str(test_name)+'_N']), False))
		test_mission = print_adat_decoded(binascii.b2a_hex(tests[str(test_name)+'_M']), False) 

		#print(tests['E_GC_1_N'])
		print("Test ID: %s" % test_name)
		print("Test Title: %s" % test_title.rstrip())
		print("Test Mission Text:")
		print('\t----------------------------------')
		for line in "".join(test_mission).splitlines():
			print ('\t%s' % line)
		print('\t----------------------------------')

		#print("bla: %s" % print_adat_decoded(binascii.b2a_hex(tests[str(test_name)+'_N']), False))
		
if __name__== "__main__":
	main()

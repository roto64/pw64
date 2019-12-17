#!/usr/bin/env python

# Finds all the UPWT chunks in a ROM
# Prints their offsets starting at FORM
# Feed it the PW64 ROM

import binascii
import sys

def main():

	# Dict for Test ID and FORM offset in ROM
	Test_IDs = {}

	# Open the ROM and find the first UPWT chunk @ 0x342E2C
	with open(sys.argv[1], 'rb') as pw64_rom:
	
		#UPWT_Section_Length
		pw64_rom.seek(int(0x342E2C), 0)

		# Read in all the UPWT chunks
		while True:
			UPWT_Data_Start = pw64_rom.tell()
			
			FORM_block_marker = pw64_rom.read(4)
			FORM_block_length = binascii.b2a_hex(pw64_rom.read(4))
			#print(FORM_block_marker)
			#print(FORM_block_length)

			UPWT_Chunk_Marker = pw64_rom.read(4)
			
			if UPWT_Chunk_Marker == "UPWT":			
				PAD_Chunk_Marker = pw64_rom.read(4)
				PAD_Chunk_Length = binascii.b2a_hex(pw64_rom.read(4))
				
				# Read 'PAD ' and do nothing
				pw64_rom.read(int(PAD_Chunk_Length, 16))

				JPTX_chunk_marker = pw64_rom.read(4)
				JPTX_chunk_length = binascii.b2a_hex(pw64_rom.read(4))

				if JPTX_chunk_marker == "JPTX":
					test_id = pw64_rom.read(int(JPTX_chunk_length, 16)).rstrip('\0')
					#print("%s (%s)" % (test_id, binascii.b2a_hex(test_id)))
					
					# The Canon missions have identical ID's for 4 tests each...
					# e.g. A_EX_[1-3]
					# Need a better solution here. Nested dicts? 
					if test_id in Test_IDs:
						# Append the offset to the ID if it "already exists" (dupe)
						test_id = test_id + '-' + hex(UPWT_Data_Start)
					# Update our global dict
					Test_IDs.update( { test_id: hex(UPWT_Data_Start) })

				# Go back to start of this FORM+FORM_LENGTH for next chunk
				pw64_rom.seek(UPWT_Data_Start + int(FORM_block_length, 16) - 4, 0)

				#print(hex(pw64_rom.tell()))
			
			# No more UPWT's
			elif UPWT_Chunk_Marker == "ADAT":
				#print("We're done")
				#print(hex(pw64_rom.tell()))
				break

		test_list = []
		for k,v in Test_IDs.iteritems():
			print("%s: %s" % (k, v))
			test_list.append(k)
			
		# For main program help "options"
		test_list.sort()
		print("Available Test IDs: " + ", ".join(test_list))

if __name__== "__main__":
  main()

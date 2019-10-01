#!/usr/bin/env python

# UPWT Parser v0.001 by roto

import binascii
import itertools
import struct
import sys


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)

def main():
	# Feed it a rip of a UPWT section from your fav hex editor.
	# Check "mio0_33015c.mio0" (from n64split's data)
	# Start the rip from FORM to FORM.
	with open(sys.argv[1], 'rb') as UPWT_Bin:
	
		FORM_Magic = UPWT_Bin.read(4)
		if FORM_Magic != "FORM":
			print("What is this?")
			sys.exit(1)
			
		FORM_Length = binascii.b2a_hex(UPWT_Bin.read(4))
	
		UPWT_Chunk = UPWT_Bin.read(4)
	
		PAD_Marker = UPWT_Bin.read(4)
		PAD_Length = binascii.b2a_hex(UPWT_Bin.read(4))
		UPWT_Bin.seek(int(PAD_Length),1) # Move PAD_Length bytes relative to current pos
	
		JPTX_Marker = UPWT_Bin.read(4)
		JPTX_Length = binascii.b2a_hex(UPWT_Bin.read(4))
		JPTX_Data = UPWT_Bin.read(int(JPTX_Length, 16))

		NAME_Marker = UPWT_Bin.read(4)
		NAME_Length = binascii.b2a_hex(UPWT_Bin.read(4))
		NAME_Data = UPWT_Bin.read(int(NAME_Length, 16))

		INFO_Marker = UPWT_Bin.read(4)
		INFO_Length = binascii.b2a_hex(UPWT_Bin.read(4))
		INFO_Data = UPWT_Bin.read(int(INFO_Length, 16))

		# Read the COMM section and parse out what we know right now.
		COMM_Marker = UPWT_Bin.read(4)
		COMM_Length = binascii.b2a_hex(UPWT_Bin.read(4))
		#COMM_Data = UPWT_Bin.read(int(COMM_Length, 16))
		
		# Go to end of ("COMM data" - 0x14) to get TPAD/LPAD/Rings/Balloons/Targets/etc counts
		UPWT_Bin.seek(int(int(COMM_Length, 16) - 0x14),1)
		COMM_Object_Thermals = int(binascii.b2a_hex(UPWT_Bin.read(1)), 16)
		COMM_Object_LocalWinds = int(binascii.b2a_hex(UPWT_Bin.read(1)), 16)
		COMM_Object_TPADs = int(binascii.b2a_hex(UPWT_Bin.read(1)), 16) # Takeoff "Pad" (also for Gyro)
		COMM_Object_LPADs = int(binascii.b2a_hex(UPWT_Bin.read(1)), 16) # RP Landing Pad
		COMM_Object_LSTPs = int(binascii.b2a_hex(UPWT_Bin.read(1)), 16) # Gyro Landing Strip
		COMM_Object_Rings = int(binascii.b2a_hex(UPWT_Bin.read(1)), 16)
		COMM_Object_Balloons = int(binascii.b2a_hex(UPWT_Bin.read(1)), 16)
		COMM_Object_Targets = int(binascii.b2a_hex(UPWT_Bin.read(1)), 16)

		# Show all the usual suspects
		print("Magic: %s" % FORM_Magic)
		print("Length: %s" % FORM_Length)
		print("\tChunk: %s" % UPWT_Chunk)
		print("\tPAD Marker: %s" % PAD_Marker)
		print("\tPAD Length: %s" % PAD_Length)
		print("\tJPTX Marker: %s" % JPTX_Marker)
		print("\tJPTX Length: %s" % JPTX_Length)
		print("\t\tJPTX Data (Test ID): %s" % JPTX_Data)
		print("\tNAME Marker: %s" % NAME_Marker)
		print("\tNAME Length: %s" % NAME_Length)
		print("\t\tNAME Data (Test \"Name\"): %s" % NAME_Data)
		print("\tINFO Marker: %s" % INFO_Marker)
		print("\tINFO Length: %s" % INFO_Length)
		print("\t\tINFO Data (Test \"Description\"): %s" % INFO_Data)
		print("\tCOMM Marker: %s" % COMM_Marker)
		print("\tCOMM Length: %s" % COMM_Length)
		print("\t\tTest / Mission Parameters:")
		#print("\t\t\tCOMM Data: %s" % COMM_Object_Data)

		# Start parsing known data
		print("\t\t\t# of Hang Glider Thermals: %s" % COMM_Object_Thermals)
		print("\t\t\t# of Local Winds: %s" % COMM_Object_LocalWinds)
		print("\t\t\t# of Takeoff Pads/Strips: %s" % COMM_Object_TPADs)
		print("\t\t\t# of Landing Pads: %s" % COMM_Object_LPADs)
		print("\t\t\t# of Landing Strips: %s" % COMM_Object_LSTPs)
		
		print("\t\t\t# of Rings: %s" % COMM_Object_Rings)
		print("\t\t\t# of Balloons: %s" % COMM_Object_Balloons)
		print("\t\t\t# of Rocket Targets: %s" % COMM_Object_Targets)

		# Go forward 12 bytes and see what chunk is next
		UPWT_Bin.seek(12,1)

		UPWT_Next_Chunk = UPWT_Bin.read(4)
	
		if UPWT_Next_Chunk == 'THER':
			UPWT_THER_Length = binascii.b2a_hex(UPWT_Bin.read(4))
			THER_Start = UPWT_Bin.tell()
			UPWT_THER_Data = binascii.b2a_hex(UPWT_Bin.read(int(UPWT_THER_Length, 16)))

			# Go back to start of THER data
			UPWT_Bin.seek(-int(UPWT_THER_Length, 16), 1)
			
			print("\t%s Marker: %s" % (UPWT_Next_Chunk, UPWT_Next_Chunk))
			print("\t%s Length: %s" % (UPWT_Next_Chunk, UPWT_THER_Length))
			print("\t%s Data: %s" % (UPWT_Next_Chunk, UPWT_THER_Data))
						
			# 0x28 bytes per THER
			UPWT_THER_Data = []
			for THER in range(1, COMM_Object_Thermals+1):
				UPWT_THER_Data.append(binascii.b2a_hex(UPWT_Bin.read(0x28)))

			counter = 0
			for THER in UPWT_THER_Data:	
				counter += 1								 
				
				# Groups 8 byte blocks, makes into a list, joins tuple, converts to bytearray from hex. disgusting.
				THER_x = bytearray.fromhex(''.join(list(grouper(THER, 8, '?'))[0]))
				THER_z = bytearray.fromhex(''.join(list(grouper(THER, 8, '?'))[1]))
				THER_y = bytearray.fromhex(''.join(list(grouper(THER, 8, '?'))[2]))
				THER_yaw = bytearray.fromhex(''.join(list(grouper(THER, 8, '?'))[3]))
				THER_pitch = bytearray.fromhex(''.join(list(grouper(THER, 8, '?'))[4]))
				THER_roll = bytearray.fromhex(''.join(list(grouper(THER, 8, '?'))[5]))

				# Round FP precision to 6 digits		
				UPWT_THER_Coordinates_Floats = [round(struct.unpack('>f', THER_x)[0],6), 
												round(struct.unpack('>f', THER_z)[0],6),
												round(struct.unpack('>f', THER_y)[0],6),
												round(struct.unpack('>f', THER_yaw)[0],6),
												round(struct.unpack('>f', THER_pitch)[0],6)]
									

				print("\t\tTHER # %s:" % counter)
				print("\t\tTHER Data: ")
				for bla in ["".join(x) for x in list(grouper(THER, 8, '?'))]:
					print("\t\t\t%s" % bla)
				
				print("\t\t\tX: %s\n\t\t\tY: %s\n\t\t\tZ: %s\n\t\t\t\n\t\t\t!!! This is wrong. Might be Height/Width?\n\t\t\tYaw: %s\n\t\t\tPitch: %s" % (UPWT_THER_Coordinates_Floats[0],
																	UPWT_THER_Coordinates_Floats[2],
																	UPWT_THER_Coordinates_Floats[1],
																	UPWT_THER_Coordinates_Floats[3],
																	UPWT_THER_Coordinates_Floats[4]))
			
			# We're done here, go back to start of this chunk + length of chunk (to get to next one)
			UPWT_Bin.seek(THER_Start + int(UPWT_THER_Length, 16), 0)
			UPWT_Next_Chunk = UPWT_Bin.read(4)
			
		if UPWT_Next_Chunk == 'TPAD':
			UPWT_TPAD_Length = binascii.b2a_hex(UPWT_Bin.read(4))
			TPAD_Start = UPWT_Bin.tell()
			
			# Represent data in Hex
			UPWT_TPAD_Data = binascii.b2a_hex(UPWT_Bin.read(int(UPWT_TPAD_Length, 16)))
		
			# Go back to start of TPAD data
			UPWT_Bin.seek(-int(UPWT_TPAD_Length, 16), 1)
		
			# Read the Float coordinates
			UPWT_TPAD_Coordinates = [binascii.b2a_hex(UPWT_Bin.read(4)), # X
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Z
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Y
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Yaw
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Pitch
									 binascii.b2a_hex(UPWT_Bin.read(4))] # Roll
									 
			#
			TPAD_x = bytearray.fromhex(UPWT_TPAD_Coordinates[0])
			TPAD_z = bytearray.fromhex(UPWT_TPAD_Coordinates[1])
			TPAD_y = bytearray.fromhex(UPWT_TPAD_Coordinates[2])
			TPAD_yaw = bytearray.fromhex(UPWT_TPAD_Coordinates[3])
			TPAD_pitch = bytearray.fromhex(UPWT_TPAD_Coordinates[4])
			TPAD_roll = bytearray.fromhex(UPWT_TPAD_Coordinates[5])
		
			#print("%s %s %s", TPAD_x, TPAD_z, TPAD_y)
			UPWT_TPAD_Coordinates_Floats = [round(struct.unpack('>f', TPAD_x)[0],6), 
											round(struct.unpack('>f', TPAD_z)[0],6),
											round(struct.unpack('>f', TPAD_y)[0],6),
											round(struct.unpack('>f', TPAD_yaw)[0],6),
											round(struct.unpack('>f', TPAD_pitch)[0],6),
											round(struct.unpack('>f', TPAD_roll)[0],6)]
			# TPAD
			print("\t%s Marker: %s" % (UPWT_Next_Chunk, UPWT_Next_Chunk))
			print("\t%s Length: %s" % (UPWT_Next_Chunk, UPWT_TPAD_Length))
			print("\t%s Data: %s" % (UPWT_Next_Chunk, UPWT_TPAD_Data))
			print("\t\t%s More Data: %s" % (UPWT_Next_Chunk, UPWT_TPAD_Coordinates))
			print("\t\tX: %s\n\t\tY: %s\n\t\tZ: %s\n\t\tYaw: %s\n\t\tPitch: %s\n\t\tRoll: %s" % (UPWT_TPAD_Coordinates_Floats[0],
																UPWT_TPAD_Coordinates_Floats[2],
																UPWT_TPAD_Coordinates_Floats[1],
																UPWT_TPAD_Coordinates_Floats[3],
																UPWT_TPAD_Coordinates_Floats[4],
																UPWT_TPAD_Coordinates_Floats[5]))
																
			# We're done here, go back to start of this chunk + length of chunk (to get to next one)
			UPWT_Bin.seek(TPAD_Start + int(UPWT_TPAD_Length, 16), 0)

			UPWT_Next_Chunk = UPWT_Bin.read(4)
	
		if UPWT_Next_Chunk == 'RNGS':
			UPWT_RNGS_Length = binascii.b2a_hex(UPWT_Bin.read(4))
			RNGS_Start = UPWT_Bin.tell()
#			UPWT_RNGS_Data = binascii.b2a_hex(UPWT_Bin.read(int(UPWT_RNGS_Length, 16)))
			
			print("\t%s Marker: %s" % (UPWT_Next_Chunk, UPWT_Next_Chunk))
			print("\t%s Length: %s" % (UPWT_Next_Chunk, UPWT_RNGS_Length))
			
			# 0x84 bytes per ring
			UPWT_RNGS_Data = []
			for ring in range(1, COMM_Object_Rings+1):
				UPWT_RNGS_Data.append(binascii.b2a_hex(UPWT_Bin.read(0x84)))

			counter = 0
			for ring in UPWT_RNGS_Data:	
				counter += 1								 
				
				# Groups 8 byte blocks, makes into a list, joins tuple, converts to bytearray from hex. disgusting.
				RNGS_x = bytearray.fromhex(''.join(list(grouper(ring, 8, '?'))[0]))
				RNGS_z = bytearray.fromhex(''.join(list(grouper(ring, 8, '?'))[1]))
				RNGS_y = bytearray.fromhex(''.join(list(grouper(ring, 8, '?'))[2]))
				RNGS_yaw = bytearray.fromhex(''.join(list(grouper(ring, 8, '?'))[3]))
				RNGS_pitch = bytearray.fromhex(''.join(list(grouper(ring, 8, '?'))[4]))
				RNGS_roll = bytearray.fromhex(''.join(list(grouper(ring, 8, '?'))[5]))
				RNGS_type = bytearray.fromhex(''.join(list(grouper(ring, 8, '?'))[28]))

				# Round FP precision to 6 digits		
				UPWT_RNGS_Coordinates_Floats = [round(struct.unpack('>f', RNGS_x)[0],6), 
												round(struct.unpack('>f', RNGS_z)[0],6),
												round(struct.unpack('>f', RNGS_y)[0],6),
												round(struct.unpack('>f', RNGS_yaw)[0],6),
												round(struct.unpack('>f', RNGS_pitch)[0],6)]
									

				print("\t\tRing # %s:" % counter)
				print("\t\tRing Data: ")
				#print(["".join(x) for x in list(grouper(ring, 8, '?'))])
				for bla in ["".join(x) for x in list(grouper(ring, 8, '?'))]:
					print("\t\t\t%s" % bla)

				### ToDo: More ring parsing:
				# 79 01 == normal static ring
				# 78 01 == rotation/tumbling on Y(?) axis 
				ring_type = list(grouper(binascii.b2a_hex(RNGS_type), 2, '?'))
				print("\t\t\tRing Details:\n\t\t\t\tRaw: %s" % binascii.b2a_hex(RNGS_type))

				ring_rotation = ''.join(ring_type[0])
				ring_unknown1 = ''.join(ring_type[1])
				ring_special = ''.join(ring_type[2])
				ring_unknown2 = ''.join(ring_type[3])
				
				if ring_rotation == "78":
					print("\t\t\t\tRotation: %s (Y-Axis)" % ring_rotation)
				elif ring_rotation == "79":
					print("\t\t\t\tRotation: %s (None)" % ring_rotation)
				elif ring_rotation == "7A":
					print("\t\t\t\tRotation: %s (X-Axis)" % ring_rotation)
					
				print("\t\t\t\tUnknown1: %s" % ring_unknown1)

				if ring_special == "01":
					print("\t\t\t\tSpecial: %s (Yes, bonus)" % ring_special)
				else:
					print("\t\t\t\tSpecial: %s (No, normal)" % ring_special)
				print("\t\t\t\tUnknown2: %s" % ring_unknown2)
				
				print("\t\t\tX: %s\n\t\t\tY: %s\n\t\t\tZ: %s\n\t\t\tYaw: %s\n\t\t\tPitch: %s" % (UPWT_RNGS_Coordinates_Floats[0],
																	UPWT_RNGS_Coordinates_Floats[2],
																	UPWT_RNGS_Coordinates_Floats[1],
																	UPWT_RNGS_Coordinates_Floats[3],
																	UPWT_RNGS_Coordinates_Floats[4]))
																	

			# Last 0x4 bytes in RNGS seem unused? So move forward...
			UPWT_Bin.seek(4, 1)
			
			# We're done here, go back to start of this chunk + length of chunk (to get to next one)
			UPWT_Bin.seek(RNGS_Start + int(UPWT_RNGS_Length, 16), 0)
			UPWT_Next_Chunk = UPWT_Bin.read(4)

		if UPWT_Next_Chunk == 'LPAD':
			UPWT_LPAD_Length = binascii.b2a_hex(UPWT_Bin.read(4))
			LPAD_Start = UPWT_Bin.tell()
			# Represent data in Hex
			UPWT_LPAD_Data = binascii.b2a_hex(UPWT_Bin.read(int(UPWT_LPAD_Length, 16)))
		
			# Go back to start of LPAD data
			UPWT_Bin.seek(-int(UPWT_LPAD_Length, 16), 1)
		
			# Read the Float coordinates
			UPWT_LPAD_Coordinates = [binascii.b2a_hex(UPWT_Bin.read(4)), # X
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Z
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Y
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Yaw
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Pitch
									 binascii.b2a_hex(UPWT_Bin.read(4))] # Roll
									 
			#
			LPAD_x = bytearray.fromhex(UPWT_LPAD_Coordinates[0])
			LPAD_z = bytearray.fromhex(UPWT_LPAD_Coordinates[1])
			LPAD_y = bytearray.fromhex(UPWT_LPAD_Coordinates[2])
			LPAD_yaw = bytearray.fromhex(UPWT_LPAD_Coordinates[3])
			LPAD_pitch = bytearray.fromhex(UPWT_LPAD_Coordinates[4])
			LPAD_roll = bytearray.fromhex(UPWT_LPAD_Coordinates[5])
		
			UPWT_LPAD_Coordinates_Floats = [round(struct.unpack('>f', LPAD_x)[0],6), 
											round(struct.unpack('>f', LPAD_z)[0],6),
											round(struct.unpack('>f', LPAD_y)[0],6),
											round(struct.unpack('>f', LPAD_yaw)[0],6),
											round(struct.unpack('>f', LPAD_pitch)[0],6),
											round(struct.unpack('>f', LPAD_roll)[0],6)]
			# LPAD
			print("\t%s Marker: %s" % (UPWT_Next_Chunk, UPWT_Next_Chunk))
			print("\t%s Length: %s" % (UPWT_Next_Chunk, UPWT_LPAD_Length))
			print("\t%s Data: %s" % (UPWT_Next_Chunk, UPWT_LPAD_Data))
			print("\t\t%s More Data: %s" % (UPWT_Next_Chunk, UPWT_LPAD_Coordinates))
			print("\t\tX: %s\n\t\tY: %s\n\t\tZ: %s\n\t\tYaw: %s\n\t\tPitch: %s\n\t\tRoll: %s" % (UPWT_LPAD_Coordinates_Floats[0],
																UPWT_LPAD_Coordinates_Floats[2],
																UPWT_LPAD_Coordinates_Floats[1],
																UPWT_LPAD_Coordinates_Floats[3],
																UPWT_LPAD_Coordinates_Floats[4],
																UPWT_LPAD_Coordinates_Floats[5]))

			# We're done here, go back to start of this chunk + length of chunk (to get to next one)
			UPWT_Bin.seek(LPAD_Start + int(UPWT_LPAD_Length, 16), 0)
			UPWT_Next_Chunk = UPWT_Bin.read(4)
			

		elif UPWT_Next_Chunk == 'LSTP':
			UPWT_LSTP_Length = binascii.b2a_hex(UPWT_Bin.read(4))
			LSTP_Start = UPWT_Bin.tell()
			UPWT_LSTP_Data = binascii.b2a_hex(UPWT_Bin.read(int(UPWT_LSTP_Length, 16)))
	
			# Go back to start of TPAD data
			UPWT_Bin.seek(-int(UPWT_LSTP_Length, 16), 1)
		
			# Read the Float coordinates
			UPWT_LSTP_Coordinates = [binascii.b2a_hex(UPWT_Bin.read(4)), # X
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Z
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Y
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Yaw
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Pitch
									 binascii.b2a_hex(UPWT_Bin.read(4))] # Roll
									 		
			LSTP_x = bytearray.fromhex(UPWT_LSTP_Coordinates[0])
			LSTP_z = bytearray.fromhex(UPWT_LSTP_Coordinates[1])
			LSTP_y = bytearray.fromhex(UPWT_LSTP_Coordinates[2])
			LSTP_yaw = bytearray.fromhex(UPWT_LSTP_Coordinates[3])
			LSTP_pitch = bytearray.fromhex(UPWT_LSTP_Coordinates[4])
			LSTP_roll = bytearray.fromhex(UPWT_LSTP_Coordinates[5])
		
			UPWT_LSTP_Coordinates_Floats = [round(struct.unpack('>f', LSTP_x)[0],6), 
											round(struct.unpack('>f', LSTP_z)[0],6),
											round(struct.unpack('>f', LSTP_y)[0],6),
											round(struct.unpack('>f', LSTP_yaw)[0],6),
											round(struct.unpack('>f', LSTP_pitch)[0],6),
											round(struct.unpack('>f', LSTP_roll)[0],6)]
			# LSTP
			print("\t%s Marker: %s" % (UPWT_Next_Chunk, UPWT_Next_Chunk))
			print("\t%s Length: %s" % (UPWT_Next_Chunk, UPWT_LSTP_Length))
			print("\t%s Data: %s" % (UPWT_Next_Chunk, UPWT_LSTP_Data))
			print("\t\t%s More Data: %s" % (UPWT_Next_Chunk, UPWT_LSTP_Coordinates))
			
			# !!! This one doesn't seem right... maybe its a bounding box coord?
			print("\t\tX: %s\n\t\tY: %s\n\t\tZ: %s\n\t\t!!! The rest is wrong...\n\t\tYaw: %s\n\t\tPitch: %s\n\t\tRoll: %s" % (UPWT_LSTP_Coordinates_Floats[0],
																UPWT_LSTP_Coordinates_Floats[2],
																UPWT_LSTP_Coordinates_Floats[1],
																UPWT_LSTP_Coordinates_Floats[3],
																UPWT_LSTP_Coordinates_Floats[4],
																UPWT_LSTP_Coordinates_Floats[5]))
			# We're done here, go back to start of this chunk + length of chunk (to get to next one)
			UPWT_Bin.seek(LSTP_Start + int(UPWT_LSTP_Length, 16), 0)
			UPWT_Next_Chunk = UPWT_Bin.read(4)
	

		if UPWT_Next_Chunk == 'BALS':
			UPWT_BALS_Length = binascii.b2a_hex(UPWT_Bin.read(4))
			BALS_Start = UPWT_Bin.tell()
			# Represent data in Hex
			UPWT_BALS_Data = binascii.b2a_hex(UPWT_Bin.read(int(UPWT_BALS_Length, 16)))
		
			# Go back to start of BALS data
			UPWT_Bin.seek(-int(UPWT_BALS_Length, 16), 1)
		
			# Read the Float coordinates
			UPWT_BALS_Coordinates = [binascii.b2a_hex(UPWT_Bin.read(4)), # X
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Z
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Y
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Yaw
									 binascii.b2a_hex(UPWT_Bin.read(4)), # Pitch
									 binascii.b2a_hex(UPWT_Bin.read(4))] # Roll
									 
			#
			BALS_x = bytearray.fromhex(UPWT_BALS_Coordinates[0])
			BALS_z = bytearray.fromhex(UPWT_BALS_Coordinates[1])
			BALS_y = bytearray.fromhex(UPWT_BALS_Coordinates[2])
			BALS_yaw = bytearray.fromhex(UPWT_BALS_Coordinates[3])
			BALS_pitch = bytearray.fromhex(UPWT_BALS_Coordinates[4])
			BALS_roll = bytearray.fromhex(UPWT_BALS_Coordinates[5])
		
			UPWT_BALS_Coordinates_Floats = [round(struct.unpack('>f', BALS_x)[0],6), 
											round(struct.unpack('>f', BALS_z)[0],6),
											round(struct.unpack('>f', BALS_y)[0],6),
											round(struct.unpack('>f', BALS_yaw)[0],6),
											round(struct.unpack('>f', BALS_pitch)[0],6),
											round(struct.unpack('>f', BALS_roll)[0],6)]
			# BALS
			print("\t%s Marker: %s" % (UPWT_Next_Chunk, UPWT_Next_Chunk))
			print("\t%s Length: %s" % (UPWT_Next_Chunk, UPWT_BALS_Length))
			print("\t%s Data: %s" % (UPWT_Next_Chunk, UPWT_BALS_Data))
			print("\t\t%s More Data: %s" % (UPWT_Next_Chunk, UPWT_BALS_Coordinates))
			print("\t\tX: %s\n\t\tY: %s\n\t\tZ: %s\n\t\tYaw: %s\n\t\tPitch: %s\n\t\tRoll: %s" % (UPWT_BALS_Coordinates_Floats[0],
																UPWT_BALS_Coordinates_Floats[2],
																UPWT_BALS_Coordinates_Floats[1],
																UPWT_BALS_Coordinates_Floats[3],
																UPWT_BALS_Coordinates_Floats[4],
																UPWT_BALS_Coordinates_Floats[5]))
			# We're done here, go back to start of this chunk + length of chunk (to get to next one)
			UPWT_Bin.seek(BALS_Start + int(UPWT_BALS_Length, 16), 0)
			UPWT_Next_Chunk = UPWT_Bin.read(4)

		elif UPWT_Next_Chunk == 'TARG':
			UPWT_TARG_Length = binascii.b2a_hex(UPWT_Bin.read(4))
			TARG_Start = UPWT_Bin.tell()
			
			print("\t%s Marker: %s" % (UPWT_Next_Chunk, UPWT_Next_Chunk))
			print("\t%s Length: %s" % (UPWT_Next_Chunk, UPWT_TARG_Length))
			
			# 0x20 bytes per TARG
			UPWT_TARG_Data = []
			for TARG in range(1, COMM_Object_Targets+1):
				UPWT_TARG_Data.append(binascii.b2a_hex(UPWT_Bin.read(0x20)))

			counter = 0
			for TARG in UPWT_TARG_Data:	
				counter += 1								 
				
				# Groups 8 byte blocks, makes into a list, joins tuple, converts to bytearray from hex. disgusting.
				TARG_x = bytearray.fromhex(''.join(list(grouper(TARG, 8, '?'))[0]))
				TARG_z = bytearray.fromhex(''.join(list(grouper(TARG, 8, '?'))[1]))
				TARG_y = bytearray.fromhex(''.join(list(grouper(TARG, 8, '?'))[2]))
				TARG_yaw = bytearray.fromhex(''.join(list(grouper(TARG, 8, '?'))[3]))
				TARG_pitch = bytearray.fromhex(''.join(list(grouper(TARG, 8, '?'))[4]))
				TARG_roll = bytearray.fromhex(''.join(list(grouper(TARG, 8, '?'))[5]))

				# Round FP precision to 6 digits		
				UPWT_TARG_Coordinates_Floats = [round(struct.unpack('>f', TARG_x)[0],6), 
												round(struct.unpack('>f', TARG_z)[0],6),
												round(struct.unpack('>f', TARG_y)[0],6),
												round(struct.unpack('>f', TARG_yaw)[0],6),
												round(struct.unpack('>f', TARG_pitch)[0],6)]
									

				print("\t\tTARG # %s:" % counter)
				print("\t\tTARG Data: ")
				
				print("\t\t\tX: %s\n\t\t\tY: %s\n\t\t\tZ: %s\n\t\t\tYaw: %s\n\t\t\tPitch: %s" % (UPWT_TARG_Coordinates_Floats[0],
																	UPWT_TARG_Coordinates_Floats[2],
																	UPWT_TARG_Coordinates_Floats[1],
																	UPWT_TARG_Coordinates_Floats[3],
																	UPWT_TARG_Coordinates_Floats[4]))
																	

			## Last 0x6 bytes in TARG seem unused? So move forward...
			#UPWT_Bin.seek(6, 1)
			
			# We're done here, go back to start of this chunk + length of chunk (to get to next one)
			UPWT_Bin.seek(TARG_Start + int(UPWT_TARG_Length, 16), 0)
			UPWT_Next_Chunk = UPWT_Bin.read(4)
		
		# Shitty EOF that doesn't always work.
		elif UPWT_Next_Chunk == '':
			print("Done")
			sys.exit(1)
			
		#print(hex(UPWT_Bin.tell()))
		#print("*** %s" % hex(UPWT_Bin.tell()))
	

if __name__== "__main__":
  main()
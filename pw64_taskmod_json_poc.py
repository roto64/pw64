#!/usr/bin/env python3

# Pilotwings 64 Mission Editor: Millenial Edition 2000 XP - Now with JSON cleaning power!
#    by roto

import binascii
import io
import itertools
import json
import os
import struct
from subprocess import call
import sys

import pw64_lib

# NOTE:
# Even if you feed a JSON that is compiled from an unmodified (stock) ROM and don't modify a task, the TABL chunk
# is rebuilt/re-compressed and ROM checksum is recalculated. Thus you won't get a 1:1 ROM back out of this script.
#
# Q: What is this?
# A: An evolution of "pw64_taskmod_poc.py" (which only did one thing: inject BALS object) but now with the ability to do more via JSON.
#    Check the README on GitHub.

# Fill me in
PW64_ROM = ""

def main():
    test_id = "E_GC_1" # All JSON data ingestion functions default to reading "E_GC_1.json"

    pw64_lib.build_fs_table(PW64_ROM)

    # Print full FS Table
    if len(sys.argv) == 2 and sys.argv[1] == "-l":
        pw64_lib.show_fs_table()
        sys.exit(0)
    # Print list of specified file type
    elif len(sys.argv) == 3 and sys.argv[1] == "-l":
        pw64_lib.show_fs_table(sys.argv[2].upper())
        sys.exit(0)

    ###
    # FIXME: There's an issue with modifying/resizing the ROM multiple times prior to patching and re-reading TABL from ROM.
    # If we don't run this change_some_text() function early on (or later on after writing the TABL patch to ROM!), there's a problem
    # with incorrect with offsets and build_fs_table blows up when trying to do ADAT lookup... fix later.
    #change_some_text()
    ###

    # Get the original (pre-mod) size of the UPWT in question
    old_upwt_size = pw64_lib.get_fs_index_and_size_of_task(test_id)[1] #0x6b8 # Best way to get this?

    # Do the actual modifications and get our new UPWT size in return
    # This should really be split into multiple functions.
    new_upwt_size = modify_upwt(test_id)

    # Update specified Task ID with new size in TABL.
    pw64_lib.update_task_size_in_tabl(test_id, new_upwt_size)

    # Does what it says.
    rebuild_TABL()

    # Inject our updated and compressed TABL back into the ROM.
    inject_TABL()

    ###
    # See FIXME above. Doing this *after* rebuilding/injecting the TABL seems to not blow anything up...
    # EDIT: Now I know why: build_adat_layout opens the ROM on disk, if that ROM was not updated, it won't have the new TABL with updates.
    # So we have to make this change BEFORE or AFTER modifying any other data on the ROM... Hmm :thinkingface:
    #
    # If we are making further changes, and the changes require lookups for files offsets then
    # we have to re-read the TABL from ROM and clear+rebuild FS table after our previous UPWT mods.
    # This MUST be done because the "fs_table" lives in memory and is not updated after TABL is rebuilt.
    pw64_lib.fs_table = pw64_lib.build_fs_table(PW64_ROM)
    change_some_text(test_id)
    ###

    # Patch all our addresses that deal with FileSystem sizes
    pw64_lib.patch_fs_addrs(new_upwt_size - old_upwt_size, PW64_ROM)

    pw64_lib.fix_rom_checksum(PW64_ROM) # Does what it says on the label.

    pw64_lib.show_fs_table("UPWT") # Show the listing of UPWT's at the end for whatever reason

def modify_upwt(test_id):

    # Read in the base (unmodified) COMM chunk and also address/offset of said  chunk
    original_comm_data_and_addr = pw64_lib.read_comm_from_rom(test_id, PW64_ROM)
    original_comm_data = original_comm_data_and_addr[0]
    original_comm_addr = original_comm_data_and_addr[1]

    print("- Original COMM Data Length from %s: %s" % (test_id, hex(len(original_comm_data))))

    # Loads in original COMM and returns modified COMM data chunk
    modified_comm_data = rebuild_comm(test_id, original_comm_data)

    # Send modified COMM and work on the rest of the data chunks in the UPWT
    final_upwt_data = assemble_final_upwt(test_id, modified_comm_data)
    print("- Modified COMM + UPWT Data Length: %s (Minus 0x88 bytes for rest of UPWT chunks/headers)" % hex(len(final_upwt_data)))

    new_comm_data_chunk_size = len(final_upwt_data)

    # Write our new COMM+DATA to the ROM at the specified address
    write_final_upwt(test_id, final_upwt_data, original_comm_addr, new_comm_data_chunk_size, PW64_ROM)

    # This one needs some re-thinking (see later "update_upwt_size" call)
    final_upwt_size = len(final_upwt_data)+0x8+0x80 # 0x8 = COMM header + size, 0x80 = FORM+PAD+JPTX+etc UPWT data+headers

    print("- Full UPWT (Headers+COMM+Data) Chunk Length: %s" % hex(final_upwt_size))

    # Modify the size of the new UPWT chunk in the FORM
    FORM_size_offset = original_comm_addr - 0x82 # What is 0x82!? Crap I don't remember why this is here...

    # Patches the FORM chunk of the UPWT (minus 0x8 bytes for FORM Maker+Size)
    pw64_lib.update_upwt_size(FORM_size_offset, final_upwt_size-0x8, PW64_ROM)

    print("* All UPWT modifications completed.")

    return final_upwt_size

def assemble_final_upwt(filename, modified_comm_data):
    # TPAD is 0x30 bytes + Marker (0x4) + Size (0x4)
    # From: E_GC_1
    TPAD_header = bytes.fromhex('5450414400000030')
    # RNGS is 0x84 bytes (per ring) + Marker (0x4) + Size of ALL RNGS (0x4)
    # From: E_GC_1
    RNGS_header = bytes.fromhex('524E475300000190') # 0x190 is 3 rings's worth of data chunks
    # LSTP is 0x28 bytes + Marker (0x4) + Size (0x4)
    # From: E_GC_1
    LSTP_header = bytes.fromhex('4C53545000000028')
    # BALS is 0x68 bytes + Marker (0x4) + Size (0x4)
    # From: E_RP_1 (balloon on top of castle)
    BALS_header = bytes.fromhex('42414C5300000068')

    # Read in the JSON file
    with open(filename + ".json", 'r') as json_in:
        data = json_in.read()
        decoded_data = json.loads(data)
    json_in.close()

    # We'll be doing some reads/writes in memory
    upwt_assembler = io.BytesIO()

    # We're going to build our new UPWT container. Write our pre-modified COMM chunk forst
    upwt_assembler.write(modified_comm_data)

    # Assemble the various parts of the UPWT
    # The order of where these chunks are placed doesn't appear to be important (which is why we append BALS at the end and it just works)
    if decoded_data["COMM"]["TPAD"] >= 1:
        upwt_assembler.seek(0, 2) # SEEK_END
        TPAD_template = rebuild_upwt_chunk("E_GC_1", "TPAD")
        upwt_assembler.write(TPAD_header)
        upwt_assembler.write(TPAD_template)

    if decoded_data["COMM"]["RNGS"] >= 1:
        upwt_assembler.seek(0, 2) # SEEK_END
        RNGS_template = rebuild_upwt_chunk("E_GC_1", "RNGS")
        RNGS_size = 0x84 * decoded_data["COMM"]["RNGS"] + 0x4 # Needs to account for the odd 0x4 bytes at the end of the RNGS chunk
        #print(hex(RNGS_size))
        RNGS_header = b'\x52\x4e\x47\x53' + b'%s' % bytes.fromhex(hex(RNGS_size)[2:].zfill(8)) # 0190... hmm do this better.
        upwt_assembler.write(RNGS_header)
        upwt_assembler.write(RNGS_template)

    if decoded_data["COMM"]["LSTP"] >= 1:
        upwt_assembler.seek(0, 2) # SEEK_END
        LSTP_template = rebuild_upwt_chunk("E_GC_1", "LSTP")
        upwt_assembler.write(LSTP_header)
        upwt_assembler.write(LSTP_template)

    if decoded_data["COMM"]["BALS"] >= 1:
        upwt_assembler.seek(0, 2) # SEEK_END
        BALS_template = rebuild_upwt_chunk("E_GC_1", "BALS")
        BALS_size = 0x68 * decoded_data["COMM"]["BALS"]  # If we have >1 BALS need to update size in chunk
        BALS_header = b'\x42\x41\x4C\x53' + b'%s' % bytes.fromhex(hex(BALS_size)[2:].zfill(8)) # 68
        upwt_assembler.write(BALS_header)
        upwt_assembler.write(BALS_template)

    # Go back to the beginning and read it all again.
    upwt_assembler.seek(0)
    upwt_data = upwt_assembler.read(upwt_assembler.getbuffer().nbytes) # A way to size up our BytesIO object
    upwt_assembler.close()

    # Send it back for writing to ROM
    return upwt_data


def rebuild_upwt_chunk(filename, chunk):
    # This function does the actual "rebuilding" of objects from JSON data.
    # If an object doesn't exist in the JSON input, it won't get added to the UPWT container. Related to COMM counts.

    # Read in the JSON file and start plugging in data
    with open(filename + ".json", 'r') as json_in:
        data = json_in.read()
        decoded_data = json.loads(data)
    json_in.close()

    # Stock chunks from ROM, to be modified if JSON data differs
    # This _mostly_ should be OK in terms of "unknown" bytes in the data stream... seems to work out fine at least for E_GC_1
    TPAD_template = bytes.fromhex('C222EB85C3CADCAC4120000041C00000000000000000000000000000000000000000000000000000000000003F800000')
    RNGS_template = bytes.fromhex('C392E937432F03D7425C000041B8000000000000000000000000000000010000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000201000000000000000000006E0000004000000000000000000000007901000000000000000000000000000000000000')
    LSTP_template = bytes.fromhex('C1E68F5CC3D80E3541200000C316D74CC31E0C4A412000000000000001000000420C000000000000')
    BALS_template = bytes.fromhex('C290210643A74D71433600008000000000000000000000000000000041200000000000003C23D70A0000000000000000402000000000001E0000000000000000411CCCCD0000000000000000000000000000000000000000000000003F80000000000000411CCCCD')

    upwt_io = io.BytesIO()

    if chunk == "TPAD":
        XPAD_layout = pw64_lib.TPAD_layout
        upwt_io.write(TPAD_template) # Lay down the default, unmodified chunk
    elif chunk == "LSTP":
        XPAD_layout = pw64_lib.LSTP_layout
        upwt_io.write(LSTP_template)
    elif chunk == "BALS":
        BALS_layout = pw64_lib.BALS_layout
        upwt_io.write(BALS_template)

        # Set up a stream object just in case we have >1 BALS chunk
        bals_stack = io.BytesIO()

        if decoded_data["COMM"]["BALS"] >= 1:
            for ball_num in range(1, decoded_data["COMM"]["BALS"] + 1):
                #print(binascii.hexlify(BALS_template))
                ball_num = str(ball_num)
                upwt_io.seek(0)
                # Go through our structure and populate the template, convert all floats back to hex
                upwt_io.seek(BALS_layout["x"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ball_num]["x"]))
                upwt_io.seek(BALS_layout["z"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ball_num]["z"]))
                upwt_io.seek(BALS_layout["y"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ball_num]["y"]))
                upwt_io.seek(BALS_layout["scale"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ball_num]["scale"]))
                # Things that don't get converted to float or decoded are straight ASCII hex
                upwt_io.seek(BALS_layout["color"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ball_num]["color"]))
                upwt_io.seek(BALS_layout["type"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ball_num]["type"]))
                upwt_io.seek(BALS_layout["solidity"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ball_num]["solidity"]))
                upwt_io.seek(BALS_layout["weight"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ball_num]["weight"]))
                upwt_io.seek(BALS_layout["popforce"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ball_num]["popforce"]))

                # Go to the end of the BALS stack, add current ring
                bals_stack.seek(0, 2)
                upwt_io.seek(0, 0)
                bals_stack.write(upwt_io.read())

        # Seek to start of bals_stack then return the ring stack (containing the X number of BALS)
        bals_stack.seek(0, 0)
        bals_data = bals_stack.read()
        bals_stack.close()

        print("* UPWT data chunk(s) rebuilt: %s" % chunk)

        return bals_data

    elif chunk == "RNGS":
        RNGS_layout = pw64_lib.RNGS_layout
        upwt_io.write(RNGS_template)

        # We likely have more than one ring so lets make a buffer for it
        rngs_stack = io.BytesIO()

        ring_count  = decoded_data["COMM"]["RNGS"]

        if  ring_count >= 1:
            for ring_num in range(1, ring_count + 1):
                ring_num = str(ring_num)
                upwt_io.seek(0)
                # Go through our structure and populate the template, convert all floats back to hex
                upwt_io.seek(RNGS_layout["x"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ring_num]["x"]))
                upwt_io.seek(RNGS_layout["z"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ring_num]["z"]))
                upwt_io.seek(RNGS_layout["y"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ring_num]["y"]))
                upwt_io.seek(RNGS_layout["yaw"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ring_num]["yaw"]))
                upwt_io.seek(RNGS_layout["pitch"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ring_num]["pitch"]))
                upwt_io.seek(RNGS_layout["roll"], 0)
                upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk][ring_num]["roll"]))
                upwt_io.seek(RNGS_layout["size"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["size"]))
                upwt_io.seek(RNGS_layout["state"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["state"]))
                upwt_io.seek(RNGS_layout["motion_axis"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["motion_axis"]))
                upwt_io.seek(RNGS_layout["motion_rad_start"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["motion_rad_start"]))
                upwt_io.seek(RNGS_layout["motion_rad_end"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["motion_rad_end"]))
                upwt_io.seek(RNGS_layout["rotation"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["rotation"]))
                upwt_io.seek(RNGS_layout["rotation_speed"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["rotation_speed"]))
                upwt_io.seek(RNGS_layout["ring_special"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["ring_special"]))
                upwt_io.seek(RNGS_layout["next_ring_unknown"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["next_ring_unknown"]))
                upwt_io.seek(RNGS_layout["next_ring_order_count"], 0)
                upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["next_ring_order_count"]))

                if int(decoded_data[chunk][ring_num]["next_ring_order_count"], 16) >= 1:
                    for ring_index in range(0, int(decoded_data[chunk][ring_num]["next_ring_order_count"], 16)):
                        upwt_io.seek(RNGS_layout["next_ring_index"][ring_index], 0)
                        upwt_io.write(bytes.fromhex(decoded_data[chunk][ring_num]["next_ring_index"][str(ring_index)]))
                else:
                    # This is a new one I found out while writing this tool...
                    # There seems to be form of list of rings to clear in order in some tasks. Sometimes its linear, sometimes there's choices.
                    # Prior to reading the next ring we have to clear the current/old index data of the "available" rings.
                    # Otherwise the next ring (even if it has 0 for the count) will re-use the RNGS_template with the previous ring's ring count.
                    # Im so tired and not sure why this works... but it will probably break for any level other than E_GC_1
                    # This will need attention later for sure.
                    upwt_io.seek(RNGS_layout["next_ring_index"][ring_index], 0)
                    upwt_io.write(bytes.fromhex("00000000"))


                # Add to our stack
                rngs_stack.seek(0, 2)
                upwt_io.seek(0, 0)
                rngs_stack.write(upwt_io.read())

        # For some reason theres another 0x4 bytes at the end of the RNGS chunk...
        rngs_stack.seek(0, 2)
        rngs_stack.write(b'\x00\x00\x00\x00')

        # Seek to start of rngs_stack, then dump the whole ring stack to a var for return
        rngs_stack.seek(0, 0)
        #upwt_io.seek(0, 0)
        ring_data = rngs_stack.read()
        rngs_stack.close()

        print("* UPWT data chunk(s) rebuilt: %s" % chunk)

        return ring_data

    if chunk == "TPAD" or chunk == "LSTP":
        upwt_io.seek(0)
        # Go through our structure and populate the template, convert all floats back to hex
        upwt_io.seek(XPAD_layout["x"], 0)
        upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk]["x"]))
        upwt_io.seek(XPAD_layout["z"], 0)
        upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk]["z"]))
        upwt_io.seek(XPAD_layout["y"], 0)
        upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk]["y"]))
        upwt_io.seek(XPAD_layout["yaw"], 0)
        upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk]["yaw"]))
        upwt_io.seek(XPAD_layout["roll"], 0)
        upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk]["roll"]))
        upwt_io.seek(XPAD_layout["pitch"], 0)
        upwt_io.write(pw64_lib.float_to_hex(decoded_data[chunk]["pitch"]))

    # If we reach here, we return one of the singular objects like TakeOff Pad or Landing Strip.
    upwt_io.seek(0)
    upwt_output_chunk = upwt_io.read()
    upwt_io.close()

    print("* UPWT data chunk(s) rebuilt: %s" % chunk)

    return upwt_output_chunk

def rebuild_comm(filename, comm_data):
    # COMM chunk is *always* 0x430 bytes in size

    # Read in the JSON file and start plugging in data
    with open(filename + ".json", 'r') as json_in:
        data = json_in.read()
        decoded_data = json.loads(data)
    json_in.close()

    COMM_layout = pw64_lib.COMM_layout

    comm_assembler = io.BytesIO()
    comm_assembler.write(comm_data)

    comm_assembler.seek(COMM_layout["pilot_class"], 0)
    comm_assembler.write(bytes.fromhex(decoded_data["COMM"]["pilot_class"]))
    comm_assembler.seek(COMM_layout["vehicle"], 0)
    comm_assembler.write(bytes.fromhex(decoded_data["COMM"]["vehicle"]))
    comm_assembler.seek(COMM_layout["test_number"], 0)
    comm_assembler.write(bytes.fromhex(decoded_data["COMM"]["test_number"]))
    comm_assembler.seek(COMM_layout["level"], 0)
    comm_assembler.write(bytes.fromhex(decoded_data["COMM"]["level"]))
    comm_assembler.seek(COMM_layout["skybox"], 0)
    comm_assembler.write(bytes.fromhex(decoded_data["COMM"]["skybox"]))
    comm_assembler.seek(COMM_layout["snow"], 0)
    comm_assembler.write(bytes.fromhex(decoded_data["COMM"]["snow"]))

    comm_assembler.seek(COMM_layout["wind_WE"], 0)
    comm_assembler.write(pw64_lib.float_to_hex(decoded_data["COMM"]["wind_WE"]))
    comm_assembler.seek(COMM_layout["wind_SN"], 0)
    comm_assembler.write(pw64_lib.float_to_hex(decoded_data["COMM"]["wind_SN"]))
    comm_assembler.seek(COMM_layout["wind_UD"], 0)
    comm_assembler.write(pw64_lib.float_to_hex(decoded_data["COMM"]["wind_UD"]))

    # These get converted from int() to bytes([])
    comm_assembler.seek(COMM_layout["THER"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["THER"]]))
    comm_assembler.seek(COMM_layout["LWND"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["LWND"]]))
    comm_assembler.seek(COMM_layout["TPAD"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["TPAD"]]))
    comm_assembler.seek(COMM_layout["LPAD"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["LPAD"]]))
    comm_assembler.seek(COMM_layout["LSTP"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["LSTP"]]))
    comm_assembler.seek(COMM_layout["RNGS"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["RNGS"]]))
    comm_assembler.seek(COMM_layout["BALS"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["BALS"]]))
    comm_assembler.seek(COMM_layout["TARG"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["TARG"]]))
    comm_assembler.seek(COMM_layout["HPAD"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["HPAD"]]))
    comm_assembler.seek(COMM_layout["BTGT"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["BTGT"]]))
    comm_assembler.seek(COMM_layout["PHTS"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["PHTS"]]))
    comm_assembler.seek(COMM_layout["FALC"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["FALC"]]))
    comm_assembler.seek(COMM_layout["UNKN"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["UNKN"]]))
    comm_assembler.seek(COMM_layout["CNTG"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["CNTG"]]))
    comm_assembler.seek(COMM_layout["HOPD"], 0)
    comm_assembler.write(bytes([decoded_data["COMM"]["HOPD"]]))

    # Rewind and populate the data to return. Yeah I know this can be optimized. Bite me.
    comm_assembler.seek(0)
    final_comm_data = comm_assembler.read()

    print("* COMM data rebuilt.")

    return final_comm_data

def write_final_upwt(test_id, final_upwt_data, addr, new_comm_data_chunk_size, output_rom):
    # We open the ROM in read-only mode, read in the original data from the ROM up to where we want to insert our new data.
    # Open a temp file in write mode, read the ROM up to the insertion address and then insert the BALS bytes we read in previously.
    # Then read in (from old ROM) and write (to temp file) the rest of the ROM.
    # This is a form of "injecting" data into a binary file. Python doesn't have an "insert" mode for writing files...
    # When done writing out this newly munged crap into a temp file, remove the original and rename our temp file back to the OG ROM name.
    # There's probably a better way to do this.

    old_upwt_size = pw64_lib.get_fs_index_and_size_of_task(test_id)[1] - 0x8 - 0x80 # 0x6b8 - FORM Header/Size - Other shit

    with open(PW64_ROM, 'rb') as pw64_rom_first, open("PW64_ROM_TMP.z64", 'wb') as pw64_rom_second:
        pw64_rom_second.write(pw64_rom_first.read(addr)) # Read all the bytes up to where we need to insert our data
        pw64_rom_second.write(final_upwt_data) # Add our newly recompiled UPWT container

        # This is where it gets kinda weird.
        # In the unmodified ROM we seek to the offset at the end of the original UPWT container's address to read then write the rest of the old ROM data to the new ROM.
        pw64_rom_first.seek(old_upwt_size, 1) # OLD: 0x630 == OLD COMM+DATA chunk! 0x6A0 = NEW (with BALS) COMM+DATA. 0x6a0 - 0x630 = 0x70!

        pw64_rom_second.write(pw64_rom_first.read()) # Read in the rest of the data from original ROM and write to temp file

        fs_size_change = len(final_upwt_data) - old_upwt_size
        if fs_size_change > 0:
            pw64_rom_second.flush()
            pw64_rom_second.seek(-fs_size_change, os.SEEK_END)
            pw64_rom_second.truncate()

    pw64_rom_second.close()
    pw64_rom_first.close()

    # Switch our files ... ooh scary.
    os.remove(PW64_ROM)
    os.rename('PW64_ROM_TMP.z64', PW64_ROM)

    print("* New UPWT container chunk injected and ROM resized by %s bytes." % hex(fs_size_change))

def change_some_text(test_id):
    # Yay one more ROM open/write operation!
    # Let's modify the Mission Objective text!
    # NOTE: Right now this only accepts a hardcoded size (0x70 bytes) because I haven't written the support code to modify TABL if you write a longass string.

    pw64_lib.build_adat_layout(PW64_ROM)
    task_message_offset = pw64_lib.adat_layout[test_id + "_M"][1] # 1: Offset

    with open(PW64_ROM, 'r+b') as pw64_rom:
        pw64_rom.seek(task_message_offset, 0)
        data = pw64_lib.encode_adat("Fly through 3 rings and...\nooh look a balloon!", 0x70)
        pw64_rom.write(data)
    pw64_rom.close()

def rebuild_TABL():
# Once we've done our mods and modified the TABL data (i.e. UPWT "file" size),
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

    print("* TABL updated, rebuilt, written out to tempfile, MIO0 re-compressed.")

def inject_TABL():
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
    with open (PW64_ROM, 'r+b') as pw64_rom: #F'ing was using the wrong mode (wb) and it was zeroing all data
        pw64_rom.seek(int(0xDE754), 0)
        with open ("TABL_NEW.mio0", 'rb') as mio0:
            pw64_rom.write(mio0.read()) # File read/write inception.
        mio0.close()
    pw64_rom.close()

    print("* New TABL chunk injected into ROM.")

if __name__== "__main__":
  main()

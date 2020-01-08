#!/usr/bin/env python3
# ADAT indexer

import pw64_lib

PW64_Rom = ""

adat_layout = {}

def main():
    build_adat_layout()

def build_adat_layout():
    # Builds a table of game strings with size and offset in ROM:
    # adat_layout[STRING_ID_ASCII][SIZE, OFFSET]
    # There is no index because the strings seem to be all over the place.
    # Size/Offset are returned as int for easier manipulation upstack (e.g. convert to hex for display or whatever)
    # So the lookup has to be done by a string as such:
    #
    # offset_of_EGC1_message = adat_layout["E_GC_1_M"][1]
    #
    # Again, "_N" is the name of a test/task and "_M" is the mission message/instruction as show in the mission start screen.
    
    # Check if we already have the FS table built, else do it
    if len(pw64_lib.fs_table) == 0:
        pw64_lib.fs_table = pw64_lib.build_fs_table(PW64_Rom)

    # Find our ADAT chunk in the FS 0x35c08c
    for fs_index, fs_attrs in pw64_lib.fs_table.items():
        if fs_attrs[pw64_lib.FS_FILE_TYPE] == "ADAT":
            adat_offset = fs_attrs[pw64_lib.FS_FILE_OFFSET]
            adat_index = fs_index

    print("ADAT (Index: %s) Addr: %s" % (adat_index, adat_offset))

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
                print("%s Marker Size: %s" % (marker.decode(), name_marker_size))
                print("%s Marker ID: %s" % (marker.decode(), name_marker_id))

            elif marker.decode() == "DATA":
                data_marker_size = int.from_bytes(pw64_rom.read(0x4), 'big')
                data_marker_offset_start = pw64_rom.tell()
                print("\t%s Marker Offset: %s" % (marker.decode(), data_marker_offset_start))
                print("\t%s Marker Size: %s" % (marker.decode(), hex(data_marker_size)))

                data_marker_data = pw64_rom.read(data_marker_size)

                adat_layout.update({name_marker_id: [data_marker_size, data_marker_offset_start]})

            if location >= int(pw64_lib.fs_table[adat_index+1][pw64_lib.FS_FILE_OFFSET], 16):
                break

    for thing, thong in adat_layout.items():
        print(thing, thong)


    test_id = "E_GC_1"
    test_title = "_N"
    test_message = "_M"

    print(adat_layout["E_GC_1_M"])
    print(adat_layout[test_id + '_M'])
    print(adat_layout[test_id + test_title])
    print(adat_layout[test_id + test_message])

    print(adat_layout[test_id + test_title][1])
    print(adat_layout[test_id + test_message][1])


            

if __name__== "__main__":
  main()

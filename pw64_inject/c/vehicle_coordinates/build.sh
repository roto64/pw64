#!/bin/bash

# Should'a made a Makefile.

# Need:
#  - armips: https://github.com/Kingcom/armips
#  - n64chain: https://github.com/tj90241/n64chain

# Current $PATH in shell
OLD_PATH=$PATH

function build_all () {
  # This builds us a ROM with some code injected. See pw64.asm.
      
  # Your path where your n64chain (https://github.com/tj90241/n64chain)  stuff lives
  BUILD_TOOLS_PATH="/code/"

  # Limit our paths to MIPS/N64 tools only.
  # Otherwise we have conflicts with GCC dev tools like 'as' in default $PATH
  # Store your n64 toolchain binaries somewhere in these paths or fix this mess yourself (sry).
  export PATH="$BUILD_TOOLS_PATH/n64_bin:$BUILD_TOOLS_PATH/mips64-elf/bin"

  # The "hook" which will check if our code is loaded and run it, or bail.
  mips64-elf-gcc -Wall -O3 -mtune=vr4300 -march=vr4300 -mabi=32 -fomit-frame-pointer -G0 -c hook.c -o hook.o

  # Build it.
  mips64-elf-gcc -Wall -O3 -mtune=vr4300 -march=vr4300 -mabi=32 -fomit-frame-pointer -G0 -c injection_test.c -o injection_test.o

  ##### This section is unnecessary for actual operation
  # For debugging, strip out all ELF/header/symbols/etc
  mips64-elf-objcopy -j .text -O binary injection_test.o injection_test.bin

  # Show us our disassembly for a quick reference
  # Don't freak out about dissaembly showing weird jumps, objdump has no context of RAM addresses....
  # ... or I haven't figured out the right flags.
  mips64-elf-objdump -b binary -m mips:4300 -D -EB injection_test.bin
  #####

  # Do the dirty work (see the ASM file for what actually happens).
  armips pw64.asm
}

function clean_all () {
  # This is what you get for messing with $PATH.
  export PATH=$OLD_PATH
  rm injection_test.bin injection_test.o hook.o
}

function fix_rom_cksum () {
  # To Do
  echo ''
}


build_all
clean_all

exit 0

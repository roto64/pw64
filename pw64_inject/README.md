Testing some SM64-style (https://github.com/shygoo/sm64-c-injection) code injection.

Contains two directories:
asm
c

Obviously depending on the dir this repo has examples of the same thing but with different methods.

What it does:
Overwrites some code that runs during the intro animation sequence to instead load code from ROM (stored in padding bytes section) to RAM and then jump to that code.

What its supposed to show:
The code we load will then show a black screen with some text while music plays in the background (because we never exited the Intro scene cleanly). That's it (for now)!


Tools you need:
  - armips: https://github.com/Kingcom/armips
  - n64chain: https://github.com/tj90241/n64chain


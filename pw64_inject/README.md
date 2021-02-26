Testing some SM64-style (https://github.com/shygoo/sm64-c-injection) code injection.

Contains two directories:
* asm:
    - a simple armips example to show a message on the start screen.
        ![bla](screenshots/injection_test_asm.png?raw=true "ASM Injection Test Screenshot")
* c:
    - injection_test: same as ASM example above but now in C
        ![bla](screenshots/injection_test_c.png?raw=true "C Injection Test Screenshot")
    - intro_banner: prints some text above the PW64 logo on the start screen
        ![bla](screenshots/intro_banner.png?raw=true "Some text on the main title screen.")
    - vehicle_coordinates: prints player's world X/Y/Z coordinates in-game
        ![bla](screenshots/vehicle_coordinates.png?raw=true "Shows Player's X/Y/Z coords in the world.")

Tools you need:
  - armips: https://github.com/Kingcom/armips
  - n64chain: https://github.com/tj90241/n64chain


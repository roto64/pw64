// Tell C we're gonna have some functions somewhere (defined in functions.asm)
extern void drawBoxSetup ();
extern void drawBox (int x1, int x2, int y1, int y2, int unk1, int unk2, int unk3, int opacity);
extern void PrintFatalError( const char* text);
extern void uvGfxEnd ();
extern void uvGfxStatePop ();
extern void uvGfxStatePush ();
extern void uvFontSet ( int font );
extern void uvFontSetScale ( int something, float something2 );
extern void uvFontSetColor (int r, int g, int b, int opacity);
extern void printOnscreenText (int x, int y, const char* text);
extern void textBringToFront ();

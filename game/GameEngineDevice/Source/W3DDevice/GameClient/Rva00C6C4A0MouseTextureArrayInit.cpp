// cl: /O2 /Ob0 /MD /EHsc
// The 50-by-21 mouse-cursor texture table at VA 0x012F8798 as the raw
// TextureClass pointer array the retail image records (stride 4, 1050 cells,
// zero-filled .data extent 4200). ILT110D6 routes to RVA 0044F3C0 (thiscall:
// zero the pointer at +0 and return this) and ILT30652 routes to the existing
// BfmeHandleCX destructor RVA 0005CC00 (null guard and Release_Ref). The
// null constructor below is this TU's only body; the compiler's 39-byte
// initializer (00C6C4A0) and 23-byte atexit cleanup (00C709D0) live in the
// MASM dump game/masm_dumps/Rva00C6C4A0EFunclets.asm, which references the
// table under its recorded name.
class TextureClass;
class BfmeHandleCX
{
public:
    BfmeHandleCX();
    ~BfmeHandleCX();
    TextureClass *rva00000000;
};
TextureClass *g_w3dMouseCursorTextures[50][21];
BfmeHandleCX::BfmeHandleCX()
{
    rva00000000 = 0;
}

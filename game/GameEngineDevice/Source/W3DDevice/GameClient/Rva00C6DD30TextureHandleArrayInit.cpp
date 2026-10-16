// cl: /O2 /Ob0 /MD /EHsc
// Retail initializer 00C6DD30 constructs a one-cell owning texture handle
// array at VA01341148 through the eh vector constructor iterator: stride 4,
// count 1, ctor ILT110D6 -> BfmeHandleCX null constructor 0044F3C0, dtor
// ILT30652 -> BfmeHandleCX destructor 0005CC00, then registers the
// compiler array cleanup 00C70FE0 with atexit. Both are compiler artifacts
// of this native array: _$E1 is the initializer and _$E2 the cleanup.
class TextureClass;
class BfmeHandleCX {
public:
    BfmeHandleCX();
    ~BfmeHandleCX();
    TextureClass *rva00000000;
};
inline BfmeHandleCX::BfmeHandleCX()
{
    rva00000000 = 0;
}
extern "C" BfmeHandleCX bfmeObjDAC[1];
BfmeHandleCX bfmeObjDAC[1];

// cl: /O2 /Ob0 /MD /EHsc
// Retail .CRT initializer 0x00C6DC90 uses the compiler vector constructor
// iterator on VA 0x01338480: stride 4, count 178, ctor 0x00891B40,
// dtor 0x00891B80. Its registered cleanup at 0x00C70F60 passes the same
// array, stride, count and destructor to the vector destructor iterator.
// The constructor's one pointer names the empty block at VA 0x012D5298;
// both routines adjust that block's 16-bit refcount. The
// EAStringC lifetime is fixed by the paired destructor and shared empty block.
// The bfmeObjDAE storage name retains its unresolved array identity.
// Native array lifetime emits COFF _$E1 (initializer) and _$E2 (cleanup);
// ledger object-symbol notes select these TU-local compiler artifacts.
struct Rva00891B80Block;
class EAStringC
{
    Rva00891B80Block *m_block;
public:
    EAStringC();
    ~EAStringC();
};
extern "C" EAStringC bfmeObjDAE[178];
EAStringC bfmeObjDAE[178];

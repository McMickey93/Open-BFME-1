// cl: /DNDEBUG /MD /EHsc
// 0x00841060 -- 25-byte constructor-like initializer: run the matched
// ?bfmeInitTL@BfmeThingTL@@QAEPAV1@PAX@Z at 0x00849970 on `this`, then install
// the stdio_istreambuf vtable 0x0112F27C (proven by the RTTI type descriptor
// 0x012C7BB0 and the constructor store at 0x0084106F per symbols.csv) at +0.
// IDENTITY IS NOT RECOVERED for the owner; the name is derived from the body
// address. The callees are the matched byte-verified rows this call site
// needs and adds nothing to.
//
// WHAT THE BYTES SHOW. The incoming dword is pushed as the callee's argument
// with `this` still in ECX, then the vtable is stored at [this+0] and `this`
// is returned in EAX:
//
//     mov eax,[esp+4] / push esi / push eax / mov esi,ecx /
//     call bfmeInitTL / mov [esi],0x112F27C / mov eax,esi / pop esi / ret 4
//
// The vtable store names the compiler-emitted symbol, the idiom
// ClearNamedValue008CD8E0.cpp uses and for the same reason: retail holds a
// HIGHLOW relocation at 0x0084106F (tools/retail_relocs.py), so the operand is
// a link-time address, and the numeric literal left this file out of the link
// (tools/link_debt.py; link_queue.csv row 18). The bytes are unchanged. The
// constructor return (`this` in EAX) is what separates this from a plain init
// method.

class BfmeThingTL
{
public:
	BfmeThingTL *bfmeInitTL(void *what);
	void *m_bfmeVft;
	void * volatile m_bfmeBaseWhat;
	void * volatile m_bfmeBaseFlag;
};

class Rva00841060Owner
{
public:
	Rva00841060Owner(void *file);

	void *m_vft;
};

// The table the store at +0 stamps is the stdio_istreambuf vftable; this
// declares the compiler-emitted symbol itself, so no linker alias stand-in is
// needed. The array type keeps the decay-to-pointer that retail's
// `mov dword ptr [esi], imm32` needs (a plain int declaration would load the
// table's first slot instead).
extern "C" const char __identifier("??_7stdio_istreambuf@_SgI@@6B@")[];

// ??0Rva00841060Owner@@QAE@PAX@Z
Rva00841060Owner::Rva00841060Owner(void *file)
{
	((BfmeThingTL *)this)->bfmeInitTL(file);
	m_vft = (void *)__identifier("??_7stdio_istreambuf@_SgI@@6B@");
}

// cl: /EHs-c-
// RefHandle008958D0's destructor at retail 0x00784A70 (35 bytes): drop the
// one counted pointer through the out-of-line decrement helper, then hand it
// to bfmeDropA when the count reaches zero.
//
// Identity: the matched parents' unwind funclets (0x00C570B8 for
// Rva00893030Manager::rva00895950, 0x00C570E8 for rva00895A00) destroy their
// RefHandle008958D0 temporaries through ILT 0x000463AD, and that stub jumps
// here; retail was linked without COMDAT folding, so this body is the
// destructor and was previously over-claimed as an opaque cleanup method.
//
// Link: the destructor is inline, so every TU that unwinds a handle emits a
// select-any copy and the linker keeps the first in link order. The Apt TUs
// at 0x00893030.. inline the drop into their copies (their parents need it),
// so this TU, which sits at the body's own retail address, must emit the
// retail form. A non-inline definition here would collide (LNK2005) with
// those select-any copies.

class Rva00894D90Accessor
{
public:
	static unsigned int decrement(unsigned int *value);
};

__declspec(noinline) void bfmeDropA(void *value);

class RefHandle008958D0
{
public:
	__declspec(noinline) ~RefHandle008958D0()
	{
		if (m_value && Rva00894D90Accessor::decrement(m_value) == 0)
			bfmeDropA(m_value);
	}

	unsigned int *m_value;
};

// ?bfme_force_refhandle008958d0_dtor_emission@@YAXPAVRefHandle008958D0@@@Z absent-from-retail
// Emits the select-any destructor COMDAT above; nothing calls it.
void bfme_force_refhandle008958d0_dtor_emission(RefHandle008958D0 *handle)
{
	handle->~RefHandle008958D0();
}

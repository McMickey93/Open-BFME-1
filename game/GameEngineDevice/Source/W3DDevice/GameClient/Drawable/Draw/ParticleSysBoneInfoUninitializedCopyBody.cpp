// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// Open-BFME5: the real out-of-line body of
// __uninitialized_copy<const ParticleSysBoneInfo *, ParticleSysBoneInfo *>.
// ParticleSysBoneInfoUninitializedCopyThunk.cpp claims the 5-byte
// incremental-link thunk that reaches it; this TU carries the body it jumps to.
// The per-element _Construct is DECLARED WITHOUT A BODY so it stays out of
// line, exactly as retail calls it. The generic loop calls _Construct, whose
// pin is the 5-byte ILT at 0x00039F18 (body 0x00768CB0, the count-first
// BFMEPayloadCopyLayout construct) that the 0x00768F60 instantiation uses.
// ParticleSysBoneInfo calls the 5-byte ILT at 0x00044675 (body 0x000A7980: the
// AsciiString plus the trailing dword), pinned in symbols.csv as
// BfmeElementConstruct, so its instantiation is specialised below.

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include/W3DDevice/GameClient/Module/W3DModelDraw.h
struct ParticleSysBoneInfo
{
	int m_raw[2];
};

// The retail body at 0x00768F60 is the same loop over the count-first
// BFMEPayloadCopyLayout (ObjectCreationList.cpp); its _Construct at
// 0x00768CB0 is a different body from the ParticleSysBoneInfo one.
struct BFMEPayloadCopyLayout
{
	int m_raw[2];
};

namespace _STL
{
struct __false_type
{
};

template <class T1, class T2>
void _Construct(T1 *destination, const T2 &value);

void __cdecl BfmeElementConstruct(void *destination, const ParticleSysBoneInfo &value);

template <class In, class Out>
Out __uninitialized_copy(In first, In last, Out result, const __false_type &)
{
	Out current = result;
	while (first != last)
	{
		_Construct(current, *first);
		++first;
		++current;
	}
	return current;
}

template <>
ParticleSysBoneInfo *__uninitialized_copy<const ParticleSysBoneInfo *, ParticleSysBoneInfo *>(
    const ParticleSysBoneInfo *first, const ParticleSysBoneInfo *last, ParticleSysBoneInfo *result, const __false_type &)
{
	ParticleSysBoneInfo *current = result;
	while (first != last)
	{
		BfmeElementConstruct(current, *first);
		++first;
		++current;
	}
	return current;
}

template BFMEPayloadCopyLayout *__uninitialized_copy<const BFMEPayloadCopyLayout *, BFMEPayloadCopyLayout *>(
    const BFMEPayloadCopyLayout *, const BFMEPayloadCopyLayout *, BFMEPayloadCopyLayout *, const __false_type &);
}

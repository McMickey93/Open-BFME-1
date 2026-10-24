// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// Open-BFME5: the real out-of-line body of
// __uninitialized_copy<const W3DAnimationInfo *, W3DAnimationInfo *> at
// retail 0x003AA640. The 5-byte incremental-link thunk at 0x0001D5F7 reaches
// it. Its per-element construct is not the generic _Construct<W3DAnimationInfo>
// that the twin body at 0x00784E70 calls (W3DAnimationInfoUninitializedCopy.cpp):
// retail calls ILT 0x0000927D to the matched _Construct at 0x003A93F0, reached
// through the address-derived payload type exactly as the W3DAnimationInfo
// allocate-and-copy body does. The construct is DECLARED WITHOUT A BODY so it
// stays out of line, exactly as retail calls it.

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include/W3DDevice/GameClient/Module/W3DModelDraw.h
class W3DAnimationInfo
{
public:
	int m_raw[4];
};

struct Gen_t_003a93f0_p16s;

namespace _STL
{
struct __false_type
{
};

template <class First, class Second>
void __cdecl _Construct(First *destination, const Second &value);

template <class In, class Out>
Out __uninitialized_copy(In first, In last, Out result, const __false_type &);

// ??$__uninitialized_copy@PBVW3DAnimationInfo@@PAV1@@_STL@@...
template <>
W3DAnimationInfo *__uninitialized_copy<const W3DAnimationInfo *, W3DAnimationInfo *>(
    const W3DAnimationInfo *first, const W3DAnimationInfo *last,
    W3DAnimationInfo *result, const __false_type &)
{
	W3DAnimationInfo *current = result;
	while (first != last)
	{
		_Construct(reinterpret_cast<Gen_t_003a93f0_p16s *>(current),
			*reinterpret_cast<const Gen_t_003a93f0_p16s *>(first));
		++first;
		++current;
	}
	return current;
}
}

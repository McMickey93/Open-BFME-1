// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// The generic out-of-line __uninitialized_copy<const W3DAnimationInfo *,
// W3DAnimationInfo *> instantiation, byte-identical at retail 0x00784E70
// (the gen-alias dup_00784e70 row). Its per-element construct is the generic
// _Construct<W3DAnimationInfo> retail reaches through ILT 0x00033AAA (body
// 0x00784DD0), which is why this instantiation cannot live in the Body TU:
// the named body at 0x003AA640 retail reaches through ILT 0x0000927D instead
// (body 0x003A93F0, the BfmeElementConstruct pin), so the two copies of the
// same template symbol need one TU each. The _Construct is DECLARED WITHOUT A
// BODY so it stays out of line, exactly as retail calls it.

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include/W3DDevice/GameClient/Module/W3DModelDraw.h
class W3DAnimationInfo
{
public:
	int m_raw[4];
};

namespace _STL
{
struct __false_type
{
};

// No body on purpose: retail calls this out of line, once per element.
template <class T1, class T2>
void _Construct(T1 *destination, const T2 &value);

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

// ??$__uninitialized_copy@PBVW3DAnimationInfo@@PAV1@@_STL@@...
template W3DAnimationInfo *__uninitialized_copy<const W3DAnimationInfo *, W3DAnimationInfo *>(
    const W3DAnimationInfo *, const W3DAnimationInfo *, W3DAnimationInfo *, const __false_type &);
}

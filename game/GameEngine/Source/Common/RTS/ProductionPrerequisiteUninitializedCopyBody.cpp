// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// The out-of-line __uninitialized_copy<const PrereqUnitRec *, PrereqUnitRec *>
// body at 0x003AB7A0 (45B), reached by the 5-byte incremental-link thunk at
// 0x000178B4. Its per-element construct is not the generic _Construct that the
// twin body at 0x005827C0 calls (ProductionPrerequisiteUninitializedCopy.cpp):
// retail calls ILT 0x0003C1A0 (body 0x003AB630), the helper the PrereqUnitRec
// allocate-and-copy body already pins as BfmeElementConstruct. It is DECLARED
// WITHOUT A BODY so it stays out of line.

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/ProductionPrerequisite.h
class ProductionPrerequisite
{
public:
	int m_raw[6];							// 24 bytes

	// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/ProductionPrerequisite.h
	struct PrereqUnitRec
	{
		int m_raw[3];						// 12 bytes
	};
};

namespace _STL
{
struct __false_type
{
};

void __cdecl BfmeElementConstruct(void *destination, const ProductionPrerequisite::PrereqUnitRec &value);

template <class In, class Out>
Out __uninitialized_copy(In first, In last, Out result, const __false_type &);

// ??$__uninitialized_copy@PBUPrereqUnitRec@ProductionPrerequisite@@PAU12@@_STL@@...
template <>
ProductionPrerequisite::PrereqUnitRec *__uninitialized_copy<const ProductionPrerequisite::PrereqUnitRec *, ProductionPrerequisite::PrereqUnitRec *>(
    const ProductionPrerequisite::PrereqUnitRec *first, const ProductionPrerequisite::PrereqUnitRec *last,
    ProductionPrerequisite::PrereqUnitRec *result, const __false_type &)
{
	ProductionPrerequisite::PrereqUnitRec *current = result;
	while (first != last)
	{
		BfmeElementConstruct(current, *first);
		++first;
		++current;
	}
	return current;
}
}

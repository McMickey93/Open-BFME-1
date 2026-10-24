// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// The out-of-line __uninitialized_copy bodies whose per-element construct is
// the pinned direct construct rather than the generic _Construct that the twin
// bodies call (ProductionPrerequisiteUninitializedCopy.cpp):
//
//   0x003AB7A0  45B  __uninitialized_copy<const PrereqUnitRec *, PrereqUnitRec *>
//                     reached by the 5-byte ILT at 0x000178B4; retail calls
//                     ILT 0x0003C1A0 (body 0x003AB630), the helper the
//                     PrereqUnitRec allocate-and-copy body pins as
//                     BfmeElementConstruct. The twin at 0x005827C0 calls the
//                     generic _Construct at ILT 0x00028957 instead.
//
//   0x003ABB40  45B  __uninitialized_copy<const ProductionPrerequisite *,
//                                          ProductionPrerequisite *>
//                     reached by the 5-byte ILT at 0x0001FFEB; retail calls
//                     ILT 0x000027A2 (body 0x003ABAD0), the helper the
//                     ProductionPrerequisite allocate-and-copy body pins as
//                     BfmeProductionPrerequisiteConstruct. The twin at
//                     0x00784DF0 calls the generic _Construct at ILT
//                     0x0003AA26 instead.
//
// Both constructs are DECLARED WITHOUT A BODY so they stay out of line.

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

void __cdecl BfmeProductionPrerequisiteConstruct(void *destination, const ProductionPrerequisite &value);

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

// ??$__uninitialized_copy@PBVProductionPrerequisite@@PAV1@@_STL@@...
template <>
ProductionPrerequisite *__uninitialized_copy<const ProductionPrerequisite *, ProductionPrerequisite *>(
    const ProductionPrerequisite *first, const ProductionPrerequisite *last,
    ProductionPrerequisite *result, const __false_type &)
{
	ProductionPrerequisite *current = result;
	while (first != last)
	{
		BfmeProductionPrerequisiteConstruct(current, *first);
		++first;
		++current;
	}
	return current;
}
}

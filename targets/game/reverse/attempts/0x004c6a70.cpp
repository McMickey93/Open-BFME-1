// ?rva004C6A70@@YA_NXZ
// partial score=0.5676 date=2026-10-27
// ?rva004C6A70@@YA_NXZ
// cl: /DNDEBUG /MD /EHsc
// Retail 0x004C6A70, 37 bytes: SEH frame, mov al,1, no state stores, no locals;
// FuncInfo 0x00E19A68 has two nested states (1->0->-1) with NULL actions and no
// try blocks; the function and its ILT 0x0004063D have no callers, so the ABI is
// unproven. Two nested locals of a class whose destructor is only empty after
// optimisation (if (0) call) keep the frame with zero state stores, but VC7.1 still
// gives them a 4-byte slot (push ecx / mov ecx,[esp+4] / add esp,0x10): 39B vs 37B,
// 12 non-reloc diffs. Retail's NULL actions mean the objects had no storage.
void f004C6A70Sink();
class Late004C6A70
{
public:
	~Late004C6A70() { if (0) f004C6A70Sink(); }
};
bool rva004C6A70()
{
	Late004C6A70 x;
	{
		Late004C6A70 y;
	}
	return true;
}

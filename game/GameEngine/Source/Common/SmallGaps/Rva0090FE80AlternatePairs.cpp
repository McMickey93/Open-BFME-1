// Retail 0x0090FE80: unreferenced strided fill after copyPairsStrided and
// Rva0090FE40ExtractReset. Each destination gets the current pair; a nonzero
// first value becomes 0 and the second value is replaced by its complement,
// a zero one becomes 1. Address-derived name, identity unproven.
struct Rva0090FE80Pair { float m_a; float m_b; };
void rva0090FE80AlternatePairs(void* dst, int stride, float a, float b, int count)
{
	for (; count; --count) {
		((Rva0090FE80Pair*)dst)->m_a = a;
		((Rva0090FE80Pair*)dst)->m_b = b;
		if (a != 0.0f) {
			a = 0.0f;
			b = 1.0f - b;
		} else {
			a = 1.0f;
		}
		dst = (char*)dst + stride;
	}
}

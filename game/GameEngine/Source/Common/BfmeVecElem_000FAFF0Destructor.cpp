// cl: /DNDEBUG /MD /EHsc
//
// The non-virtual destructor of the 96-byte element walked by the vector
// operations at 0x000FAF90 and 0x000FAFF0. Retail 0x000D1690 destroys the
// 28-byte record at +0x44 through the 0x0002671F ILT (whose 0x000CFA40 body is
// the audited opaque Gen_000F9C60 destructor), then releases the AsciiString
// at +0x00 through StringBase<char>::releaseBuffer at 0x00887940. The member
// layout is the one proven by the matched 96-byte Rva000FB210Element vector
// bodies (Rva000FB2E0Insert.cpp).
//
// The old ??1WorkerAIUpdateModuleData@@UAE@XZ pin at this address is false:
// the real WorkerAIUpdateModuleData destructor is the 79-byte 0x00124510 body
// (AudioEventRTS at +0x90, then its base at +0), matched separately.

class BFMERetailAsciiString
{
public:
	~BFMERetailAsciiString() { releaseBuffer(); }

private:
	void releaseBuffer();
	void *m_data;
};

class Gen_000F9C60
{
public:
	~Gen_000F9C60();
};

class BfmeVecElem_000FAFF0
{
public:
	~BfmeVecElem_000FAFF0();

private:
	BFMERetailAsciiString m_name;			// +0x00
	char m_bfmeGap[0x40];				// +0x04
	Gen_000F9C60 m_audioEvent;			// +0x44
};

// ??1BfmeVecElem_000FAFF0@@QAE@XZ
BfmeVecElem_000FAFF0::~BfmeVecElem_000FAFF0()
{
}

// ??_GBfmeVecElem_000FAFF0@@QAEPAXI@Z: the scalar deleting destructor MSVC
// emits alongside the non-virtual destructor. Retail 0xD3E80 calls the
// 0xD1690 destructor through the 0x2C3BD ILT, then operator delete 0x881EB0.
void bfmeDeleteBfmeVecElem_000FAFF0(BfmeVecElem_000FAFF0 *block)
{
	delete block;
}

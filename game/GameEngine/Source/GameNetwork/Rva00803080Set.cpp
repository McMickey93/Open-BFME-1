// cl: /O2 /Ob0

// Retail global at 0x0112C6F4, recorded as ?g_bfmeVftUUA@@3PAPAXA.
// Retail table at VA 0x0112C6F4: 2 slots, ending before 0x0112C6FC.
// Keep each witnessed ILT target symbolic so the table relocates with the image.
extern "C" void __identifier("?update@Rva00803080@@QAEXI@Z")();
extern "C" void __identifier("??_GGen008030A0@@UAEPAXI@Z")();
void *g_bfmeVftUUA[] = {
    reinterpret_cast<void *>(&__identifier("?update@Rva00803080@@QAEXI@Z")),
    reinterpret_cast<void *>(&__identifier("??_GGen008030A0@@UAEPAXI@Z")),
};

class Rva00803080
{
	void *m_00;
	int m_04;
	int m_08;
	int m_0C;
	int m_10;

public:
	Rva00803080 &set(int a);
};

Rva00803080 &Rva00803080::set(int a)
{
	m_04 = a;
	m_00 = (void *)g_bfmeVftUUA;
	m_08 = 0;
	m_0C = 0;
	m_10 = 0;
	return *this;
}

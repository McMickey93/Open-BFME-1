// A ring-buffer push.

class Gen_0024D1E0
{
public:
	void bfmePush(unsigned char value);

private:
	char m_bfmeHead[0x390];					// +0x000
	unsigned char m_bfmeBuffer[8];				// +0x390
	int m_bfmeIndex;					// +0x398
};

// ?bfmePush@Gen_0024D1E0@@QAEXE@Z
void Gen_0024D1E0::bfmePush(unsigned char value)
{
	m_bfmeBuffer[m_bfmeIndex] = value;

	++m_bfmeIndex;

	if (m_bfmeIndex == 8)
		m_bfmeIndex = 0;
}

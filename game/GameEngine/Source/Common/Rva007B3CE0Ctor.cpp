// cl: /O2 /Ob0

// Retail calls the base initializer through ILT 0xAF38 and tail-jumps through
// ILT 0xE9A3. Use their existing row identities with the same this pointer.
class Rva007AEB70State
{
public:
	void initializeFields();
};

class BfmeB1050
{
public:
	void bfmeBase1050();
};

class Rva007B3CE0
{
	char m_pad[0x58];
	int m_58;
	int m_5C;
	float m_60;
	char m_64;

public:
	void initialize();
};

void Rva007B3CE0::initialize()
{
	reinterpret_cast<BfmeB1050 *>(this)->bfmeBase1050();
	m_58 = 0;
	m_5C = 0;
	m_60 = 20.0f;
	m_64 = 0;
	reinterpret_cast<Rva007AEB70State *>(this)->initializeFields();
}

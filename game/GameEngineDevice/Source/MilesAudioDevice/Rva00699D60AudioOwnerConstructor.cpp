// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
// Retail 0x00699CB0 (130 bytes): the element constructor AudioManagerInit
// (0x006B8220) hands to the ??_L vector constructor through ILT 0x000315B6,
// which symbols.csv pins as ??0Rva00699D60AudioOwner@@QAE@XZ. The layout is
// the one the matched destructor 0x00699D60 (Rva00699D60AudioOwnerDestructor.cpp)
// tears down: the holder at +0x08 and the handles at +0x1C/+0x20/+0x24 are the
// unwind states 0, 1 and 2. Field names keep their offsets.

// Unwind state 0 destroys this holder through ILT 0x00008A99, which jumps to
// the matched ??1Rva00691200Holder@@QAE@XZ (0x00691200): the same one-pointer
// holder PlayingAudioConstructor.cpp declares.
class Rva00691200Holder
{
public:
	Rva00691200Holder() : m_pointer(0) {}
	~Rva00691200Holder();

	void *m_pointer;
};

class Rva00690FF0Handle
{
public:
	Rva00690FF0Handle();
	~Rva00690FF0Handle();

	void *m_pointer;
};

class Rva006910F0Handle
{
public:
	Rva006910F0Handle();
	~Rva006910F0Handle();

	void *m_pointer;
};

class Rva00699D60AudioOwner
{
public:
	Rva00699D60AudioOwner(void);

	unsigned char m_byte00;
	unsigned char m_byte01;
	void *m_sample;
	Rva00691200Holder m_child;
	unsigned char m_byte0C;
	int m_field10;
	unsigned char *m_array;
	int m_field18;
	Rva00690FF0Handle m_special;
	Rva006910F0Handle m_ref20;
	Rva006910F0Handle m_ref24;
	int m_field28;
	int m_field2C;
	int m_field30;
	int m_field34;
	int m_field38;
	unsigned char m_byte3C;
};

Rva00699D60AudioOwner::Rva00699D60AudioOwner(void)
	: m_byte00(0),
	  m_byte01(0),
	  m_sample(0),
	  m_byte0C(0),
	  m_field10(0),
	  m_array(0),
	  m_field18(0),
	  m_field28(0),
	  m_field2C(0),
	  m_field30(0),
	  m_field34(0),
	  m_field38(0),
	  m_byte3C(0)
{
}

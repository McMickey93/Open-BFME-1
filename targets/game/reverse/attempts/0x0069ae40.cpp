// ?validate@Rva006B9320Owner@@QAE_NPAURva006B9320Request@@@Z
// partial score=0.6222 date=2026-10-16
// ?validate@Rva006B9320Owner@@QAE_NPAURva006B9320Request@@@Z
// cl: /O2 /EHsc /DNDEBUG /DWIN32 /D_WINDOWS /MD
extern float g_bfmeElapsedScale;

struct Rva006B9320Field
{
	char m_pad00[0x54];
	float m_field54;
};

struct Rva006B9320Target
{
	char m_pad00[0x41];
	bool m_flag41;
	bool m_flag42;
	bool isFlag41() const { return this != 0 && m_flag41; }
	bool isFlag42() const { return this == 0 || m_flag42; }
};

struct Rva006B9320Request
{
	int m_action;
	Rva006B9320Field *m_field;
	void *m_payload;
	Rva006B9320Target *m_target;
	unsigned char m_flag10;
	unsigned char m_flag11;
	bool m_flag12;
	bool m_flag13;
	bool m_flag14;
};

class Rva006B9320Owner
{
public:
	bool validate(Rva006B9320Request *request);
};

static inline bool rva006B9320Flag41(const Rva006B9320Target *target)
{
	return target != 0 && target->m_flag41;
}

static inline bool rva006B9320Flag42(const Rva006B9320Target *target)
{
	return target == 0 || target->m_flag42;
}

bool Rva006B9320Owner::validate(Rva006B9320Request *request)
{
	if (request->m_flag12 || request->m_flag13 || request->m_flag14)
		return false;
	if (request->m_field && request->m_field->m_field54 >= g_bfmeElapsedScale)
		return false;
	if (request->m_target == 0)
		return true;
	if (request->m_target->isFlag41())
		return true;
	if (request->m_target->isFlag42())
		return true;
	return false;
}

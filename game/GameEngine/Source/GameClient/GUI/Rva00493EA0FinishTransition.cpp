// cl: /DNDEBUG /DWIN32 /MD /EHsc

struct Rva00493EA0Payload
{
	unsigned int first;
	unsigned int second;
};

class Rva00493F30TransitionState;
class AsciiString;

// ILT 0x00020C5C reaches the matched stream opener row 0x00494FA0.
class Rva00494EC0EntryView
{
public:
	void rva00494FA0(const AsciiString &name, unsigned int value);
};

class Rva00493EA0Controller
{
public:
	void complete(Rva00493F30TransitionState *owner);
	unsigned char m_padding[0x30];
	unsigned int m_first;
	unsigned int m_second;
};

class Rva00493F30TransitionState
{
friend class Rva00493EA0Controller;
public:
	void finishTransition(void);
private:
	unsigned char m_padding0[0x218];
	Rva00493EA0Controller m_controller;
	unsigned int m_previousFlags;
	Rva00493EA0Payload m_payload;
	unsigned int m_first;
	unsigned int m_second;
	bool m_enabled;
};

void Rva00493EA0Controller::complete(Rva00493F30TransitionState *owner)
{
	unsigned int second = owner->m_second;
	unsigned int first = owner->m_first;
	m_first = first;
	m_second = second;
	((Rva00494EC0EntryView *)this)->rva00494FA0(
		*(const AsciiString *)&owner->m_payload, owner->m_payload.second);
}

void Rva00493F30TransitionState::finishTransition(void)
{
	if (m_enabled)
		m_controller.complete(this);
}

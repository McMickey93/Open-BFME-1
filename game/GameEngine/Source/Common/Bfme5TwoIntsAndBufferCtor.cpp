class Gen003A0410
{
public:
	Gen003A0410(void);
};

// Inline the two zero initializations without emitting a competing constructor.
// Cleanup names the verified complete destructor at 0x0039D550.
class AttributeHandleStandIn
{
public:
	__declspec(dllimport) __forceinline AttributeHandleStandIn(void) : m_bfmeValue(0) {}
	~AttributeHandleStandIn(void);

private:
	int m_bfmeValue;
};

class Gen_00581ED0
{
public:
	Gen_00581ED0(void);

private:
	AttributeHandleStandIn m_bfme00;
	AttributeHandleStandIn m_bfme04;
	Gen003A0410 m_bfme08;
};

// ??0Gen_00581ED0@@QAE@XZ
Gen_00581ED0::Gen_00581ED0(void)
{
}

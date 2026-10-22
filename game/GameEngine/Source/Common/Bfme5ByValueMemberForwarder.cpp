// Retail 0x0057ED70 forwards a 24-byte preference copy to the profile at +0x390.
// Constructor 0x0057ECF0 owns that copy; apply at 0x005674F0 takes the
// same six stack words as SkirmishPreferences. The member-pointer ABI view
// keeps those words in the outgoing argument slot, without another temporary.
// The final screen refresh is the rowed levelBar at 0x0057C340.

class Gen_0057ECF0
{
public:
	Gen_0057ECF0(const Gen_0057ECF0 &other);
	~Gen_0057ECF0(void);

private:
	int m_bfmeValues[6];
};

class SkirmishPreferences;

class Rva005674F0Profile
{
public:
	void apply(SkirmishPreferences value);

private:
	char m_bfmeFields[0x1C];
};

class BfmeAptScreenSkirmish
{
public:
	void levelBar();
};

class Gen_0057ED70
{
public:
	void bfmeForward(void);

private:
	char m_bfme00[0x390];
	Rva005674F0Profile m_bfmeConsumer;
	Gen_0057ECF0 m_bfmeArgument;
};

// ?bfmeForward@Gen_0057ED70@@QAEXXZ
void Gen_0057ED70::bfmeForward(void)
{
	// The 24-byte argument is copied by the rowed constructor before the call.
	typedef void (Rva005674F0Profile::*Apply)(Gen_0057ECF0);
	Apply apply = reinterpret_cast<Apply>(&Rva005674F0Profile::apply);
	(m_bfmeConsumer.*apply)(m_bfmeArgument);
	reinterpret_cast<BfmeAptScreenSkirmish *>(this)->levelBar();
}

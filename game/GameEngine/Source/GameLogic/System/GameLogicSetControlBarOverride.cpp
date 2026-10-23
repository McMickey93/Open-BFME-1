// readable body of ?setControlBarOverride@GameLogic@@QAEXABVAsciiString@@HPBVCommandButton@@@Z: game/GameEngine/Source/GameLogic/System/GameLogic.cpp
#include <string.h>

class CommandButton;

extern const char g_NAMEKEY_empty_string;

struct BfmeAsciiStringBuffer
{
	char header[8];
	char data[1];
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/AsciiString.h

// Retail inlines this wrapper into StringBase<char> directly; declare just the
// StringBase<char> members it reaches (see build/whatif/wrapfix.py).
template <class T> class StringBase
{
	friend class AsciiString;
	friend class UnicodeString;
public:
	void set(const StringBase<T> &other);
private:
	void releaseBuffer();
};
class AsciiString
{
public:
	AsciiString(const char *text);
	~AsciiString() { ((StringBase<char> *)this)->releaseBuffer(); }

	const char *str() const
	{
		return buffer != 0 ? buffer->data : &g_NAMEKEY_empty_string;
	}

private:
	BfmeAsciiStringBuffer *buffer;
};

class ControlBarOverrideMapABI
{
public:
	const CommandButton *&findOrInsert(const AsciiString &key);
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/GameLogic.h
class GameLogic
{
private:
	char pad[0x20];
	ControlBarOverrideMapABI controlBarOverrides;

public:
	void setControlBarOverride(const AsciiString &commandSetName, int slot,
		const CommandButton *commandButton);
};

void GameLogic::setControlBarOverride(const AsciiString &commandSetName, int slot,
	const CommandButton *commandButton)
{
	char buffer[256];
	buffer[0] = '0' + slot;
	strcpy(&buffer[1], commandSetName.str());
	AsciiString key(buffer);
	controlBarOverrides.findOrInsert(key) = commandButton;
}

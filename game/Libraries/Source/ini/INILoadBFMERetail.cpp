// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/ini

#include <string.h>
#include "Common/AsciiString.h"
#include "Common/INIException.h"

// The five-argument load's parameters keep their established spelling.
class BFMERetailAsciiString : public AsciiString
{
public:
	BFMERetailAsciiString(const char *text) : AsciiString(text) {}
	BFMERetailAsciiString(const BFMERetailAsciiString &other) : AsciiString(other) {}
};

class RetailLayoutString
{
public:
	void set(const char *text, int length);
	const char *str() const { return m_text ? m_text + 8 : ""; }
	RetailLayoutString &operator=(const char *text)
	{
		set(text, strlen(text));
		return *this;
	}

private:
	char *m_text;
};

class Xfer;

enum INILoadType
{
	INI_LOAD_INVALID
};

class INILineBuffer
{
public:
	void clear();

private:
	char m_storage[0x14];
};

class INI
{
public:
	bool load(BFMERetailAsciiString file, BFMERetailAsciiString block,
		BFMERetailAsciiString name, int loadType, int reload);
	void load(AsciiString filename, int loadType, Xfer *pXfer,
		void (*parse)(INI *ini));

protected:
	void prepFile(BFMERetailAsciiString file, int loadType);
	void prepFile(AsciiString file, INILoadType loadType);
	void readLine();
	void parseLine(BFMERetailAsciiString file);
	inline void unPrepFile();

private:
	void *m_file;
	RetailLayoutString m_filename;
	unsigned m_lineNum;
	unsigned m_lineCount;
	char m_buffer[0x404];
	const char *m_seps;
	const char *m_sepsPercent;
	const char *m_sepsColon;
	const char *m_sepsQuote;
	const char *m_blockEndToken;
	const char *m_endScriptToken;
	unsigned char m_endOfFile;
	char m_curBlockStart[0x404];
	char m_padding[3];
	INILineBuffer m_lines;
};

static void *g_Va0130CE54 = 0;
extern void setFPMode();
extern bool __cdecl rva00851BF0(BFMERetailAsciiString block,
	BFMERetailAsciiString name, const char *line);

inline void INI::unPrepFile()
{
	m_lines.clear();
	m_filename = "None";
	m_lineNum = 0;
	m_lineCount = 0;
	m_endOfFile = 0;
	g_Va0130CE54 = 0;
}

bool INI::load(BFMERetailAsciiString file, BFMERetailAsciiString block,
	BFMERetailAsciiString name, int loadType, int reload)
{
	setFPMode();
	g_Va0130CE54 = (void *)reload;
	prepFile(file, loadType);
	bool eof = false;

	try
	{
		while (m_endOfFile == eof)
		{
			readLine();
			if (rva00851BF0(block, name, m_buffer))
			{
				parseLine(file);
				return true;
			}
		}
	}
	catch (...)
	{
		unPrepFile();
		throw;
	}

	unPrepFile();
	return eof;
}

// Retail 0x00853CB0 (394 B to its first outer catch; ret 0x10 at 0x00853EBD).
// BFME's loader for files whose blocks all share one parser (Video.ini, the
// subtitle files): the parser arrives as the fourth argument and parseLine's
// dispatch is written inline, so a missing parser is reported exactly like an
// unknown block keyword. Callers VideoPlayer::init (0x0081CB30) and
// MapCache::loadStandardMaps (0x004507A0); body and identity evidence in
// targets/game/reverse/identity_evidence/00853cb0-ini-callback-load.md.
//
// The first inner catch reads the file name and both exception fields into
// locals before it throws; as one argument list MSVC pushes the name as soon
// as it has it and every catch block comes out with its registers rotated.
void INI::load(AsciiString filename, int loadType, Xfer *pXfer,
	void (*parse)(INI *ini))
{
	setFPMode();

	g_Va0130CE54 = pXfer;
	prepFile(filename, (INILoadType)loadType);

	try
	{
		while (m_endOfFile == 0)
		{
			readLine();

			const char *token = strtok(m_buffer, m_seps);
			if (token)
			{
				if (parse)
				{
					strcpy(m_curBlockStart, m_buffer);
					try
					{
						(*parse)(this);
					}
					catch (INIException &e)
					{
						const char *file = m_filename.str();
						char *message = e.mFailureMessage;
						int argCount = e.m_argCount;
						throw INIException(argCount,
							"%s\n\nError parsing INI block '%s' in file '%s'.",
							message, token, file);
					}
					catch (...)
					{
						throw INIException(8,
							"Unknown error parsing INI block '%s' in file '%s'.",
							token, m_filename.str());
					}
					strcpy(m_curBlockStart, "NO_BLOCK");
				}
				else
				{
					throw INIException(5,
						"Unknown block '%s'.\n\nError parsing INI block '%s' in file '%s'.",
						token, token, m_filename.str());
				}
			}
		}
	}
	catch (INIException &e)
	{
		throw INIException(e.m_argCount, e.mFailureMessage);
	}
	catch (...)
	{
		unPrepFile();
		throw;
	}

	unPrepFile();
}

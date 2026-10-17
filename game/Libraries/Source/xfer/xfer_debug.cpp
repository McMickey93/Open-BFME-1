// cl: /DNDEBUG /MD /O2
// Clean C++ conversion of the raw-byte formatter at retail RVA 0x009D9220.
extern "C" void __cdecl bfmeAppend(void *stream, const char *format, ...);

class XferSaveAsText
{
public:
	XferSaveAsText *XferRawBytes(const void *data, unsigned int length);

private:
	unsigned char m_pad[4];
	bool m_pending;
};

XferSaveAsText *XferSaveAsText::XferRawBytes(const void *data, unsigned int length)
{
	if (length != 0 && data == 0)
		return this;

	if (m_pending)
	{
		bfmeAppend(this, "\n");
		m_pending = false;
	}

	if (length == 0)
	{
		bfmeAppend(this, 0);
		bfmeAppend(this, "--- 0 raw bytes\n");
		return this;
	}

	for (unsigned int row = 0; row < length; row += 16)
	{
		bfmeAppend(this, 0);
		bfmeAppend(this, "%04x", row);

		for (unsigned int col = 0; col < 16; ++col)
		{
			if ((col & 7) == 0)
				bfmeAppend(this, " ");

			if (col + row < length)
				bfmeAppend(this, " %02x", static_cast<unsigned int>(static_cast<const unsigned char *>(data)[col + row]));
			else
				bfmeAppend(this, "   ");
		}

		bfmeAppend(this, "  ");

		for (unsigned int col = 0; col < 16 && col + row < length; ++col)
		{
			unsigned char raw = static_cast<const unsigned char *>(data)[col + row];
			bfmeAppend(this, "%c",
				raw > 0x20 ? raw : '.');
		}

		bfmeAppend(this, "\n");
	}

	return this;
}

// Retail 0x009D9160 (26 B): a file-static indent writer that sends one tab per level to
// the stream's virtual write (slot +0x10). Every retail use is inlined (no direct caller),
// so it keeps an address-derived name; as a file-static it takes the level count in EAX
// and the stream in ESI, retail's private convention.
class Rva009D9160Stream
{
public:
	virtual void slot00();
	virtual void slot04();
	virtual void slot08();
	virtual void slot0C();
	virtual void write(const char *text, int length);
};

// ?rva009D9160@@YAXHPAVRva009D9160Stream@@@Z
static __declspec(noinline) void rva009D9160(int levels, Rva009D9160Stream *stream)
{
	for (; levels != 0; --levels)
		stream->write("\t", 1);
}

// ?rva009D9160Caller@@YAXHPAVRva009D9160Stream@@@Z absent-from-retail TU-local caller that
// keeps the static above alive.
void rva009D9160Caller(int levels, Rva009D9160Stream *stream)
{
	rva009D9160(levels, stream);
}

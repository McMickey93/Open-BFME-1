// cl: /EHs-c-
//
// APT queued-primitive submit at 0x007874F0 (191 B, cdecl): beside the flush at
// 0x00785FD0 (Rva00785FD0AptFlush.cpp), which it calls directly. The source's
// item (vtable +0x08) gets the current 2x3 transform at 0x0130692C; mode 1
// appends it to the 0x01306978 queue, mode -1 removes it unless the queue is
// empty (both set the dirty byte 0x01306950), and mode 0 or an empty removal
// flushes the queue and cleans the item up. The queue's push_back/remove are
// reached through ILTs 0x0002D0D8/0x00040BC4 (address-derived pins).
//
// Shape: retail keeps the item in ESI and a copy in its one frame slot for the
// queue calls (a separate `queued` local), and lays the modes out as a switch.

struct Rva007845D0Transform
{
	int m_words[6];
};

class Rva00785FD0Item
{
public:
	void cleanup();

	unsigned char m_unreconstructed_000[0x10];
	Rva007845D0Transform m_transform;			// +0x10
};

class Rva007874F0Source
{
public:
	virtual void slot00();
	virtual void slot04();
	virtual Rva00785FD0Item *getItem();			// +0x08
};

struct RvaListNode;

// The queue object at 0x01306978 (data row type RvaList); its list methods are
// address-derived until the element type is known.
class Rva01306978Queue
{
public:
	void push_back(Rva00785FD0Item *const &item);
	void remove(Rva00785FD0Item *const &item);
	bool empty() const { return *(RvaListNode *const *)m_node == m_node; }

	RvaListNode *m_node;
	int m_pad[2];
};

class RvaList : public Rva01306978Queue
{
};

class Rva00785FD0Renderer;

extern char g_rva00785FD0Dirty;
extern Rva00785FD0Renderer *g_rva00785FD0Renderer;
extern RvaList g_rva01306978Object;
extern Rva007845D0Transform g_Rva00F0692CTransform;

void rva00785FD0Flush();

void rva007874F0Submit(Rva007874F0Source *source, int mode)
{
	if (!g_rva00785FD0Renderer || !source)
		return;

	Rva00785FD0Item *item = source->getItem();
	Rva00785FD0Item *queued = item;
	if (!item)
		return;

	item->m_transform = g_Rva00F0692CTransform;
	switch (mode)
	{
	case 1:
		g_rva01306978Object.push_back(queued);
		g_rva00785FD0Dirty = 1;
		return;
	case -1:
		if (!g_rva01306978Object.empty())
		{
			g_rva01306978Object.remove(queued);
			g_rva00785FD0Dirty = 1;
			return;
		}
	case 0:
		break;
	default:
		return;
	}
	rva00785FD0Flush();
	item->cleanup();
}

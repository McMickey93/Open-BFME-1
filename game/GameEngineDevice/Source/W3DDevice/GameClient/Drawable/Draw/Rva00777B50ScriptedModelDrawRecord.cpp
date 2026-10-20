// cl: /DNDEBUG /DWIN32 /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport
// Open-BFME: retail 0x00777B50 (350 bytes, thiscall, ret 0x10), a
// W3DScriptedModelDraw.cpp body: its three GameClientRandomValue calls name
// that file (lines 8737-8739). It builds one 32-byte record (a ref-counted
// object, a bone name, an optional random offset and a value), registers the
// object with the global at 0x012F8058 and appends the record to the vector at
// +0x130. No caller or vtable proves the method's name, so it keeps the
// address.

#include <string>
#include <vector>

typedef int Int;
typedef float Real;
typedef bool Bool;

int GetGameClientRandomValue(int lo, int hi, char *file, int line);

class Rva00777B50RefObject
{
public:
	void *m_vtbl;
	Int m_refCount;
};

// The record is the gen-tgrid vector payload Gen_t_00776080_p32cd; its
// destructor is the shared out-of-line 0x00769D90.
struct Gen_t_00776080_p32cd
{
	Rva00777B50RefObject *m_object;
	_STL::string m_boneName;
	Real m_offsetX;
	Real m_offsetY;
	Real m_offsetZ;
	Int m_value;
};

class GameLODManager
{
public:
	char m_pad0000[0x16c4];
	Int m_16c4;
};
extern GameLODManager *TheGameLODManager;

class BfmeGlobPB
{
public:
	virtual void vslot00();
	virtual void vslot04();
	virtual void vslot08(Rva00777B50RefObject *object);
};
extern BfmeGlobPB *g_bfmeGlobPB;

class Rva00777B50RenderObj
{
public:
	virtual void vslot000();
	virtual void vslot004();
	virtual void vslot008();
	virtual void vslot00C();
	virtual void vslot010();
	virtual void vslot014();
	virtual void vslot018();
	virtual void vslot01C();
	virtual void vslot020();
	virtual void vslot024();
	virtual void vslot028();
	virtual void vslot02C();
	virtual void vslot030();
	virtual void vslot034();
	virtual void vslot038();
	virtual void vslot03C();
	virtual void vslot040();
	virtual void vslot044();
	virtual void vslot048();
	virtual void vslot04C();
	virtual void vslot050();
	virtual void vslot054();
	virtual void vslot058();
	virtual void vslot05C();
	virtual void vslot060();
	virtual void vslot064();
	virtual void vslot068();
	virtual void vslot06C();
	virtual void vslot070();
	virtual void vslot074();
	virtual void vslot078();
	virtual void vslot07C();
	virtual void vslot080();
	virtual void vslot084();
	virtual void vslot088();
	virtual void vslot08C();
	virtual void vslot090();
	virtual void vslot094();
	virtual void vslot098();
	virtual void vslot09C();
	virtual void vslot0A0();
	virtual void vslot0A4();
	virtual void vslot0A8();
	virtual void vslot0AC();
	virtual void vslot0B0();
	virtual void vslot0B4();
	virtual void vslot0B8();
	virtual void vslot0BC();
	virtual void vslot0C0();
	virtual Int vslot0C4(const char *boneName);
};

class Rva00777B50Owner
{
public:
	void rva00777B50(Rva00777B50RefObject *object, const char *boneName, Bool randomOffset, Int value);

	char m_pad000[0x34];
	Rva00777B50RenderObj *m_renderObject;	///< +0x34
	char m_pad038[0x130 - 0x38];
	_STL::vector<Gen_t_00776080_p32cd> m_records;	///< +0x130
};

void Rva00777B50Owner::rva00777B50(Rva00777B50RefObject *object, const char *boneName, Bool randomOffset, Int value)
{
	if (TheGameLODManager && TheGameLODManager->m_16c4 <= 2)
		return;
	if (!object)
		return;
	if (!boneName)
		return;
	if (!m_renderObject)
		return;
	if (!m_renderObject->vslot0C4(boneName))
		return;

	Gen_t_00776080_p32cd record;
	record.m_object = object;
	++record.m_object->m_refCount;
	record.m_boneName = boneName;
	if (randomOffset)
	{
		record.m_offsetX = (Real)GetGameClientRandomValue(-3, 3, "F:\\bfme\\Code\\gameenginedevice\\Source\\W3DDevice\\GameClient\\Drawable\\W3DScriptedModelDraw.cpp", 0x2221);
		record.m_offsetY = (Real)GetGameClientRandomValue(-3, 3, "F:\\bfme\\Code\\gameenginedevice\\Source\\W3DDevice\\GameClient\\Drawable\\W3DScriptedModelDraw.cpp", 0x2222);
		record.m_offsetZ = (Real)GetGameClientRandomValue(-3, 3, "F:\\bfme\\Code\\gameenginedevice\\Source\\W3DDevice\\GameClient\\Drawable\\W3DScriptedModelDraw.cpp", 0x2223);
	}
	else
	{
		record.m_offsetX = 0;
		record.m_offsetY = 0;
		record.m_offsetZ = 0;
	}
	record.m_value = value;
	g_bfmeGlobPB->vslot08(record.m_object);
	m_records.push_back(record);
}

class Object {};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/GameLogic.h
class GameLogic
{
public:
	Object *findObjectByID(int id);
	void destroyObject(Object *object);
};

extern GameLogic *TheGameLogic;

class BfmeDestroyable
{
public:
	virtual void bfmeDestroy(int deleting);
};

class BfmeModuleInterface
{
public:
#define BFME_MODULE_SLOT(n) virtual void slot##n();
	BFME_MODULE_SLOT(00) BFME_MODULE_SLOT(01) BFME_MODULE_SLOT(02) BFME_MODULE_SLOT(03)
	BFME_MODULE_SLOT(04) BFME_MODULE_SLOT(05) BFME_MODULE_SLOT(06) BFME_MODULE_SLOT(07)
	BFME_MODULE_SLOT(08) BFME_MODULE_SLOT(09) BFME_MODULE_SLOT(10) BFME_MODULE_SLOT(11)
	BFME_MODULE_SLOT(12) BFME_MODULE_SLOT(13) BFME_MODULE_SLOT(14) BFME_MODULE_SLOT(15)
	BFME_MODULE_SLOT(16) BFME_MODULE_SLOT(17) BFME_MODULE_SLOT(18) BFME_MODULE_SLOT(19)
	BFME_MODULE_SLOT(20) BFME_MODULE_SLOT(21) BFME_MODULE_SLOT(22) BFME_MODULE_SLOT(23)
	BFME_MODULE_SLOT(24) BFME_MODULE_SLOT(25) BFME_MODULE_SLOT(26) BFME_MODULE_SLOT(27)
	BFME_MODULE_SLOT(28) BFME_MODULE_SLOT(29)
#undef BFME_MODULE_SLOT
	virtual BfmeDestroyable *bfmeFind();
};

class Gen_0028CF50
{
public:
	void bfmeRelease(void);

private:
	char m_bfmeFields[0x24];
	int m_bfmeObjectID;
};

// Walks the owner's behavior modules (Object+0x1F0) and returns the first non-null
// result of BehaviorModuleInterface slot +0x78. File-static: MSVC gives it the private
// convention retail uses, with the owner object arriving in EAX.
static __declspec(noinline) BfmeDestroyable *bfmeFindModule(Object *obj)
{
	for (char **u = *reinterpret_cast<char ***>(reinterpret_cast<char *>(obj) + 0x1F0); *u; ++u) {
		BfmeDestroyable *found = reinterpret_cast<BfmeModuleInterface *>(*u + 0xC)->bfmeFind();
		if (found)
			return found;
	}
	return 0;
}

// Retail 0x0028CF30 (24 B): looks the object up by ID and tail-calls the module scan.
// Every retail use is inlined (no direct caller), so it keeps an address-derived name;
// as a file-static it takes the ID in EAX like retail.
static __declspec(noinline) BfmeDestroyable *rva0028CF30(int id)
{
	Object *object = TheGameLogic->findObjectByID(id);
	if (object)
		return bfmeFindModule(object);
	return 0;
}

// ?rva0028CF30Caller@@YAPAVBfmeDestroyable@@H@Z absent-from-retail TU-local caller that
// keeps the static above alive.
BfmeDestroyable *rva0028CF30Caller(int id)
{
	return rva0028CF30(id);
}

// ?bfmeRelease@Gen_0028CF50@@QAEXXZ
void Gen_0028CF50::bfmeRelease(void)
{
	if (m_bfmeObjectID != 0) {
		Object *object = TheGameLogic->findObjectByID(m_bfmeObjectID);
		if (object != 0) {
			BfmeDestroyable *module = bfmeFindModule(object);
			if (module != 0) {
				module->bfmeDestroy(0);
				TheGameLogic->destroyObject(object);
			}
		}
		m_bfmeObjectID = 0;
	}
}

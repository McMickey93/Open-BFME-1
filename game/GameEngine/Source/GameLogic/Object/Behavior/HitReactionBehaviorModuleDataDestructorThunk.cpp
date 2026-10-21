// cl: /DNDEBUG /MD /EHsc
// HitReactionBehaviorModuleData destructor, retail 0x00291EB0 (80 bytes).
// Both four-byte members call ILT 0x0001A401 -> 0x0039D550, the matched
// AttributeHandleStandIn destructor. They are not WWLib Buffer objects
// (12 bytes, destructor 0x009E1E30); the old Buffer pin hid that collision.

class AttributeHandleStandIn
{
public:
	~AttributeHandleStandIn();
private:
	unsigned char m_pad[4];
};

class HitReactionBehaviorModuleDataBase
{
public:
	virtual ~HitReactionBehaviorModuleDataBase() {}
private:
	unsigned char m_pad[0x14];
};

class __declspec(novtable) HitReactionBehaviorModuleData : public HitReactionBehaviorModuleDataBase
{
public:
	virtual ~HitReactionBehaviorModuleData();
private:
	AttributeHandleStandIn m_a;
	AttributeHandleStandIn m_b;
};

// ??1HitReactionBehaviorModuleData@@UAE@XZ
HitReactionBehaviorModuleData::~HitReactionBehaviorModuleData()
{
}

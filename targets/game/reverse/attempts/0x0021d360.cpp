// ?method@Rva0021D360Owner@@QAEXPAVObject@@@Z
// partial score=0.3306 date=2026-10-20
// cl: /O2 /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport
#include <map>
class Object;
class RvaC4390First;
class RvaC4390Second { public: RvaC4390First *resolve(int); };
class GarrisonContain { public: virtual void onRemoving(Object *); };
class ContestableContain { public: void updateContestStatus(); };
class BfmeSubBDB { public: void bfmeDoBDB(void *, int); };
class Rva0021D360Secondary
{
public:
	virtual void _sec_slot00();
	virtual void _sec_slot01();
	virtual void _sec_slot02();
	virtual void _sec_slot03();
	virtual void _sec_slot04();
	virtual void _sec_slot05();
	virtual void _sec_slot06();
	virtual void _sec_slot07();
	virtual void _sec_slot08();
	virtual void _sec_slot09();
	virtual void _sec_slot10();
	virtual void _sec_slot11();
	virtual void _sec_slot12();
	virtual void _sec_slot13();
	virtual void _sec_slot14();
	virtual void _sec_slot15();
	virtual void _sec_slot16();
	virtual void _sec_slot17();
	virtual void _sec_slot18();
	virtual void _sec_slot19();
	virtual void _sec_slot20();
	virtual void _sec_slot21();
	virtual void _sec_slot22();
	virtual void _sec_slot23();
	virtual void _sec_slot24();
	virtual void _sec_slot25();
	virtual void _sec_slot26();
	virtual void _sec_slot27();
	virtual void _sec_slot28();
	virtual void _sec_slot29();
	virtual void _sec_slot30();
	virtual void _sec_slot31();
	virtual void _sec_slot32();
	virtual void _sec_slot33();
	virtual void _sec_slot34();
	virtual void _sec_slot35();
	virtual void _sec_slot36();
	virtual void _sec_slot37();
	virtual void _sec_slot38();
	virtual void _sec_slot39();
	virtual void _sec_slot40();
	virtual void _sec_slot41();
	virtual void _sec_slot42();
	virtual void _sec_slot43();
	virtual void _sec_slot44();
	virtual void _sec_slot45();
	virtual void _sec_slot46();
	virtual void _sec_slot47();
	virtual void _sec_slot48();
	void unusedRemoving(Object *object);		// +0x48, direct (non-virtual) call to the known thunk
	virtual bool _sec_slotC4();			// +0xC4, unresolved
};

// Primary module (secondary - 0x20): an unresolved no-arg query at +0x6c.
class Rva0021D360Primary
{
public:
	virtual void _pri_slot00();
	virtual void _pri_slot01();
	virtual void _pri_slot02();
	virtual void _pri_slot03();
	virtual void _pri_slot04();
	virtual void _pri_slot05();
	virtual void _pri_slot06();
	virtual void _pri_slot07();
	virtual void _pri_slot08();
	virtual void _pri_slot09();
	virtual void _pri_slot10();
	virtual void _pri_slot11();
	virtual void _pri_slot12();
	virtual void _pri_slot13();
	virtual void _pri_slot14();
	virtual void _pri_slot15();
	virtual void _pri_slot16();
	virtual void _pri_slot17();
	virtual void _pri_slot18();
	virtual void _pri_slot19();
	virtual void _pri_slot20();
	virtual void _pri_slot21();
	virtual void _pri_slot22();
	virtual void _pri_slot23();
	virtual void _pri_slot24();
	virtual void _pri_slot25();
	virtual void _pri_slot26();
	virtual int _pri_slot6c(Object *object);	// +0x6c, unresolved
};


struct ContestableMapEntry { Object *m_object; unsigned char m_count; unsigned char m_pad[3]; };
class Rva0021D360Owner: public Rva0021D360Secondary {
public:
 void method(Object *);
private:
 char m_unreconstructed[0x9a4-4];
 _STL::map<Object *,ContestableMapEntry> m_objectData;
};
void Rva0021D360Owner::method(Object *object)
{
 if (!object) return;
 ((GarrisonContain *)this)->GarrisonContain::onRemoving(object);
 if (!_sec_slotC4()) return;
 Rva0021D360Primary *primary=(Rva0021D360Primary *)((char *)this-0x20);
 Object *related = primary->_pri_slot6c(object) ? (Object *)((RvaC4390Second *)object)->resolve(0) : 0;
 typedef _STL::map<Object *, ContestableMapEntry> ObjectDataMap;
 ObjectDataMap::iterator found = related ? m_objectData.find(related) : m_objectData.find(object);
 if (found != m_objectData.end()) {
  for (ObjectDataMap::iterator it=m_objectData.begin();it!=m_objectData.end();++it) {
   if (it->second.m_object==object || it->second.m_object==related) {
    it->second.m_object=0;
    --found->second.m_count;
   }
   if (!related && it->first==found->second.m_object) --it->second.m_count;
  }
  ((BfmeSubBDB *)primary)->bfmeDoBDB(object,(int)&found);
  ((ContestableContain *)primary)->updateContestStatus();
 }
}

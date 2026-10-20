// ?notify@Gen0002857EOwner@@QAEXPAVGen0002857E@@@Z
// partial score=0.9686 date=2026-10-20
// cl: /O2 /EHsc /DNDEBUG /DWIN32 /D_WINDOWS /MD /D_STLP_USE_STATIC_LIB /Iinputs/reference/shims/stringinline
// stlport
#include "StringInline.h"
#include <set>
extern "C" __declspec(dllimport) unsigned long __stdcall WaitForSingleObject(void*,unsigned long);
extern "C" __declspec(dllimport) int __stdcall ReleaseMutex(void*);
class Rva00691ED0Key {
public:
 Rva00691ED0Key(unsigned,AsciiString);
 unsigned m_primary;
 AsciiString m_name;
};
struct Rva006934C0Key { unsigned m_id; AsciiString m_name; };
namespace _STL { template<> struct less<Rva006934C0Key> {
 bool operator()(const Rva006934C0Key&a,const Rva006934C0Key&b) const;
}; }
typedef _STL::_Rb_tree<Rva006934C0Key,Rva006934C0Key,_STL::_Identity<Rva006934C0Key>,_STL::less<Rva006934C0Key>,_STL::allocator<Rva006934C0Key> > Rva006934C0Tree;
class Gen0002857E {
public:
 AsciiString m_name;
 char m_pad04[0x38-4];
 unsigned m_stamp;
 char m_pad3c[5];
 bool m_active;
};
class Gen0002857EMutexGuard {
public:
 Gen0002857EMutexGuard(void*handle) {
  m_owned=0; m_handle=handle;
  if(WaitForSingleObject(handle,0xffffffff)!=0x102) m_owned=1;
 }
 ~Gen0002857EMutexGuard() { if(m_owned) ReleaseMutex(m_handle); }
private:
 void*m_handle;
 char m_owned;
};
class Gen0002857EOwner {
public:
 void notify(Gen0002857E*self);
 void destroy(Gen0002857E*,int);
private:
 char m_pad20[0x20];
 Rva006934C0Tree m_set;
 char m_pad48[0x48-0x20-sizeof(Rva006934C0Tree)];
 void*m_mutex;
};
void Gen0002857EOwner::notify(Gen0002857E*self) {
 Gen0002857EMutexGuard guard(m_mutex);
 if(self->m_active) {
  Rva00691ED0Key key(self->m_stamp,self->m_name);
  m_set.insert_unique(reinterpret_cast<const Rva006934C0Key&>(key));
 } else destroy(self,1);
}

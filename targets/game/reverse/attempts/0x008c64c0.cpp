// ?Rva008C64C0@@YAPAVAptValue@@PAV1@H@Z
// partial score=0.3149 date=2026-10-20
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
class AptValue
{
public:
 virtual void addRef();
 float toNumber();
 unsigned char undefined() const { return (unsigned char)(~(m_flags >> 15)) & 1; }
 unsigned char isType(unsigned char t) const { unsigned f = m_flags; return (f & 0x3f) == t && !((unsigned char)(~(f >> 15)) & 1); }
 unsigned m_flags;
};
class AptInteger
{
public:
 static AptValue *Create(int value);
};
class BfmeNode1220
{
public:
 int bfmeTest1220(int *name, int flags);
};
struct Rva008AE770Stack { int field00; int field04; AptValue **field08; };
extern Rva008AE770Stack Rva008AE770TheStack;
extern char *Rva008A5380Holder;
extern AptValue *g_bfmeFallbackDB;
struct Rva008C64C0Interval
{
 int m_used;
 AptValue *m_function;
 float m_interval;
 float m_remaining;
 AptValue *m_object;
 int m_argCount;
 int m_field18;
 AptValue **m_args;
};

// ?Rva008C64C0@@YAPAVAptValue@@PAV1@H@Z
#define INTERVALS ((Rva008C64C0Interval *)*(char **)(Rva008A5380Holder + 0x1230))
AptValue *Rva008C64C0(AptValue *, int argCount)
{
 AptValue *first = Rva008AE770TheStack.field08[Rva008AE770TheStack.field00 - 1];
 AptValue *intervalValue = Rva008AE770TheStack.field08[Rva008AE770TheStack.field00 - 2];
 int consumed = 2;
 if (first->undefined())
  return AptInteger::Create(0);
 int count = *(int *)(Rva008A5380Holder + 0x12a4);
 int slot = 0;
 for (; slot < count; ++slot)
 {
  if (INTERVALS[slot].m_used == 0)
  {
   ++*(int *)(Rva008A5380Holder + 0x1234);
   INTERVALS[slot].m_used = 1;
   INTERVALS[slot].m_object = g_bfmeFallbackDB;
   AptValue *function = first;
   unsigned flags = first->m_flags;
   unsigned kind = flags & 0x3f;
   if (!(kind == 10 && !((unsigned char)(~(flags >> 15)) & 1)) && !(kind == 9 && !((unsigned char)(~(flags >> 15)) & 1)))
   {
    intervalValue = Rva008AE770TheStack.field08[Rva008AE770TheStack.field00 - 3];
    function = (AptValue *)((BfmeNode1220 *)first)->bfmeTest1220(
     (int *)((char *)Rva008AE770TheStack.field08[Rva008AE770TheStack.field00 - 2] + 8), 0);
    consumed = 3;
    INTERVALS[slot].m_object = first;
   }
   INTERVALS[slot].m_function = function;
   INTERVALS[slot].m_function->addRef();
   INTERVALS[slot].m_interval = intervalValue->toNumber();
   INTERVALS[slot].m_remaining = INTERVALS[slot].m_interval;
   if (argCount > consumed)
   {
    int extra = argCount - consumed;
    for (int i = 0; i < extra; ++i)
    {
     AptValue *arg = Rva008AE770TheStack.field08[Rva008AE770TheStack.field00 - i - consumed - 1];
     INTERVALS[slot].m_args[INTERVALS[slot].m_argCount] = arg;
     ++INTERVALS[slot].m_argCount;
     arg->addRef();
    }
   }
   return AptInteger::Create(slot);
  }
 }
 return AptInteger::Create(slot);
}

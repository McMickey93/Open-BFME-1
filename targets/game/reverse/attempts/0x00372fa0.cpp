// ?method@Rva00372FA0Owner@@QAEHPBXH_N@Z
// partial score=0.9227 date=2026-10-20
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport
int Rva00372E40(void *, int, const void *, bool);

class Rva00372FA0Owner {
public:
    int method(const void *whatToBuild, int slot, bool flag);
private:
    struct SlotRange { int *begin; int *end; };
    char m_pad00[0x9c];
    int m_state;
    void *m_fieldA0; void *context() const { return m_fieldA0; }
    char m_padA4[0x14];
    SlotRange m_primary;
    char m_padC0[0x1c];
    SlotRange m_secondary;
};

int Rva00372FA0Owner::method(const void *whatToBuild, int slot, bool flag)
{
    if (!whatToBuild) return 0;
    SlotRange *range = &m_primary;
    if (*(const unsigned int *)((const char *)whatToBuild + 0xcc) & 0x80000000u)
        range = &m_secondary;
    if (slot == -2) {
        for (int *entry = range->begin; entry != range->end; ++entry) {
            int result = Rva00372E40(context(), *entry, whatToBuild, flag);
            if (result) return result;
        }
    } else {
        unsigned int count = range->end - range->begin;
        if (count > 0) {
            if ((unsigned int)slot > count - 1) slot = count - 1;
            else if (slot < 0) slot = 0;
            int result = Rva00372E40(context(), range->begin[slot], whatToBuild, flag);
            if (result) return result;
        }
    }
    return 0;
}

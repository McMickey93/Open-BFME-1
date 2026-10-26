// cl: /O2
// 0x007EB6E0: call slot 1 then forward through the result's +0x6A8 member.
class Rva007EB6E0Object
{
public:
    virtual Rva007EB6E0Object *unused0(void);
    virtual Rva007EB6E0Object *advance(void);
    void invoke(void);
private:
    char m_pad0[0x6A4];
    Rva007EB6E0Object *m_next;
};

void Rva007EB6E0Object::invoke(void)
{
    Rva007EB6E0Object *result = advance();
    result->m_next->advance();
}

// 0x007EB6D0: the same chain one slot deeper: call slot 1, then tail-call
// slot 3 of the object held at the result's +0x24. Unreferenced in retail.
class Rva007EB6D0Target
{
public:
    virtual void slot0(void);
    virtual void slot1(void);
    virtual void slot2(void);
    virtual void slot3(void);
};

class Rva007EB6D0Result
{
public:
    char m_pad0[0x24];
    Rva007EB6D0Target *m_target;
};

class Rva007EB6D0Object
{
public:
    virtual void unused0(void);
    virtual Rva007EB6D0Result *result(void);
    void invoke(void);
};

void Rva007EB6D0Object::invoke(void)
{
    Rva007EB6D0Result *value = result();
    value->m_target->slot3();
}

// ?Rva007EB820BoundCallback@@YAXXZ: recorded as ?Rva007EB820@@YAXXZ at 0x00BEB820
void Rva007EB820();

class Rva007EB850Log
{
public:
    Rva007EB850Log();
    virtual void emit();
private:
    void (*m_callback)();
    unsigned int m_fields[3];
};

Rva007EB850Log::Rva007EB850Log()
{
    m_callback = &Rva007EB820;
    for (int i = 0; i < 3; ++i)
        m_fields[i] = 0;
}

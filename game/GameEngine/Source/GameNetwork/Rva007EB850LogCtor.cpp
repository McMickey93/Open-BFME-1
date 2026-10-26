extern "C" int __cdecl printf(const char *, ...);

// 0x007EB820 (13 B): the default output callback the constructor installs.
// Vtable 0x01129D30 slot 1 (0x007EB780) calls it as m_callback(m_08, message),
// cdecl with two arguments; it prints the message through retail printf.
void Rva007EB820PrintMessage(void *context, const char *message)
{
	printf("%s", message);
}

class Rva007EB850Log
{
public:
    Rva007EB850Log();
    virtual void emit();
private:
    void (*m_callback)(void *, const char *);
    unsigned int m_fields[3];
};

Rva007EB850Log::Rva007EB850Log()
{
    m_callback = &Rva007EB820PrintMessage;
    for (int i = 0; i < 3; ++i)
        m_fields[i] = 0;
}

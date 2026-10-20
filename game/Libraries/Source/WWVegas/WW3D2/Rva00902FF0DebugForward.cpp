// cl: /O2 /G7 /arch:SSE /MD /DNDEBUG

// Retail reads the pointer cell at VA 0x01336E5C. Its single verified
// definition is in debug/Rva00F36E5C.cpp; this class is only a caller view.
extern void *g_Rva00F36E5C;

class Rva00902FF0DebugView
{
public:
    virtual void v00(); virtual void v01(); virtual void v02(); virtual void v03();
    virtual void v04(); virtual void v05(); virtual void v06(); virtual void v07();
    virtual void v08(); virtual void v09(); virtual void v10(); virtual void v11();
    virtual void v12(); virtual void v13(); virtual void v14(); virtual void v15();
    virtual void v16(); virtual void v17(); virtual void v18(); virtual void v19();
    virtual void v20(); virtual void v21(); virtual void v22(); virtual void v23();
    virtual void v24(); virtual void v25(); virtual void v26(); virtual void v27();
    virtual void v28(); virtual void v29();
    virtual void slot30(int a, int b, int c);
};

// ?rva00902FF0@@YAXHHH@Z
// Open BFME 2: Code/GameEngine/Source/Common/GapBodiesGE41.cpp
void rva00902FF0(int a, int b, int c)
{
    static_cast<Rva00902FF0DebugView *>(g_Rva00F36E5C)->slot30(a, b, c);
}

// ?bfmeEnd982C0078B4F0@BfmeHub982@@QAEXXZ
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/debug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Igame
// stlport
#define Matrix4x4 Matrix4
#define __PLACEMENT_VEC_NEW_INLINE
#define Vector4 BfmeMatrixRowVector4
#include "Libraries/Source/WWVegas/WW3D2/dx8wrapper.h"
#include "Libraries/Source/WWVegas/WWMath/matrix4.h"
#include "vertmaterial.h"
#undef Vector4

extern int BfmeRenderWidth;
extern int BfmeRenderHeight;
#define RendererDisplayWidth ((unsigned)BfmeRenderWidth)
#define RendererDisplayHeight ((unsigned)BfmeRenderHeight)

struct Rva0078B4F0DX8State : DX8Wrapper
{
    static __forceinline unsigned &dirty() { return render_state_changed; }
    static __forceinline Matrix4 &view() { return render_state.view; }
    static __forceinline Matrix4 &world() { return render_state.world; }
};

// Retail pushes ILT 0x00045561 (Vector4's default constructor) for an unused
// 4x16-byte temporary. The header's Vector4 constructor is __forceinline and
// would let the array disappear, so keep this one out of line. The TU's
// Matrix4 rows use the renamed header type above.
class Vector4
{
public:
    Vector4();
    float X, Y, Z, W;
};

class BfmeHandleCX { void *m_resource; };
class BfmeHub982
{
public:
    void bfmeEnd982C0078B4F0();
private:
    bool m_modeChanged;
    bool m_pendingTextureChange;
    unsigned char m_padding02[2];
    BfmeHandleCX m_texture;
    unsigned m_mode;
    unsigned m_stencilGeneration;
    Matrix4 m_world;
    Matrix4 m_view;
    Matrix4 m_projection;
    DX8VertexBufferClass *m_vertexBuffer;
    unsigned m_vertexOffset;
    unsigned m_vertexCount;
    unsigned m_reserved;
};

// ?bfmeEnd982C0078B4F0@BfmeHub982@@QAEXXZ
void BfmeHub982::bfmeEnd982C0078B4F0()
{
    D3DVIEWPORT8 viewport = {0, 0, RendererDisplayWidth, RendererDisplayHeight, 0.0f, 1.0f};
    DX8Wrapper::Set_Viewport(&viewport);
    const unsigned viewIdentity = 0x80000;

    DX8Wrapper::Get_Transform(D3DTS_VIEW, m_view);
    DX8Wrapper::Get_Transform(D3DTS_PROJECTION, m_projection);
    if (!(Rva0078B4F0DX8State::dirty() & viewIdentity)) {
        Rva0078B4F0DX8State::view().Make_Identity();
        Rva0078B4F0DX8State::dirty() |= viewIdentity | 2;
    }
    Matrix4 view(true);
    DX8Wrapper::Set_Transform(D3DTS_PROJECTION, view);
    {
        Matrix4 transposedWorld = m_world.Transpose();
        Vector4 unusedWorldRows[4];
        Rva0078B4F0DX8State::world() = transposedWorld;
        Rva0078B4F0DX8State::dirty() = (Rva0078B4F0DX8State::dirty() & ~0x40000) | 1;
    }
    VertexMaterialClass *material = VertexMaterialClass::Get_Preset(VertexMaterialClass::PRELIT_DIFFUSE);
    DX8Wrapper::Set_Material(material);
    REF_PTR_RELEASE(material);
    DX8Wrapper::Set_Vertex_Buffer(m_vertexBuffer, 0);
    m_modeChanged = true;
    m_pendingTextureChange = true;
}

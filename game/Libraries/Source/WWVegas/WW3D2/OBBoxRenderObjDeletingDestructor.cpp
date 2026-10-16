// cl: /DNDEBUG /MD /EHsc

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2/boxrobj.h
//
// Neither BoxRenderObjClass nor OBBoxRenderObjClass declares a destructor, so
// ~OBBoxRenderObjClass (retail 0x00957BB0) is the implicit one: a bare jump to
// RenderObjClass::~RenderObjClass 0x0091FC10 with no vptr store. The
// scalar-deleting wrapper 0x00957B90 calls it.
class RenderObjClass
{
public:
	virtual ~RenderObjClass();
};

class BoxRenderObjClass : public RenderObjClass
{
public:
	BoxRenderObjClass();
};

// boxrobj.cpp's own ??_GOBBoxRenderObjClass carries the W3DMPO adjustment, so
// this TU supplies the retail wrapper. The tag constructor only makes the
// compiler emit the vtable (and with it ??_G) without a copy of any retail
// constructor.
struct OBBoxRenderObjVtableTag;

class OBBoxRenderObjClass : public BoxRenderObjClass
{
public:
	explicit OBBoxRenderObjClass( OBBoxRenderObjVtableTag * ) {}
};

void Force_OBBoxRenderObj_Deleting_Destructor()
{
	OBBoxRenderObjClass box( 0 );
}

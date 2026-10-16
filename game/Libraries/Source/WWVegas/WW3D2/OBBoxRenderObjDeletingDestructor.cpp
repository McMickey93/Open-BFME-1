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
	RenderObjClass();
	virtual ~RenderObjClass();
};

class BoxRenderObjClass : public RenderObjClass
{
};

class OBBoxRenderObjClass : public BoxRenderObjClass
{
};

void Force_OBBoxRenderObj_Deleting_Destructor()
{
	OBBoxRenderObjClass box;
}

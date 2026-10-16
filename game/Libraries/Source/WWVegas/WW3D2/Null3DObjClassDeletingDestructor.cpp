// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME5: Null3DObjClass scalar-deleting destructor at retail RVA
// 0x00972960.  Its matched constructors at 0x009726A0/0x009726E0 install
// vtable 0x0113E87C, whose Clone, Class_ID=22, Render, and bounding-volume
// slots identify Null3DObjClass.  nullrobj.h declares no destructor, so the
// complete destructor at 0x00972980 is the implicit one: a bare jump to
// RenderObjClass::~RenderObjClass 0x0091FC10.

class RenderObjClass
{
public:
	RenderObjClass();
	virtual ~RenderObjClass();
};

class Null3DObjClass : public RenderObjClass
{
};

void forceNull3DObjClassDeletingDestructor()
{
	Null3DObjClass value;
}

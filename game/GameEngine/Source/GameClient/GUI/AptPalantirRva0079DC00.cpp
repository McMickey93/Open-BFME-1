// cl: /Igame /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Igame/Libraries/Source/WWVegas /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WW3D2 /Igame/Libraries/Source/WWVegas/WWMath /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Igame/Libraries/Source/WWVegas/WWDebug
// stlport
// Retail 0x0079DC00, 454 bytes: AptPalantir vtable 0x01127A48 slot 9 routes
// through ILT 0x000396A3 to this body (the AptPalantir constructor at
// 0x0079D9F0 installs that table; the base Rva00597FC0Client table has
// __purecall in slot 9). The method name stays address-derived.
// Fields +0x510 scene, +0x514 camera and +0x518 render object are the ones the
// palantir scene initializer at 0x0079E0F0 creates. The viewport arithmetic is
// the one the matched 0x00789BF0 viewport renderer uses.
#include <new>
#define _OPERATOR_NEW_DEFINED_
#define Matrix4x4 Matrix4
#include "WW3D2/camera.h"
#include "WW3D2/w3derr.h"
// The matched BFME scene renderer returns bool.
#define WW3DErrorType bool
#include "WW3D2/ww3d.h"
#undef WW3DErrorType
#include "GameEngine/Include/GameClient/Display.h"

// Retail .data float read at 0x012BBB78 (160.0 in the shipped image).
float g_Va012BBB78 = 160.0f;

class AptPalantir
{
public:
	virtual ~AptPalantir();
	virtual void rva0079dc00(int x, int y, int width, int height);

private:
	char m_base[0x50C];
	SceneClass *m_510;
	CameraClass *m_514;
	RenderObjClass *m_518;
};

void AptPalantir::rva0079dc00(int x, int y, int width, int height)
{
	if (m_518) {
		Matrix3D transform(true);
		transform.Rotate_X(-1.5707964f);
		transform.Translate_Z(g_Va012BBB78);
		m_514->Set_Transform(transform);
		float dh = (float)TheDisplay->getHeight();
		float dw = (float)TheDisplay->getWidth();
		float invw = 1.0f / dw;
		Vector2 lo;
		lo.X = x * invw;
		float invh = 1.0f / dh;
		lo.Y = y * invh;
		Vector2 hi(lo.X + width * invw, lo.Y + height * invh);
		m_514->Set_Viewport(lo, hi);
		m_514->Set_View_Plane(0.87266463f, -1.0f);
		WW3D::Render(m_510, m_514, false, false, Vector3(0, 0, 0));
	}
}

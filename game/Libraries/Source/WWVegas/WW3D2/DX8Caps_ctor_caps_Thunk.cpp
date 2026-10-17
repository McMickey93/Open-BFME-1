// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// Open-BFME5: lift the capability-record DX8 constructor to clean C++.

#include "wwstring.h"

struct IDirect3D8;
struct IDirect3DDevice8;
struct _D3DADAPTER_IDENTIFIER8;
enum WW3DFormat { WW3DFormat_dummy = 0 };

// Both constructors call retail 0x0091C230, whose ledger row is the naked
// lift in DX8CapsComputeCapsThunk.cpp defining _bfme_DX8Caps_Compute_Caps_91C230
// (tools/callees.py 0x91cbf0 261 and 0x91cb00 233 print that object symbol).
// Nothing defines the pinned ?Compute_Caps@DX8Caps@@AAEX...8@@@Z, so the calls
// name the lift through a raw pointer bridge that keeps the two-argument
// thiscall shape.
extern "C" void bfme_DX8Caps_Compute_Caps_91C230();

struct _D3DCAPS8
{
	unsigned char m_unreconstructed_00[0x1C];
	unsigned DevCaps;
	unsigned char m_unreconstructed_20[0x110];
};
typedef _D3DCAPS8 D3DCAPS8;

class DX8Caps
{
public:
	DX8Caps(IDirect3D8 *, const D3DCAPS8 &, WW3DFormat,
		const _D3DADAPTER_IDENTIFIER8 &);
	DX8Caps(IDirect3D8 *, IDirect3DDevice8 *, WW3DFormat,
		const _D3DADAPTER_IDENTIFIER8 &);

private:
	void Init_Caps(IDirect3DDevice8 *);

	int m_maxDisplayWidth;
	int m_maxDisplayHeight;
	D3DCAPS8 m_caps;
	bool m_supportTnL;
	unsigned char m_unreconstructed_139[0x153];
	int m_vendorId;
	unsigned char m_unreconstructed_290[0x0C];
	StringClass m_driverDLL;
	IDirect3D8 *m_direct3D;
	StringClass m_capsLog;
	StringClass m_compactLog;
};

// ??0DX8Caps@@QAE@PAUIDirect3D8@@ABU_D3DCAPS8@@W4WW3DFormat@@ABU_D3DADAPTER_IDENTIFIER8@@@Z
DX8Caps::DX8Caps(IDirect3D8 *direct3D, const D3DCAPS8 &caps,
	WW3DFormat displayFormat, const _D3DADAPTER_IDENTIFIER8 &adapterIdentifier)
	: m_maxDisplayWidth(0),
	  m_maxDisplayHeight(0),
	  m_caps(caps),
	  m_vendorId(0),
	  m_direct3D(direct3D)
{
	if ((m_caps.DevCaps & 0x10000) == 0x10000) {
		m_supportTnL = true;
	} else {
		m_supportTnL = false;
	}

	union
	{
		void (*raw)(void);
		void (DX8Caps::*typed)(WW3DFormat, const _D3DADAPTER_IDENTIFIER8 &);
	} computeCaps;
	computeCaps.raw = &bfme_DX8Caps_Compute_Caps_91C230;
	(this->*computeCaps.typed)(displayFormat, adapterIdentifier);
}

// ??0DX8Caps@@QAE@PAUIDirect3D8@@PAUIDirect3DDevice8@@W4WW3DFormat@@ABU_D3DADAPTER_IDENTIFIER8@@@Z
DX8Caps::DX8Caps(IDirect3D8 *direct3D, IDirect3DDevice8 *device,
	WW3DFormat displayFormat, const _D3DADAPTER_IDENTIFIER8 &adapterIdentifier)
	: m_maxDisplayWidth(0),
	  m_maxDisplayHeight(0),
	  m_vendorId(0),
	  m_direct3D(direct3D)
{
	Init_Caps(device);
	union
	{
		void (*raw)(void);
		void (DX8Caps::*typed)(WW3DFormat, const _D3DADAPTER_IDENTIFIER8 &);
	} computeCaps;
	computeCaps.raw = &bfme_DX8Caps_Compute_Caps_91C230;
	(this->*computeCaps.typed)(displayFormat, adapterIdentifier);
}

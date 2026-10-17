// cl: /Iinputs/reference/shims/dx8wrapper /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/debug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Igame/Libraries/Source/WWVegas/WW3D2

// stlport
#define Matrix4x4 Matrix4
#define __PLACEMENT_VEC_NEW_INLINE
#include "dx8wrapper.h"
#include <math.h>
struct ResolutionAccess007833E0 : DX8Wrapper { using DX8Wrapper::Get_Device_Resolution; };
// Retail copies the six floats then derives display scales from APT and DX8 dimensions.
struct Rva007845D0Transform { float m[6]; };
extern Rva007845D0Transform g_Rva00F0692CTransform;
extern Rva007845D0Transform g_Rva00F06914Transform;
int g_Va0130699C[4] = {0, 0, 0, 0};
float g_Va012BB86C = 1.0f;
float g_Va012BB870 = 1.0f;
float g_Va012BB874 = 1.0f;
float g_Va012BB878 = 1.0f;
int g_Va012BB860 = 3;
extern float Rva01126A68Threshold;
void Rva00892A00Query(void **, void **);
// Retail 0x007831B0 (37 B) and 0x00783720 (72 B) bracket setScaledTransform: two
// file-statics on the same six-float transform and float pairs. MSVC gives them private
// register conventions (point ECX, transform EAX, out EDX; point ECX, min EDX, max ESI),
// reproduced here through an absent-from-retail TU-local caller.
struct Rva007831B0Point { float x, y; };

static void rva007831B0(const Rva007831B0Point *point, const Rva007845D0Transform *transform,
	Rva007831B0Point *out)
{
	out->x = transform->m[0] * point->x + transform->m[2] * point->y + transform->m[4];
	out->y = transform->m[1] * point->x + transform->m[3] * point->y + transform->m[5];
}

static void rva00783720(const Rva007831B0Point *point, Rva007831B0Point *minimum,
	Rva007831B0Point *maximum)
{
	if (minimum->x > point->x)
		minimum->x = point->x;
	else if (maximum->x < point->x)
		maximum->x = point->x;
	if (minimum->y > point->y)
		minimum->y = point->y;
	else if (maximum->y < point->y)
		maximum->y = point->y;
}

// absent-from-retail: TU-local caller that keeps both statics above alive.
void rva007831B0Caller(const Rva007831B0Point *point, const Rva007845D0Transform *transform,
	Rva007831B0Point *out, Rva007831B0Point *minimum, Rva007831B0Point *maximum)
{
	rva007831B0(point, transform, out);
	rva00783720(out, minimum, maximum);
}

void setScaledTransform007833E0(const Rva007845D0Transform *transform)
{
 g_Rva00F0692CTransform = *transform;
 // One contiguous output record: bit depth, display width/height, APT width/height.
 // The existing APT query exposes its two 32-bit outputs as void **.
 int dimensions[5];
 bool windowed;
 Rva00892A00Query((void **)&dimensions[3], (void **)&dimensions[4]);
 ResolutionAccess007833E0::Get_Device_Resolution(dimensions[1],dimensions[2],dimensions[0],windowed);
 // Keeping width separately preserves the retail load scheduling.
 int width = dimensions[1];
 if ((int)dimensions[3] != g_Va0130699C[0] ||
     (int)dimensions[4] != g_Va0130699C[1] ||
     width != g_Va0130699C[2] ||
     dimensions[2] != g_Va0130699C[3]) {
  if (dimensions[3]) g_Va012BB86C = (float)width / (int)dimensions[3];
  else g_Va012BB86C = 1.0f;
  if (dimensions[4]) g_Va012BB870 = (float)dimensions[2] / (int)dimensions[4];
  else g_Va012BB870 = 1.0f;
  if (g_Va012BB86C != 0.0f) g_Va012BB874 = 1.0f / g_Va012BB86C;
  else g_Va012BB874 = 1.0f;
  if (g_Va012BB870 != 0.0f) g_Va012BB878 = 1.0f / g_Va012BB870;
  else g_Va012BB878 = 1.0f;
  g_Va0130699C[0] = (int)dimensions[3];
  g_Va0130699C[1] = (int)dimensions[4];
  g_Va0130699C[2] = width;
  g_Va0130699C[3] = dimensions[2];
 }
 g_Rva00F0692CTransform.m[4] *= g_Va012BB86C;
 g_Rva00F0692CTransform.m[5] *= g_Va012BB870;
 g_Rva00F06914Transform = g_Rva00F0692CTransform;
 g_Rva00F0692CTransform.m[0] *= g_Va012BB86C;
 g_Rva00F0692CTransform.m[2] *= g_Va012BB86C;
 g_Rva00F0692CTransform.m[1] *= g_Va012BB870;
 g_Rva00F0692CTransform.m[3] *= g_Va012BB870;
 // Retail accepts unordered comparisons here; do not rewrite these as <=.
 if (!(fabs(g_Rva00F0692CTransform.m[0] - 1.0f) > Rva01126A68Threshold ) && !(
     fabs(g_Rva00F0692CTransform.m[1]) > Rva01126A68Threshold ) && !(
     fabs(g_Rva00F0692CTransform.m[2]) > Rva01126A68Threshold ) && !(
     fabs(g_Rva00F0692CTransform.m[3] - 1.0f) > Rva01126A68Threshold))
  g_Va012BB860 = 3;
 else g_Va012BB860 = 1;
}



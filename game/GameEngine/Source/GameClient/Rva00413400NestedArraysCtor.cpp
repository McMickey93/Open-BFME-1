// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWMath
#include "coord3d.h"

// Drawable::Drawable at 0x00418DA0 passes this+0x31C at +0x2D2 and calls
// this constructor through ILT 0x0003B700 at +0x313; the next field starts
// at +0x3AC, proving this subobject's 0x90-byte extent. Its semantic class
// is not established, so the owner name retains this body's address.
// The 16-byte row constructor at ILT 0x00045561 is retail Vector4's default
// constructor (ilt_oracle CONFIRMED), also used by the
// SpawnPointProductionExitUpdate matrix-array constructor. This declaration
// retains the witnessed layout without asserting this owner's semantic class.
class Vector4
{
public:
    Vector4();
    float X, Y, Z, W;
};

struct Rva00413400Matrix
{
    Vector4 rows[3];
};

struct Rva00413400Owner
{
    Rva00413400Owner();
    Rva00413400Matrix matrices[2];
    Coord3D points[4];
};

Rva00413400Owner::Rva00413400Owner() {}

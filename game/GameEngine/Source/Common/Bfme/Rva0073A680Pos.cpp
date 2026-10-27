// 33-byte Vec3 getter with individual member assignments. It returns the
// out pointer: W3DView 0x00743CE0 copies the vector through the returned EAX.

struct Vec3
{
	int x;
	int y;
	int z;
};

class Rva0073A680
{
public:
	Vec3 *getPosition( Vec3 *out ) const;

	char m_pad00[ 0x4B8 ];
	int  m_x;
	int  m_y;
	int  m_z;
};

// ?getPosition@Rva0073A680@@QBEPAUVec3@@PAU2@@Z
Vec3 *Rva0073A680::getPosition( Vec3 *out ) const
{
	out->x = m_x;
	out->y = m_y;
	out->z = m_z;
	return out;
}

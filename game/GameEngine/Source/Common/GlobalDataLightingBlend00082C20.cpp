// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include
#include <math.h>
#include "Lib/BaseType.h"

class BfmeVec3JF
{
public:
	float m_bfmeXJF;
	float m_bfmeYJF;
	float m_bfmeZJF;
};

class BfmeLightingJF
{
public:
	typedef RGBColor RGBColorJF;
	typedef Coord3D Coord3DJF;
	RGBColorJF ambient;
	RGBColorJF diffuse;
	Coord3DJF lightPos;
};

class BfmeSetJF
{
public:
	BfmeLightingJF m_bfmeLightsJF[3];
};

class BfmeXfJF
{
public:
	bool rva00082C20JF(int firstIndex, int secondIndex, float factor);
	__forceinline bool bfmeLoadJF(int index);

	unsigned char m_bfmeHeadJF[0x218];
	int m_bfmeIndexJF;
	unsigned char m_bfmeGap2JF[8];
	BfmeSetJF m_bfmeSetsJF[6];
	BfmeSetJF m_bfmeObjectSetsJF[6];
	BfmeSetJF m_bfmeThirdSetsJF[6];
	BfmeVec3JF m_bfmeOutJF[3][3];
};

// ?bfmeLoadJF@BfmeXfJF@@QAE_NH@Z absent-from-retail
//-------------------------------------------------------------------------------------------------
//-------------------------------------------------------------------------------------------------
__forceinline bool BfmeXfJF::bfmeLoadJF(int index)
{
    if (index >= 6 || index < 1)
        return false;
    m_bfmeIndexJF = index;
    for (int i = 0; i < 3; ++i)
    {
        m_bfmeOutJF[0][i] = *(BfmeVec3JF *)&m_bfmeSetsJF[index].m_bfmeLightsJF[i].ambient;
        m_bfmeOutJF[1][i] = *(BfmeVec3JF *)&m_bfmeSetsJF[index].m_bfmeLightsJF[i].diffuse;
        m_bfmeOutJF[2][i] = *(BfmeVec3JF *)&m_bfmeSetsJF[index].m_bfmeLightsJF[i].lightPos;
    }
    return true;
}

// ?rva00082C20JF@BfmeXfJF@@QAE_NHHM@Z
// Evidence: targets/game/reverse/identity_evidence/00082c20-lighting-blend-retry.md
bool BfmeXfJF::rva00082C20JF(int firstIndex, int secondIndex, float factor)
{
	if (firstIndex < 6 && firstIndex >= 1 &&
		secondIndex < 6 && secondIndex >= 1)
	{
		BfmeXfJF &first = *this;
		BfmeXfJF &second = *this;
		BfmeXfJF &out = *this;
		float oneMinusFactor = (float)(1.0 - factor);

#define BFME_BLEND(dst, lhs, rhs) \
        { \
            const float &firstValue = (lhs); \
            const float &secondValue = (rhs); \
            float &outValue = (dst); \
            outValue = oneMinusFactor * firstValue + factor * secondValue; \
        }
#define BFME_BLEND_REVERSED(dst, lhs, rhs) \
        { \
            const float &firstValue = (lhs); \
            const float &secondValue = (rhs); \
            float &outValue = (dst); \
            outValue = factor * secondValue + oneMinusFactor * firstValue; \
        }

		int i;
		for (i = 0; i < 3; ++i)
		{
			BFME_BLEND(out.m_bfmeSetsJF[5].m_bfmeLightsJF[i].ambient.red, first.m_bfmeSetsJF[firstIndex].m_bfmeLightsJF[i].ambient.red, second.m_bfmeSetsJF[secondIndex].m_bfmeLightsJF[i].ambient.red);
			BFME_BLEND_REVERSED(out.m_bfmeSetsJF[5].m_bfmeLightsJF[i].ambient.green, first.m_bfmeSetsJF[firstIndex].m_bfmeLightsJF[i].ambient.green, second.m_bfmeSetsJF[secondIndex].m_bfmeLightsJF[i].ambient.green);
			BFME_BLEND(out.m_bfmeSetsJF[5].m_bfmeLightsJF[i].ambient.red, first.m_bfmeSetsJF[firstIndex].m_bfmeLightsJF[i].ambient.blue, second.m_bfmeSetsJF[secondIndex].m_bfmeLightsJF[i].ambient.blue);
			BFME_BLEND(out.m_bfmeSetsJF[5].m_bfmeLightsJF[i].diffuse.red, first.m_bfmeSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.red, second.m_bfmeSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.red);
			BFME_BLEND(out.m_bfmeSetsJF[5].m_bfmeLightsJF[i].diffuse.green, first.m_bfmeSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.green, second.m_bfmeSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.green);
			BFME_BLEND(out.m_bfmeSetsJF[5].m_bfmeLightsJF[i].diffuse.red, first.m_bfmeSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.blue, second.m_bfmeSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.blue);
			BFME_BLEND(out.m_bfmeSetsJF[5].m_bfmeLightsJF[i].lightPos.x, first.m_bfmeSetsJF[firstIndex].m_bfmeLightsJF[i].lightPos.x, second.m_bfmeSetsJF[secondIndex].m_bfmeLightsJF[i].lightPos.x);
			BFME_BLEND(out.m_bfmeSetsJF[5].m_bfmeLightsJF[i].lightPos.y, first.m_bfmeSetsJF[firstIndex].m_bfmeLightsJF[i].lightPos.y, second.m_bfmeSetsJF[secondIndex].m_bfmeLightsJF[i].lightPos.y);
			BFME_BLEND(out.m_bfmeSetsJF[5].m_bfmeLightsJF[i].lightPos.z, first.m_bfmeSetsJF[firstIndex].m_bfmeLightsJF[i].lightPos.z, second.m_bfmeSetsJF[secondIndex].m_bfmeLightsJF[i].lightPos.z);
			BFME_BLEND(out.m_bfmeObjectSetsJF[5].m_bfmeLightsJF[i].diffuse.red, first.m_bfmeObjectSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.red, second.m_bfmeObjectSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.red);
			BFME_BLEND(out.m_bfmeObjectSetsJF[5].m_bfmeLightsJF[i].diffuse.green, first.m_bfmeObjectSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.green, second.m_bfmeObjectSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.green);
			BFME_BLEND(out.m_bfmeObjectSetsJF[5].m_bfmeLightsJF[i].diffuse.red, first.m_bfmeObjectSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.blue, second.m_bfmeObjectSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.blue);
			BFME_BLEND(out.m_bfmeObjectSetsJF[5].m_bfmeLightsJF[i].diffuse.red, first.m_bfmeObjectSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.red, second.m_bfmeObjectSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.red);
			BFME_BLEND(out.m_bfmeObjectSetsJF[5].m_bfmeLightsJF[i].diffuse.green, first.m_bfmeObjectSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.green, second.m_bfmeObjectSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.green);
			BFME_BLEND(out.m_bfmeObjectSetsJF[5].m_bfmeLightsJF[i].diffuse.red, first.m_bfmeObjectSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.blue, second.m_bfmeObjectSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.blue);
			BFME_BLEND(out.m_bfmeObjectSetsJF[5].m_bfmeLightsJF[i].lightPos.x, first.m_bfmeObjectSetsJF[firstIndex].m_bfmeLightsJF[i].lightPos.x, second.m_bfmeObjectSetsJF[secondIndex].m_bfmeLightsJF[i].lightPos.x);
			BFME_BLEND(out.m_bfmeObjectSetsJF[5].m_bfmeLightsJF[i].lightPos.y, first.m_bfmeObjectSetsJF[firstIndex].m_bfmeLightsJF[i].lightPos.y, second.m_bfmeObjectSetsJF[secondIndex].m_bfmeLightsJF[i].lightPos.y);
			BFME_BLEND(out.m_bfmeObjectSetsJF[5].m_bfmeLightsJF[i].lightPos.z, first.m_bfmeObjectSetsJF[firstIndex].m_bfmeLightsJF[i].lightPos.z, second.m_bfmeObjectSetsJF[secondIndex].m_bfmeLightsJF[i].lightPos.z);
			BFME_BLEND(out.m_bfmeThirdSetsJF[5].m_bfmeLightsJF[i].ambient.red, first.m_bfmeThirdSetsJF[firstIndex].m_bfmeLightsJF[i].ambient.red, second.m_bfmeThirdSetsJF[secondIndex].m_bfmeLightsJF[i].ambient.red);
			BFME_BLEND(out.m_bfmeThirdSetsJF[5].m_bfmeLightsJF[i].ambient.green, first.m_bfmeThirdSetsJF[firstIndex].m_bfmeLightsJF[i].ambient.green, second.m_bfmeThirdSetsJF[secondIndex].m_bfmeLightsJF[i].ambient.green);
			BFME_BLEND(out.m_bfmeThirdSetsJF[5].m_bfmeLightsJF[i].ambient.red, first.m_bfmeThirdSetsJF[firstIndex].m_bfmeLightsJF[i].ambient.blue, second.m_bfmeThirdSetsJF[secondIndex].m_bfmeLightsJF[i].ambient.blue);
			BFME_BLEND(out.m_bfmeThirdSetsJF[5].m_bfmeLightsJF[i].diffuse.red, first.m_bfmeThirdSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.red, second.m_bfmeThirdSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.red);
			BFME_BLEND(out.m_bfmeThirdSetsJF[5].m_bfmeLightsJF[i].diffuse.green, first.m_bfmeThirdSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.green, second.m_bfmeThirdSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.green);
			BFME_BLEND(out.m_bfmeThirdSetsJF[5].m_bfmeLightsJF[i].diffuse.red, first.m_bfmeThirdSetsJF[firstIndex].m_bfmeLightsJF[i].diffuse.blue, second.m_bfmeThirdSetsJF[secondIndex].m_bfmeLightsJF[i].diffuse.blue);
			BFME_BLEND(out.m_bfmeThirdSetsJF[5].m_bfmeLightsJF[i].lightPos.x, first.m_bfmeThirdSetsJF[firstIndex].m_bfmeLightsJF[i].lightPos.x, second.m_bfmeThirdSetsJF[secondIndex].m_bfmeLightsJF[i].lightPos.x);
			BFME_BLEND(out.m_bfmeThirdSetsJF[5].m_bfmeLightsJF[i].lightPos.y, first.m_bfmeThirdSetsJF[firstIndex].m_bfmeLightsJF[i].lightPos.y, second.m_bfmeThirdSetsJF[secondIndex].m_bfmeLightsJF[i].lightPos.y);
			BFME_BLEND(out.m_bfmeThirdSetsJF[5].m_bfmeLightsJF[i].lightPos.z, first.m_bfmeThirdSetsJF[firstIndex].m_bfmeLightsJF[i].lightPos.z, second.m_bfmeThirdSetsJF[secondIndex].m_bfmeLightsJF[i].lightPos.z);
		}

#undef BFME_BLEND_REVERSED
#undef BFME_BLEND

		m_bfmeIndexJF = 5;
		return bfmeLoadJF(m_bfmeIndexJF);
	}

	return false;
}

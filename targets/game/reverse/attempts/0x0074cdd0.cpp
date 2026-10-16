// ?query@Rva0074CDD0@@QAEEHH@Z
// partial score=0.5793 date=2026-10-16
// cl: /DNDEBUG /MD /EHsc
#include <stdlib.h>
extern float rva012BB2D4Scale, rva012BB2D0Threshold;
class Rva0074BD10Owner {public:bool rva0074BD10(int,int);};
class Rva0074CDD0 {
public:
    unsigned char query(int x, int y);
    bool rva0074BD10(int x, int y);
    bool isCliffMappedTexture(int x, int y) {
        int index = (originY + y) * width + originX + x;
        if (index < 0 || index >= count) return false;
        return cliffInfo[index] != 0;
    }
    unsigned char beforeWidth[8];
    int width;
    unsigned char beforeCount[0x14];
    int count;
    unsigned short *heights;
    unsigned char beforeCliff[0x6c];
    void **cliffInfo;
    unsigned char beforeOrigin[0x12048];
    int originX, originY;
};

unsigned char Rva0074CDD0::query(int x, int y) {
    const int stride = width;
    if (isCliffMappedTexture(x, y) && reinterpret_cast<Rva0074BD10Owner *>(this)->rva0074BD10(x, y))
        return *reinterpret_cast<volatile unsigned char *>(&y);
    int index = y * stride + x;
    if (index < 0 || index >= count || !heights || index >= count - stride - 1)
        return 0;
    int h1 = heights[index], h2 = heights[index + 1];
    int hi = h1 >= h2 ? h1 : h2;
    int lo = h1 <= h2 ? h1 : h2;
    int h4 = heights[index + width + 1], h3 = heights[index + width];
    if (lo > h4) lo = h4;
    if (hi < h4) hi = h4;
    if (lo > h3) lo = h3;
    if (hi < h3) hi = h3;
    if ((hi - lo) * rva012BB2D4Scale > rva012BB2D0Threshold) {
        int secondDiagonal = abs(h2 - h3);
        int firstDiagonal = abs(h1 - h4);
        int result = firstDiagonal > secondDiagonal;
        return result;
    }
    return 0;
}

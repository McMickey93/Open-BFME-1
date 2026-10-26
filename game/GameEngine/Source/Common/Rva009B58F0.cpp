// cl: /O2 /G6 /Ob1 /DNDEBUG /MD
#include <string.h>
struct Rva009B58F0BlockContext
{
	unsigned char pad0[4];
	int mode;
	short frame;
	short dc;
};

struct Rva009B58F0Quantizer
{
	unsigned char pad0[0x180];
	short *dequant[4];
};

struct Rva009B58F0State
{
	unsigned char pad0[4];
	unsigned char *coefficients;
	int mode;
	int blockModes[6];
	unsigned char pad24[0x78 - 0x24];
	int plane;
	unsigned char pad7C[0xBC - 0x7C];
	Rva009B58F0BlockContext *above;
	Rva009B58F0BlockContext *left;
	short *lastDC;
	unsigned char padC8[0x13C - 0xC8];
	Rva009B58F0Quantizer *quantizer;
	unsigned char pad140[0x270 - 0x140];
	short *reconstruction;
	unsigned char pad274[0x4520 - 0x274];
	int useHuffman;
};

typedef void (__cdecl *Rva009B58F0Callback)(unsigned char *, short *, short *);

extern unsigned char g_Rva01142608[];
extern const unsigned short Rva01142BA0Table[];
extern int g_bfmeTableJX;
#define g_01356B64 (((Rva009B58F0Callback *)&g_bfmeTableJX)[1])
#define g_01356B84 (((Rva009B58F0Callback *)&g_bfmeTableJX)[9])
#define g_01356C5C (((Rva009B58F0Callback *)&g_bfmeTableJX)[63])
unsigned char Rva009B4A10(unsigned char *, short *, int);	// matched body; formerly reached as d_009b4a10
typedef unsigned char (__cdecl *Rva009B4A10Fn)(void *, short *, int);
#define VP6_ReadHuffTokens(p,a,b) ((Rva009B4A10Fn)Rva009B4A10)(p,(short *)(a),b)
extern void d_009ab9d0();
typedef unsigned char (__cdecl *Rva009AB9D0Fn)(void *, short *, int, void *, void *);
#define VP6_ReadTokens(p,a,b,c,d) ((Rva009AB9D0Fn)d_009ab9d0)(p,(short *)(a),b,c,d)
struct Rva009B4880State;
struct Rva009B4880Neighbor;
struct Rva009B5830State;
void Rva009B4880PredictValue(Rva009B4880State *, int, short *, const Rva009B4880Neighbor *, const Rva009B4880Neighbor *);
void Rva009B5830ReconstructBlock(Rva009B5830State *, int);

#define VP6_COEFS (pbi->coefficients + block * 128)
// ?Rva009B58F0@@YAXPAEHIH@Z
// Ported from Open BFME 2 Code/Libraries/Source/VP6/DecodeBlock.cpp.
void __cdecl Rva009B58F0(unsigned char *ctx, int row, unsigned column, int block)
{
	Rva009B58F0State *pbi = (Rva009B58F0State *)ctx;
	int decoded = pbi->useHuffman ? VP6_ReadHuffTokens(pbi, VP6_COEFS, pbi->plane != 0) : VP6_ReadTokens(pbi, VP6_COEFS, pbi->plane != 0, pbi->above, pbi->left);
	Rva009B4880PredictValue((Rva009B4880State *)pbi, block, pbi->lastDC, (const Rva009B4880Neighbor *)pbi->above, (const Rva009B4880Neighbor *)pbi->left);
	pbi->left->mode = pbi->blockModes[block];
	pbi->above->mode = pbi->left->mode;
	pbi->left->dc = *(short *)VP6_COEFS;
	pbi->above->dc = pbi->left->dc;
	pbi->left->frame = (short)Rva01142BA0Table[pbi->mode * 2];
	pbi->above->frame = pbi->left->frame;
	if ((int)decoded <= 1) {
		g_01356B64(VP6_COEFS, pbi->quantizer->dequant[g_Rva01142608[block]], pbi->reconstruction);
		*(short *)VP6_COEFS = 0;
	} else if ((int)decoded <= 10) {
		g_01356B84(VP6_COEFS, pbi->quantizer->dequant[g_Rva01142608[block]], pbi->reconstruction);
		memset(VP6_COEFS, 0, 16);
		memset(VP6_COEFS + 0x10, 0, 8);
		memset(VP6_COEFS + 0x20, 0, 8);
		memset(VP6_COEFS + 0x30, 0, 8);
		*(short *)(VP6_COEFS + 0x40) = 0;
	} else {
		g_01356C5C(VP6_COEFS, pbi->quantizer->dequant[g_Rva01142608[block]], pbi->reconstruction);
		memset(VP6_COEFS, 0, 128);
	}
	Rva009B5830ReconstructBlock((Rva009B5830State *)pbi, block);
}

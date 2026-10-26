// ?inGameTailA0_0043B4F0@W3DInGameUI@@UAEXXZ
// stlport
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/display /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad
#define Matrix4x4 Matrix4
#include "PreRTS.h"
#include <math.h>
#include "GameClient/Display.h"

typedef unsigned char byte;




#define DECLARE_TEN(prefix) \
	virtual void prefix##0(); virtual void prefix##1(); \
	virtual void prefix##2(); virtual void prefix##3(); \
	virtual void prefix##4(); virtual void prefix##5(); \
	virtual void prefix##6(); virtual void prefix##7(); \
	virtual void prefix##8(); virtual void prefix##9();

class WindowManagerSlots
{
public:
	DECLARE_TEN(windowA)
	DECLARE_TEN(windowB)
	DECLARE_TEN(windowC)
	virtual void windowD0(); virtual void windowD1();
	virtual void windowD2(); virtual void windowD3();
	virtual void windowD4(); virtual void windowD5();
};

class GameWindowManager : public WindowManagerSlots
{
public:
	virtual void winRepaintWindows();

private:
	unsigned char m_unmodelled_04[0x34];

public:
	int m_drawState;
};

class W3DInGameUISlots
{
public:
	virtual void draw();
	DECLARE_TEN(inGameA)
	DECLARE_TEN(inGameB)
	DECLARE_TEN(inGameC)
	DECLARE_TEN(inGameD)
	DECLARE_TEN(inGameE)
	DECLARE_TEN(inGameF)
	DECLARE_TEN(inGameG)
	virtual void inGameH1(); virtual void inGameH2();
	virtual void inGameH3();
};

class DisplayLine
{
public:
	virtual void slot00(); virtual void slot01(); virtual void slot02();
	virtual void slot03(); virtual void slot04(); virtual void slot05();
	virtual void slot06(); virtual void slot07(); virtual void slot08();
	virtual void slot09();
	virtual void setColor(UnsignedInt color, UnsignedInt dropColor); // +0x28 slot 10
	virtual void slot11(); virtual void slot12(); virtual void slot13();
	virtual void draw(Int x, Int y, Int a, Int b);             // +0x38 slot 14
	virtual void getSize(Int *width, Int *height);             // +0x3c slot 15
};

struct MilitarySubtitleRecord
{
	unsigned char m_pad00[0x08];
	DisplayLine *m_lines[4];      // +0x08 .. +0x14
	Int m_lineX[4];               // +0x18 .. +0x24
	DisplayLine *m_block;         // +0x28
	Int m_lineCount;              // +0x2c
	unsigned char m_pad30[4];
	UnsignedInt m_startFrame;     // +0x34
	UnsignedInt m_endFrame;       // +0x38
	unsigned char m_pad3c[4];
	UnsignedInt m_color;          // +0x40
};



#define g_bfme40BC00 1.0f
#define g_bfme40BC0C 0.5f
#define g_bfme4C8615 30.0f

class W3DInGameUI : public W3DInGameUISlots
{
public:
	virtual void draw();
	virtual void preDraw();
	virtual void postDraw();
	virtual void inGameTailA0_0043B4F0();
	virtual void inGameTailA1(); virtual void inGameTailA2();
	virtual void inGameTailA3(); virtual void inGameTailA4();
	virtual void inGameTailA5(); virtual void inGameTailA6();
	virtual void inGameTailA7(); virtual void inGameTailA8();
	virtual void inGameTailA9();
	DECLARE_TEN(inGameTailB)
	DECLARE_TEN(inGameTailC)
	virtual void inGameTailD0(); virtual void inGameTailD1();
	virtual void inGameTailD2(); virtual void inGameTailD3();
	virtual void drawSelectionRegion();
	virtual void drawMoveHints(View *view);
	virtual void drawAttackHints(View *view);
	virtual void drawPlaceAngle(View *view);

private:
	unsigned char m_unmodelled_04[0x818 - 4];

public:
	MilitarySubtitleRecord *m_subtitle;    // +0x818
	unsigned char m_pad81c[0x86c - 0x81c];
	Real m_widthFraction;                  // +0x86c
	Real m_heightFraction;                 // +0x870
	unsigned char m_pad874[0x890 - 0x874];
	Int m_fadeDuration;                    // +0x890
};

#undef DECLARE_TEN

// ?inGameTailA0_0043B4F0@W3DInGameUI@@UAEXXZ
void W3DInGameUI::inGameTailA0_0043B4F0()
{
	Int index = 0;
	Int startY;
	if ((Int)m_subtitle == index)
		return;

	UnsignedInt frameDelta = m_subtitle->m_startFrame - m_subtitle->m_endFrame;
	Real fraction = (Real)frameDelta / m_fadeDuration;
	fraction = g_bfme40BC00 - fraction;

	UnsignedInt width = TheDisplay->getWidth();
	Real fx = (Real)(UnsignedInt)width * m_widthFraction + g_bfme40BC0C;
	Int startX = fast_float2long_round((Real)floor((double)fx));

	UnsignedInt height = TheDisplay->getHeight();
	Real fy = (Real)(UnsignedInt)height * m_heightFraction + g_bfme40BC0C;
	startY = fast_float2long_round((Real)floor((double)fy));

	byte a, r, g, b;
	GameGetColorComponents((Int)m_subtitle->m_color, &r, &g, &b, &a);
	UnsignedInt dropColor = ((UnsignedInt)a) << 24;

	Int cursorY = startY;
	ICoord2D blockPos;
	Int &blockY = blockPos.y;
	Int measuredW;
	measuredW = 0;
	Int byteOffset = 8;
	for (; (UnsignedInt)index <= (UnsignedInt)m_subtitle->m_lineCount; ++index, byteOffset += 4)
	{
		Int measuredH;
		blockY = cursorY;
		m_subtitle->m_lines[index]->getSize(&measuredW, &measuredH);
		m_subtitle->m_lines[index]->setColor(m_subtitle->m_color, dropColor);
		Int lineX = startX + m_subtitle->m_lineX[index];
		m_subtitle->m_lines[index]->draw(lineX, cursorY, 1, 1);
		cursorY += measuredH;
	}

	Int &blockX = blockPos.x;
	blockX = (Int)((Real)(m_subtitle->m_lineX[m_subtitle->m_lineCount] + measuredW)
		+ (g_bfme40BC00 - fraction) * g_bfme4C8615 + startX);
	a = (byte)(Int)((Real)a * fraction);
	UnsignedInt blockColor = (((UnsignedInt)a) << 24)
		| (((UnsignedInt)r) << 16) | (((UnsignedInt)g) << 8) | b;
	UnsignedInt blockDropColor = ((UnsignedInt)a) << 24;
	m_subtitle->m_block->setColor(blockColor, blockDropColor);
	m_subtitle->m_block->draw(blockX, blockY, 1, 1);
}

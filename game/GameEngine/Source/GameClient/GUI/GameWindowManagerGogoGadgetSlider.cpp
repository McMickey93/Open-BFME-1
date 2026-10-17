// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/gamewindowlist /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad

// GameWindowManager slot 20 of the vtable at VA 0x010F8B60, between the
// matched gadget factories at 0x0047D090 and 0x0047D500: Zero Hour's
// gogoGadgetSlider reshaped around the BFME creation descriptor its siblings
// take. Retail ends with ret 0x10 (descriptor, SliderData, font, visual),
// creates the slider through slot 29 and the thumb through
// gogoGadgetPushButton (slot 14) with a second descriptor on the stack.
// ILT slot 11655 contradicts both the Zero Hour decoration and this
// descriptor spelling on GameWindowManager, so the class keeps the address
// token, as the gogoGadgetTextEntry sibling (0x0047FCF0) does. All calls here
// are virtual; the class name changes no byte.

#include <string.h>

class GameFont;
class GameWindow;

class WinInstanceData
{
public:
	WinInstanceData();
	virtual ~WinInstanceData();
	void init();
	unsigned int getStyle() const { return m_style; }

	char m_gap04[0x8];
	unsigned int m_style;
	char m_gap10[0x4];
	GameWindow *m_owner;
	char m_gap18[0x190];
};

class GameWindow
{
public:
	int winSetOwner(GameWindow *owner);
	void winSetUserData(void *data);
};

// The creation descriptor of the BFME gadget factories. Fields keep their
// offsets: +0x10/+0x14 are the width and height the thumb sizes use.
struct Rva0047D2B0FactoryInput
{
	GameWindow *m_owner00;
	unsigned int m_status04;
	int m_field08;
	int m_field0C;
	int m_width10;
	int m_height14;
	int m_field18[6];
	WinInstanceData *m_instData30;
};

typedef struct _SliderData
{
	int minVal;
	int maxVal;
	float numTicks;
	int position;
} SliderData;

class Rva0047D2B0GameWindowManager
{
public:
	virtual void v00();
	virtual void v01();
	virtual void v02();
	virtual void v03();
	virtual void v04();
	virtual void v05();
	virtual void v06();
	virtual void v07();
	virtual void v08();
	virtual void v09();
	virtual void v10();
	virtual void v11();
	virtual void v12();
	virtual void v13();
	virtual GameWindow *gogoGadgetPushButton(Rva0047D2B0FactoryInput *, GameFont *, bool);
	virtual void v15();
	virtual void v16();
	virtual void v17();
	virtual void v18();
	virtual void v19();
	virtual GameWindow *gogoGadgetSlider(Rva0047D2B0FactoryInput *, SliderData *, GameFont *, bool);
	virtual void v21();
	virtual void v22();
	virtual void v23();
	virtual void v24();
	virtual void assignDefaultGadgetLook(GameWindow *, GameFont *, bool);
	virtual void v26();
	virtual void v27();
	virtual void v28();
	virtual GameWindow *winCreate(Rva0047D2B0FactoryInput *);
};

GameWindow *Rva0047D2B0GameWindowManager::gogoGadgetSlider(Rva0047D2B0FactoryInput *input,
	SliderData *sliderData, GameFont *defaultFont, bool defaultVisual)
{
	input->m_status04 |= 0x100;
	GameWindow *slider = winCreate(input);
	if (slider == 0)
		return 0;
	slider->winSetOwner(input->m_owner00);

	WinInstanceData buttonInstData;
	Rva0047D2B0FactoryInput thumb;
	thumb.m_field08 = 0;
	thumb.m_field0C = 0;
	thumb.m_width10 = 0;
	thumb.m_height14 = 0;
	thumb.m_field18[0] = 0;
	thumb.m_field18[1] = 0;
	thumb.m_field18[2] = 0;
	thumb.m_field18[3] = 0;
	thumb.m_field18[4] = 0;
	thumb.m_field18[5] = 0;
	thumb.m_owner00 = slider;
	thumb.m_status04 = input->m_status04 | 0xc;
	thumb.m_instData30 = &buttonInstData;
	buttonInstData.init();
	thumb.m_status04 &= ~0x10;
	buttonInstData.m_owner = slider;
	buttonInstData.m_style = 1;
	if (input->m_instData30->getStyle() & 0x400)
		buttonInstData.m_style |= 0x400;
	if (input->m_instData30->getStyle() & 0x10) {
		thumb.m_field0C = 0;
		thumb.m_width10 = 13;
		thumb.m_height14 = 16;
		gogoGadgetPushButton(&thumb, 0, true);
	} else {
		thumb.m_field0C = 0;
		thumb.m_width10 = input->m_width10;
		thumb.m_height14 = input->m_width10 + 1;
		gogoGadgetPushButton(&thumb, 0, true);
	}

	if (sliderData->maxVal == sliderData->minVal)
		sliderData->maxVal = sliderData->minVal + 1;
	if (input->m_instData30->getStyle() & 0x10)
		sliderData->numTicks = (float)(input->m_width10 - 13) / (sliderData->maxVal - sliderData->minVal);
	else
		sliderData->numTicks = (float)(input->m_height14 - 16) / (sliderData->maxVal - sliderData->minVal);

	SliderData *data = new SliderData;
	memcpy(data, sliderData, sizeof(SliderData));
	slider->winSetUserData(data);
	assignDefaultGadgetLook(slider, defaultFont, defaultVisual);
	return slider;
}

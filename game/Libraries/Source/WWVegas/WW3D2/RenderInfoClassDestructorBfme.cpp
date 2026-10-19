// RenderInfoClass::~RenderInfoClass at retail 0x00923880, 162 bytes.
// Zero Hour's destructor is empty. BFME's pops every pass left on the
// material-pass stack (Pop_Material_Pass inlined: a rejected push only
// decrements the reject count), then drains the second 32-entry pass stack
// that BFME adds at +0x130 the same way. The class is spelled with the retail
// layout of RenderInfoClassConstructorBfme.cpp (whose +0x130/+0x1B0/+0x1B4
// fields are this second stack, its count and reject count) rather than the
// Zero Hour header.

class CameraClass;
class LightEnvironmentClass;
class TexProjectClass;

class MaterialPassClass
{
public:
	virtual void Delete_This();

	void Release_Ref()
	{
		if (--NumRefs == 0)
			Delete_This();
	}

private:
	int NumRefs;
};

class RenderInfoClass
{
public:
	~RenderInfoClass(void);

	enum RINFO_OVERRIDE_FLAGS
	{
		RINFO_OVERRIDE_DEFAULT = 0x0000
	};

	CameraClass &Camera;

	float fog_scale;
	float fog_start;
	float fog_end;
	float alphaOverride;
	float materialPassAlphaOverride;
	float materialPassEmissiveOverride;

	LightEnvironmentClass *light_environment;
	TexProjectClass *Texture_Projector;

protected:
	MaterialPassClass *AdditionalMaterialPassArray[32];
	unsigned AdditionalMaterialPassCount;
	unsigned RejectedMaterialPasses;
	RINFO_OVERRIDE_FLAGS OverrideFlag[32];
	unsigned OverrideFlagLevel;
	MaterialPassClass *SecondMaterialPassArray[32];
	unsigned SecondMaterialPassCount;
	unsigned SecondRejectedMaterialPasses;
};

// ??1RenderInfoClass@@QAE@XZ
RenderInfoClass::~RenderInfoClass(void)
{
	while (AdditionalMaterialPassCount) {
		if (RejectedMaterialPasses == 0) {
			AdditionalMaterialPassCount--;
			MaterialPassClass *mpass = AdditionalMaterialPassArray[AdditionalMaterialPassCount];
			if (mpass)
				mpass->Release_Ref();
		} else {
			RejectedMaterialPasses--;
		}
	}
	while (SecondMaterialPassCount) {
		if (SecondRejectedMaterialPasses) {
			SecondRejectedMaterialPasses--;
		} else {
			SecondMaterialPassCount--;
			MaterialPassClass *mpass = SecondMaterialPassArray[SecondMaterialPassCount];
			if (mpass)
				mpass->Release_Ref();
		}
	}
}

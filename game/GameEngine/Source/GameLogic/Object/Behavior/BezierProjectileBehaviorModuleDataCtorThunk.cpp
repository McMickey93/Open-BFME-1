// cl: /DNDEBUG /MD /EHsc
// Open-BFME5: BezierProjectileBehavior module-data constructor.
//
// The named friend_newModuleData factory at retail 0x001152C0 allocates 0xAC
// bytes and calls this constructor. Landed projectile behavior bodies consume
// the kill flag at +0x18, behavior flag at +0x4A, and four effect pointers at
// +0x94..+0xA0, independently fixing the important parts of this layout.

#include <string.h>

struct BezierProjectileSixWords
{
	void clear()
	{
		memset( m_words, 0, sizeof( m_words ) );
	}

	unsigned int m_words[ 6 ];
};

class BezierProjectileBehaviorModuleData
{
public:
	BezierProjectileBehaviorModuleData();
	virtual ~BezierProjectileBehaviorModuleData();

private:
	unsigned int m_moduleData;
	unsigned int m_firstHeight;
	unsigned int m_secondHeight;
	unsigned int m_firstPercentIndent;
	unsigned int m_secondPercentIndent;
	unsigned char m_killInsteadOfDestroy;
	unsigned char m_dieOnImpact;
	unsigned char m_pad1A[ 2 ];
	unsigned int m_effectFrame;
	unsigned int m_bounceDistance;
	unsigned int m_bounceFirstHeight;
	unsigned int m_bounceSecondHeight;
	unsigned int m_bounceFirstPercentIndent;
	unsigned int m_bounceSecondPercentIndent;
	unsigned int m_value34;
	unsigned int m_finalStuckTime;
	unsigned int m_preLandingStateTime;
	unsigned int m_invisibleFrames;
	unsigned int m_fadeInTime;
	unsigned char m_tumbleRandomly;
	unsigned char m_enabled;
	unsigned char m_objectFire;
	unsigned char m_pad4B;
	unsigned int m_garrisonHitKillCount;
	BezierProjectileSixWords m_firstCurve;
	BezierProjectileSixWords m_secondCurve;
	unsigned int m_garrisonHitKillFX;
	unsigned int m_flightPathAdjustDistPerSecond;
	unsigned char m_flag88;
	unsigned char m_pad89[ 3 ];
	float m_minCurveFraction;
	float m_maxCurveFraction;
	void *m_groundHitFX;
	void *m_groundBounceFX;
	void *m_groundHitWeapon;
	void *m_groundBounceWeapon;
	int m_preLandingEmotion;
	unsigned int m_preLandingEmotionRadius;
};

// ??0BezierProjectileBehaviorModuleData@@QAE@XZ
BezierProjectileBehaviorModuleData::BezierProjectileBehaviorModuleData()
{
	m_firstHeight = 0;
	m_secondHeight = 0;
	m_firstPercentIndent = 0;
	m_secondPercentIndent = 0;
	m_killInsteadOfDestroy = 0;
	m_dieOnImpact = 0;
	m_effectFrame = 0;
	m_bounceDistance = 0;
	m_bounceFirstHeight = 0;
	m_bounceSecondHeight = 0;
	m_bounceFirstPercentIndent = 0;
	m_bounceSecondPercentIndent = 0;
	m_value34 = 0;
	m_finalStuckTime = 0;
	m_preLandingStateTime = 0;
	m_invisibleFrames = 0;
	m_fadeInTime = 0;
	m_tumbleRandomly = 0;
	m_enabled = 1;
	m_objectFire = 0;
	m_garrisonHitKillCount = 0;
	m_firstCurve.clear();
	m_secondCurve.clear();
	m_garrisonHitKillFX = 0;
	m_flightPathAdjustDistPerSecond = 0;
	m_flag88 = 0;
	m_minCurveFraction = 0.33f;
	m_maxCurveFraction = 0.66f;
	m_groundHitFX = 0;
	m_groundBounceFX = 0;
	m_groundHitWeapon = 0;
	m_groundBounceWeapon = 0;
	m_preLandingEmotion = -1;
	m_preLandingEmotionRadius = 0;
}

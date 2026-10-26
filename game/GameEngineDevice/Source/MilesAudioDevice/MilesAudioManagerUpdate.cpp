// cl: /O2 /EHsc /DNDEBUG /DWIN32 /D_WINDOWS /MD /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include
//
// Retail 0x006B9C90, 588 bytes.  Miles audio vtable 0x0111C0C0 slot 5 (+0x14)
// routes through ILT 0x0002BD32 to this body; after BFME's extra
// SubsystemInterface::loadIniFilesFromLegend at slot 2 that is the
// SubsystemInterface::update slot, so this is MilesAudioManager::update.
// The frame builds a LatchRestore<bool> (vtable 0x010892D8, the template the
// landed GameLogic::update also uses) over a function-local re-entry flag.
//
// Under the manager mutex (+0x95C) and the latch it runs the 0x006B7AE0
// re-initialisation once the AudioSettings+0x70 period has elapsed since the
// +0xB68 timestamp and the once-initialised static from 0x006AD9B0 allows it,
// reads virtual slot 99 into +0x44 and raises +0x635.  It then calls the
// per-frame helpers in retail order, updates slot 2 and the current slot of
// the three 0x1C4-byte slots at +0xB8, clears the four request flags, decays
// every slot's counters and frees a finished +0xB58 job.

#include "Common/LatchRestore.h"

extern "C" __declspec(dllimport) unsigned long __stdcall WaitForSingleObject(
	void *handle, unsigned long milliseconds);
extern "C" __declspec(dllimport) int __stdcall ReleaseMutex(void *handle);
extern "C" __declspec(dllimport) __int64 __cdecl _time64(__int64 *timer);

extern void j_0000c30b();
extern void j_0002f68f();
extern void j_00048c84();
extern void j_00002f13();
extern void j_00019dad();
extern void j_0002e6ae();
extern void j_0004ac82();
extern void j_00044be3();
extern void j_0003d7d0();
extern void j_00017f85();
extern void j_00047cee();
extern void j_0000d33c();
extern void j_0002f1d5();
extern void j_00044661();

class GameEngine;
class GameLogic;
extern GameEngine *TheGameEngine;
extern GameLogic *TheGameLogic;  // retail 0x012F0898; data_rows.csv line 976 owns this name there

class BfmeGameLogicPause
{
public:
	bool isGamePaused();
};

struct Rva006B9C90EngineState
{
	char pad00[0x30];
	int dword_30;
};

class Rva006B9C90MutexGuard
{
public:
	Rva006B9C90MutexGuard(void *handle)
	{
		m_owned = 0;
		m_handle = handle;
		if (WaitForSingleObject(handle, 0xFFFFFFFF) != 0x102)
			m_owned = 1;
	}

	~Rva006B9C90MutexGuard()
	{
		if (m_owned)
		{
			ReleaseMutex(m_handle);
			m_owned = 0;
		}
	}

private:
	void *m_handle;
	char m_owned;
};

struct AudioSettings
{
	char pad00[0x70];
	int dword_70;
};

// Out-parameter the 0x006B2FC0 and 0x006B69F0 helpers fill.  Retail packs
// it into the latch's 12-byte slot, which an int alone does not reproduce.
struct Rva006B9C90Scratch
{
	int dword_0;
	int dword_4;
	int dword_8;
};

class Rva006B9C90Slot
{
public:
	char pad[0x1c4];
};

struct Rva006B9C90Job
{
	char pad00[0x08];
	char *m_begin;
	char *m_end;
	char pad10[0x14 - 0x10];
	int m_status;
};

class MilesAudioManager
{
public:
	virtual void vslot00(); virtual void vslot01(); virtual void vslot02(); virtual void vslot03();
	virtual void vslot04();
	virtual void update();
	virtual void vslot06(); virtual void vslot07();
	virtual void vslot08(); virtual void vslot09(); virtual void vslot10(); virtual void vslot11();
	virtual void vslot12(); virtual void vslot13(); virtual void vslot14(); virtual void vslot15();
	virtual void vslot16(); virtual void vslot17(); virtual void vslot18(); virtual void vslot19();
	virtual void vslot20(); virtual void vslot21(); virtual void vslot22(); virtual void vslot23();
	virtual void vslot24(); virtual void vslot25(); virtual void vslot26(); virtual void vslot27();
	virtual void vslot28(); virtual void vslot29(); virtual void vslot30(); virtual void vslot31();
	virtual void vslot32(); virtual void vslot33(); virtual void vslot34(); virtual void vslot35();
	virtual void vslot36(); virtual void vslot37(); virtual void vslot38(); virtual void vslot39();
	virtual void vslot40(); virtual void vslot41(); virtual void vslot42(); virtual void vslot43();
	virtual void vslot44(); virtual void vslot45(); virtual void vslot46(); virtual void vslot47();
	virtual void vslot48(); virtual void vslot49(); virtual void vslot50(); virtual void vslot51();
	virtual void vslot52(); virtual void vslot53(); virtual void vslot54(); virtual void vslot55();
	virtual void vslot56(); virtual void vslot57(); virtual void vslot58(); virtual void vslot59();
	virtual void vslot60(); virtual void vslot61(); virtual void vslot62(); virtual void vslot63();
	virtual void vslot64(); virtual void vslot65(); virtual void vslot66(); virtual void vslot67();
	virtual void vslot68(); virtual void vslot69(); virtual void vslot70(); virtual void vslot71();
	virtual void vslot72(); virtual void vslot73(); virtual void vslot74(); virtual void vslot75();
	virtual void vslot76(); virtual void vslot77(); virtual void vslot78(); virtual void vslot79();
	virtual void vslot80(); virtual void vslot81(); virtual void vslot82(); virtual void vslot83();
	virtual void vslot84(); virtual void vslot85(); virtual void vslot86(); virtual void vslot87();
	virtual void vslot88(); virtual void vslot89(); virtual void vslot90(); virtual void vslot91();
	virtual void vslot92(); virtual void vslot93(); virtual void vslot94(); virtual void vslot95();
	virtual void vslot96(); virtual void vslot97(); virtual void vslot98();
	virtual float vslot99();

private:
	char pad008[0x0c - 0x08];
	AudioSettings *m_audioSettings;
	char pad010[0x44 - 0x10];
	float float_44;
	char pad048[0xb8 - 0x48];
	Rva006B9C90Slot m_slots[3];
	int dword_604;
	char pad608[0x631 - 0x608];
	unsigned char byte_631;
	char pad632[0x634 - 0x632];
	unsigned char byte_634;
	unsigned char byte_635;
	unsigned char byte_636;
	char pad637[0x95c - 0x637];
	void *m_mutex;
	char pad960[0xadc - 0x960];
	int *m_pairsBegin;
	int *m_pairsEnd;
	char padae4[0xb58 - 0xae4];
	Rva006B9C90Job *m_job;
	char padb5c[0xb68 - 0xb5c];
	__int64 qword_b68;
};

void MilesAudioManager::update()
{
	typedef void (MilesAudioManager::*VoidFn)();
	typedef bool (MilesAudioManager::*BoolFn)();
	typedef void (MilesAudioManager::*PtrFn)(Rva006B9C90Scratch *);
	typedef void (Rva006B9C90Slot::*SlotUpdateFn)(float);
	typedef void (Rva006B9C90Slot::*SlotFn)();
	typedef void (Rva006B9C90Job::*JobFn)();

	void *handle = m_mutex;
	Rva006B9C90MutexGuard guard(handle);

	static bool s_inUpdate = false;
	if (s_inUpdate)
		return;

	{
		LatchRestore<bool> latch(s_inUpdate, true);

		if (m_audioSettings->dword_70 > 0 &&
			_time64(0) - qword_b68 > m_audioSettings->dword_70)
		{
			union { void (__cdecl *freeFunction)(); BoolFn memberFunction; } call2f1d5;
			call2f1d5.freeFunction = ::j_0002f1d5;
			static bool s_allowReinit = (this->*call2f1d5.memberFunction)();
			if (s_allowReinit)
			{
				union { void (__cdecl *freeFunction)(); VoidFn memberFunction; } call44661;
				call44661.freeFunction = ::j_00044661;
				(this->*call44661.memberFunction)();
			}
		}

		float_44 = vslot99();

		if (byte_636 || (m_pairsBegin != m_pairsEnd && TheGameEngine != 0 &&
			((Rva006B9C90EngineState *)TheGameEngine)->dword_30 == 1))
			byte_635 = 1;
	}

	union { void (__cdecl *freeFunction)(); VoidFn memberFunction; } callc30b;
	callc30b.freeFunction = ::j_0000c30b;
	(this->*callc30b.memberFunction)();

	union { void (__cdecl *freeFunction)(); SlotUpdateFn memberFunction; } call2f68f;
	call2f68f.freeFunction = ::j_0002f68f;
	(m_slots[2].*call2f68f.memberFunction)(float_44);
	if (dword_604 != 2 && TheGameLogic != 0 &&
		!((BfmeGameLogicPause *)TheGameLogic)->isGamePaused())
		(m_slots[dword_604].*call2f68f.memberFunction)(float_44);

	union { void (__cdecl *freeFunction)(); VoidFn memberFunction; } call48c84;
	call48c84.freeFunction = ::j_00048c84;
	(this->*call48c84.memberFunction)();
	union { void (__cdecl *freeFunction)(); VoidFn memberFunction; } call2f13;
	call2f13.freeFunction = ::j_00002f13;
	(this->*call2f13.memberFunction)();
	union { void (__cdecl *freeFunction)(); VoidFn memberFunction; } call19dad;
	call19dad.freeFunction = ::j_00019dad;
	(this->*call19dad.memberFunction)();
	union { void (__cdecl *freeFunction)(); VoidFn memberFunction; } call2e6ae;
	call2e6ae.freeFunction = ::j_0002e6ae;
	(this->*call2e6ae.memberFunction)();

	{
		Rva006B9C90Scratch scratch;
		union { void (__cdecl *freeFunction)(); PtrFn memberFunction; } call4ac82;
		call4ac82.freeFunction = ::j_0004ac82;
		(this->*call4ac82.memberFunction)(&scratch);
		union { void (__cdecl *freeFunction)(); PtrFn memberFunction; } call44be3;
		call44be3.freeFunction = ::j_00044be3;
		(this->*call44be3.memberFunction)(&scratch);
	}
	union { void (__cdecl *freeFunction)(); VoidFn memberFunction; } call3d7d0;
	call3d7d0.freeFunction = ::j_0003d7d0;
	(this->*call3d7d0.memberFunction)();
	union { void (__cdecl *freeFunction)(); VoidFn memberFunction; } call17f85;
	call17f85.freeFunction = ::j_00017f85;
	(this->*call17f85.memberFunction)();

	byte_631 = 0;
	byte_634 = 0;
	byte_635 = 0;
	byte_636 = 0;

	union { void (__cdecl *freeFunction)(); SlotFn memberFunction; } call47cee;
	call47cee.freeFunction = ::j_00047cee;
	for (int i = 0; i < 3; ++i)
		(m_slots[i].*call47cee.memberFunction)();

	Rva006B9C90Job *job = m_job;
	if (job != 0 && job->m_status == 1 &&
		!((unsigned int)((job->m_end - job->m_begin) >> 3) > 0))
	{
		union { void (__cdecl *freeFunction)(); JobFn memberFunction; } calld33c;
		calld33c.freeFunction = ::j_0000d33c;
		(job->*calld33c.memberFunction)();
		::operator delete(job);
		m_job = 0;
	}
}

// cl: /DNDEBUG /DWIN32 /D_WINDOWS /DBFME_MODULE_NO_MPO /MD /EHsc /Iinputs/reference/shims/specialpowermoduledata /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad
// stlport
#define Matrix4x4 Matrix4  // BFME renamed it
/*
**	Command & Conquer Generals Zero Hour(tm)
**	Copyright 2025 Electronic Arts Inc.
**
**	This program is free software: you can redistribute it and/or modify
**	it under the terms of the GNU General Public License as published by
**	the Free Software Foundation, either version 3 of the License, or
**	(at your option) any later version.
**
**	This program is distributed in the hope that it will be useful,
**	but WITHOUT ANY WARRANTY; without even the implied warranty of
**	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
**	GNU General Public License for more details.
**
**	You should have received a copy of the GNU General Public License
**	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

////////////////////////////////////////////////////////////////////////////////
//																																						//
//  (c) 2001-2003 Electronic Arts Inc.																				//
//																																						//
////////////////////////////////////////////////////////////////////////////////

// FILE: CashHackSpecialPower.cpp /////////////////////////////////////////////////////////////
// Author: Amit Kumar, July 2002
// Desc:   The Cash Hack will steal money from an enemy player
///////////////////////////////////////////////////////////////////////////////////////////////////

// INCLUDES ///////////////////////////////////////////////////////////////////////////////////////
#include "PreRTS.h"	// This must go first in EVERY cpp file int the GameEngine

#include "Common/Player.h"
#include "Common/Team.h"
#include "Common/Xfer.h"
#include "GameClient/GameText.h"
#include "GameLogic/Object.h"
#include "GameLogic/PartitionManager.h"
#include "GameLogic/Module/CashHackSpecialPower.h"
#include "GameClient/InGameUI.h"

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// byte-exact reconstruction: game/GameEngine/Source/GameLogic/Object/SpecialPower/CashHackSpecialPowerModuleDataConstructor.cpp
// ??0CashHackSpecialPowerModuleData@@QAE@XZ present-unmatched
CashHackSpecialPowerModuleData::CashHackSpecialPowerModuleData( void )
{
	m_upgrades.clear();
	m_defaultAmountToSteal = 0;
}

//-------------------------------------------------------------------------------------------------
//-------------------------------------------------------------------------------------------------
static void parseCashHackUpgradePair( INI* ini, void * /*instance*/, void *store, const void* /*userData*/ )
{
	CashHackSpecialPowerModuleData::Upgrades up;

	INI::parseScience(ini, NULL, &up.m_science, NULL);
	INI::parseInt(ini, NULL, &up.m_amountToSteal, NULL);

	std::vector<CashHackSpecialPowerModuleData::Upgrades>* s = (std::vector<CashHackSpecialPowerModuleData::Upgrades>*)store;
	s->push_back(up);
} 

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
/*static*/ void CashHackSpecialPowerModuleData::buildFieldParse(MultiIniFieldParse& p)
{
	SpecialPowerModuleData::buildFieldParse( p );
	
	static const FieldParse dataFieldParse[] = 
	{
		{ "UpgradeMoneyAmount", parseCashHackUpgradePair, NULL, offsetof( CashHackSpecialPowerModuleData, m_upgrades ) },
		{ "MoneyAmount", INI::parseInt, NULL, offsetof( CashHackSpecialPowerModuleData, m_defaultAmountToSteal ) },
		{ 0, 0, 0, 0 }
	};
	p.add(dataFieldParse);
	
}  // end buildFieldParse

///////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// The module hierarchy needs BFME_MODULE_NO_MPO on this file's own cl line:
// retail's Module has no MemoryPoolObject base, so BehaviorModule spans 0x0C
// and this constructor's second vtable store lands at +0x0C, where the wider
// layout puts a fourth vptr at +0x04 and +0x14 and shifts everything.
CashHackSpecialPower::CashHackSpecialPower( Thing *thing, const ModuleData *moduleData )
												: SpecialPowerModule( thing, moduleData )
{

}  // end CashHackSpecialPower

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// Protected visibility preserves retail's MAE destructor and deleting-wrapper symbols.
CashHackSpecialPower::~CashHackSpecialPower( void )
{

}  // end ~CashHackSpecialPower

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
void CashHackSpecialPower::doSpecialPowerAtLocation( const Coord3D *loc, Real angle, UnsignedInt commandOptions )
{
	if (getObject()->isDisabled())
		return;

	// only allowed at objects
	return;
}  

//-------------------------------------------------------------------------------------------------
//-------------------------------------------------------------------------------------------------
// ?findAmountToSteal@CashHackSpecialPower@@IBEHXZ is emitted by
// CashHackSpecialPowerFindAmountToStealThunk.cpp.

typedef std::vector<CashHackSpecialPowerModuleData::Upgrades> CashHackUpgradesVector;
typedef CashHackUpgradesVector::iterator (CashHackUpgradesVector::*CashHackBegin)();
typedef CashHackUpgradesVector::const_iterator (CashHackUpgradesVector::*CashHackConstBegin)() const;
static volatile CashHackBegin cashHackBeginAnchor = &CashHackUpgradesVector::begin;
static volatile CashHackConstBegin cashHackConstBeginAnchor = &CashHackUpgradesVector::begin;

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// Retail action 0x00258800..0x002589B7; GUI:AddCash/GUI:LoseCash anchors.
// BFME2 2a0f7acb06 CashHackSpecialPowerAction independent tracker access
// guides this BFME1 reconstruction. E8B20 is the existing GameLogic-gated
// bfmeAddCount provider rather than ungated ScoreKeeper C85F0.
class Gen_000E8AF0 { public: void bfmeAddCount(int); };
class Rva00258800Player : public Player {
public:
 Money *at48Money() { return reinterpret_cast<Money *>(reinterpret_cast<char *>(this)+0x48); }
 Gen_000E8AF0 *at348Tracker() { return reinterpret_cast<Gen_000E8AF0 *>(reinterpret_cast<char *>(this)+0x348); }
};
class Rva00258800UiView
{
public:
#define INGAME_UI_SLOT(n) virtual void slot##n() = 0
	INGAME_UI_SLOT(00); INGAME_UI_SLOT(01); INGAME_UI_SLOT(02); INGAME_UI_SLOT(03);
	INGAME_UI_SLOT(04); INGAME_UI_SLOT(05); INGAME_UI_SLOT(06); INGAME_UI_SLOT(07);
	INGAME_UI_SLOT(08); INGAME_UI_SLOT(09); INGAME_UI_SLOT(10); INGAME_UI_SLOT(11);
	INGAME_UI_SLOT(12); INGAME_UI_SLOT(13); INGAME_UI_SLOT(14); INGAME_UI_SLOT(15);
	INGAME_UI_SLOT(16); INGAME_UI_SLOT(17); INGAME_UI_SLOT(18); INGAME_UI_SLOT(19);
	INGAME_UI_SLOT(20); INGAME_UI_SLOT(21); INGAME_UI_SLOT(22); INGAME_UI_SLOT(23);
	INGAME_UI_SLOT(24); INGAME_UI_SLOT(25); INGAME_UI_SLOT(26); INGAME_UI_SLOT(27);
	INGAME_UI_SLOT(28); INGAME_UI_SLOT(29); INGAME_UI_SLOT(30); INGAME_UI_SLOT(31);
	INGAME_UI_SLOT(32); INGAME_UI_SLOT(33); INGAME_UI_SLOT(34); INGAME_UI_SLOT(35);
	INGAME_UI_SLOT(36); INGAME_UI_SLOT(37); INGAME_UI_SLOT(38); INGAME_UI_SLOT(39);
	INGAME_UI_SLOT(40); INGAME_UI_SLOT(41); INGAME_UI_SLOT(42); INGAME_UI_SLOT(43);
	INGAME_UI_SLOT(44); INGAME_UI_SLOT(45); INGAME_UI_SLOT(46); INGAME_UI_SLOT(47);
	INGAME_UI_SLOT(48); INGAME_UI_SLOT(49); INGAME_UI_SLOT(50); INGAME_UI_SLOT(51);
	INGAME_UI_SLOT(52); INGAME_UI_SLOT(53); INGAME_UI_SLOT(54); INGAME_UI_SLOT(55);
	INGAME_UI_SLOT(56); INGAME_UI_SLOT(57); INGAME_UI_SLOT(58); INGAME_UI_SLOT(59);
	INGAME_UI_SLOT(60); INGAME_UI_SLOT(61); INGAME_UI_SLOT(62); INGAME_UI_SLOT(63);
	INGAME_UI_SLOT(64); INGAME_UI_SLOT(65); INGAME_UI_SLOT(66); INGAME_UI_SLOT(67);
	INGAME_UI_SLOT(68); INGAME_UI_SLOT(69); INGAME_UI_SLOT(70); INGAME_UI_SLOT(71);
	INGAME_UI_SLOT(72); INGAME_UI_SLOT(73); INGAME_UI_SLOT(74); INGAME_UI_SLOT(75);
	INGAME_UI_SLOT(76); INGAME_UI_SLOT(77); INGAME_UI_SLOT(78); INGAME_UI_SLOT(79);
	INGAME_UI_SLOT(80); INGAME_UI_SLOT(81); INGAME_UI_SLOT(82); INGAME_UI_SLOT(83);
	INGAME_UI_SLOT(84); INGAME_UI_SLOT(85); INGAME_UI_SLOT(86); INGAME_UI_SLOT(87);
	INGAME_UI_SLOT(88); INGAME_UI_SLOT(89); INGAME_UI_SLOT(90); INGAME_UI_SLOT(91);
	INGAME_UI_SLOT(92); INGAME_UI_SLOT(93);
#undef INGAME_UI_SLOT
	virtual void addFloatingText(const UnicodeString &text, const Coord3D *position,
		UnsignedInt color) = 0;
};


static __forceinline const UnsignedInt &cashMinimum(const UnsignedInt &desired,
	const UnsignedInt &available)
{
	return desired < available ? desired : available;
}

void CashHackSpecialPower::doSpecialPowerAtObject(Object *victim, UnsignedInt commandOptions)
{
	if (getObject()->isDisabled())
		return;

	// sanity
	if (!victim)
		return;

	// call the base class action cause we are *EXTENDING* functionality
	SpecialPowerModule::doSpecialPowerAtObject(victim, commandOptions);

	// get our module data
	Object *self = getObject();

	//Steal a thousand cash from the other team!
	Money *targetMoney = reinterpret_cast<Rva00258800Player *>(victim->getControllingPlayer())->at48Money();
	Money *selfMoney = reinterpret_cast<Rva00258800Player *>(self->getControllingPlayer())->at48Money();
	if (targetMoney && selfMoney)
	{
		UnsignedInt cash = targetMoney->countMoney();
		UnsignedInt desiredAmount = findAmountToSteal();
		//Check to see if they have 1000 cash, otherwise, take the remainder!
		cash = cashMinimum(desiredAmount, cash);
		if (cash > 0)
		{
			//Steal the cash
			targetMoney->withdraw(cash);
			selfMoney->deposit(cash);
			reinterpret_cast<Rva00258800Player *>(self->getControllingPlayer())->at348Tracker()->bfmeAddCount(cash);

			//Display cash income floating over the blacklotus
			UnicodeString moneyString;
			moneyString.format(TheGameText->fetch("GUI:AddCash"), cash);
			Coord3D pos;
			pos.zero();
			pos.add(self->getPosition());
			pos.z += 20.0f; //add a little z to make it show up above the unit.
			reinterpret_cast<Rva00258800UiView *>(TheInGameUI)->addFloatingText(moneyString, &pos, GameMakeColor(0, 255, 0, 255));

			//Display cash lost floating over the target
			moneyString.format(TheGameText->fetch("GUI:LoseCash"), cash);
			pos.zero();
			pos.add(victim->getPosition());
			pos.z += 30.0f; //add a little z to make it show up above the unit.
			reinterpret_cast<Rva00258800UiView *>(TheInGameUI)->addFloatingText(moneyString, &pos, GameMakeColor(255, 0, 0, 255));
		}
	}

}

// ------------------------------------------------------------------------------------------------
/** CRC */
// ------------------------------------------------------------------------------------------------
// ?crc@CashHackSpecialPower@@MAEXPAVXfer@@@Z present-unmatched
void CashHackSpecialPower::crc( Xfer *xfer )
{

	// extend base class
	SpecialPowerModule::crc( xfer );

}  // end crc

// ------------------------------------------------------------------------------------------------
/** Xfer method
	* Version Info:
	* 1: Initial version */
// ------------------------------------------------------------------------------------------------
// ?xfer@CashHackSpecialPower@@MAEXPAVXfer@@@Z present-unmatched
void CashHackSpecialPower::xfer( Xfer *xfer )
{

	// version
	XferVersion currentVersion = 1;
	XferVersion version = currentVersion;
	xfer->xferVersion( &version, currentVersion );

	// extend base class
	SpecialPowerModule::xfer( xfer );

}  // end xfer

// ------------------------------------------------------------------------------------------------
/** Load post process */
// ------------------------------------------------------------------------------------------------
// ?loadPostProcess@CashHackSpecialPower@@MAEXXZ present-unmatched
void CashHackSpecialPower::loadPostProcess( void )
{

	// extend base class
	SpecialPowerModule::loadPostProcess();

}  // end loadPostProcess

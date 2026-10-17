# 0x00853CB0 INI::load(AsciiString, int, Xfer*, INIBlockParse): exact body, gate-blocked

Session a2/48, 2026-10-17, model=claude-opus-5-5.

## Identity and boundary

- Retail 0x00853CB0..0x00853EC0 (528 B, ret 0x10 at 0x00853EBD). setFPMode; s_xfer = arg 3 (store to 0x0130CE54 at 0x00853CF1); prepFile(filename, loadType); per-line strtok, then the fourth argument is called cdecl with the INI pointer (0x00853D5F) instead of findBlockParse. The three INIException throw sites and texts are parseLine's (0x00851350).
- Outer catches are 0x00853E3A (catch INIException&, 36 B) and 0x00853E5E (catch-all, unPrepFile + rethrow, 17 B), named by FuncInfo 0x00E45944. The inlined unPrepFile tail runs 0x00853E6F..0x00853EC0.
- The gen-dump row's 345 B cuts `mov esi,[esi+4]` at +0x157, so the verifier refuses that extent. 394 B (up to the first outer catch) verifies.
- Callers that spell it as the unresolved link-queue #17 name `?load@INI@@QAEXVAsciiString@@HHPAX@Z`: VideoPlayer::init (0x0081CB30), Gen_0081DBE0::bfmeLoad_0081DD20, INI::loadSubsystemFiles (0x000BB310), MapCache::loadStandardMaps (0x004507A0).

## Why it is not landed

The declaration has to go into inputs/reference/shims/ini_parser/Common/INI.h and game/GameEngine/Include/Common/INI/INI.h. Either edit makes tools/header_dependents.py reach 1,646 sources, INIMapCache.cpp among them. INIMapCache.cpp's two insert_unique rows at 0x0064CBD0 are already red on origin: their less<AsciiString> call resolves to 0x62FA0, but retail calls ILT 0x1C01C (pin retired in fdfa67e1f9). The pre-commit scoped header gate therefore fails, even with every changed TU green (ini.cpp 58/58 plus both catch rows; caller TUs 1/1, 1/1, 2/2 and 3/3).

## Landing recipe

To land, once INIMapCache.cpp is green again:
1. Paste the body below into game/GameEngine/Source/Common/INI/ini.cpp right after
   the 3-argument INI::load ("}  // end load").
2. inputs/reference/shims/ini_parser/Common/INI.h, after the 3-arg load declaration:
     void load( AsciiString filename, Int loadType, Xfer *pXfer, INIBlockParse parse );
3. game/GameEngine/Include/Common/INI/INI.h: replace
     void load(AsciiString filename, int loadType, int reload, void* xfer);
   with
     void load(AsciiString filename, int loadType, Xfer* xfer, void (*parse)(INI*));
   and the TU-local INI views in GameClient/VideoPlayerInit.cpp and
   GameClient/MapCacheLoad.cpp the same way (add `class Xfer;`). Callers cast the
   4th argument to (void (*)(INI *)): Gen0081DBE0Load.cpp, VideoPlayerInit.cpp (x3),
   MapCacheLoad.cpp, ini_subsystem.cpp. All four caller TUs were green with that.
4. Delete the wrong symbols.csv pin ?load@INI@@QAEXVAsciiString@@HHPAX@Z,0x00853CB0
   (the HPAVXfer@@P6AXPAV1@@Z@Z pin at the same address is the right one).
5. Ledger: add_match <name> 0x00853CB0 394 ini.cpp --replace-rva 0x00853CB0
   --boundary-evidence (the 345 B gen-dump cuts `mov esi,[esi+4]` at +0x157; 394 runs
   to the outer catch at 0x00853E3A). Then rebind the gen_asm catch rows:
   ?dup_00853E3A@@YAXXZ 0x00853E3A 36 (compiler-catch;parent=<name>;object-symbol=$L at
   body +0x18A) and ?dup_00853E5E@@YAXXZ 0x00853E5E 17 ($L at +0x1AE). The labels
   were $L64060/$L64061 in build/match (the data-row probe object numbers them
   differently). Then eh_state_pins.py --source ini.cpp --fix (it renumbers 8 uw pins).
6. The link queue #17 name ?load@INI@@QAEXVAsciiString@@HHPAX@Z then disappears.

## Body (probe EXACT 528/528, modulo relocations)

```cpp
//-------------------------------------------------------------------------------------------------
//-------------------------------------------------------------------------------------------------
// ?load@INI@@QAEXVAsciiString@@HPAVXfer@@P6AXPAV1@@Z@Z
// Retail 0x00853CB0, 528 bytes including its four catch blocks. BFME's loader
// for files whose blocks all share one parser (Video.ini, the subtitle files):
// the parser comes in as the fourth argument and parseLine's dispatch is
// written inline, so a missing parser is reported exactly like an unknown
// block keyword.
//
// The first catch reads the file name and both exception fields into locals
// before it throws. Spelled as one argument list instead, MSVC pushes the name
// as soon as it has it and every catch block of the function comes out with
// its registers rotated one step from retail's.
void INI::load( AsciiString filename, Int loadType, Xfer *pXfer, INIBlockParse parse )
{
	setFPMode();

	s_xfer = pXfer;
	prepFile(filename, (INILoadType)loadType);

	try
	{
		while( m_endOfFile == FALSE )
		{
			readLine();

			const char *token = strtok( m_buffer, m_seps );
			if( token )
			{
				if( parse )
				{
					strcpy(m_curBlockStart, m_buffer);
					try
					{
						(*parse)( this );
					}
					catch( INIException& e )
					{
						const char *file = m_filename.str();
						char *message = e.mFailureMessage;
						int argCount = e.m_argCount;
						throw INIException( argCount,
							"%s\n\nError parsing INI block '%s' in file '%s'.",
							message, token, file );
					}
					catch (...)
					{
						throw INIException( 8,
							"Unknown error parsing INI block '%s' in file '%s'.",
							token, m_filename.str() );
					}
					strcpy(m_curBlockStart, "NO_BLOCK");
				}
				else
				{
					throw INIException( 5,
						"Unknown block '%s'.\n\nError parsing INI block '%s' in file '%s'.",
						token, token, m_filename.str() );
				}
			}
		}
	}
	catch( INIException& e )
	{
		throw INIException( e.m_argCount, e.mFailureMessage );
	}
	catch (...)
	{
		unPrepFile();
		throw;
	}

	unPrepFile();

}  // end load
```

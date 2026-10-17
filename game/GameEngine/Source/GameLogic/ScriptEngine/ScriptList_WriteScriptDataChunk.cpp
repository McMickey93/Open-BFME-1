// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// BFME script handles keep older versions alive so editor references remain stable.

#include "ascii_string.h"

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/DataChunk.h
class DataChunkOutput
{
public:
	void openDataChunk(char *name, unsigned short version);
	void closeDataChunk();
	void writeAsciiString(const AsciiString &string);
	void writeByte(char value);
};

class Script;
class ScriptGroup;

struct ScriptData
{
	ScriptData *previousVersion;
	void *unused;
	Script *childGroups;
	Script *scripts;
	bool active;
	bool subroutine;
};

struct ScriptRecord
{
	char unused[8];
	AsciiString name;
	bool deleted;
	char alignment;
	volatile short version;
	ScriptData *data;
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/Scripts.h
class ScriptList
{
private:
	char unused[0x18];
	ScriptRecord *records;

	friend void WriteScriptDataChunk(DataChunkOutput &, ScriptList *, Script *);
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/Scripts.h
class Script
{
private:
	Script *next;
	int recordIndex;
	volatile int version;

	friend void WriteScriptDataChunk(DataChunkOutput &, ScriptList *, Script *);
};

// ILT 0x000285D3 -> 0x00357B30, the "Script" chunk writer for a chain of
// script handles; see targets/game/reverse/identity_evidence/00357b30-script-chunk-writer.md.
void j_000285d3(DataChunkOutput &output, ScriptList *list, Script *script);

void WriteScriptDataChunk(DataChunkOutput &output, ScriptList *list, Script *script)
{
	while (script)
	{
		int recordIndex = script->recordIndex;
		ScriptRecord *records = list->records;
		int scriptVersion = script->version;
		ScriptRecord *record = &records[recordIndex];
		if (record->version == scriptVersion && !record->deleted)
		{
			int recordVersion = record->version;
			ScriptData *data = record->data;
			if (recordVersion > scriptVersion)
			{
				int versionsBack = recordVersion - scriptVersion;
				do
				{
					--versionsBack;
					data = data->previousVersion;
				} while (versionsBack);
			}

			output.openDataChunk("ScriptGroup", 3);
			output.writeAsciiString(list->records[script->recordIndex].name);
			output.writeByte(data->active);
			output.writeByte(data->subroutine);
			if (data->childGroups)
				WriteScriptDataChunk(output, list, data->childGroups);
			if (data->scripts)
				j_000285d3(output, list, data->scripts);
			output.closeDataChunk();
		}
		script = script->next;
	}
}

// ?provideBattleStat@BfmeAptScreenScoreScreen@@QAEXHPAD_N@Z
// partial score=0.4397 date=2026-10-23
// ?provideBattleStat@BfmeAptScreenScoreScreen@@QAEXHPAD_N@Z
// cl: /DNDEBUG /MD /EHsc

extern "C" int __declspec(dllimport) __cdecl sprintf(
	char *buffer, const char *format, ... );

class BfmeAptScreenScoreScreen
{
public:
	void provideBattleStat( int index, char *text, bool setting );

	unsigned char m_unmodelled00[0x294];
	int m_battleStats[7][3];				// +0x294
};

void BfmeAptScreenScoreScreen::provideBattleStat(
	int index, char *text, bool setting )
{
	if (setting)
		return;

	int row = index / 3;
	int column = index % 3;
	*(short *)text = '0';
	if (row < 0 || row >= 7 || column < 0 || column >= 3)
		return;

	if (column == 1)
		sprintf(text, "x %d", m_battleStats[row][1]);
	else
		sprintf(text, "%d", m_battleStats[row][column]);
}

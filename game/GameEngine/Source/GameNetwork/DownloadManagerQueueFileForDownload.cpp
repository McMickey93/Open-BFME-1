// cl: /D_STLP_USE_STATIC_LIB /DBFME_STLP_NODE_ALLOC /D_STLP_NO_EXCEPTIONS /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/asciistring_downloadmanager /Iinputs/reference/shims/stlp_nodealloc /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Icode/Libraries/Source/WWVegas/WWLib
// stlport
#define _STLP_NO_EXCEPTIONS 1
#define Matrix4x4 Matrix4
#define __PLACEMENT_VEC_NEW_INLINE

#include "PreRTS.h"

#include "GameNetwork/DownloadManager.h"

// Retail inlines ~AsciiString: temporaries are released by a direct call to
// StringBase<char>::releaseBuffer (0x00887940), not the ??1AsciiString stub.
inline AsciiString::~AsciiString() { ((StringBase<char> *)this)->releaseBuffer(); }

class Open2Rec6270C0
{
public:
	Open2Rec6270C0( const Open2Rec6270C0 &other );
};

// Keep this unit's list instantiation separate, but use the shared record's
// lifetime and destructor (also used by BFME2's DownloadManager.cpp).
class BfmeErasedValue_00627200 : public QueuedDownload
{
public:
    BfmeErasedValue_00627200() {}
    __forceinline ~BfmeErasedValue_00627200() {}
};

namespace std
{
template <>
inline void _Construct<BfmeErasedValue_00627200, BfmeErasedValue_00627200>(
	BfmeErasedValue_00627200 *place, const BfmeErasedValue_00627200 &value )
{
	new ( place ) Open2Rec6270C0( *(const Open2Rec6270C0 *)&value );
}
}

class Rva00627810DownloadManager
{
public:
	void queueFileForDownload( AsciiString server, AsciiString username,
		AsciiString password, AsciiString file, AsciiString localfile,
		AsciiString regkey, Bool tryResume );

private:
	unsigned char m_prefix[0x18];
	std::list<BfmeErasedValue_00627200> m_queuedDownloads;
};

// ?queueFileForDownload@DownloadManager@@QAEXVAsciiString@@00000_N@Z
void Rva00627810DownloadManager::queueFileForDownload( AsciiString server, AsciiString username, AsciiString password, AsciiString file, AsciiString localfile, AsciiString regkey, Bool tryResume )
{
	BfmeErasedValue_00627200 q;
	q.file = file;
	q.localFile = localfile;
	q.password = password;
	q.regKey = regkey;
	q.server = server;
	q.tryResume = tryResume;
	q.userName = username;

	m_queuedDownloads.push_back(q);
}

// cl: /DNDEBUG /MD /EHsc
//
// Complete destructors of thirteen NetCommandMsg subclasses (7 bytes each):
// `mov [ecx], ??_7NetCommandMsg@@6B@ / ret`. Each subclass destructor is
// empty and does not re-seat its own vftable; the only store is the inlined
// empty ~NetCommandMsg putting the base vftable (0x0111A20C) back. Each body
// is the one behind the ILT its class's ??_G calls, and ilt_oracle CONFIRMS
// the ??1 name at that ILT:
//   0x006628B0 ~NetFrameCommandMsg               ILT 0x000265D0
//   0x006738F0 ~NetAckStage1CommandMsg           ILT 0x00037C40
//   0x006739F0 ~NetAckStage2CommandMsg           ILT 0x000391FD
//   0x00673AE0 ~NetPlayerLeaveCommandMsg         ILT 0x00034A45
//   0x00673B50 ~NetDestroyPlayerCommandMsg       ILT 0x0000B8C0
//   0x00673BC0 ~NetKeepAliveCommandMsg           ILT 0x00013949
//   0x00673C10 ~NetDisconnectKeepAliveCommandMsg ILT 0x0002C070
//   0x00673C60 ~NetDisconnectPlayerCommandMsg    ILT 0x00047B77
//   0x00673D10 ~NetDisconnectVoteCommandMsg      ILT 0x0003C81C
//   0x00673DA0 ~NetProgressCommandMsg            ILT 0x00003E04
//   0x00674070 ~NetFileProgressCommandMsg        ILT 0x000342F2
//   0x00674100 ~NetDisconnectFrameCommandMsg     ILT 0x0000AAFB
//   0x00674350 ~NetDisconnectScreenOffCommandMsg ILT 0x0000CD24
// novtable reproduces the missing re-seat (as AI/AIDockMoveToEntryStateDestructor.cpp)
// and keeps this TU from emitting the subclass vftables.

class NetCommandMsg
{
public:
	virtual ~NetCommandMsg() {}
};

#define BFME_NET_COMMAND_MSG_DTOR( NAME )                                     \
	class __declspec(novtable) NAME : public NetCommandMsg                    \
	{                                                                         \
	public:                                                                   \
		virtual ~NAME();                                                      \
	};                                                                        \
	NAME::~NAME()                                                             \
	{                                                                         \
	}

BFME_NET_COMMAND_MSG_DTOR( NetFrameCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetAckStage1CommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetAckStage2CommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetPlayerLeaveCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetDestroyPlayerCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetKeepAliveCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetDisconnectKeepAliveCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetDisconnectPlayerCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetDisconnectVoteCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetProgressCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetFileProgressCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetDisconnectFrameCommandMsg )
BFME_NET_COMMAND_MSG_DTOR( NetDisconnectScreenOffCommandMsg )

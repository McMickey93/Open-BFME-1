# 0x004ECD10 identity: the lift's two-string signature is refuted

## Claim

The matched row at 0x004ECD10 (557 bytes) carries the Open-BFME5 lift name
`?showNotificationBox@@YAXVAsciiString@@VUnicodeString@@@Z`, a naked
`__emit` copy of the retail bytes under an assumed signature. The body is now
reconstructed in clean C++ as
`?Rva004ECD10BuddyMessageNotify@@YAXVBuddyMessage@@@Z`
(game/GameEngine/Source/GameClient/GUI/GUICallbacks/Menus/Rva004ECD10BuddyMessageNotify.cpp),
and the lift TU showNotificationBox_Thunk.cpp is deleted.

## The lift signature is wrong

The body takes ONE argument, a BuddyMessage BY VALUE:

1. The by-value argument block is the 24 bytes at [esp+0x9c..0xb0] on entry
   (six dwords, matching BuddyMessage's layout: m_timestamp, m_senderID,
   m_senderNick, m_recipientID, m_recipientNick, m_message), and the last
   call of the normal path (0x004ECF22, ILT 0x00021445 -> ~BuddyMessage
   0x004EA4B0) is entered with `this` = [esp+0x9c] = the argument slot itself;
   ~BuddyMessage destroys +0x8/+0x10 (AsciiString) and +0x14 (UnicodeString).
   A two-string cdecl signature would place only 8 bytes of arguments there.
2. The null-fallback constants inside the two inlined `str()` reads at
   +0x29/+0x47 prove the field types: the read of the last dword
   ([esp+0xb0]) falls back to the WIDE empty string 0x0107388C (m_message,
   UnicodeString), and the read of the third dword ([esp+0xa4]) falls back to
   the ASCII empty string 0x0107388B (m_senderNick) — exactly the declared
   BuddyMessage field order.
3. Every caller builds 0x18 bytes of by-value argument and cleans them:
   matched HandleBuddyResponses 0x004EE510 (four sites, ILT 0x00037FC9),
   matched Rva004EDED0BuddyMessageNotification 0x004EDED0 (one site, ILT
   0x00037FC9), and matched dup_004EE1C0 0x004EE1C0 (one site through the raw
   thunk symbol j_00037fc9 typed as `void (__cdecl*)(BuddyMessage)`).

## The new name is address-derived

No FunctionLexicon row or export names this address (verified by scanning
.data/.rdata for the body address and its ILT thunk), so the row keeps the
address token. `BuddyMessageNotify` describes what the retail body does:
format L"[%hs] %s" (0x011021E4), hand the text to the in-game chat forward
?Rva005127A0Forward@@YA_NVUnicodeString@@H@Z (0x005127A0) with
GameSpyColor[8] (0x012B9220 = 0x012B9200 + 8*4, GSCOLOR_PLAYER_BUDDY), and
when the chat did not take it play "GUIMessageReceived" (AudioEventRTS
two-argument ctor 0x000B2CC0 with argument 2), cap a copy of m_message at 30
characters, format it into TheGameText->fetch("Buddy:MessageNotification")
and dispatch it through ?Rva004EBA70NotificationDispatch (0x004EBA70) with
AsciiString::TheEmptyString (0x01336E50). The BFME2 twin Rva00416589
(BuddyDefsSendMessage.cpp) is the same body with a cap of 11 instead of 30.

## Boundary

Plain RET at 0x004ECF3C; INT3 padding 0x004ECF3D..0x004ECF3F; size 557
(0x22D) confirmed by the probe: 557/557 bytes, zero non-relocation
differences, 35 relocations resolved.

## Caller updates

WOLBuddyResponses.cpp and Rva004EDED0BuddyMessageNotification.cpp declared
the extern "C" lift alias `bfme_showNotificationBox_4ECD10`; both now declare
`Rva004ECD10BuddyMessageNotify(BuddyMessage)` instead (same cdecl by-value
ABI, same call encoding). dup_004EE1C0 keeps calling through the raw thunk.

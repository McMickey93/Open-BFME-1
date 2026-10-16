# ~GameResultsThreadClass 0x00640180 and its base destructor

Retail 0x00640180 is `jmp 0x009DB530` (ThreadClass::~ThreadClass, matched).
`ilt_oracle check ??1GameResultsThreadClass@@UAE@XZ 0x000447A6` is CONFIRMED
(exact); ILT 0x000447A6 jumps to 0x00640180. GameResultsThread.cpp emits the
implicit virtual destructor of GameResultsThreadClass, which tail-jumps to its
base's destructor. That base, GameResultsThreadBase, is the TU's 0x50-byte
layout stand-in for BFME's ThreadClass (the reference thread.h is 8 bytes
wider), exactly as BFMENetworkBackendDestructor.cpp's BFMENetworkThreadBase,
whose destructor is already pinned at 0x009DB530. The stand-in's destructor is
therefore ThreadClass's body, not a second identity.

pin-identity-override: ??1GameResultsThreadBase@@UAE@XZ 0x009DB530 caller=0x00640180 layout stand-in for ThreadClass in GameResultsThread.cpp; the implicit ~GameResultsThreadClass tail-jumps here

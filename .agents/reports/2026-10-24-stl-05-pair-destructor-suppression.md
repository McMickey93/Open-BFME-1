# UnicodeString/AsciiString pair destructor suppression attempt

Queue 402 reports a duplicate pair destructor between MapUtil.cpp and the retail-proven MapUtil_pair_UnicodeString_AsciiString_dtor_Thunk.cpp (76 bytes). Census-only link_check confirms both duplicate and wrong selected-definition blockers, 0/76 linked bytes.

Attempt: add `extern template struct _STL::pair<const UnicodeString, AsciiString>;` after MapUtil's includes, so the canonical destructor could own emission. The source compiles, but direct COFF inspection still shows the destructor as an external definition in section 731. Suppressing the class instantiation does not suppress this implicitly generated special member in the VS2003 configuration. The change is ineffective and was fully reverted.

The scoped MapUtil gate also fails 1/76 functions: insert_unique's less<AsciiString> calls at +0xC9 and +0x1FE resolve to 0x00062FA0, whereas retail calls ILT 0x0001C01C -> 0x006455D0. Re-running the unmodified source reproduces the exact same failure, establishing this as an upstream prerequisite rather than a change induced by the attempt. No speculative callee pin was added.

BFME2 read-only comparison: Code/GameEngine/Source/GameClient/MapUtil.cpp uses the same map<UnicodeString, AsciiString> display-to-filename structure. It confirms the pair type, but does not supply a safe VS2003 implicit-destructor suppression mechanism.

Outcome: blocked; no source change or useful partial implementation retained. Follow-up needs a proven way to stop the implicit special member plus repair of the existing comparator identity. Normal report/log commit hooks apply; no linked-byte gain claimed.

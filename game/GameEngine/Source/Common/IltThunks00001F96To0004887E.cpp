// cl: /DNDEBUG /MD /EHsc
// Five incremental-link thunks no row claimed: each is one `jmp` to an
// independently matched body, and nothing in retail calls any of them.
// Claimed by address, as the ILT convention says; each target is an address
// pin. Under /O2 a tail call with no arguments is exactly `E9 rel32`.
//
//   0x00001F96 -> 0x005DC1E0  ConcreteModuleTemplate<BoxEmissionVolumeModule> destructor
//   0x00006F05 -> 0x006F63B0  GameFileClass::Set_Name
//   0x00024131 -> 0x00483310  list<GameWindow *>::erase
//   0x00040A1B -> 0x0008B600  GameMessage::getCommandTypeAsAsciiString
//   0x0004887E -> 0x000AA7B0  _Rb_tree<int, pair<const int, AsciiString>>::_M_erase

void b_005dc1e0();
void b_006f63b0();
void b_00483310();
void b_0008b600();
void b_000aa7b0();

void j_00001f96() { b_005dc1e0(); }
void j_00006f05() { b_006f63b0(); }
void j_00024131() { b_00483310(); }
void j_00040a1b() { b_0008b600(); }
void j_0004887e() { b_000aa7b0(); }

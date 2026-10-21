// cl: /DNDEBUG /MD /EHsc
// Incremental-link thunks no row claimed: each is one `jmp` to an
// independently matched body. Claimed by address, as the ILT convention says;
// each target is an address pin. Under /O2 a tail call with no arguments is
// exactly `E9 rel32`.
//
//   0x00001BA9 -> 0x00169F80  ?get@Rva00169F80@@QBEHXZ
//   0x0000579F -> 0x0016A020  ?get@Rva0016A020@@QBEPBVAudioEventRTS@@XZ
//   0x0000A097 -> 0x0016A030  ?get@Rva0016A030@@QBEPBVAudioEventRTS@@XZ
//   0x000101CC -> 0x00169F90  ?get@Rva00169F90@@QBEEXZ
//   0x0001B4AA -> 0x006BE480  ?method@Rva006BE480@@QBEMXZ
//   0x0001C41D -> 0x00169FA0  ?get@Rva00169FA0@@QBEHXZ
//   0x0001D985 -> 0x00169FC0  ?get@Rva00169FC0@@QBEHXZ
//   0x000219D6 -> 0x00169FE0  ?get@Rva00169FE0@@QBEHXZ
//   0x00023DD5 -> 0x006BE470  ?method@Rva006BE470@@UAEXXZ
//   0x0002A3AB -> 0x00169F50  ?isPositive@Rva00169F50@@QBEHXZ
//   0x0002B29C -> 0x0016A000  ?get@Rva0016A000@@QBEEXZ
//   0x0002B2E7 -> 0x00169FF0  ?storeWord@Rva00169FF0@@QAEXI@Z
//   0x000331D6 -> 0x0016A010  ?get@Rva0016A010@@QBEPBVAudioEventRTS@@XZ
//   0x00034658 -> 0x006BE420  ?method@Rva006BE420@@UAE_NMM@Z
//   0x00036494 -> 0x0059A670  ?get@Rva0059A670@@SAIPBI@Z
//   0x0003B2C8 -> 0x00169FD0  ?get@Rva00169FD0@@QBEHXZ
//   0x0003BAD4 -> 0x00169FB0  ?storeWord@Rva00169FB0@@QAEXI@Z
//   0x0003C178 -> 0x00169F70  ?get@Rva00169F70@@QBEHXZ
//   0x0003DBBD -> 0x00784B50  ??0?$_STLP_alloc_proxy@PAU?$_List_node@PAVShellMenuSchemeImage@@@_STL@@U12@V?$allocator@U?
//   0x00041010 -> 0x0059A680  ?get@Rva0059A680@@SAIPBI@Z
//   0x00045D77 -> 0x0059A6B0  ?update@ButtonFlashTransition@@UAEXH@Z

void b_00169f50();
void b_00169f70();
void b_00169f80();
void b_00169f90();
void b_00169fa0();
void b_00169fb0();
void b_00169fc0();
void b_00169fd0();
void b_00169fe0();
void b_00169ff0();
void b_0016a000();
void b_0016a010();
void b_0016a020();
void b_0016a030();
void b_0059a670();
void b_0059a680();
void b_0059a6b0();
void b_006be420();
void b_006be470();
void b_006be480();
void b_00784b50();

void j_00001ba9() { b_00169f80(); }
void j_0000579f() { b_0016a020(); }
void j_0000a097() { b_0016a030(); }
void j_000101cc() { b_00169f90(); }
void j_0001b4aa() { b_006be480(); }
void j_0001c41d() { b_00169fa0(); }
void j_0001d985() { b_00169fc0(); }
void j_000219d6() { b_00169fe0(); }
void j_00023dd5() { b_006be470(); }
void j_0002a3ab() { b_00169f50(); }
void j_0002b29c() { b_0016a000(); }
void j_0002b2e7() { b_00169ff0(); }
void j_000331d6() { b_0016a010(); }
void j_00034658() { b_006be420(); }
void j_00036494() { b_0059a670(); }
void j_0003b2c8() { b_00169fd0(); }
void j_0003bad4() { b_00169fb0(); }
void j_0003c178() { b_00169f70(); }
void j_0003dbbd() { b_00784b50(); }
void j_00041010() { b_0059a680(); }
void j_00045d77() { b_0059a6b0(); }

.386
.model flat
; PointGroupClass anonymous volume renderer at 0x00917E10, 952 bytes.
; Address-derived identity: ECX (this) flows to ESI and is passed to the
; matched PointGroupClass members ?prepare_shader@PointGroupClass@@QAEXXZ,
; ?Render@PointGroupClass@@QAEXAAVRenderInfoClass@@H@Z,
; ?rva00917920@..., ?rva00912880@..., ?rva00916CD0@... and
; ?rva00913AF0@..., so the class is witnessed; no source names the member.
; Boundary: ret 12 at +0x3B5 (three stack arguments) then eight INT3 bytes to
; the next body at 0x009181D0.  A 0x005F31A0-side caller TU declares the same
; address as ?rva00917E10@Rva00917E10@@QAEXAAVRenderInfoClass@@IH@Z (ret 12).
;
; WHY MASM.  The recoverable C++ bank (targets/game/reverse/attempts/0x00917e10.cpp)
; compiles to exactly 952 bytes with 31 relocations and instruction shape
; 1.000, but twelve x87 operand bytes at +0x2D3..+0x306 (the transformed Y and
; Z dot products) keep retail's term order: retail loads [esp+48]/[esp+4c]/[esp+44]
; for Y and [esp+58]/[esp+5c]/[esp+54] for Z, while VC7.1's schedule of the
; same scalar expression loads 4c/44/48 and 5c/54/58 (fmul st(n) indices
; follow).  Fifty-one measured formulations -- all 36 scale/store component
; orders, 8 multiplication commutations, 7 result-lifetime variants, explicit
; Y-Z-X expressions, both canonical Transform_Vector overloads, strict-float
; and narrow-volatile loads -- never move those twelve bytes: a
; float/x87-term-order codegen blocker (blocked verdicts in re_attempts.log).
;
; Body is the verbatim symbolic lift of the gen-dump bytes in
; game/gen_asm/d_0090e910.asm: db literals with every reference site
; symbolic; byte-identical to retail outside the relocation slots.
; Evidence: targets/game/reverse/identity_evidence/00917e10-masm-x87-term-order.md

EXTERN ?prepare_shader@PointGroupClass@@QAEXXZ:NEAR
EXTERN ?rva00917920@PointGroupClass@@QAEXPAPAVVector3@@PAPAVVector4@@PAPAMPAPAE3@Z:NEAR
EXTERN ?updatePoolSizes@Rva00914860Sizer@@QAEXHHPAH@Z:NEAR
EXTERN ?rva00912880@PointGroupClass@@QAEXPAVVector4@@H@Z:NEAR
EXTERN ?rva00916CD0@PointGroupClass@@QAEXPAEHH@Z:NEAR
EXTERN ?Rva0133F49CChanged@@3IA:BYTE
EXTERN ?render_state_view@DX8Wrapper@@0VMatrix4@@A:BYTE
EXTERN g_Va013410DC:BYTE
EXTERN g_Va013410EC:BYTE
EXTERN g_Va013410FC:BYTE
EXTERN g_Va013410D0:BYTE
EXTERN g_Va013410E0:BYTE
EXTERN g_Va013410F0:BYTE
EXTERN g_Va01341100:BYTE
EXTERN g_Va013410D4:BYTE
EXTERN g_Va013410E4:BYTE
EXTERN g_Va013410F4:BYTE
EXTERN g_Va01341104:BYTE
EXTERN g_Va0134127C:BYTE
EXTERN ?transformed_loc@PointGroupClass@@0V?$VectorClass@VVector3@@@@A:BYTE
EXTERN ?j_0003fc7e@@YAXXZ:NEAR
EXTERN __real@4f800000:BYTE
EXTERN ?g_bfmeScaleBK@@3MA:BYTE
EXTERN ?Get_Position@RenderObjClass@@QBE?AVVector3@@XZ:NEAR
EXTERN g_Va01341278:BYTE
EXTERN ?d_009148c0@@YAXXZ:NEAR
EXTERN ?rva00913AF0@PointGroupClass@@QAEXH_N@Z:NEAR
EXTERN ?Render@PointGroupClass@@QAEXAAVRenderInfoClass@@H@Z:NEAR
_TEXT SEGMENT
public ?Rva00917E10@@YAXXZ
?Rva00917E10@@YAXXZ PROC
    db 081h, 0ECh, 08Ch, 000h, 000h, 000h, 056h, 057h, 08Bh, 0BCh, 024h, 09Ch, 000h, 000h, 000h, 083h
    db 0FFh, 001h, 08Bh, 0F1h, 00Fh, 086h, 07Ch, 003h, 000h, 000h, 08Bh, 046h, 030h, 0A8h, 001h, 00Fh
    db 084h, 071h, 003h, 000h, 000h, 0A8h, 002h, 00Fh, 084h, 069h, 003h, 000h, 000h, 083h, 0FFh, 010h
    db 076h, 00Ch, 0BFh, 010h, 000h, 000h, 000h, 089h, 0BCh, 024h, 09Ch, 000h, 000h, 000h, 08Bh, 046h
    db 01Ch, 053h, 033h, 0DBh, 03Bh, 0C3h, 00Fh, 084h, 03Eh, 003h, 000h, 000h, 055h, 08Bh, 0CEh
    call ?prepare_shader@PointGroupClass@@QAEXXZ
    db 08Dh, 044h, 024h, 028h, 050h, 08Dh, 04Ch, 024h, 030h, 051h, 08Dh, 054h, 024h, 028h, 052h, 08Dh
    db 044h, 024h, 030h, 050h, 08Dh, 04Ch, 024h, 020h, 051h, 08Bh, 0CEh, 089h, 05Ch, 024h, 024h, 089h
    db 05Ch, 024h, 038h, 089h, 05Ch, 024h, 034h, 089h, 05Ch, 024h, 040h, 089h, 05Ch, 024h, 03Ch
    call ?rva00917920@PointGroupClass@@QAEXPAPAVVector3@@PAPAVVector4@@PAPAMPAPAE3@Z
    db 08Bh, 054h, 024h, 010h, 08Bh, 04Eh, 004h, 08Dh, 084h, 024h, 084h, 000h, 000h, 000h, 050h, 08Bh
    db 046h, 01Ch, 089h, 094h, 024h, 08Ch, 000h, 000h, 000h, 08Bh, 051h, 010h, 052h, 050h, 08Bh, 0CEh
    call ?updatePoolSizes@Rva00914860Sizer@@QAEXHHPAH@Z
    db 08Bh, 04Eh, 01Ch, 08Bh, 06Ch, 024h, 024h, 051h, 055h, 08Bh, 0CEh
    call ?rva00912880@PointGroupClass@@QAEXPAVVector4@@H@Z
    db 08Bh, 094h, 024h, 0A8h, 000h, 000h, 000h, 08Bh, 046h, 01Ch, 08Bh, 04Ch, 024h, 028h, 052h, 050h
    db 051h, 08Bh, 0CEh
    call ?rva00916CD0@PointGroupClass@@QAEXPAEHH@Z
    db 0F7h, 005h
    dd ?Rva0133F49CChanged@@3IA
    db 000h, 000h, 008h, 000h, 074h, 03Eh, 0C7h, 044h, 024h, 034h, 000h, 000h, 080h, 03Fh, 089h, 05Ch
    db 024h, 038h, 089h, 05Ch, 024h, 03Ch, 089h, 05Ch, 024h, 040h, 089h, 05Ch, 024h, 044h, 0C7h, 044h
    db 024h, 048h, 000h, 000h, 080h, 03Fh, 089h, 05Ch, 024h, 04Ch, 089h, 05Ch, 024h, 050h, 089h, 05Ch
    db 024h, 054h, 089h, 05Ch, 024h, 058h, 0C7h, 044h, 024h, 05Ch, 000h, 000h, 080h, 03Fh, 089h, 05Ch
    db 024h, 060h, 0EBh, 074h, 08Bh, 015h
    dd ?render_state_view@DX8Wrapper@@0VMatrix4@@A
    db 0A1h
    dd g_Va013410DC
    db 08Bh, 00Dh
    dd g_Va013410EC
    db 089h, 054h, 024h, 034h, 08Bh, 015h
    dd g_Va013410FC
    db 089h, 044h, 024h, 038h, 0A1h
    dd g_Va013410D0
    db 089h, 04Ch, 024h, 03Ch, 08Bh, 00Dh
    dd g_Va013410E0
    db 089h, 054h, 024h, 040h, 08Bh, 015h
    dd g_Va013410F0
    db 089h, 044h, 024h, 044h, 0A1h
    dd g_Va01341100
    db 089h, 04Ch, 024h, 048h, 08Bh, 00Dh
    dd g_Va013410D4
    db 089h, 054h, 024h, 04Ch, 08Bh, 015h
    dd g_Va013410E4
    db 089h, 044h, 024h, 050h, 0A1h
    dd g_Va013410F4
    db 089h, 04Ch, 024h, 054h, 08Bh, 00Dh
    dd g_Va01341104
    db 089h, 054h, 024h, 058h, 089h, 044h, 024h, 05Ch, 089h, 04Ch, 024h, 060h, 08Bh, 046h, 01Ch, 039h
    db 005h
    dd g_Va0134127C
    db 07Dh, 00Fh, 053h, 08Dh, 014h, 000h, 052h, 0B9h
    dd ?transformed_loc@PointGroupClass@@0V?$VectorClass@VVector3@@@@A
    call ?j_0003fc7e@@YAXXZ
    db 03Bh, 0FBh, 089h, 05Ch, 024h, 010h, 00Fh, 08Eh, 0D0h, 001h, 000h, 000h, 085h, 0FFh, 089h, 07Ch
    db 024h, 030h, 0DBh, 044h, 024h, 030h, 07Dh, 006h, 0D8h, 005h
    dd __real@4f800000
    db 03Bh, 0EBh, 0D9h, 05Ch, 024h, 028h, 08Bh, 06Ch, 024h, 020h, 00Fh, 094h, 044h, 024h, 030h, 08Dh
    db 09Bh, 000h, 000h, 000h, 000h, 0DBh, 044h, 024h, 010h, 08Bh, 08Ch, 024h, 0A0h, 000h, 000h, 000h
    db 08Bh, 009h, 08Dh, 044h, 024h, 078h, 0D8h, 00Dh
    dd ?g_bfmeScaleBK@@3MA
    db 050h, 0D8h, 074h, 024h, 02Ch, 0D9h, 05Ch, 024h, 028h
    call ?Get_Position@RenderObjClass@@QBE?AVVector3@@XZ
    db 08Bh, 046h, 01Ch, 033h, 0D2h, 03Bh, 0C3h, 00Fh, 08Eh, 03Bh, 001h, 000h, 000h, 08Bh, 08Ch, 024h
    db 088h, 000h, 000h, 000h, 0BFh, 0F8h, 0FFh, 0FFh, 0FFh, 08Dh, 041h, 008h, 02Bh, 0F9h, 0D9h, 044h
    db 024h, 078h, 0D8h, 060h, 0F8h, 0D9h, 05Ch, 024h, 014h, 0D9h, 044h, 024h, 07Ch, 0D8h, 060h, 0FCh
    db 0D9h, 05Ch, 024h, 018h, 0D9h, 084h, 024h, 080h, 000h, 000h, 000h, 0D8h, 020h, 0D9h, 054h, 024h
    db 01Ch, 0D8h, 04Ch, 024h, 01Ch, 0D9h, 044h, 024h, 018h, 0D8h, 04Ch, 024h, 018h, 0DEh, 0C1h, 0D9h
    db 044h, 024h, 014h, 0D8h, 04Ch, 024h, 014h, 0DEh, 0C1h, 0D9h, 05Ch, 024h, 020h, 0D9h, 044h, 024h
    db 020h, 0D9h, 0FAh, 0D9h, 05Ch, 024h, 074h, 0D9h, 044h, 024h, 024h, 08Bh, 01Dh
    dd g_Va01341278
    db 0D8h, 04Ch, 095h, 000h, 08Dh, 00Ch, 007h, 042h, 083h, 0C0h, 00Ch, 0D8h, 074h, 024h, 074h, 0D9h
    db 044h, 024h, 014h, 0D8h, 0C9h, 0D9h, 044h, 024h, 018h, 0D8h, 0CAh, 0D9h, 05Ch, 024h, 018h, 0D9h
    db 044h, 024h, 01Ch, 0D8h, 0CAh, 0D9h, 05Ch, 024h, 01Ch, 0D8h, 040h, 0ECh, 0DDh, 0D9h, 0D9h, 044h
    db 024h, 018h, 0D8h, 040h, 0F0h, 0D9h, 044h, 024h, 01Ch, 0D8h, 040h, 0F4h, 0D9h, 044h, 024h, 03Ch
    db 0D8h, 0C9h, 0D9h, 044h, 024h, 038h, 0D8h, 0CBh, 0DEh, 0C1h, 0D9h, 044h, 024h, 034h, 0D8h, 0CCh
    db 0DEh, 0C1h, 0D8h, 044h, 024h, 040h, 0D9h, 09Ch, 024h, 08Ch, 000h, 000h, 000h, 0D9h, 044h, 024h
    db 048h, 0D8h, 0CAh, 0D9h, 044h, 024h, 04Ch, 0D8h, 0CAh, 0DEh, 0C1h, 0D9h, 044h, 024h, 044h, 0D8h
    db 0CCh, 0DEh, 0C1h, 0D8h, 044h, 024h, 050h, 0D9h, 09Ch, 024h, 090h, 000h, 000h, 000h, 0D9h, 044h
    db 024h, 058h, 0D8h, 0CAh, 0D9h, 044h, 024h, 05Ch, 0D8h, 0CAh, 0DEh, 0C1h, 0D9h, 044h, 024h, 054h
    db 0D8h, 0CCh, 0DEh, 0C1h, 0D8h, 044h, 024h, 060h, 0DDh, 0DBh, 0DDh, 0D8h, 0DDh, 0D8h, 0D9h, 084h
    db 024h, 08Ch, 000h, 000h, 000h, 0D9h, 01Ch, 00Bh, 08Bh, 01Dh
    dd g_Va01341278
    db 0D9h, 084h, 024h, 090h, 000h, 000h, 000h, 0D9h, 05Ch, 00Bh, 004h, 08Bh, 01Dh
    dd g_Va01341278
    db 0D9h, 05Ch, 00Bh, 008h, 08Bh, 04Eh, 01Ch, 03Bh, 0D1h, 00Fh, 08Ch, 0DFh, 0FEh, 0FFh, 0FFh, 08Bh
    db 0BCh, 024h, 0A4h, 000h, 000h, 000h, 033h, 0DBh, 08Bh, 056h, 01Ch, 08Bh, 04Ch, 024h, 02Ch, 0A1h
    dd g_Va01341278
    db 052h, 051h, 055h, 050h, 08Bh, 0CEh
    call ?d_009148c0@@YAXXZ
    db 08Bh, 054h, 024h, 030h, 08Bh, 084h, 024h, 084h, 000h, 000h, 000h, 052h, 050h, 08Bh, 0CEh
    call ?rva00913AF0@PointGroupClass@@QAEXH_N@Z
    db 08Bh, 044h, 024h, 010h, 040h, 03Bh, 0C7h, 089h, 044h, 024h, 010h, 00Fh, 08Ch, 057h, 0FEh, 0FFh
    db 0FFh, 05Dh, 05Bh, 05Fh, 05Eh, 081h, 0C4h, 08Ch, 000h, 000h, 000h, 0C2h, 00Ch, 000h, 08Bh, 08Ch
    db 024h, 0A0h, 000h, 000h, 000h, 08Bh, 094h, 024h, 098h, 000h, 000h, 000h, 051h, 052h, 08Bh, 0CEh
    call ?Render@PointGroupClass@@QAEXAAVRenderInfoClass@@H@Z
    db 05Fh, 05Eh, 081h, 0C4h, 08Ch, 000h, 000h, 000h, 0C2h, 00Ch, 000h
?Rva00917E10@@YAXXZ ENDP
_TEXT ENDS
END

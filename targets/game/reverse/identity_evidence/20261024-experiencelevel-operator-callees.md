# ExperienceLevel::operator= (0x00381690) callee identities (2026-10-24)

Served link item: `??4ExperienceLevel@@QAEAAV0@ABV0@@Z` (link_queue rank 24,
census 21ef97bd08, 599 B in ExperienceLevelListAssignment.cpp and
Rva00382210ExperienceLevelSystem.cpp). The only definition is the byte-true
701-byte COMDAT copy in ExperienceLevelCopyConstructor.obj; the census judged
the kept copy `wrong` because three of its call relocations resolve through
functions.csv rows whose names sit on bodies retail's own thunk table
contradicts. This session fixed the erase axis and mapped the wall the other
two axes hit; the item stays blocked on the `_Construct` row retirement, which
needs a strings-family repair of three dependent matched rows first.

## Evidence per callee

- `??$_Construct@VAsciiString@@V1@@_STL@@YAXPAVAsciiString@@ABV1@@Z`
  - ilt_oracle: CONFIRMED at ILT 0x00007554 -> 0x000620B0 (exact slot,
    p_false 5.22e-04); CONTRADICTED at 0x0004725D -> 0x00756D90
    (documented in pin-candidates-op1-batch4-oracle.md, which lists the
    LadderDefs body under "not changed").
  - ExperienceLevelCopyConstructor.obj's own copy (66 bytes, digest
    fb34dd5ed1e7) shape-matches retail at 0x000620B0 and differs at
    0x00756D90 (relocation-masked compare against the retail image).
  - THE WALL: retiring the 0x00756D90 row's name (to `?dup_00756D90`, the
    batch-4 convention) fails the byte gate of three matched rows whose
    retail bytes encode the 0x0004725D route into 0x00756D90 and which
    resolve that call through this name's candidate list
    (?dup_00757E20@@YAXXZ at 0x00757E20 in GameAudio.cpp, the
    0x00757C70 anchor row in AsciiStringVectorInsert.cpp, and one more of
    the 8 delta rows). A route= pin at 0x0004725D is inadmissible while the
    row is renamed (the route gate requires the reached body's matched row
    to carry this very name), and a plain second pin is a one-name-one-body
    conflict (0x7554 follows to 0x620B0, 0x4725D follows to 0x756D90).
    Unblocking the served item therefore needs the strings-family owner to
    respell those three callers first (the ObjectTypesXfer pattern), then
    retire the 0x00756D90 name; the name is already pin-only-correct at
    0x00007554.

- `?_M_insert_overflow@?$vector@VAsciiString@@V?$allocator@VAsciiString@@@_STL@@@_STL@@IAEXPAVAsciiString@@ABV3@ABU__false_type@2@I_N@Z`
  - ilt_oracle: CONFIRMED at 0x0003827B -> 0x00063700 (exact slot,
    p_false 2.61e-04); CONTRADICTED at 0x000112C0 -> 0x00757C70
    (pin-candidates-op1-batch4-oracle.md). The symbols.csv pin at
    0x0003827B already documents the twin pair (268-byte bodies at
    0x00063700 and 0x00757C70).
  - The batch-4 `?dup_00757C70` row's object-symbol still routes the name
    to 0x00757C70 in the truth ledger. Adding the `gen-alias` token (the
    ICF-twin dup_ convention build.py documents) removes that shadow and
    was verified admissible, but with the `_Construct` row still shadowing
    0x00007554 the operator= copy stays `wrong`, and alone the token
    flips ExperienceLevelCopyConstructor.obj's own 7cef75237f61 copy from
    `retail` (vs 0x00757C70) to `wrong` (vs 0x00063700, whose internal
    _Construct reaches 0x000620B0) -- so it was NOT landed. Land it together
    with the `_Construct` retirement: then this TU's copy proves `retail`
    against the confirmed 0x00063700 home.

- `?erase@?$vector@VAsciiString@@V?$allocator@VAsciiString@@@_STL@@@_STL@@QAEPAVAsciiString@@PAV3@0@Z` -- LANDED
  - ilt_oracle: CONFIRMED at ILT 0x00024C17 -> 0x00065960 (exact slot,
    p_false 3.26e-04); CONTRADICTED at 0x0002FD8D -> 0x006FA560.
  - Retail's operator= calls this exact ILT at 0x00381690+0x115.
  - ExperienceLevelCopyConstructor.obj's own copy (76 bytes, digest
    8ff46609624c) shape-matches retail at 0x00065960 and differs at
    0x006FA560; the GameAudio.cpp row's own copy (077bed5e64ef) matches
    0x006FA560, so the name cannot move to the pinned body and stays
    pin-only (batch-4 rule).
  - Retiring the 0x006FA560 row's name was measured net-negative for the
    census: the first vector<AsciiString>::erase COMDAT in link order is
    GameAudio.obj's (077bed5e64ef), so flipping the truth home for the name
    marks the kept copy wrong and charges `wrong_selected` to about ten
    currently-linked files. That repair belongs to the strings-family owner.
  - LANDED instead: ExperienceLevelCopyConstructor.cpp now clears
    m_attributeModifiers through the TU-scoped
    `Rva00065960AttributeRange::erase(void *, void *)` view, an abi-view=
    pin at ILT 0x00024C17 (canonical: the matched gen-tgrid vec_p4cd row's
    erase at 0x00065960) -- the same additive-candidate route
    CRCParameterCheck::clear (0x00065A40) and the EnragedBehavior
    module-data constructor already spell. The call encoding is unchanged
    (build.sh ExperienceLevelCopyConstructor.cpp: 2/2 matched); the TU no
    longer instantiates vector<AsciiString>::erase, so its wrong-shaped
    COMDAT copy (a census loser for this file) disappears, and the
    operator= copy's erase relocation now proves `retail`.

## Where this leaves the served item

RetailTruth over the recompiled object: the `??4ExperienceLevel` copy's erase
relocation now lands; `_Construct` (+0x143) and `_M_insert_overflow` (+0x163)
still fail against the 0x00756D90 / 0x00757C70 shadows, so the copy keeps
verdict `wrong` and the 599 B stay blocked. The full unblock recipe is
documented above and needs the strings-family owner: respell the three
0x0004725D-route callers, retire `??$_Construct@VAsciiString` from 0x00756D90,
add the gen-alias token to `?dup_00757C70`. Every other relocation of the copy
already proves.

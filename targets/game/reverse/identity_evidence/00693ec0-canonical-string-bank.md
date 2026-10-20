# 00693EC0 bank: canonical AsciiString, not a type rename

This change affects a banked, nonmatching experiment only. It does not change
production source, function identities, pins, or accepted reconstruction bytes.

The previous bank redeclared `AsciiString` locally with an out-of-line copy
constructor and destructor. The new bank includes the existing canonical
`inputs/reference/shims/stringinline/StringInline.h`, whose `AsciiString`
definition forwards its copy construction and destruction to `StringBase<char>`.
The name remains `AsciiString`; it is neither renamed nor replaced by a key type.

The name-regression heuristic pairs removal of that local declaration with
`Rva00691ED0Key` and `Rva006934C0Key`. These are separate, existing key views:

- `game/GameEngine/Source/GameNetwork/Rva00691ED0KeyCtor.cpp` defines the
  verified 88-byte constructor at 00691ED0. It takes an unsigned primary value
  and a by-value AsciiString, stores the first word, copies the string into
  the second word, and destroys the argument.
- `game/Libraries/Source/WWVegas/WWLib/RvaTreeInsertUnique006934C0Compound.cpp`
  defines the already verified compound-key tree insertion at 006934C0.
  Its key consists of an unsigned word and an AsciiString. The native return
  is a two-word iterator/bool pair, not the old bank's void insertion call.
- `Gen0002857ERelease.cpp` stamps referent+38 before notifying its owner.
  The complete retail notification copies the referent's first string word,
  loads that timestamp, constructs the key through ILT 00005E16, and inserts
  it through ILT 0002B4E5. Its RET4 at +BC proves the complete 191-byte extent.

The six-byte near miss still requires strict relocation, identity and alias
review before any future production landing. Neither its measured0.9686 score
nor these snapshot-specific false-pairing corrections establish acceptance.

The two name_corrections entries bind only the exact before/after bank snapshots,
as permitted by docs/naming_evidence.md for a removed type paired with the wrong
new type. No inherited descriptive name is being weakened.

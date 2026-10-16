# STLport /Od find_if / __find_if with _Neq_char_bound (0x0082D470, 0x0082DFA0)

Both bodies sit in the STLport library region BFME linked unoptimised
(`/Od /Ob1`: stdexcept destructors, `__debug_alloc`, `_Rb_global<bool>` and the
`basic_string<char>` members around 0x0082AE40-0x00832000).

Caller proof. The only caller of 0x0082DFA0 is 0x0082E350 (241 bytes), a
thiscall on the STLport `_String_base` with the same shape as
`basic_string<char>::rfind(char, size_type) const` at 0x0082E070 (npos when
`len < 1`, `min(len - 1, pos)`, `last = start + min + 1`) plus one extra
`const_reverse_iterator` local (frame 0x50 against rfind's 0x4C). That is STLport
4.5.3 `basic_string<char>::find_last_not_of(char, size_type) const`
(`inputs/vendor/stlport/stl/_string.c`: `__rlast = const_reverse_iterator(__last)`
then `find_if(__rlast, rend(), _Neq_char_bound<_Traits>(__c))`). So 0x0082DFA0
is `_STL::find_if<reverse_iterator<const char*>, _Neq_char_bound<char_traits<char> > >`
and its only callee 0x0082D470 is the random-access `__find_if` over the same
arguments.

Names (old placeholder -> real):

- 0x0082DFA0 `?bfmeFwdVMV@@YA?AUBfmeItVMV@@U1@0D@Z` ->
  `??$find_if@V?$reverse_iterator@PBD@_STL@@U?$_Neq_char_bound@V?$char_traits@D@_STL@@@2@@_STL@@YA?AV?$reverse_iterator@PBD@0@V10@0U?$_Neq_char_bound@V?$char_traits@D@_STL@@@0@@Z`
- 0x0082D470 `?bfmeRFindNotChV32@@YAPAPADPAPADPAD1D@Z` ->
  `??$__find_if@V?$reverse_iterator@PBD@_STL@@U?$_Neq_char_bound@V?$char_traits@D@_STL@@@2@@_STL@@YA?AV?$reverse_iterator@PBD@0@V10@0U?$_Neq_char_bound@V?$char_traits@D@_STL@@@0@ABUrandom_access_iterator_tag@0@@Z`

Byte proof. Each body is an explicit instantiation of the vendored STLport
4.5.3 template from `<string>`, compiled `/Od /Ob1 /D_STLP_USE_STATIC_LIB
/D_STLP_NO_EXCEPTIONS`, and byte-matches at its full extent (57/57 and
596/596). Neither mangled name appears anywhere else in functions.csv or
symbols.csv. The frozen gen-tgrid TU game/gen_small/tgrid_004.cpp (explicit
`template class basic_string<char>`, /O2) also emits COMDAT copies of both
names; with these rows the link census keeps the retail-proven /Od copies
(tools/link_check.py: BfmeConv1443/1472/1484 all LINK).

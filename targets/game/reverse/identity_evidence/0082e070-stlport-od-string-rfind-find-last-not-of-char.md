# STLport /Od basic_string<char>::rfind(char) and find_last_not_of(char) (0x0082E070, 0x0082E350)

Both bodies sit in the STLport library region BFME linked unoptimised
(`/Od /Ob1`), next to their callees proven in
`0082d0b0-stlport-od-find-if-char-bound.md` and
`0082d470-stlport-od-find-if-neq-char-bound.md`.

0x0082E070 (235 bytes) is a thiscall on the 12-byte STLport `_String_base`
(`[this+0]` start, `[this+4]` finish). It returns -1 (npos) when
`finish - start < 1`, takes `min(len - 1, pos)` through the address-of-min
pattern, builds `const_reverse_iterator(start + min + 1)` and `rend()`, calls
`find_if<reverse_iterator<const char*>, _Eq_char_bound>` (0x0082DE30) and
returns `(result.base() - 1) - begin()` or npos: STLport 4.5.3
`basic_string<char>::rfind(char, size_type) const` (`stl/_string.c`).

0x0082E350 (241 bytes) is the same shape with the extra named
`const_reverse_iterator __rlast` local (frame 0x50 against 0x4C) and the call to
`find_if<..., _Neq_char_bound>` (0x0082DFA0): STLport 4.5.3
`basic_string<char>::find_last_not_of(char, size_type) const`.

Names (old placeholder -> real):

- 0x0082E070 `?bfmeRFindChV40@@YGHDI@Z` ->
  `?rfind@?$basic_string@DV?$char_traits@D@_STL@@V?$allocator@D@2@@_STL@@QBEIDI@Z`
- 0x0082E350 `?bfmeRFindChV42@@YGHDI@Z` ->
  `?find_last_not_of@?$basic_string@DV?$char_traits@D@_STL@@V?$allocator@D@2@@_STL@@QBEIDI@Z`

Byte proof: each is an explicit member instantiation of the vendored STLport
4.5.3 `basic_string<char>` from `<string>` under `/Od /Ob1
/D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS` and matches at its full extent.
Neither mangled name is claimed or pinned elsewhere. The 29-byte caller
0x0082E9B0 still calls rfind under the placeholder pin
`?bfmeFwdThreeSUA@BfmeThingSUA@@QAEXDH@Z` (0x0082E070); that pin is left alone.

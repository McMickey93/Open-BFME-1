# Queue 13: terrain-cache vector push_back

Blocked by provider identity. The caller uses `Rva00746420Record`; its pin
routes ILT 0x00044495 to retail 0x007463A0. The 62-byte ledger provider at that
address is `vector<Gen_t_007463a0_p24cd>::push_back` in immutable
`game/gen_small/tgrid_121.cpp`. Equal payload size does not equate those C++
types or their nontrivial element contracts.

A TU-local specialization declaration was actually compiled: the caller still
passes 1/1 functions, three DIR32 references and all guards. Its COFF then has
only an undefined reference to the Rva00746420Record push_back. link_check
changes from selected-not-retail to unresolved. The census confirms that the
caller was the only provider of that mangled name; the generated provider has
a different mangled name. Thus suppression alone makes a provider hole.

The attempt was reverted and the restored caller again passes 1/1 and all
scoped guards. No generated source, pin or baseline was changed. A future
repair needs independent element construction/overflow identities and a real
C++ provider at the official path, rather than a guessed type rename or alias.
`callees.py 0x007463A0 62` identifies ILT 0x00023399 -> 0x00745960 and
ILT 0x000349FF -> 0x007416E0. The re_log locator is the synthetic queue key.

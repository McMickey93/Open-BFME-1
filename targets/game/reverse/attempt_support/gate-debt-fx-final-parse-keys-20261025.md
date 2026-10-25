# FX HeightOffset data gate debt

Parent: 497cb4fc72. Shard 1/4 served ?g_01114504@FXParticleSystem@@3QBDB.
Retail VA 0x01114504 contains "HeightOffset" followed by NUL (13 bytes).
Existing FX INI consumers reference that same const-char-array symbol.
Define its existing declaration in place without changing its type, namespace,
name, consumer expressions or any function. No donor input or inferred identity.

add_data_match.py proves sizeof 13 under build flags and exact retail bytes,
with zero relocations, and alone writes the data row. The exact keyed pass-test
succeeds first try, removes its exemption and verifies 470/470 functions,
24 string literals, 93 float constants, 1042 DIR32 references and 20 data rows.
Normal scoped build and commit hooks verify the final batch. Five additional
served FX string keys were held by another agent and skipped without edits.

This entry is batched with four same-pattern debug strings documented in
[gate-debt-debug-string-keys-20261025.md](gate-debt-debug-string-keys-20261025.md).

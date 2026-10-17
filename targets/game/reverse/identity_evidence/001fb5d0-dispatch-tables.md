# FireWeapon dispatch block at VA 010A3DD4

The registered FireWeaponWhenDamagedBehavior constructor at 001FB5D0 installs
five pointers inside the interval [010A3DD4,010A3F30). The five dispatch
tables begin at 010A3DD4, 010A3DE8, 010A3E34, 010A3E40 and 010A3F04.
Their nonzero code-entry counts are respectively 3, 16, 2, 41 and 11; zero
words separate the tables. The final primary table ends immediately before
the zero at 010A3F30. This establishes the complete 348-byte constant block.

The source is an array of 87 native function-pointer words. Every nonzero
entry refers to the independently ledgered ILT at that exact retail address;
the other 14 words are zero. There are no numeric image-address initializers.
add_data_match verifies all 348 bytes and all 73 pointer relocations.

The address-qualified block name claims these bytes, not guessed original
symbol names. Its five table addresses retain the registered constructor's
exact values. Existing MobMemberSlavedUpdate-labelled DIR32 records remain
untouched; the factory/name/extent proof in 001fb5d0-constructor-bank.md
shows why those names cannot identify this constructor's owner.

The native constructor can bind these verified BFME tables in its first
member initializer while retaining the reference class declaration. The
same spelling preserves all 652 instruction bytes in a probe. Promotion
still requires the strict function gate and all UpdateModule dependents.

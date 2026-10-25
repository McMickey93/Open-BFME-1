# Five existing data owners: obsolete no-owner exceptions

At BFME 1 a0bdac923e0d, the gate-debt fallback served 1012 DIR32
exceptions. Five existing matched data owners now pass their keyed
`tools/repair_queue.py pass-test` with their old no-owner exceptions removed.
The tool removed those five entries, leaving 1007. No baseline was edited by
hand. Exact existing COFF names were added as source comments so the repair
queue can locate and reverify each defining unit.

| Existing owner | Existing BFME 1 evidence | Keyed scoped result |
| --- | --- | --- |
| `?g_0112A5C4@@3PAPAXA` | Matched 24-byte table at VA 0112A5C4; six bounded retail slots, each relocated to its existing ledger target; allocator initializer installs the table. | Functions 1/1, data 2/2, DIR32 6, zero body exceptions. |
| `?__narrow_atoms@_STL@@3QBDB` | Matched five-byte STLport table at VA 0112F430, retail bytes `2B 2D 30 78 58`; existing numeric-input widen consumers. | Functions 3/3, data 1/1, zero body exceptions. |
| `?g_012F8054@@3HA` | Matched four-byte zero cell at VA 012F8054; existing matched debug overlay reads it in its frame comparison. | Functions 1/1, data 2/2, DIR32 16, zero body exceptions; 21 bounded local-table entries checked. |
| `?g_classic0130B2A0@@3V_Locale_impl@_STL@@A` | Matched 24-byte zero storage at VA 0130B2A0, bounded by the next object; existing classic-locale pointer at VA 012C7464 points here, and the existing builder placement-constructs it. | Functions 1/1, data 2/2, DIR32 1, zero body exceptions. |
| `?g_0134C948@@3PADA` | Matched 256-byte zero buffer at VA 0134C948, bounded by VA 0134CA48; existing matched copy body references it. | Functions 1/1, data 1/1, DIR32 1, zero body exceptions. |

These are the existing data identities, extents and relationships, checked by
the normal data/relocation and function gates. No function body, data row,
name, layout, pin, compiler flag, verifier or executable byte changes. The
address-derived owners retain their existing uncertainty about semantic names.
The allocator table does not establish a new class identity. The locale
storage does not establish additional class-layout facts.

External consumers are checked separately: NumGetBaseOrZeroWide.cpp verifies
both narrow/wide functions and six DIR32 references; the classic-locale builder
is checked through stlport_classic_locale_impl.cpp. CSV, declared-unmatched and
whitespace checks also pass. Commit hooks recheck the deleted exceptions.

Read-only BFME 2 master e2fdc5620c5834c1c98de24aa3510d72e2cbcc69 was
searched for the exact owners. Its STLport narrow/wide numeric-input helpers
and valid-grouping source confirm a corresponding upstream table use, but no
donor repair was imported or needed for these already-matched owners. The
pinned beed8a16790a reference was left unchanged.

## Linking review and blockers

The census-only link queue and BFME 2 provider sweep were inspected, followed
by served claims and the call-by-row-name `near` queue. The RefHandle008958D0
destructor and OpenContain::onRemoving were recorded blocked and released.
Their existing attempt evidence still applies: preserving the former's
retail-shaped COMDAT changes its matched parents/EH actions, and the latter's
integer-tree lookup still has conflicting selected retail identities. Current
BFME 2 evidence does not resolve either prerequisite. No disproven compiler
trial was repeated. See the new re_attempts.log entries for the exact symbols.

The `near` candidates also retain their previously recorded prerequisites:
GameBrowser callback retirement is refused by the sole-writer DIR32 tool;
return-handle wrappers need ABI/layout reconciliation; deleting-destructor
wrappers need supported class identity and compiler-shape reconciliation.
Globals family selection has no open row. Strings/STLport families remain
separate work requiring their owner/ABI evidence. The prior handoff
link-seat-owned-data-debts-20261025.md documents the stale findBridge preview
and 524 unavailable current objects; this session does not claim that the
census estimates are newly linked bytes.

`tools/progress.py origin/master`: +0 B exact C++, +0 B census linked.
Measured improvement: five fewer gate debts, each with its machine pass test.
No full build or census build was started.

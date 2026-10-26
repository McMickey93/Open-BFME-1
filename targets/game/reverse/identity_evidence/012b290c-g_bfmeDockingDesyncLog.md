# g_bfmeDockingDesyncLog at VA 0x012B290C (1 B, .data, initial 1)

BFME 1 target evidence: dir32_addresses.csv records only
?g_bfmeDockingDesyncLog@@3_NA at 0x012B290C, read as a byte flag by the matched
WorkerAIUpdate/DozerAIUpdate newTask bodies (`if (g_bfmeDockingDesyncLog)`).
Retail .data holds 01 00 00 00 there (raw section bytes), so the byte is
initialised true; the next three bytes are zero padding. No data row or source
defined it: link queue #28 (census 179d0eb281) lists it as the only blocker of
WorkerAIUpdateNewTaskBfme.cpp, which already defines the sibling flag
g_bfmeDockingTraceActive (0x012F0478). The name is the existing recorded
placeholder; its EA identity is unknown.

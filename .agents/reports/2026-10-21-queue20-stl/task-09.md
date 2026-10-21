# Queue 9: Coord3D default resize

The canonical 22-byte one-argument resize owner is
`Coord3DVectorDefaultResizeThunk.cpp`, retail RVA 0x000B7D10. BezierSegment
explicitly instantiated the vector class and emitted the 32-byte upstream
variant. A TU-local specialization declaration suppresses only that emitter.

After rebasing, `./build.sh game/GameEngine/Source/Common/Bezier/BezierSegment.cpp`
passes 68/68 functions and one data row; string, constant, DIR32 and body guards
pass. The original pre-interruption check also passed 68/68.

Before and after, `link_check.py --census-only` on the canonical owner reports
0/1 linking and selected-not-retail against the October 19 e9a5ae5b4c census.
This is partial emitter cleanup, not a complete LINKED claim; that historical
census cannot demonstrate current global selection.

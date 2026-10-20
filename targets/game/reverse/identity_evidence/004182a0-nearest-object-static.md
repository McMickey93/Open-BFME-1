# 0x004182A0 nearest-object query (file-static of the 0x00419F00 TU)

- Boundary: retail 0x004182A0, 271 bytes.
- Linkage: both call sites in the matched notify00419F00 (0x00419F00) reach
  it with a direct call, not through the ILT, so it is internal to that TU.
  The C++ matches only that way. The former member spelling,
  `Object::nearest004182A0`, kept an ESI/EDI receiver swap across 35
  attempts.
- Body: five stack filters are linked behind the kind-of filter
  (root, on-map, local-player, shroud), and that head is the filters argument
  of PartitionManager::getClosestObject. The pieces are:
  - the root filter, vtable 0x01083B80;
  - PartitionFilterOnMap, vtable 0x0109687C;
  - PartitionFilterPlayer for ThePlayerList's local player;
  - a kind-of mask over bits 121 and 157, vtable 0x010F11B4, recorded as
    Rva00410750VptrZeroBlockObject;
  - the shroud filter BfmeA1196(this, true).
  The query takes the object's position and TheEva+0x60 as the radius, from
  the centre in 2D.
- Identity stays address-derived. The old pin
  `?nearest004182A0@Object@@QAEPAV1@XZ` described the member spelling, and
  retail's direct call refutes that linkage.

pin-identity-override: ?nearest004182A0@@YAPAVObject@@PAUBfmeSrc1196@@@Z 0x004182A0 the matched hand-written notify00419F00 caller=0x00419F00 calls it directly at both castle sites; internal linkage replaces the member-spelling pin

// cl: /O2 /MD
// Address-derived data owner: dir32_addresses.csv records ?Rva012D6D75@@3_NA
// at VA 0x012D6D75, one byte after WW3D::IsSortingEnabled (0x012D6D74). Retail
// .data holds 01 there and the next recorded datum is 0x012D6D7C, so the
// readers (the sort test in PointGroupClassSubmit.cpp and
// W3DFXParticleSystemDoParticles.cpp) see a bool that starts true. Identity beyond the address is unproven.

bool Rva012D6D75 = true;

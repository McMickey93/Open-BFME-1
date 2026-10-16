# 0x0005C5D0 is ??0GameClientRandomVariable@@QAE@XZ; 16 over-claims retired

Approved by the project lead 2026-10-16.

0x0005C5D0 is a 13-byte constructor that zeroes three dwords
(`mov eax,ecx / xor ecx,ecx / mov [eax],ecx / mov [eax+4],ecx / mov [eax+8],ecx / ret`).
Seventeen functions.csv rows claimed it, from an era that assumed identical-COMDAT
folding. Retail was linked without ICF, so the body has one identity.

- exports.csv ordinal 246 (authoritative) names the thunk 0x0002466D ->
  0x0005C5D0 `??0GameClientRandomVariable@@QAE@XZ`. That row stays.
- No byte-matched caller lands on 0x0005C5D0 under any of the other sixteen
  names (relocations of every census object that names them, resolved against
  the retail image). Those rows are retired:
  ??0?$DLNodeClass@USmudge@@@@QAE@XZ, ??0?$DLNodeClass@USmudgeSet@@@@QAE@XZ,
  ??0?$DLNodeClass@VSortingNodeStruct@@@@QAE@XZ,
  ??0?$DLNodeClass@VThumbnailManagerClass@@@@QAE@XZ,
  ??0AnimSet@GenericObjectCreationNugget@@QAE@XZ, ??0ArmorTemplateSet@@QAE@XZ,
  ??0AssistanceRequestData@@QAE@XZ, ??0DistLODDefClass@@QAE@XZ,
  ??0DistLODNodeDefStruct@@QAE@XZ, ??0ModuleInfo@@QAE@XZ,
  ??0ModuleTemplate@ModuleFactory@@QAE@XZ, ??0ObjectCreationList@@QAE@XZ,
  ??0Smudge@@QAE@XZ, ??0TeamsInfoRec@@QAE@XZ,
  ??0WeaponRecoilInfo@W3DModelDraw@@QAE@XZ.
- `??0ResolutionDescClass@@QAE@XZ` is re-homed. The matched
  `VectorClass<ResolutionDescClass>` constructor and operator= (0x00906240,
  0x00905C80) call its byte-twin 0x009036E0 directly under that name, so it moves
  there, replacing ?dup_009036e0 (a gen-alias row).

# 0x009302C0 is VectorClass<BfmeHandleCX>::Resize, not VectorClass<MixFileCreator::FileInfoStruct>::Resize

The 403-byte body at 0x009302C0 was lifted as a naked `__emit` thunk named
`?Resize@?$VectorClass@UFileInfoStruct@MixFileCreator@@@@UAE_NHPBUFileInfoStruct@MixFileCreator@@@Z`.
Its own bytes refute that element type:

- It allocates `newsize*4+4` bytes and passes element size **4** to the EH vector
  constructor iterator (+0x36..+0x65) and the vector destructor iterator (+0x147).
  MixFileCreator::FileInfoStruct is 16 bytes: the matched
  `VectorClass<MixFileCreator::FileInfoStruct>::operator[]` (0x006EAC20) scales by `shl eax,4`.
- The constructor and destructor it pushes are ILT 0x000110D6 -> 0x0044F3C0
  (`??0BfmeHandleCX@@QAE@XZ`, matched) and ILT 0x00030652 -> 0x0005CC00
  (`??1BfmeHandleCX@@QAE@XZ`, matched): the four-byte TextureClass handle.
- The inlined element assignment in the copy loop adds a reference to the
  incoming TextureClass (16-bit count at +4) and calls `TextureClass::Release_Ref`
  on the old pointer.

WWLib's vector.h `VectorClass<T>::Resize`, instantiated for that handle in
VectorClassBfmeHandleCXResize.cpp (with the throw() `operator delete[]` lever of
VectorClassResizeNothrowDelete.cpp), reproduces all 403 bytes. The handle keeps
its existing address-era class name; only the template argument is corrected.

## 0x00930BE0 is DynamicVectorClass<BfmeHandleCX>::Resize

The 47-byte body at 0x00930BE0, ledgered as
`DynamicVectorClass<MixFileCreator::FileInfoStruct>::Resize` (mixfile.cpp), calls
0x009302C0 directly (+0x0F) and then clamps ActiveCount to VectorMax: the
DynamicVectorClass<T>::Resize of vector.h for the same element. Instantiated
beside the base Resize it compiles exact over all 47 bytes.

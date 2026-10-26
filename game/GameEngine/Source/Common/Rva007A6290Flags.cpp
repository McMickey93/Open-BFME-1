// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc

// the one definition is ?TheBfmeDrawableDirtyFlags@@3HA (data_rows 0x012EF418)
extern int TheBfmeDrawableDirtyFlags;

int __cdecl rva007A6290Has(unsigned int mask)
{
	return (TheBfmeDrawableDirtyFlags & mask) == mask;
}

void __cdecl rva007A62B0Clear(unsigned int mask)
{
	TheBfmeDrawableDirtyFlags &= ~mask;
}

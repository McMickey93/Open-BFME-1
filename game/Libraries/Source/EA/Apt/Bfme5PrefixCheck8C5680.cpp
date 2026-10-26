// Compare a string against the current command prefix.
const char *rva012D5A08Prefix = "FSCommand:";
extern "C" unsigned __cdecl strlen(const char *);
extern "C" int __cdecl strncmp(const char *, const char *, unsigned);

unsigned char __stdcall bfmeHasPrefix8C5680(const char *text)
{
	const char *prefix = rva012D5A08Prefix;
	return strncmp(text, prefix, strlen(prefix)) == 0;
}

// Retail VA 0x01337858: the two-string callback cell the stripped command goes to.
// retail 0x01337858; its one definition is ?g_bfmeSlot10VB@@3P6AXXZA (data_rows),
// a void() slot this caller invokes with two strings.
typedef void (__cdecl *BfmeProcVB)();
extern BfmeProcVB g_bfmeSlot10VB;
typedef void (__cdecl *Rva01337858Callback)(const char *, const char *);

// Retail 0x008C56C0 (46 B, unreferenced): skip the prefix length and hand the
// rest of the command and its argument to the callback cell; always 1.
int __stdcall bfmeStripPrefixForward8C56C0(const char *command, const char *args)
{
	((Rva01337858Callback)g_bfmeSlot10VB)(command + strlen(rva012D5A08Prefix), args);
	return 1;
}

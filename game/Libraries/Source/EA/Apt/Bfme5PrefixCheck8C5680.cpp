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
extern void (__cdecl *rva01337858Callback)(const char *, const char *);

// Retail 0x008C56C0 (46 B, unreferenced): skip the prefix length and hand the
// rest of the command and its argument to the callback cell; always 1.
int __stdcall bfmeStripPrefixForward8C56C0(const char *command, const char *args)
{
	rva01337858Callback(command + strlen(rva012D5A08Prefix), args);
	return 1;
}

// ?nextParam@@YAPADPAD0@Z
// The Zero Hour WinMain tokenizer names this body. Retail stores its static
// cursor at 0x012ED264 and loads strpbrk through 0x013594C4.
#include <string.h>

typedef char *(__cdecl *StrpbrkFunction)(const char *, const char *);
extern "C" StrpbrkFunction _imp__strpbrk;

char *nextParam(char *newSource, char *seps)
{
	static char *source = NULL;
	if (newSource)
	{
		source = newSource;
	}
	if (!source)
	{
		return NULL;
	}

	char *first = source;
	if (first)
	{
		StrpbrkFunction find = _imp__strpbrk;
		char *firstSep = find(first, seps);
		char firstChar[2] = {0, 0};
		if (firstSep == first)
		{
			firstChar[0] = *first;
			while (*first == firstChar[0]) first++;
		}

		char *end;
		if (firstChar[0])
			end = find(first, firstChar);
		else
			end = find(first, seps);

		if (end)
		{
			source = end+1;
			*end = 0;
			if (!*source)
				source = NULL;
		}
		else
		{
			source = NULL;
		}

		if (first && !*first)
			first = NULL;
	}

	return first;
}

// strtrim ====================================================================
/** Trim leading and trailing whitespace from a character string (in place). */
// Zero Hour WinMain's file-static; retail 0x0005D5B0 sits beside nextParam and
// takes buffer in EAX through VC7.1's private static convention. WWLib's
// trim.cpp owns the plain name (0x009E7EB0), so this copy takes the twin namespace.
//=============================================================================
namespace Rva0005D5B0Twin {
static char* strtrim(char* buffer)
{
	if (buffer != NULL) {
		//	Strip leading white space from the string.
		char * source = buffer;
		while ((*source != 0) && ((unsigned char)*source <= 32))
		{
			source++;
		}

		if (source != buffer)
		{
			strcpy(buffer, source);
		}

		//	Clip trailing white space from the string.
		for (int index = strlen(buffer)-1; index >= 0; index--)
		{
			if ((*source != 0) && ((unsigned char)buffer[index] <= 32))
			{
				buffer[index] = '\0';
			}
			else
			{
				break;
			}
		}
	}

	return buffer;
}
}

// absent-from-retail: TU-local caller that keeps the static above alive, as
// WinMain's argv loop does with argv[argc++] = strtrim(token).
char *strtrimCaller(char *token)
{
	return Rva0005D5B0Twin::strtrim(token);
}

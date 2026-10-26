// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/asciistring_downloadmanager /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib
/*
** Command & Conquer Generals Zero Hour(tm)
** Copyright 2025 Electronic Arts Inc.
**
** This program is free software: you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation, either version 3 of the License, or
** (at your option) any later version.
*/

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "Common/AsciiString.h"

// Retail inlines ~AsciiString: every temporary here is released by a direct call to
// StringBase<char>::releaseBuffer (0x00887940), not the ??1AsciiString stub.
inline AsciiString::~AsciiString()
{
	((StringBase<char> *)this)->releaseBuffer();
}

static const char *registryString(const AsciiString &value)
{
	char *data = *reinterpret_cast<char *const *>(&value);
	return data ? data + 8 : "";
}

static int registryLength(const AsciiString &value)
{
	char *data = *reinterpret_cast<char *const *>(&value);
	return data ? *(unsigned short *)(data + 4) : 0;
}

bool getUnsignedIntFromRegistry(HKEY root, AsciiString path, AsciiString key, unsigned int &val)
{
	HKEY handle;
	unsigned char buffer[4];
	unsigned long size = 4;
	unsigned long type;
	int returnValue;

	if ((returnValue = RegOpenKeyEx(root, registryString(path), 0, KEY_READ, &handle)) == ERROR_SUCCESS)
	{
		returnValue = RegQueryValueEx(handle, registryString(key), NULL, &type, buffer, &size);
		RegCloseKey(handle);
	}

	if (returnValue == ERROR_SUCCESS)
	{
		val = *(unsigned int *)buffer;
		return true;
	}

	return false;
}

bool GetUnsignedIntFromRegistry(AsciiString path, AsciiString key, unsigned int &val)
{
	AsciiString fullPath = "SOFTWARE\\Electronic Arts\\EA Games\\The Battle for Middle-earth";

	((StringBase<char> *)&fullPath)->concat(registryString(path), registryLength(path));
	if (getUnsignedIntFromRegistry(HKEY_LOCAL_MACHINE, registryString(fullPath), registryString(key), val))
		return true;

	return getUnsignedIntFromRegistry(HKEY_CURRENT_USER, registryString(fullPath), registryString(key), val);
}

// ?bfmeLocalUserMapsReady@@YA_NXZ @0x00109EB0
// Cached UseLocalUserMaps registry flag (0x012ABE78); negative until first read.
// The direct write to the out value inside the same-TU callee chain is what lets
// VC7.1 pack `registryValue` onto the first by-value saved-esp slot (frame 8).
bool bfmeLocalUserMapsReady(void)
{
	static int value = -1;
	if (value < 0)
	{
		unsigned int registryValue;
		value = GetUnsignedIntFromRegistry("", "UseLocalUserMaps", registryValue)
			? registryValue
			: 1;
	}

	return value != 0;
}

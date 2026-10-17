// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/sweep /Igame/Libraries/Source/WWVegas/WWLib
//
// Retail 0x00938620, 1057 bytes. EA's file is
// Libraries/Source/WWVegas/WW3D2/assetinit.cpp (ea_evidence.csv, wb1).
//
// W3DDisplay::init (0x006ED5B0) is the only caller: it copy-constructs two
// by-value AsciiStrings (GlobalData +0xDC0 and +0xDC4) into the argument slots
// and this body's unwind map destroys both, so the ABI is
// bool(AsciiString, AsciiString). The function's own name is unknown and keeps
// the address.
//
// It runs the two asset builder tools, then looks for asset.dat inside the .big
// archive named by the second argument (the archive's directory is big-endian:
// count at +8, entries from +16 as offset, size, NUL-terminated name), and then
// loads <first argument>\asset.dat and ./asset.dat through Load_Asset_Catalog.
// Only the last load decides the result.

#include <windows.h>
#include <stdio.h>
#include <string.h>
#include "ascii_string.h"

// Retail inlines isEmpty (0x0005E4C0) at both argument tests.
template<> inline bool StringBase<char>::isEmpty() const { return m_data == 0 || m_data->length == 0; }

#define CREATE_NO_WINDOW 0x08000000
extern "C" __declspec(dllimport) BOOL WINAPI GetExitCodeProcess(HANDLE process, DWORD *exitCode);
// WSOCK32 htonl.
extern "C" __declspec(dllimport) unsigned long __stdcall htonl(unsigned long value);

// Retail .data pointers to the two .big signatures the archive header is
// compared against: 0x012D719C -> "BIGF", 0x012D71A0 -> "BIG4".
extern char *g_Va012D719C;
extern char *g_Va012D71A0;

void Create_Rva00972880_Prototype(void);
bool Load_Asset_Catalog(void *stream);
void Rva009EBC50(int value);

bool Rva00938620(AsciiString assetPath, AsciiString bigFile)
{
	PROCESS_INFORMATION processInfo;
	STARTUPINFOA startupInfo;

	Create_Rva00972880_Prototype();

	memset(&startupInfo, 0, sizeof(startupInfo));
	startupInfo.cb = sizeof(startupInfo);
	if (CreateProcessA(NULL, "TextureAssetBuilder.exe", NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL,
			&startupInfo, &processInfo)) {
		DWORD exitCode;
		WaitForSingleObject(processInfo.hProcess, INFINITE);
		GetExitCodeProcess(processInfo.hProcess, &exitCode);
		CloseHandle(processInfo.hProcess);
		CloseHandle(processInfo.hThread);
	}

	memset(&startupInfo, 0, sizeof(startupInfo));
	startupInfo.cb = sizeof(startupInfo);
	if (CreateProcessA(NULL, "assetCacheBuilder.exe", NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL,
			&startupInfo, &processInfo)) {
		WaitForSingleObject(processInfo.hProcess, INFINITE);
		CloseHandle(processInfo.hProcess);
		CloseHandle(processInfo.hThread);
	}

	if (!bigFile.isEmpty()) {
		FILE *fp = fopen(bigFile.str(), "rb");
		if (fp != NULL) {
			char name[MAX_PATH];
			fread(name, 4, 1, fp);
			name[4] = 0;
			if (strcmp(name, g_Va012D719C) == 0 || strcmp(name, g_Va012D71A0) == 0) {
				int archiveSize = 0;
				int count = 0;
				fread(&archiveSize, 4, 1, fp);
				fread(&count, 4, 1, fp);
				count = htonl(count);
				fseek(fp, 16, SEEK_SET);
				int i;
				for (i = 0; i < count; ++i) {
					int size = 0;
					int offset = 0;
					fread(&offset, 4, 1, fp);
					fread(&size, 4, 1, fp);
					size = htonl(size);
					offset = htonl(offset);
					int len = -1;
					do {
						++len;
						fread(&name[len], 1, 1, fp);
					} while (name[len] != 0);
					int pos = len;
					while (pos >= 0 && name[pos] != '\\' && name[pos] != '/') {
						--pos;
					}
					if (_strcmpi(&name[pos + 1], "asset.dat") == 0) {
						fseek(fp, offset, SEEK_SET);
						break;
					}
				}
				if (i < count) {
					Load_Asset_Catalog(fp);
				}
			}
			fclose(fp);
		}
	}

	if (!assetPath.isEmpty()) {
		assetPath.StringBase<char>::concat("\\asset.dat", 10);
		FILE *fp = fopen(assetPath.str(), "rb");
		if (fp != NULL) {
			Load_Asset_Catalog(fp);
			fclose(fp);
		}
	}

	FILE *fp = fopen("asset.dat", "rb");
	if (fp == NULL) {
		return false;
	}
	bool loaded = Load_Asset_Catalog(fp);
	fclose(fp);
	if (!loaded) {
		return false;
	}
	MEMORYSTATUS status;
	GlobalMemoryStatus(&status);
	if (status.dwTotalPhys > 0x20000000) {
		Rva009EBC50(status.dwTotalPhys - 0x20000000);
	} else {
		Rva009EBC50(0);
	}
	return true;
}

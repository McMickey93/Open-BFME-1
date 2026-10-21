// cl: /O2 /MD
// Six-byte FF 25 [IAT] import stubs from the KERNEL32/USER32/GDI32/OLEAUT32 import-stub table at 0x0081BE86 that no row claimed.
// Retail links several copies of some stubs, so each keeps an address-derived
// name, as the matched _mbslen stub at 0x009F7262 does. stdcall stubs take
// the argument bytes their Platform SDK import decoration states; the cdecl
// CRT stubs never touch their arguments. A tail call is exactly `jmp [slot]`.

extern "C" __declspec(dllimport) int __stdcall CloseHandle(int);
extern "C" __declspec(dllimport) int __stdcall CompareStringA(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall CompareStringW(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall CopyFileA(int, int, int);
extern "C" __declspec(dllimport) int __stdcall CreateDirectoryA(int, int);
extern "C" __declspec(dllimport) int __stdcall CreateDirectoryW(int, int);
extern "C" __declspec(dllimport) int __stdcall CreateEventA(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall CreateFileA(int, int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall CreateMutexA(int, int, int);
extern "C" __declspec(dllimport) int __stdcall CreateMutexW(int, int, int);
extern "C" __declspec(dllimport) int __stdcall CreateProcessA(int, int, int, int, int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall CreateThread(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall DeleteCriticalSection(int);
extern "C" __declspec(dllimport) int __stdcall DeleteFileA(int);
extern "C" __declspec(dllimport) int __stdcall EnterCriticalSection(int);
extern "C" __declspec(dllimport) int __stdcall FindClose(int);
extern "C" __declspec(dllimport) int __stdcall FindFirstFileA(int, int);
extern "C" __declspec(dllimport) int __stdcall FindNextFileA(int, int);
extern "C" __declspec(dllimport) int __stdcall FormatMessageA(int, int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall FormatMessageW(int, int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall FreeLibrary(int);
extern "C" __declspec(dllimport) int __stdcall GetACP(void);
extern "C" __declspec(dllimport) int __stdcall GetCommConfig(int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetCommState(int, int);
extern "C" __declspec(dllimport) int __stdcall GetCommandLineA(void);
extern "C" __declspec(dllimport) int __stdcall GetComputerNameA(int, int);
extern "C" __declspec(dllimport) int __stdcall GetCurrentDirectoryA(int, int);
extern "C" __declspec(dllimport) int __stdcall GetCurrentThread(void);
extern "C" __declspec(dllimport) int __stdcall GetCurrentThreadId(void);
extern "C" __declspec(dllimport) int __stdcall GetDateFormatA(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetDateFormatW(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetDiskFreeSpaceExA(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetDriveTypeA(int);
extern "C" __declspec(dllimport) int __stdcall GetEnvironmentStrings(void);
extern "C" __declspec(dllimport) int __stdcall GetEnvironmentVariableA(int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetEnvironmentVariableW(int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetLastError(void);
extern "C" __declspec(dllimport) int __stdcall GetLocalTime(int);
extern "C" __declspec(dllimport) int __stdcall GetLocaleInfoA(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetModuleFileNameA(int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetModuleFileNameW(int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetModuleHandleA(int);
extern "C" __declspec(dllimport) int __stdcall GetOverlappedResult(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetProcAddress(int, int);
extern "C" __declspec(dllimport) int __stdcall GetProcessHeap(void);
extern "C" __declspec(dllimport) int __stdcall GetStringTypeA(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetStringTypeExW(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetTempFileNameA(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetTempPathA(int, int);
extern "C" __declspec(dllimport) int __stdcall GetThreadLocale(void);
extern "C" __declspec(dllimport) int __stdcall GetTickCount(void);
extern "C" __declspec(dllimport) int __stdcall GetTimeFormatA(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetTimeFormatW(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetTimeZoneInformation(int);
extern "C" __declspec(dllimport) int __stdcall GetVersion(void);
extern "C" __declspec(dllimport) int __stdcall GetVersionExA(int);
extern "C" __declspec(dllimport) int __stdcall GetVolumeInformationA(int, int, int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall HeapAlloc(int, int, int);
extern "C" __declspec(dllimport) int __stdcall HeapFree(int, int, int);
extern "C" __declspec(dllimport) int __stdcall InitializeCriticalSection(int);
extern "C" __declspec(dllimport) int __stdcall InterlockedDecrement(int);
extern "C" __declspec(dllimport) int __stdcall InterlockedExchange(int, int);
extern "C" __declspec(dllimport) int __stdcall InterlockedIncrement(int);
extern "C" __declspec(dllimport) int __stdcall IsBadReadPtr(int, int);
extern "C" __declspec(dllimport) int __stdcall IsIconic(int);
extern "C" __declspec(dllimport) int __stdcall LeaveCriticalSection(int);
extern "C" __declspec(dllimport) int __stdcall LoadLibraryA(int);
extern "C" __declspec(dllimport) int __stdcall LocalAlloc(int, int);
extern "C" __declspec(dllimport) int __stdcall LocalFree(int);
extern "C" __declspec(dllimport) int __stdcall MapViewOfFileEx(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall MultiByteToWideChar(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall OpenEventA(int, int, int);
extern "C" __declspec(dllimport) int __stdcall OutputDebugStringA(int);
extern "C" __declspec(dllimport) int __stdcall PurgeComm(int, int);
extern "C" __declspec(dllimport) int __stdcall QueryPerformanceCounter(int);
extern "C" __declspec(dllimport) int __stdcall QueryPerformanceFrequency(int);
extern "C" __declspec(dllimport) int __stdcall RaiseException(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall ReadFile(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall ReleaseMutex(int);
extern "C" __declspec(dllimport) int __stdcall RemoveDirectoryA(int);
extern "C" __declspec(dllimport) int __stdcall SetCommConfig(int, int, int);
extern "C" __declspec(dllimport) int __stdcall SetCommMask(int, int);
extern "C" __declspec(dllimport) int __stdcall SetCommState(int, int);
extern "C" __declspec(dllimport) int __stdcall SetCommTimeouts(int, int);
extern "C" __declspec(dllimport) int __stdcall SetCurrentDirectoryA(int);
extern "C" __declspec(dllimport) int __stdcall SetErrorMode(int);
extern "C" __declspec(dllimport) int __stdcall SetEvent(int);
extern "C" __declspec(dllimport) int __stdcall SetThreadPriority(int, int);
extern "C" __declspec(dllimport) int __stdcall SetupComm(int, int, int);
extern "C" __declspec(dllimport) int __stdcall ShowCursor(int);
extern "C" __declspec(dllimport) int __stdcall Sleep(int);
extern "C" __declspec(dllimport) int __stdcall SysAllocString(int);
extern "C" __declspec(dllimport) int __stdcall SysFreeString(int);
extern "C" __declspec(dllimport) int __stdcall SysStringLen(int);
extern "C" __declspec(dllimport) int __stdcall TerminateProcess(int, int);
extern "C" __declspec(dllimport) int __stdcall TerminateThread(int, int);
extern "C" __declspec(dllimport) int __stdcall UnmapViewOfFile(int);
extern "C" __declspec(dllimport) int __stdcall WaitCommEvent(int, int, int);
extern "C" __declspec(dllimport) int __stdcall WaitForMultipleObjects(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall WaitForSingleObject(int, int);
extern "C" __declspec(dllimport) int __stdcall WideCharToMultiByte(int, int, int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall WriteFile(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall lstrcmpi(int, int);
extern "C" __declspec(dllimport) int __stdcall lstrcmpiW(int, int);
extern "C" __declspec(dllimport) int __stdcall lstrlenA(int);
extern "C" __declspec(dllimport) int __stdcall lstrlenW(int);

int __stdcall Rva0081BE86InterlockedExchange(int a0, int a1) { return InterlockedExchange(a0, a1); }
int __stdcall Rva0081BE8CGetACP(void) { return GetACP(); }
int __stdcall Rva0081BE92GetLocaleInfoA(int a0, int a1, int a2, int a3) { return GetLocaleInfoA(a0, a1, a2, a3); }
int __stdcall Rva0081BE98GetThreadLocale(void) { return GetThreadLocale(); }
int __stdcall Rva0081BE9EGetVersionExA(int a0) { return GetVersionExA(a0); }
int __stdcall Rva0081BEA4MultiByteToWideChar(int a0, int a1, int a2, int a3, int a4, int a5) { return MultiByteToWideChar(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva0081BEAAWideCharToMultiByte(int a0, int a1, int a2, int a3, int a4, int a5, int a6, int a7) { return WideCharToMultiByte(a0, a1, a2, a3, a4, a5, a6, a7); }
int __stdcall Rva0081BEB0lstrlenA(int a0) { return lstrlenA(a0); }
int __stdcall Rva0081BEB6lstrlenW(int a0) { return lstrlenW(a0); }
int __stdcall Rva0081BEBCGetLastError(void) { return GetLastError(); }
int __stdcall Rva0081BEC2LeaveCriticalSection(int a0) { return LeaveCriticalSection(a0); }
int __stdcall Rva0081BEC8EnterCriticalSection(int a0) { return EnterCriticalSection(a0); }
int __stdcall Rva0081BECEFreeLibrary(int a0) { return FreeLibrary(a0); }
int __stdcall Rva0081BED4GetProcAddress(int a0, int a1) { return GetProcAddress(a0, a1); }
int __stdcall Rva0081BEDALoadLibraryA(int a0) { return LoadLibraryA(a0); }
int __stdcall Rva0081BEE0GetVersion(void) { return GetVersion(); }
int __stdcall Rva0081BEE6lstrcmpi(int a0, int a1) { return lstrcmpi(a0, a1); }
int __stdcall Rva0081BEEClstrcmpiW(int a0, int a1) { return lstrcmpiW(a0, a1); }
int __stdcall Rva0081BEF2CompareStringA(int a0, int a1, int a2, int a3, int a4, int a5) { return CompareStringA(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva0081BEF8CompareStringW(int a0, int a1, int a2, int a3, int a4, int a5) { return CompareStringW(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva0081BEFEGetEnvironmentVariableA(int a0, int a1, int a2) { return GetEnvironmentVariableA(a0, a1, a2); }
int __stdcall Rva0081BF04GetEnvironmentVariableW(int a0, int a1, int a2) { return GetEnvironmentVariableW(a0, a1, a2); }
int __stdcall Rva0081BF0AGetStringTypeA(int a0, int a1, int a2, int a3, int a4) { return GetStringTypeA(a0, a1, a2, a3, a4); }
int __stdcall Rva0081BF10GetStringTypeExW(int a0, int a1, int a2, int a3, int a4) { return GetStringTypeExW(a0, a1, a2, a3, a4); }
int __stdcall Rva0081BF16CloseHandle(int a0) { return CloseHandle(a0); }
int __stdcall Rva0081BF1CCreateMutexW(int a0, int a1, int a2) { return CreateMutexW(a0, a1, a2); }
int __stdcall Rva0081BF22SetCurrentDirectoryA(int a0) { return SetCurrentDirectoryA(a0); }
int __stdcall Rva0081BF28GetModuleFileNameA(int a0, int a1, int a2) { return GetModuleFileNameA(a0, a1, a2); }
int __stdcall Rva0081BF2EGetLocalTime(int a0) { return GetLocalTime(a0); }
int __stdcall Rva0081BF34Sleep(int a0) { return Sleep(a0); }
int __stdcall Rva0081BF3ACreateProcessA(int a0, int a1, int a2, int a3, int a4, int a5, int a6, int a7, int a8, int a9) { return CreateProcessA(a0, a1, a2, a3, a4, a5, a6, a7, a8, a9); }
int __stdcall Rva0081BF40GetCommandLineA(void) { return GetCommandLineA(); }
int __stdcall Rva0081BF46GetEnvironmentStrings(void) { return GetEnvironmentStrings(); }
int __stdcall Rva0081BF4CTerminateProcess(int a0, int a1) { return TerminateProcess(a0, a1); }
int __stdcall Rva0081BF52CreateDirectoryA(int a0, int a1) { return CreateDirectoryA(a0, a1); }
int __stdcall Rva0081BF58CreateDirectoryW(int a0, int a1) { return CreateDirectoryW(a0, a1); }
int __stdcall Rva0081BF5EInterlockedIncrement(int a0) { return InterlockedIncrement(a0); }
int __stdcall Rva0081BF64InterlockedDecrement(int a0) { return InterlockedDecrement(a0); }
int __stdcall Rva0081BF6AOutputDebugStringA(int a0) { return OutputDebugStringA(a0); }
int __stdcall Rva0081BF70CreateMutexA(int a0, int a1, int a2) { return CreateMutexA(a0, a1, a2); }
int __stdcall Rva0081BF76MapViewOfFileEx(int a0, int a1, int a2, int a3, int a4, int a5) { return MapViewOfFileEx(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva0081BF7CSetEvent(int a0) { return SetEvent(a0); }
int __stdcall Rva0081BF82OpenEventA(int a0, int a1, int a2) { return OpenEventA(a0, a1, a2); }
int __stdcall Rva0081BF88UnmapViewOfFile(int a0) { return UnmapViewOfFile(a0); }
int __stdcall Rva0081BF8EInitializeCriticalSection(int a0) { return InitializeCriticalSection(a0); }
int __stdcall Rva0081BF94DeleteCriticalSection(int a0) { return DeleteCriticalSection(a0); }
int __stdcall Rva0081BF9AGetDateFormatW(int a0, int a1, int a2, int a3, int a4, int a5) { return GetDateFormatW(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva0081BFA0GetDateFormatA(int a0, int a1, int a2, int a3, int a4, int a5) { return GetDateFormatA(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva0081BFA6GetTimeFormatW(int a0, int a1, int a2, int a3, int a4, int a5) { return GetTimeFormatW(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva0081BFACGetTimeFormatA(int a0, int a1, int a2, int a3, int a4, int a5) { return GetTimeFormatA(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva0081BFB2FindClose(int a0) { return FindClose(a0); }
int __stdcall Rva0081BFB8FindNextFileA(int a0, int a1) { return FindNextFileA(a0, a1); }
int __stdcall Rva0081BFBEFindFirstFileA(int a0, int a1) { return FindFirstFileA(a0, a1); }
int __stdcall Rva0081BFC4GetCurrentDirectoryA(int a0, int a1) { return GetCurrentDirectoryA(a0, a1); }
int __stdcall Rva0081BFCADeleteFileA(int a0) { return DeleteFileA(a0); }
int __stdcall Rva0081BFD0GetComputerNameA(int a0, int a1) { return GetComputerNameA(a0, a1); }
int __stdcall Rva0081BFD6QueryPerformanceFrequency(int a0) { return QueryPerformanceFrequency(a0); }
int __stdcall Rva0081BFDCQueryPerformanceCounter(int a0) { return QueryPerformanceCounter(a0); }
int __stdcall Rva0081BFE2WaitForSingleObject(int a0, int a1) { return WaitForSingleObject(a0, a1); }
int __stdcall Rva0081BFE8ReleaseMutex(int a0) { return ReleaseMutex(a0); }
int __stdcall Rva0081BFEESetThreadPriority(int a0, int a1) { return SetThreadPriority(a0, a1); }
int __stdcall Rva0081BFF4GetCurrentThread(void) { return GetCurrentThread(); }
int __stdcall Rva0081BFFAGetCurrentThreadId(void) { return GetCurrentThreadId(); }
int __stdcall Rva0081C000CreateThread(int a0, int a1, int a2, int a3, int a4, int a5) { return CreateThread(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva0081C006WriteFile(int a0, int a1, int a2, int a3, int a4) { return WriteFile(a0, a1, a2, a3, a4); }
int __stdcall Rva0081C00CCreateFileA(int a0, int a1, int a2, int a3, int a4, int a5, int a6) { return CreateFileA(a0, a1, a2, a3, a4, a5, a6); }
int __stdcall Rva0081C012GetTempFileNameA(int a0, int a1, int a2, int a3) { return GetTempFileNameA(a0, a1, a2, a3); }
int __stdcall Rva0081C018GetTempPathA(int a0, int a1) { return GetTempPathA(a0, a1); }
int __stdcall Rva0081C01ERemoveDirectoryA(int a0) { return RemoveDirectoryA(a0); }
int __stdcall Rva0081C024CopyFileA(int a0, int a1, int a2) { return CopyFileA(a0, a1, a2); }
int __stdcall Rva0081C02AFormatMessageW(int a0, int a1, int a2, int a3, int a4, int a5, int a6) { return FormatMessageW(a0, a1, a2, a3, a4, a5, a6); }
int __stdcall Rva0081C030FormatMessageA(int a0, int a1, int a2, int a3, int a4, int a5, int a6) { return FormatMessageA(a0, a1, a2, a3, a4, a5, a6); }
int __stdcall Rva0081C036GetModuleFileNameW(int a0, int a1, int a2) { return GetModuleFileNameW(a0, a1, a2); }
int __stdcall Rva0081C03CIsBadReadPtr(int a0, int a1) { return IsBadReadPtr(a0, a1); }
int __stdcall Rva0081C042GetTimeZoneInformation(int a0) { return GetTimeZoneInformation(a0); }
int __stdcall Rva0081C048GetDiskFreeSpaceExA(int a0, int a1, int a2, int a3) { return GetDiskFreeSpaceExA(a0, a1, a2, a3); }
int __stdcall Rva0081C04EGetTickCount(void) { return GetTickCount(); }
int __stdcall Rva0081C054TerminateThread(int a0, int a1) { return TerminateThread(a0, a1); }
int __stdcall Rva0081C05AGetVolumeInformationA(int a0, int a1, int a2, int a3, int a4, int a5, int a6, int a7) { return GetVolumeInformationA(a0, a1, a2, a3, a4, a5, a6, a7); }
int __stdcall Rva0081C060GetDriveTypeA(int a0) { return GetDriveTypeA(a0); }
int __stdcall Rva0081C066SetErrorMode(int a0) { return SetErrorMode(a0); }
int __stdcall Rva0081C06CLocalFree(int a0) { return LocalFree(a0); }
int __stdcall Rva0081C072LocalAlloc(int a0, int a1) { return LocalAlloc(a0, a1); }
int __stdcall Rva0081C078HeapFree(int a0, int a1, int a2) { return HeapFree(a0, a1, a2); }
int __stdcall Rva0081C07EHeapAlloc(int a0, int a1, int a2) { return HeapAlloc(a0, a1, a2); }
int __stdcall Rva0081C084GetProcessHeap(void) { return GetProcessHeap(); }
int __stdcall Rva0081C08ARaiseException(int a0, int a1, int a2, int a3) { return RaiseException(a0, a1, a2, a3); }
int __stdcall Rva0081C090GetModuleHandleA(int a0) { return GetModuleHandleA(a0); }
int __stdcall Rva0081C096CreateEventA(int a0, int a1, int a2, int a3) { return CreateEventA(a0, a1, a2, a3); }
int __stdcall Rva0081C09CWaitForMultipleObjects(int a0, int a1, int a2, int a3) { return WaitForMultipleObjects(a0, a1, a2, a3); }
int __stdcall Rva0081C0A2WaitCommEvent(int a0, int a1, int a2) { return WaitCommEvent(a0, a1, a2); }
int __stdcall Rva0081C0A8GetOverlappedResult(int a0, int a1, int a2, int a3) { return GetOverlappedResult(a0, a1, a2, a3); }
int __stdcall Rva0081C0AEReadFile(int a0, int a1, int a2, int a3, int a4) { return ReadFile(a0, a1, a2, a3, a4); }
int __stdcall Rva0081C0B4SetCommMask(int a0, int a1) { return SetCommMask(a0, a1); }
int __stdcall Rva0081C0BAPurgeComm(int a0, int a1) { return PurgeComm(a0, a1); }
int __stdcall Rva0081C0C0SetCommState(int a0, int a1) { return SetCommState(a0, a1); }
int __stdcall Rva0081C0C6GetCommState(int a0, int a1) { return GetCommState(a0, a1); }
int __stdcall Rva0081C0CCSetCommConfig(int a0, int a1, int a2) { return SetCommConfig(a0, a1, a2); }
int __stdcall Rva0081C0D2GetCommConfig(int a0, int a1, int a2) { return GetCommConfig(a0, a1, a2); }
int __stdcall Rva0081C0D8SetCommTimeouts(int a0, int a1) { return SetCommTimeouts(a0, a1); }
int __stdcall Rva0081C0DESetupComm(int a0, int a1, int a2) { return SetupComm(a0, a1, a2); }
int __stdcall Rva0081C1B0ShowCursor(int a0) { return ShowCursor(a0); }
int __stdcall Rva0081C1B6IsIconic(int a0) { return IsIconic(a0); }
int __stdcall Rva0081C2CASysFreeString(int a0) { return SysFreeString(a0); }
int __stdcall Rva0081C2D0SysStringLen(int a0) { return SysStringLen(a0); }
int __stdcall Rva0081C2D6SysAllocString(int a0) { return SysAllocString(a0); }

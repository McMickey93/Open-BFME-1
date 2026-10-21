// cl: /O2 /MD
// Six-byte FF 25 [IAT] import stubs from the KERNEL32/USER32/GDI32/ADVAPI32/OLEAUT32 import-stub table at 0x00AFE378 that no row claimed.
// Retail links several copies of some stubs, so each keeps an address-derived
// name, as the matched _mbslen stub at 0x009F7262 does. stdcall stubs take
// the argument bytes their Platform SDK import decoration states; the cdecl
// CRT stubs never touch their arguments. A tail call is exactly `jmp [slot]`.

extern "C" __declspec(dllimport) int __stdcall AllocConsole(void);
extern "C" __declspec(dllimport) int __stdcall CreateErrorInfo(int);
extern "C" __declspec(dllimport) int __stdcall CreateFileMappingA(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall CreateFileW(int, int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall DebugBreak(void);
extern "C" __declspec(dllimport) int __stdcall DosDateTimeToFileTime(int, int, int);
extern "C" __declspec(dllimport) int __stdcall EnumSystemLocalesA(int, int);
extern "C" __declspec(dllimport) int __stdcall ExitProcess(int);
extern "C" __declspec(dllimport) int __stdcall FileTimeToDosDateTime(int, int, int);
extern "C" __declspec(dllimport) int __stdcall FindResourceA(int, int, int);
extern "C" __declspec(dllimport) int __stdcall FindResourceW(int, int, int);
extern "C" __declspec(dllimport) int __stdcall FreeConsole(void);
extern "C" __declspec(dllimport) int __stdcall GetCPInfo(int, int);
extern "C" __declspec(dllimport) int __stdcall GetConsoleScreenBufferInfo(int, int);
extern "C" __declspec(dllimport) int __stdcall GetConsoleTitleA(int, int);
extern "C" __declspec(dllimport) int __stdcall GetCurrentProcess(void);
extern "C" __declspec(dllimport) int __stdcall GetCurrentProcessId(void);
extern "C" __declspec(dllimport) int __stdcall GetErrorInfo(int, int);
extern "C" __declspec(dllimport) int __stdcall GetExitCodeProcess(int, int);
extern "C" __declspec(dllimport) int __stdcall GetExitCodeThread(int, int);
extern "C" __declspec(dllimport) int __stdcall GetFileInformationByHandle(int, int);
extern "C" __declspec(dllimport) int __stdcall GetFileSize(int, int);
extern "C" __declspec(dllimport) int __stdcall GetFileType(int);
extern "C" __declspec(dllimport) int __stdcall GetFullPathNameA(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetNumberOfConsoleInputEvents(int, int);
extern "C" __declspec(dllimport) int __stdcall GetPriorityClass(int);
extern "C" __declspec(dllimport) int __stdcall GetStartupInfoA(int);
extern "C" __declspec(dllimport) int __stdcall GetStdHandle(int);
extern "C" __declspec(dllimport) int __stdcall GetStringTypeA(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetStringTypeW(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall GetSystemInfo(int);
extern "C" __declspec(dllimport) int __stdcall GetSystemTimeAsFileTime(int);
extern "C" __declspec(dllimport) int __stdcall GetThreadPriority(int);
extern "C" __declspec(dllimport) int __stdcall GlobalAlloc(int, int);
extern "C" __declspec(dllimport) int __stdcall GlobalFree(int);
extern "C" __declspec(dllimport) int __stdcall GlobalMemoryStatus(int);
extern "C" __declspec(dllimport) int __stdcall GlobalReAlloc(int, int, int);
extern "C" __declspec(dllimport) int __stdcall GlobalSize(int);
extern "C" __declspec(dllimport) int __stdcall HeapCreate(int, int, int);
extern "C" __declspec(dllimport) int __stdcall HeapSetInformation(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall InterlockedCompareExchange(int, int, int);
extern "C" __declspec(dllimport) int __stdcall IsBadCodePtr(int);
extern "C" __declspec(dllimport) int __stdcall IsProcessorFeaturePresent(int);
extern "C" __declspec(dllimport) int __stdcall LCMapStringA(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall LCMapStringW(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall LoadResource(int, int);
extern "C" __declspec(dllimport) int __stdcall LockResource(int);
extern "C" __declspec(dllimport) int __stdcall MapViewOfFile(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall MulDiv(int, int, int);
extern "C" __declspec(dllimport) int __stdcall OutputDebugStringW(int);
extern "C" __declspec(dllimport) int __stdcall ReadConsoleInputA(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall ReadProcessMemory(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall RegDeleteValueA(int, int);
extern "C" __declspec(dllimport) int __stdcall RegEnumValueA(int, int, int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall RegSetValueExW(int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall ResumeThread(int);
extern "C" __declspec(dllimport) int __stdcall SetConsoleCtrlHandler(int, int);
extern "C" __declspec(dllimport) int __stdcall SetConsoleCursorInfo(int, int);
extern "C" __declspec(dllimport) int __stdcall SetConsoleMode(int, int);
extern "C" __declspec(dllimport) int __stdcall SetConsoleScreenBufferSize(int, int);
extern "C" __declspec(dllimport) int __stdcall SetConsoleTitleA(int);
extern "C" __declspec(dllimport) int __stdcall SetConsoleWindowInfo(int, int, int);
extern "C" __declspec(dllimport) int __stdcall SetEndOfFile(int);
extern "C" __declspec(dllimport) int __stdcall SetErrorInfo(int, int);
extern "C" __declspec(dllimport) int __stdcall SetFilePointer(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall SetFileTime(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall SetNamedPipeHandleState(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall SetPriorityClass(int, int);
extern "C" __declspec(dllimport) int __stdcall SetUnhandledExceptionFilter(int);
extern "C" __declspec(dllimport) int __stdcall SizeofResource(int, int);
extern "C" __declspec(dllimport) int __stdcall SuspendThread(int);
extern "C" __declspec(dllimport) int __stdcall VariantChangeType(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall VariantClear(int);
extern "C" __declspec(dllimport) int __stdcall VariantInit(int);
extern "C" __declspec(dllimport) int __stdcall VirtualAlloc(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall VirtualFree(int, int, int);
extern "C" __declspec(dllimport) int __stdcall VirtualProtect(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall VirtualQuery(int, int, int);
extern "C" __declspec(dllimport) int __stdcall WriteConsoleOutputA(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall WriteProcessMemory(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall lstrcpy(int, int);
extern "C" __declspec(dllimport) int __stdcall lstrcpyn(int, int, int);

int __stdcall Rva00AFE378GetFileType(int a0) { return GetFileType(a0); }
int __stdcall Rva00AFE37EGetFileSize(int a0, int a1) { return GetFileSize(a0, a1); }
int __stdcall Rva00AFE384GetSystemInfo(int a0) { return GetSystemInfo(a0); }
int __stdcall Rva00AFE38ASetFilePointer(int a0, int a1, int a2, int a3) { return SetFilePointer(a0, a1, a2, a3); }
int __stdcall Rva00AFE390SetEndOfFile(int a0) { return SetEndOfFile(a0); }
int __stdcall Rva00AFE396MapViewOfFile(int a0, int a1, int a2, int a3, int a4) { return MapViewOfFile(a0, a1, a2, a3, a4); }
int __stdcall Rva00AFE39CCreateFileMappingA(int a0, int a1, int a2, int a3, int a4, int a5) { return CreateFileMappingA(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva00AFE3A2GetStringTypeW(int a0, int a1, int a2, int a3) { return GetStringTypeW(a0, a1, a2, a3); }
int __stdcall Rva00AFE3A8LCMapStringW(int a0, int a1, int a2, int a3, int a4, int a5) { return LCMapStringW(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva00AFE3AEGetCPInfo(int a0, int a1) { return GetCPInfo(a0, a1); }
int __stdcall Rva00AFE3B4EnumSystemLocalesA(int a0, int a1) { return EnumSystemLocalesA(a0, a1); }
int __stdcall Rva00AFE3BALCMapStringA(int a0, int a1, int a2, int a3, int a4, int a5) { return LCMapStringA(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva00AFE3C0GetStringTypeA(int a0, int a1, int a2, int a3, int a4) { return GetStringTypeA(a0, a1, a2, a3, a4); }
int __stdcall Rva00AFE3C6SetPriorityClass(int a0, int a1) { return SetPriorityClass(a0, a1); }
int __stdcall Rva00AFE3CCGetThreadPriority(int a0) { return GetThreadPriority(a0); }
int __stdcall Rva00AFE3D2GetPriorityClass(int a0) { return GetPriorityClass(a0); }
int __stdcall Rva00AFE3D8GetCurrentProcess(void) { return GetCurrentProcess(); }
int __stdcall Rva00AFE3DEWriteProcessMemory(int a0, int a1, int a2, int a3, int a4) { return WriteProcessMemory(a0, a1, a2, a3, a4); }
int __stdcall Rva00AFE3E4VirtualProtect(int a0, int a1, int a2, int a3) { return VirtualProtect(a0, a1, a2, a3); }
int __stdcall Rva00AFE3FCGetCurrentProcessId(void) { return GetCurrentProcessId(); }
int __stdcall Rva00AFE402HeapSetInformation(int a0, int a1, int a2, int a3) { return HeapSetInformation(a0, a1, a2, a3); }
int __stdcall Rva00AFE408HeapCreate(int a0, int a1, int a2) { return HeapCreate(a0, a1, a2); }
int __stdcall Rva00AFE40EMulDiv(int a0, int a1, int a2) { return MulDiv(a0, a1, a2); }
int __stdcall Rva00AFE414SetUnhandledExceptionFilter(int a0) { return SetUnhandledExceptionFilter(a0); }
int __stdcall Rva00AFE41AIsBadCodePtr(int a0) { return IsBadCodePtr(a0); }
int __stdcall Rva00AFE420ReadProcessMemory(int a0, int a1, int a2, int a3, int a4) { return ReadProcessMemory(a0, a1, a2, a3, a4); }
int __stdcall Rva00AFE42CResumeThread(int a0) { return ResumeThread(a0); }
int __stdcall Rva00AFE438GetExitCodeThread(int a0, int a1) { return GetExitCodeThread(a0, a1); }
int __stdcall Rva00AFE43ESuspendThread(int a0) { return SuspendThread(a0); }
int __stdcall Rva00AFE444ExitProcess(int a0) { return ExitProcess(a0); }
int __stdcall Rva00AFE44AVirtualQuery(int a0, int a1, int a2) { return VirtualQuery(a0, a1, a2); }
int __stdcall Rva00AFE450GlobalFree(int a0) { return GlobalFree(a0); }
int __stdcall Rva00AFE456GlobalAlloc(int a0, int a1) { return GlobalAlloc(a0, a1); }
int __stdcall Rva00AFE45CGlobalSize(int a0) { return GlobalSize(a0); }
int __stdcall Rva00AFE462GlobalReAlloc(int a0, int a1, int a2) { return GlobalReAlloc(a0, a1, a2); }
int __stdcall Rva00AFE468SetNamedPipeHandleState(int a0, int a1, int a2, int a3) { return SetNamedPipeHandleState(a0, a1, a2, a3); }
int __stdcall Rva00AFE46EFreeConsole(void) { return FreeConsole(); }
int __stdcall Rva00AFE474WriteConsoleOutputA(int a0, int a1, int a2, int a3, int a4) { return WriteConsoleOutputA(a0, a1, a2, a3, a4); }
int __stdcall Rva00AFE47AGetConsoleScreenBufferInfo(int a0, int a1) { return GetConsoleScreenBufferInfo(a0, a1); }
int __stdcall Rva00AFE480ReadConsoleInputA(int a0, int a1, int a2, int a3) { return ReadConsoleInputA(a0, a1, a2, a3); }
int __stdcall Rva00AFE486GetNumberOfConsoleInputEvents(int a0, int a1) { return GetNumberOfConsoleInputEvents(a0, a1); }
int __stdcall Rva00AFE48CGetStdHandle(int a0) { return GetStdHandle(a0); }
int __stdcall Rva00AFE492SetConsoleScreenBufferSize(int a0, int a1) { return SetConsoleScreenBufferSize(a0, a1); }
int __stdcall Rva00AFE498SetConsoleWindowInfo(int a0, int a1, int a2) { return SetConsoleWindowInfo(a0, a1, a2); }
int __stdcall Rva00AFE49ESetConsoleTitleA(int a0) { return SetConsoleTitleA(a0); }
int __stdcall Rva00AFE4A4GetConsoleTitleA(int a0, int a1) { return GetConsoleTitleA(a0, a1); }
int __stdcall Rva00AFE4AASetConsoleCtrlHandler(int a0, int a1) { return SetConsoleCtrlHandler(a0, a1); }
int __stdcall Rva00AFE4B0SetConsoleCursorInfo(int a0, int a1) { return SetConsoleCursorInfo(a0, a1); }
int __stdcall Rva00AFE4B6SetConsoleMode(int a0, int a1) { return SetConsoleMode(a0, a1); }
int __stdcall Rva00AFE4BCAllocConsole(void) { return AllocConsole(); }
int __stdcall Rva00AFE4C2lstrcpy(int a0, int a1) { return lstrcpy(a0, a1); }
int __stdcall Rva00AFE4C8GlobalMemoryStatus(int a0) { return GlobalMemoryStatus(a0); }
int __stdcall Rva00AFE4CEGetExitCodeProcess(int a0, int a1) { return GetExitCodeProcess(a0, a1); }
int __stdcall Rva00AFE4D4lstrcpyn(int a0, int a1, int a2) { return lstrcpyn(a0, a1, a2); }
int __stdcall Rva00AFE4DAFileTimeToDosDateTime(int a0, int a1, int a2) { return FileTimeToDosDateTime(a0, a1, a2); }
int __stdcall Rva00AFE4E0GetFileInformationByHandle(int a0, int a1) { return GetFileInformationByHandle(a0, a1); }
int __stdcall Rva00AFE4E6SetFileTime(int a0, int a1, int a2, int a3) { return SetFileTime(a0, a1, a2, a3); }
int __stdcall Rva00AFE4ECDosDateTimeToFileTime(int a0, int a1, int a2) { return DosDateTimeToFileTime(a0, a1, a2); }
int __stdcall Rva00AFE4F2GetStartupInfoA(int a0) { return GetStartupInfoA(a0); }
int __stdcall Rva00AFE4F8DebugBreak(void) { return DebugBreak(); }
int __stdcall Rva00AFE4FEGetSystemTimeAsFileTime(int a0) { return GetSystemTimeAsFileTime(a0); }
int __stdcall Rva00AFE504IsProcessorFeaturePresent(int a0) { return IsProcessorFeaturePresent(a0); }
int __stdcall Rva00AFE50ACreateFileW(int a0, int a1, int a2, int a3, int a4, int a5, int a6) { return CreateFileW(a0, a1, a2, a3, a4, a5, a6); }
int __stdcall Rva00AFE510LockResource(int a0) { return LockResource(a0); }
int __stdcall Rva00AFE516LoadResource(int a0, int a1) { return LoadResource(a0, a1); }
int __stdcall Rva00AFE51CSizeofResource(int a0, int a1) { return SizeofResource(a0, a1); }
int __stdcall Rva00AFE522FindResourceA(int a0, int a1, int a2) { return FindResourceA(a0, a1, a2); }
int __stdcall Rva00AFE528FindResourceW(int a0, int a1, int a2) { return FindResourceW(a0, a1, a2); }
int __stdcall Rva00AFE52EInterlockedCompareExchange(int a0, int a1, int a2) { return InterlockedCompareExchange(a0, a1, a2); }
int __stdcall Rva00AFE534GetFullPathNameA(int a0, int a1, int a2, int a3) { return GetFullPathNameA(a0, a1, a2, a3); }
int __stdcall Rva00AFE53AVirtualFree(int a0, int a1, int a2) { return VirtualFree(a0, a1, a2); }
int __stdcall Rva00AFE540VirtualAlloc(int a0, int a1, int a2, int a3) { return VirtualAlloc(a0, a1, a2, a3); }
int __stdcall Rva00AFE546OutputDebugStringW(int a0) { return OutputDebugStringW(a0); }
int __stdcall Rva00AFE618RegDeleteValueA(int a0, int a1) { return RegDeleteValueA(a0, a1); }
int __stdcall Rva00AFE61ERegSetValueExW(int a0, int a1, int a2, int a3, int a4, int a5) { return RegSetValueExW(a0, a1, a2, a3, a4, a5); }
int __stdcall Rva00AFE624RegEnumValueA(int a0, int a1, int a2, int a3, int a4, int a5, int a6, int a7) { return RegEnumValueA(a0, a1, a2, a3, a4, a5, a6, a7); }
int __stdcall Rva00AFE64EGetErrorInfo(int a0, int a1) { return GetErrorInfo(a0, a1); }
int __stdcall Rva00AFE654VariantClear(int a0) { return VariantClear(a0); }
int __stdcall Rva00AFE65AVariantChangeType(int a0, int a1, int a2, int a3) { return VariantChangeType(a0, a1, a2, a3); }
int __stdcall Rva00AFE660VariantInit(int a0) { return VariantInit(a0); }
int __stdcall Rva00AFE666SetErrorInfo(int a0, int a1) { return SetErrorInfo(a0, a1); }
int __stdcall Rva00AFE66CCreateErrorInfo(int a0) { return CreateErrorInfo(a0); }

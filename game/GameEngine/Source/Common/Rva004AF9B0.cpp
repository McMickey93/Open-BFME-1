// Retail 0x004AF9B0 (46 B): a file-static push-button test whose every retail use is
// inlined (no direct caller), so it keeps an address-derived name. It is false for a
// hidden window, else true when the button's user data has a positive field at +0x144.
// As a static, MSVC gives it retail's private convention with the window in ESI.
class GameWindow
{
public:
	bool winIsHidden();
};

void *GadgetButtonGetData(GameWindow *g);

// ?rva004AF9B0@@YA_NPAVGameWindow@@@Z (window arrives in ESI)
static __declspec(noinline) bool rva004AF9B0(GameWindow *window)
{
	if (window->winIsHidden())
		return false;
	char *data = static_cast<char *>(GadgetButtonGetData(window));
	return data && *reinterpret_cast<int *>(data + 0x144) > 0;
}

// ?rva004AF9B0Caller@@YA_NPAVGameWindow@@@Z absent-from-retail TU-local caller that keeps
// the static above alive.
bool rva004AF9B0Caller(GameWindow *window)
{
	return rva004AF9B0(window);
}

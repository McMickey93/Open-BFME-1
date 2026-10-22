// cl: /DNDEBUG /MD /GX- /O2 /Ob2 /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWSaveLoad /Igame/Libraries/Source/WWVegas/WW3D2 /Igame/Libraries/Source/WWVegas/Wwutil /Igame/Libraries/Source/WWVegas/WWDownload /Igame/Libraries/Source/Compression /Igame/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/shims/sweep

// ShareBufferClass<unsigned short>::~ShareBufferClass at retail 0x009240D0
// (29 bytes): the only out-of-line ShareBufferClass destructor in retail.
// BFME frees RawBuffer with no null test and no member resets, unlike the
// Zero Hour sharebuf.h body, so the class is declared locally here.

#include "always.h"
#include "refcount.h"

template <class T>
class ShareBufferClass : public RefCountClass
{
public:
	virtual ~ShareBufferClass(void);

protected:
	T *RawBuffer;
	T *Array;
	int Count;
	int Alignment;
};

template <class T>
ShareBufferClass<T>::~ShareBufferClass(void)
{
	delete[] RawBuffer;
}

template ShareBufferClass<unsigned short>::~ShareBufferClass(void);

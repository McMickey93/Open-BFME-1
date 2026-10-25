// cl: /O2 /MD
extern void j_00046add(void);
extern void bfmeForward_00C6FFC0(void);

// Gate debt ?g_rva012F146C@@3VRva00C6B6C0Init@@A: reference recorded ?TheBfmeObject_00C6FFC0@@3VGen_00C6FFC0Target@@A.
class Gen_00C6FFC0Target
{
public:
	Gen_00C6FFC0Target()
	{
		char allocator;
		typedef void *(Gen_00C6FFC0Target::*Member)(int);
		union { void (*function)(void); Member method; } call;
		call.function = (void (*)(void))j_00046add;
		(this->*call.method)((int)&allocator);
		atexit(bfmeForward_00C6FFC0);
	}
};

Gen_00C6FFC0Target TheBfmeObject_00C6FFC0;

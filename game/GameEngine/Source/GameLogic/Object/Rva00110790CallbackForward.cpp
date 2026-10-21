// Retail 0x00110790 forwards callback arguments one and three to
// GameState::addPostProcessSnapshot through its ILT slot 0x0001F546.
class Snapshot;

class GameState
{
};

extern void j_0001f546();

template <class R, class A, class B>
__forceinline R call2(void (*p)(), void *self, A a, B b)
{
	typedef R (GameState::*F)(A, B);
	union { void (*p)(); F f; } u;
	u.p = p;
	return (((GameState *)self)->*u.f)(a, b);
}

void __cdecl rva00110790Forward(Snapshot *snapshot, GameState *state, unsigned int sequence)
{
	call2<void>(j_0001f546, state, snapshot, sequence);
}

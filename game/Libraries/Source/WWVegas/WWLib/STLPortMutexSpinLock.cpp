// cl: /DNDEBUG /MD /EHs-c- /Od

// STLport 4.5.3's mutex spin loop.  The implementation is kept in a focused
// translation unit so the compiler emits the out-of-line template member that
// the retail executable uses.

// Native forwarder preserves InterlockedExchange's EAX result even though
// its existing declaration discards it. The spin caller observes that result.
void Rva0082AD60Invoke(void *, int);
void rva0082BE10Shift(int);
typedef long (__cdecl *AtomicExchangeResult)(volatile long *, long);

namespace _STL
{

template <int Instance>
struct _STLP_mutex_spin
{
    enum { __low_max = 30, __high_max = 1000 };
    static unsigned __max;
    static unsigned __last;
	static void __cdecl _M_do_lock(volatile long *lock);
};

template <int Instance>
void __cdecl _STLP_mutex_spin<Instance>::_M_do_lock(volatile long *__lock)
{
    if (reinterpret_cast<AtomicExchangeResult>(Rva0082AD60Invoke)(__lock, 1))
    {
        unsigned __my_spin_max = _STLP_mutex_spin<0>::__max;
        unsigned __my_last_spins = _STLP_mutex_spin<0>::__last;
        volatile unsigned __junk = 17;
        unsigned __i;

        for (__i = 0; __i < __my_spin_max; ++__i)
        {
            if (__i < __my_last_spins / 2 || *__lock)
			{
                __junk *= __junk;
                __junk *= __junk;
                __junk *= __junk;
                __junk *= __junk;
			}
            else if (!reinterpret_cast<AtomicExchangeResult>(Rva0082AD60Invoke)(__lock, 1))
            {
                _STLP_mutex_spin<0>::__last = __i;
                _STLP_mutex_spin<0>::__max = __high_max;
				return;
			}
		}

        _STLP_mutex_spin<0>::__max = __low_max;
        for (__i = 0; ; ++__i)
        {
            int __log_nsec = __i + 6;
            if (__log_nsec > 27)
                __log_nsec = 27;
            if (!reinterpret_cast<AtomicExchangeResult>(Rva0082AD60Invoke)(__lock, 1))
                break;
            rva0082BE10Shift(__log_nsec);
        }
    }
}

template void __cdecl _STLP_mutex_spin<0>::_M_do_lock(volatile long *);

} // namespace _STL

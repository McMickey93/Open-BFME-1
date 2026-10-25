// cl: /O2 /G6 /GS /MD
// BFME 1 body at RVA 0x007E8B00 (549 bytes). Its only caller is the FESL
// message field writer at 0x007E8D30 (Rva007E8D30 in
// game/GameEngine/Source/GameNetwork/Rva007E8D30FeslSetField.cpp), which
// invokes it through the gen-dump symbol; the record and field strings, the
// 549-byte boundary and the class-table/separator references are independent
// BFME 1 evidence (targets/game/reverse/identity_evidence/
// 007e8b00-conditional-separator.md).
//
// The body is ported from the BFME 2 FESL clean-room unit
// Code/GameEngine/Source/GameNetwork/Rva007E8D30FeslSetField.cpp at donor
// revision ce1b975697c2f20e514174e3875f8820d1dba612. Its linked 549-byte
// donor body is exact against BFME 1 outside the relocation fields, and the
// donor source compiles to the full 549-byte BFME 1 body modulo those fields.
// The donor's class table and separator live in BFME 1 at VA 0x011295B0 and
// 0x012C37EE; the dump already names those retail references g_Va011295B0 and
// g_Va012C37EE, so the port keeps the address-derived names rather than
// inventing EA identifiers.
//
// The final equivalent clear paths and the volatile separator read are
// substantive: they retain the allocation weights that give retail's late EBP
// save and the EBX value pointer. Earlier BFME 1 reconstructions stopped at
// 544 bytes with pValue/iLength in the opposite registers.
extern "C" void * __cdecl memmove( void *dest, const void *src, unsigned int count );
extern "C" int __cdecl memcmp( const void *left, const void *right, unsigned int count );
extern "C" void * __cdecl memcpy( void *dest, const void *src, unsigned int count );

extern unsigned char g_Va011295B0[];
extern char g_Va012C37EE;

// ?Rva007E8B00@@YAHPAEHPBD@Z
int __cdecl Rva007E8B00( unsigned char *buffer, int size, const char *field )
{
	int i;
	int iDelta;
	unsigned char *p;
	unsigned char *pValue;
	unsigned char *pTail;
	unsigned char cClassBuffer;
	unsigned char cClassField;
	unsigned char *pBuffer;

	pBuffer = buffer;

	if ( pBuffer == 0 )
	{
		return -1;
	}

	if ( field == 0 || (unsigned int)*field <= ' ' )
	{
		return -1;
	}

	if ( *field == '~' )
	{
		for ( p = pBuffer; *p != 0; p++ )
		{
		}

		if ( p != pBuffer && p[ -1 ] >= ' '
			&& p[ -1 ] != g_Va012C37EE
			&& p < pBuffer + size - 1 )
		{
			*p = g_Va012C37EE;
			p++;
			*p = 0;
		}

		pTail = p;
		pValue = pTail;
	}
	else
	{
		p = pBuffer;

		for ( ;; )
		{
			if ( *p == 0 )
			{
				if ( p != pBuffer && p[ -1 ] >= ' '
					&& p[ -1 ] != g_Va012C37EE
					&& p < pBuffer + size - 1 )
				{
					*p = g_Va012C37EE;
					p++;
					*p = 0;
				}

				pTail = p;
				pValue = pTail;
				break;
			}

			if ( *p <= ' ' )
			{
				p++;
				continue;
			}

			if ( g_Va011295B0[ *p ] == 1 )
			{
				pTail = p;
				pValue = pTail;
				break;
			}

			for ( i = 0; ; i++ )
			{
				cClassBuffer = g_Va011295B0[ p[ i ] ];
				cClassField = g_Va011295B0[ (unsigned char)field[ i ] ];

				if ( cClassBuffer != cClassField || cClassBuffer < 2 )
				{
					break;
				}
			}

			if ( cClassBuffer + cClassField == 2 )
			{
				pTail = p;
				pValue = pTail;

				for ( ; *pTail >= ' '; pTail++ )
				{
				}

				if ( *pTail > 0 )
				{
					pTail++;
				}

				break;
			}

			do
			{
				p++;
			}
			while ( *p >= ' ' );
		}
	}

	for ( i = 0; (unsigned int)field[ i ] >= ' '; i++ )
	{
	}
	i++;

	iDelta = i - ( pTail - pValue );

	for ( p = pTail; *p != 0; p++ )
	{
	}

	p++;

	if ( iDelta > 0 && pBuffer + size - p < iDelta )
	{
		return -1;
	}

	if ( iDelta == 0 && memcmp( pValue, field, i ) == 0 )
	{
		return 0;
	}

	if ( iDelta > 0 )
	{
		memmove( pTail + iDelta, pTail, p - pTail );
	}

	if ( iDelta < 0 )
	{
		memmove( pValue, pValue - iDelta, p - ( pValue - iDelta ) );
	}

	memcpy( pValue, field, i );

	if ( pValue[ i ] == 0 && g_Va012C37EE != '\n' )
	{
		// Equivalent paths retain the allocation weights needed by VC7.1.
		// Their merged store gives retail's late EBP save and EBX value pointer.
		if ( i > 0 )
			goto clearPositive;
		pValue[ i - 1 ] = 0;
		goto clearDone;
clearPositive:
		pValue[ i - 1 ] = 0;
clearDone:
		;
	}
	else
	{
		pValue[ i - 1 ] = *(volatile char *)&g_Va012C37EE;
	}

	return i - 1;
}

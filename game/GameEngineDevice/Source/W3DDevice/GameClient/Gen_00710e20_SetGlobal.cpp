// cl: /DNDEBUG /MD /EHsc

// Retail 0x00710E20. Store a byte into a global. cdecl (ret not ret 4).

// Retail .data byte at VA 0x012D6E04, also read by ShaderClass::Apply.
unsigned char g_00710e20 = 0x60;

// ?set_00710e20@@YAXE@Z
void set_00710e20(unsigned char v)
{
	g_00710e20 = v;
}

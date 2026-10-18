// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /GX

class BfmeOwnVUM
{
public:
	BfmeOwnVUM( const BfmeOwnVUM &other );
	~BfmeOwnVUM();

private:
	void *m_vptr;
	char m_bfme04[ 4 ];
	char m_bfme08[ 0x44 ];
	char m_bfme4c[ 4 ];
	char m_bfme50[ 0x28 ];
	char m_bfme78[ 4 ];
	char m_bfme7c[ 0x30 ];
	char m_bfmeac[ 4 ];
	char m_bfmeb0[ 4 ];
};

typedef char BfmeOwnVUMSize[ ( sizeof( BfmeOwnVUM ) == 0xB4 ) ? 1 : -1 ];

struct Rva00364980HeapElement
{
	char m_bytes[ 0xB4 ];
};

struct Rva00364980HeapCompare
{
	void *m_state;
};

void rva00362360UnguardedLinearInsert( Rva00364980HeapElement *last,
	Rva00364980HeapElement value, Rva00364980HeapCompare compare );

typedef void ( *LinearInsertFn )( BfmeOwnVUM *last, BfmeOwnVUM value,
	Rva00364980HeapCompare compare );

void rva00363B80UnguardedInsertionSortAux( Rva00364980HeapElement *first,
	Rva00364980HeapElement *last, Rva00364980HeapElement *,
	Rva00364980HeapCompare compare )
{
	LinearInsertFn insert = (LinearInsertFn)rva00362360UnguardedLinearInsert;
	for( Rva00364980HeapElement *current = first; current != last; ++current )
	{
		insert( (BfmeOwnVUM *)current,
			BfmeOwnVUM( *(BfmeOwnVUM *)current ), compare );
	}
}

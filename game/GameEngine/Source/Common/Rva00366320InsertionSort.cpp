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

void rva003653E0LinearInsert( Rva00364980HeapElement *first,
	Rva00364980HeapElement *last, Rva00364980HeapElement value,
	Rva00364980HeapCompare compare );

typedef void ( *LinearInsertFn )( BfmeOwnVUM *first, BfmeOwnVUM *last,
	BfmeOwnVUM value, Rva00364980HeapCompare compare );

void rva00366320InsertionSort( Rva00364980HeapElement *first,
	Rva00364980HeapElement *last, Rva00364980HeapCompare compare )
{
	if( first == last )
		return;

	LinearInsertFn insert = (LinearInsertFn)rva003653E0LinearInsert;
	for( Rva00364980HeapElement *current = first + 1;
		current != last; ++current )
	{
		insert( (BfmeOwnVUM *)first, (BfmeOwnVUM *)current,
			BfmeOwnVUM( *(BfmeOwnVUM *)current ), compare );
	}
}

class TextureClass
{
public:
	void Release_Ref();
};

class Rva009EBCE0AssetReference
{
public:
	__forceinline ~Rva009EBCE0AssetReference()
	{
		if (m_texture != 0)
			m_texture->Release_Ref();
	}

	TextureClass *m_texture;
};

Rva009EBCE0AssetReference Rva009EBCE0_GetPrototype(const char *name);

class Gen00971730
{
public:
	__forceinline Gen00971730() { m_bfmeRefXT = 0; }
	Gen00971730(void *ref);
	~Gen00971730();

	void *m_bfmeRefXT;
};

Gen00971730::~Gen00971730()
{
	if (m_bfmeRefXT != 0)
		static_cast<TextureClass *>(m_bfmeRefXT)->Release_Ref();
}

Gen00971730 bfmeMakeXT(const char *name)
{
	if (name == 0)
		return Gen00971730();

	return Gen00971730(&(Rva009EBCE0AssetReference &)Rva009EBCE0_GetPrototype(name));
}

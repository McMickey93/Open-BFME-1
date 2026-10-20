// cl: /DNDEBUG /MD /EHsc
// Retail 0x005C3A90, 119 bytes through RET 12. The operation corresponds to
// ParticleSys.cpp's createAttachedParticleSystemID, but that member's name is
// contradicted by the retail ILT order, so this wrapper keeps its address.
// Factory ABI and nullable handle: W3DTankDrawCreateEmitters.cpp (0x0077EC40).
// System ID +0xAC: ParticleSystemDestructor.cpp and ParticleSystemSetMaster.cpp.
// Object +0x74 and attached-object ID +0xB8: BFME layout witnesses.

class ParticleSystemTemplate;

class Object
{
public:
	unsigned char m_beforeID[0x74];
	unsigned int m_id;
};

class ParticleSystem
{
public:
	unsigned char m_beforeSystemID[0xAC];
	unsigned int m_systemID;
	unsigned char m_beforeAttachedObject[8];
	unsigned int m_attachedToObjectID;
};

ParticleSystem *Make00001B18();

class BfmeParticleSystemHandle
{
public:
	BfmeParticleSystemHandle(const BfmeParticleSystemHandle &that);
	~BfmeParticleSystemHandle() throw();
	operator bool() const { return m_system != 0; }
	ParticleSystem *operator->() const
	{
		if (!m_system)
			return Make00001B18();
		return m_system;
	}

	ParticleSystem *m_system;
	BfmeParticleSystemHandle *m_previous;
	BfmeParticleSystemHandle *m_next;
};

class ParticleSystemManager
{
public:
	BfmeParticleSystemHandle createParticleSystem(
		const ParticleSystemTemplate *systemTemplate, bool createSlaves) throw();
};

extern ParticleSystemManager *TheParticleSystemManager;

unsigned int __stdcall rva005C3A90(const ParticleSystemTemplate *systemTemplate,
	Object *attachTo, bool createSlaves)
{
	BfmeParticleSystemHandle system =
		TheParticleSystemManager->createParticleSystem(systemTemplate, createSlaves);
	unsigned int result;
	if (system)
	{
		if (attachTo)
			system->m_attachedToObjectID = attachTo->m_id;
		result = system->m_systemID;
	}
	else
		result = 0;
	return result;
}

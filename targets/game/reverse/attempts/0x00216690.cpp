// ?shouldFireWeapon@FireWeaponCollide@@UAE_NXZ
// partial score=0.8561 date=2026-10-16
// ?shouldFireWeapon@FireWeaponCollide@@UAE_NXZ
// cl: /O2 /DNDEBUG /DWIN32 /MD /EHsc
typedef bool Bool;

class ObjectStatusMaskType
{
public:
	Bool testForAny(const ObjectStatusMaskType &that) const;
	void set(unsigned int a, unsigned int b, unsigned int c) { w0 = a; w1 = b; w2 = c; }
	unsigned int w0, w1, w2;
};

class Object
{
public:
	const ObjectStatusMaskType &getStatusBits() const { return m_status; }

private:
	unsigned char m_unmodelled_000[0x90];
	ObjectStatusMaskType m_status;
};

class FireWeaponCollideModuleData
{
	unsigned char m_prefix[0x0c];

public:
	ObjectStatusMaskType m_requiredStatus;
	ObjectStatusMaskType m_forbiddenStatus;
	Bool m_fireOnce;
};

class FireWeaponCollide
{
public:
	virtual Bool shouldFireWeapon();

protected:
	const FireWeaponCollideModuleData *getFireWeaponCollideModuleData() const { return m_moduleData; }
	Object *getObject() const { return m_object; }

private:
	const FireWeaponCollideModuleData *m_moduleData;
	Object *m_object;
	unsigned char m_between[0x0c];
	Bool m_everFired;
};

// ?shouldFireWeapon@FireWeaponCollide@@UAE_NXZ
Bool FireWeaponCollide::shouldFireWeapon()
{
	const FireWeaponCollideModuleData *d = getFireWeaponCollideModuleData();
	FireWeaponCollide *volatile self = this;
	ObjectStatusMaskType status = getObject()->getStatusBits();
	ObjectStatusMaskType tmp;

	tmp.set(status.w0, status.w1, status.w2);
	if (tmp.testForAny(d->m_forbiddenStatus))
		return false;

	tmp.set(~status.w0, ~status.w1, ~status.w2 & 0x003fffff);
	if (tmp.testForAny(d->m_requiredStatus))
		return false;

	if (self->m_everFired && d->m_fireOnce)
		return false;

	return true;
}

# 0x00942E90 / 0x00942EA0 / 0x00942EB0 are SceneIterator's dtor, ctor and ??_G

## The vftable

VA 0x0113CEB0 is already recorded in dir32_addresses.csv as
`??_7SceneIterator@@6B@`. It has five slots:

| slot | target | ledger |
|---|---|---|
| 0 | 0x00942EB0 | was `??_GRva00942EB0Deleting@@UAEPAXI@Z` |
| 1-4 | 0x0088C500 | `__purecall` |

This matches WW3D2 scene.h (Zero Hour reference) exactly:

    class SceneIterator {
    public:
        virtual ~SceneIterator(void) { };
        virtual void First(void) = 0;
        virtual void Next(void) = 0;
        virtual bool Is_Done(void) = 0;
        virtual RenderObjClass * Current_Item(void) = 0;
    protected:
        SceneIterator(void) { };
    };

That is one virtual destructor plus four pure virtuals. The matched
SimpleSceneIterator (0x009431B0 First, 0x009431C0 Next, 0x009431D0 Is_Done,
0x00943950 Current_Item, 0x00943CE0 dtor) derives from it.

## The three bodies

- 0x00942E90, 7 B: `mov [ecx],0x0113CEB0; ret`. This is the inline
  `~SceneIterator() {}` emitted out of line: `??1SceneIterator@@UAE@XZ`.
- 0x00942EA0, 9 B: `mov eax,ecx; mov [eax],0x0113CEB0; ret`. This is the
  protected inline constructor: `??0SceneIterator@@IAE@XZ`.
- 0x00942EB0, 31 B: slot 0 of that vftable, the scalar deleting destructor
  `??_GSceneIterator@@UAEPAXI@Z`.

All three sit together between int3 runs. The first two were unclaimed.
The real game/Libraries/Source/WWVegas/WW3D2/scene.cpp TU emits all three,
and each probes EXACT (tools/probe.py).

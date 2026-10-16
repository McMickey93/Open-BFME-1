// ?updatePosition@Rva003CC890@@QAEXXZ
// cl: /DNDEBUG /MD /Igame/Libraries/Include
// Evidence: targets/game/reverse/identity_evidence/003ccb70-split-coordinate-copy.md
#include "Lib/Coord3D.h"
#include <math.h>
#include <string.h>

struct Rva003CC940Point {
    float m_at00, m_at04, m_at08;
    // ??0Rva003CC940Point@@QAE@XZ absent-from-retail
    Rva003CC940Point() {}
    // ??0Rva003CC940Point@@QAE@ABU0@@Z absent-from-retail
    Rva003CC940Point(const Rva003CC940Point &other)
        : m_at00(other.m_at00), m_at04(other.m_at04), m_at08(other.m_at08) {}
};

class LargeGroupAudioGridCell { public: Rva003CC940Point getPreferredAudioPosition(); };

// ?copyPosition003CCB70@@YAXPAUCoord3D@@PBU1@@Z absent-from-retail
// Copy X before the remaining two coordinate words.
static __forceinline void copyPosition003CCB70(Coord3D *destination, const Coord3D *source)
{
    memcpy(destination, source, sizeof(float));
    memcpy((char *)destination + sizeof(float), (const char *)source + sizeof(float), 2 * sizeof(float));
}

class AudioEventRTS
{
public:
    void resolveOwnerPosition(Coord3D *position, bool *found);
    void setPosition(const Coord3D *position);
    char m_head[0x0c];
    unsigned int m_handle;
};

struct Rva003CCB70Event
{
    unsigned int m_head;
    AudioEventRTS m_event;
};

struct Rva003CCB70Data
{
    char m_head[0x10];
    float m_step;
};

class Rva003CCB70Audio
{
public:
    virtual void slot00(); virtual void slot04(); virtual void slot08();
    virtual void slot0c(); virtual void slot10(); virtual void slot14();
    virtual void slot18(); virtual void slot1c(); virtual void slot20();
    virtual void slot24(); virtual void slot28(); virtual void slot2c();
    virtual void slot30(); virtual void slot34(); virtual void slot38();
    virtual void slot3c(); virtual void slot40(); virtual void slot44();
    virtual void slot48(); virtual void slot4c(); virtual void slot50();
    virtual void slot54(); virtual void slot58(); virtual void slot5c();
    virtual void slot60(); virtual void slot64(); virtual void slot68();
    virtual void slot6c(); virtual void slot70(); virtual void slot74();
    virtual void slot78(); virtual void slot7c(); virtual void slot80();
    virtual void slot84(); virtual void slot88(); virtual void slot8c();
    virtual void slot90(); virtual void slot94(); virtual void slot98();
    virtual void slot9c(); virtual void slota0(); virtual void slota4();
    virtual void slota8(); virtual void slotac(); virtual void slotb0();
    virtual void slotb4(unsigned int handle, const Coord3D *position);
};
class AudioManager;
extern AudioManager *TheAudio;

class Rva003CC890
{
public:
    void position(Coord3D *position);
    void updatePosition();
    char m_head[0x08];
    Rva003CCB70Data *m_data;
    Rva003CCB70Event *m_event;
    void *m_nodes[8];
    int m_pad30;
    int m_flag;
    unsigned char m_refs;
};

// ?updatePosition@Rva003CC890@@QAEXXZ
void Rva003CC890::updatePosition()
{
    if (m_event)
    {
        Rva003CC940Point targetPoint = ((LargeGroupAudioGridCell *)this)->getPreferredAudioPosition();
        const Coord3D &target = *(const Coord3D *)&targetPoint;
        Coord3D current;
        bool found;
        m_event->m_event.resolveOwnerPosition(&current, &found);
        float step = m_data->m_step;
        if (!found)
            copyPosition003CCB70(&current, &target);
        Coord3D result;
        int frames = m_flag;
        if (frames > 0)
        {
            float fraction = 1.0f / frames;
            result.x = current.x + (target.x - current.x) * fraction;
            result.y = current.y + (target.y - current.y) * fraction;
            result.z = current.z + (target.z - current.z) * fraction;
        }
        else
        {
            Coord3D delta;
            delta.x = target.x - current.x;
            delta.y = target.y - current.y;
            delta.z = target.z - current.z;
            float distanceSqr = delta.x * delta.x + delta.y * delta.y + delta.z * delta.z;
            if (distanceSqr <= step * step)
                copyPosition003CCB70(&result, &target);
            else
            {
                double scale = step / sqrt(distanceSqr);
                result = current;
                delta.x *= scale;
                delta.y *= scale;
                delta.z *= scale;
                result.x += delta.x;
                result.y += delta.y;
                result.z += delta.z;
            }
        }
        m_event->m_event.setPosition(&result);
        ((Rva003CCB70Audio *)TheAudio)->slotb4(m_event->m_event.m_handle, &result);
    }
}

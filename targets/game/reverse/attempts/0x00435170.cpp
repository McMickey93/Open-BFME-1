// ?refresh@Rva00435270Layout@@AAEXXZ
// partial score=0.3897 date=2026-10-20
// stlport
// cl: /DNDEBUG /MD /EHsc /Iinputs/reference/shims/stringinline
#include <vector>
#include <algorithm>
#include "StringInline.h"

struct Gen_t_00434fa0_p8cd {
    int a[2];
    Gen_t_00434fa0_p8cd();
    Gen_t_00434fa0_p8cd(const Gen_t_00434fa0_p8cd&);
    ~Gen_t_00434fa0_p8cd();
    Gen_t_00434fa0_p8cd& operator=(const Gen_t_00434fa0_p8cd&);
};
class Rva00435270Receiver {
public:
    virtual void slot00();
    virtual void setState(UnicodeString text);
};
class Rva00435270Layout {
public:
    void apply();
private:
    void refresh();
    char m_unreconstructed00[8];
    std::vector<Gen_t_00434fa0_p8cd> m_pending08;
    char m_unreconstructed14[0x10];
    int m_count24;
    int m_progress28;
    int m_owner2C;
    int m_count30;
    Rva00435270Receiver **m_receivers34;
    int *m_values38;
    int m_cursor3C;
    int m_unreconstructed40;
    float m_timer44;
    float m_step48;
};

void Rva00435270Layout::refresh()
{
    float &timer = m_timer44;
    if (timer > 0.0f || m_pending08.size() != 0) {
        timer -= m_step48;
        timer = std::max(timer, 0.0f);
        if (timer == 0.0f && m_pending08.size() > 0) {
            m_receivers34[m_cursor3C % m_count24]->setState(
                *(const UnicodeString *)&m_pending08[0]);
            m_values38[m_cursor3C % m_count24] = m_pending08[0].a[1];
            m_pending08.erase(m_pending08.begin());
            timer = (float)m_count30;
            ++m_cursor3C;
        }
    }
}

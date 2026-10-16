// ?playMovie@WindowVideoManager@@QAEXPAVGameWindow@@VAsciiString@@W4WindowVideoPlayType@@@Z
// partial score=1.0 date=2026-10-15
// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWLib
// stlport
#include "ascii_string.h"
#include <hash_map>
class GameWindow;
class VideoBuffer;
enum WindowVideoPlayType { WINDOW_PLAY_MOVIE_ONCE=0 };
class WindowVideo {
public:
 WindowVideo();
 void init(GameWindow *,AsciiString,WindowVideoPlayType,VideoBuffer *);
private:
 WindowVideoPlayType m_playType;
 GameWindow *m_win;
 VideoBuffer *m_videoBuffer;
 AsciiString m_movieName;
 int m_state;
};
class VideoBuffer {
public:
 virtual void slot00();virtual void slot04();virtual void slot08();virtual void slot0c();
 virtual void slot10();virtual void slot14();virtual void slot18();virtual void close();
 virtual void slot20();virtual void slot24();virtual void slot28();virtual void slot2c();
 virtual void slot30();virtual void slot34();virtual bool attach(void *);
};
class VideoPlayer {
public:
 virtual void slot00();virtual void slot04();virtual void slot08();virtual void slot0c();
 virtual void slot10();virtual void slot14();virtual void slot18();virtual void slot1c();
 virtual void slot20();virtual void slot24();virtual void slot28();virtual void slot2c();
 virtual VideoBuffer *open(AsciiString,int);
};
class Display {
public:
 virtual void slot00();virtual void slot04();virtual void slot08();virtual void slot0c();
 virtual void slot10();virtual void slot14();virtual void slot18();virtual void slot1c();
 virtual void slot20();virtual void slot24();virtual void slot28();virtual void slot2c();
 virtual void slot30();virtual void slot34();virtual void slot38();virtual void slot3c();
 virtual void slot40();virtual void slot44();virtual void slot48();virtual void slot4c();
 virtual void slot50();virtual void slot54();virtual void slot58();virtual void slot5c();
 virtual void slot60();virtual void slot64();virtual void slot68();virtual void slot6c();
 virtual void slot70();virtual void slot74();virtual void slot78();virtual void slot7c();
 virtual void slot80();virtual void *createVideoBuffer(bool);
};
extern VideoPlayer *TheVideoPlayer;
extern Display *TheDisplay;
enum Gen_e_00498c40 { Rva004991D0MappedZero=0 };
namespace _STL { template<> Gen_e_00498c40 &hash_map<int,Gen_e_00498c40>::operator[](const int&); }
class WindowVideoManager {
public:
 void stopAndRemoveMovie(GameWindow*);
 void playMovie(GameWindow*,AsciiString,WindowVideoPlayType);
private:
 char m_pad00[8];
 _STL::hash_map<int,Gen_e_00498c40> m_playingVideos;
 bool m_stopAllMovies;
 bool m_pauseAllMovies;
};
void WindowVideoManager::playMovie(GameWindow *win,AsciiString movieName,WindowVideoPlayType playType) {
 stopAndRemoveMovie(win);
 VideoBuffer *videoStream=TheVideoPlayer->open(movieName,0);
 if(videoStream==0)return;
 if(!videoStream->attach(TheDisplay->createVideoBuffer(false))) {videoStream->close();return;}
 WindowVideo *winVid=new WindowVideo;
 winVid->init(win,movieName,playType,videoStream);
 m_playingVideos[(const int &)win]=(Gen_e_00498c40)(int)winVid;
 m_pauseAllMovies=false;
 m_stopAllMovies=false;
}

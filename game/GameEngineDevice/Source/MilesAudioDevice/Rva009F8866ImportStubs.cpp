// cl: /O2 /MD
// Six-byte FF 25 [IAT] import stubs from the WINMM/mss32/COMCTL32 import-stub table at 0x009F8866 that no row claimed.
// Retail links several copies of some stubs, so each keeps an address-derived
// name, as the matched _mbslen stub at 0x009F7262 does. stdcall stubs take
// the argument bytes their Platform SDK import decoration states; the cdecl
// CRT stubs never touch their arguments. A tail call is exactly `jmp [slot]`.

extern "C" __declspec(dllimport) int __stdcall AIL_3D_room_type(int);
extern "C" __declspec(dllimport) int __stdcall AIL_3D_sample_offset(int);
extern "C" __declspec(dllimport) int __stdcall AIL_3D_sample_playback_rate(int);
extern "C" __declspec(dllimport) int __stdcall AIL_3D_sample_status(int);
extern "C" __declspec(dllimport) int __stdcall AIL_WAV_info(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_allocate_3D_sample_handle(int);
extern "C" __declspec(dllimport) int __stdcall AIL_allocate_sample_handle(int);
extern "C" __declspec(dllimport) int __stdcall AIL_close_3D_listener(int);
extern "C" __declspec(dllimport) int __stdcall AIL_close_3D_provider(int);
extern "C" __declspec(dllimport) int __stdcall AIL_close_stream(int);
extern "C" __declspec(dllimport) int __stdcall AIL_decompress_ADPCM(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_enumerate_3D_providers(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_enumerate_filters(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_get_DirectSound_info(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_get_preference(int);
extern "C" __declspec(dllimport) int __stdcall AIL_init_sample(int);
extern "C" __declspec(dllimport) int __stdcall AIL_last_error(void);
extern "C" __declspec(dllimport) int __stdcall AIL_lock_mutex(void);
extern "C" __declspec(dllimport) int __stdcall AIL_open_3D_listener(int);
extern "C" __declspec(dllimport) int __stdcall AIL_open_3D_provider(int);
extern "C" __declspec(dllimport) int __stdcall AIL_open_stream(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_pause_stream(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_quick_handles(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_quick_load_and_play(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_quick_set_volume(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_quick_shutdown(void);
extern "C" __declspec(dllimport) int __stdcall AIL_quick_startup(int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_quick_status(int);
extern "C" __declspec(dllimport) int __stdcall AIL_quick_unload(int);
extern "C" __declspec(dllimport) int __stdcall AIL_register_3D_EOS_callback(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_register_EOS_callback(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_register_stream_callback(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_register_timer(int);
extern "C" __declspec(dllimport) int __stdcall AIL_release_3D_sample_handle(int);
extern "C" __declspec(dllimport) int __stdcall AIL_release_sample_handle(int);
extern "C" __declspec(dllimport) int __stdcall AIL_release_timer_handle(int);
extern "C" __declspec(dllimport) int __stdcall AIL_resume_3D_sample(int);
extern "C" __declspec(dllimport) int __stdcall AIL_resume_sample(int);
extern "C" __declspec(dllimport) int __stdcall AIL_sample_playback_rate(int);
extern "C" __declspec(dllimport) int __stdcall AIL_sample_volume_pan(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_serve(void);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_orientation(int, int, int, int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_position(int, int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_rolloff_factor(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_room_type(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_sample_distances(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_sample_effects_level(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_sample_file(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_sample_loop_count(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_sample_occlusion(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_sample_playback_rate(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_sample_volume(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_speaker_type(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_3D_user_data(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_digital_master_room_type(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_filter_sample_preference(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_preference(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_sample_file(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_sample_playback_rate(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_sample_processor(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_sample_reverb_levels(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_sample_user_data(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_sample_volume_pan(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_stream_loop_count(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_stream_ms_position(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_stream_reverb_levels(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_stream_volume_pan(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_set_timer_period(int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_shutdown(void);
extern "C" __declspec(dllimport) int __stdcall AIL_start_3D_sample(int);
extern "C" __declspec(dllimport) int __stdcall AIL_start_sample(int);
extern "C" __declspec(dllimport) int __stdcall AIL_start_stream(int);
extern "C" __declspec(dllimport) int __stdcall AIL_start_timer(int);
extern "C" __declspec(dllimport) int __stdcall AIL_startup(void);
extern "C" __declspec(dllimport) int __stdcall AIL_stop_3D_sample(int);
extern "C" __declspec(dllimport) int __stdcall AIL_stop_sample(int);
extern "C" __declspec(dllimport) int __stdcall AIL_stop_timer(int);
extern "C" __declspec(dllimport) int __stdcall AIL_stream_loop_count(int);
extern "C" __declspec(dllimport) int __stdcall AIL_stream_ms_position(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_stream_volume_pan(int, int, int);
extern "C" __declspec(dllimport) int __stdcall AIL_unlock_mutex(void);
extern "C" __declspec(dllimport) int __stdcall InitCommonControls(void);
extern "C" __declspec(dllimport) int __stdcall timeBeginPeriod(int);
extern "C" __declspec(dllimport) int __stdcall timeEndPeriod(int);
extern "C" __declspec(dllimport) int __stdcall timeGetTime(void);

int __stdcall Rva009F8866timeGetTime(void) { return timeGetTime(); }
int __stdcall Rva009F886CtimeBeginPeriod(int a0) { return timeBeginPeriod(a0); }
int __stdcall Rva009F8872timeEndPeriod(int a0) { return timeEndPeriod(a0); }
int __stdcall Rva009F88BAAIL_decompress_ADPCM(int a0, int a1, int a2) { return AIL_decompress_ADPCM(a0, a1, a2); }
int __stdcall Rva009F88C0AIL_WAV_info(int a0, int a1) { return AIL_WAV_info(a0, a1); }
int __stdcall Rva009F88C6AIL_lock_mutex(void) { return AIL_lock_mutex(); }
int __stdcall Rva009F88CCAIL_unlock_mutex(void) { return AIL_unlock_mutex(); }
int __stdcall Rva009F88D2AIL_3D_sample_status(int a0) { return AIL_3D_sample_status(a0); }
int __stdcall Rva009F88D8AIL_start_timer(int a0) { return AIL_start_timer(a0); }
int __stdcall Rva009F88DEAIL_stop_timer(int a0) { return AIL_stop_timer(a0); }
int __stdcall Rva009F88E4AIL_set_digital_master_room_type(int a0, int a1) { return AIL_set_digital_master_room_type(a0, a1); }
int __stdcall Rva009F88EAAIL_set_3D_room_type(int a0, int a1) { return AIL_set_3D_room_type(a0, a1); }
int __stdcall Rva009F88F0AIL_enumerate_3D_providers(int a0, int a1, int a2) { return AIL_enumerate_3D_providers(a0, a1, a2); }
int __stdcall Rva009F88F6AIL_enumerate_filters(int a0, int a1, int a2) { return AIL_enumerate_filters(a0, a1, a2); }
int __stdcall Rva009F88FCAIL_serve(void) { return AIL_serve(); }
int __stdcall Rva009F8902AIL_set_preference(int a0, int a1) { return AIL_set_preference(a0, a1); }
int __stdcall Rva009F8908AIL_get_preference(int a0) { return AIL_get_preference(a0); }
int __stdcall Rva009F890EAIL_stop_3D_sample(int a0) { return AIL_stop_3D_sample(a0); }
int __stdcall Rva009F8914AIL_set_3D_position(int a0, int a1, int a2, int a3) { return AIL_set_3D_position(a0, a1, a2, a3); }
int __stdcall Rva009F891AAIL_set_3D_orientation(int a0, int a1, int a2, int a3, int a4, int a5, int a6) { return AIL_set_3D_orientation(a0, a1, a2, a3, a4, a5, a6); }
int __stdcall Rva009F8920AIL_set_3D_sample_effects_level(int a0, int a1) { return AIL_set_3D_sample_effects_level(a0, a1); }
int __stdcall Rva009F8926AIL_set_sample_reverb_levels(int a0, int a1, int a2) { return AIL_set_sample_reverb_levels(a0, a1, a2); }
int __stdcall Rva009F892CAIL_set_stream_reverb_levels(int a0, int a1, int a2) { return AIL_set_stream_reverb_levels(a0, a1, a2); }
int __stdcall Rva009F8932AIL_resume_sample(int a0) { return AIL_resume_sample(a0); }
int __stdcall Rva009F8938AIL_stop_sample(int a0) { return AIL_stop_sample(a0); }
int __stdcall Rva009F893EAIL_resume_3D_sample(int a0) { return AIL_resume_3D_sample(a0); }
int __stdcall Rva009F8944AIL_pause_stream(int a0, int a1) { return AIL_pause_stream(a0, a1); }
int __stdcall Rva009F894AAIL_close_3D_provider(int a0) { return AIL_close_3D_provider(a0); }
int __stdcall Rva009F8950AIL_close_3D_listener(int a0) { return AIL_close_3D_listener(a0); }
int __stdcall Rva009F8956AIL_set_3D_speaker_type(int a0, int a1) { return AIL_set_3D_speaker_type(a0, a1); }
int __stdcall Rva009F895CAIL_open_3D_listener(int a0) { return AIL_open_3D_listener(a0); }
int __stdcall Rva009F8962AIL_quick_status(int a0) { return AIL_quick_status(a0); }
int __stdcall Rva009F8968AIL_quick_unload(int a0) { return AIL_quick_unload(a0); }
int __stdcall Rva009F896EAIL_3D_room_type(int a0) { return AIL_3D_room_type(a0); }
int __stdcall Rva009F8974AIL_register_stream_callback(int a0, int a1) { return AIL_register_stream_callback(a0, a1); }
int __stdcall Rva009F897AAIL_register_3D_EOS_callback(int a0, int a1) { return AIL_register_3D_EOS_callback(a0, a1); }
int __stdcall Rva009F8980AIL_register_EOS_callback(int a0, int a1) { return AIL_register_EOS_callback(a0, a1); }
int __stdcall Rva009F8986AIL_release_sample_handle(int a0) { return AIL_release_sample_handle(a0); }
int __stdcall Rva009F898CAIL_release_3D_sample_handle(int a0) { return AIL_release_3D_sample_handle(a0); }
int __stdcall Rva009F8992AIL_close_stream(int a0) { return AIL_close_stream(a0); }
int __stdcall Rva009F8998AIL_stream_ms_position(int a0, int a1, int a2) { return AIL_stream_ms_position(a0, a1, a2); }
int __stdcall Rva009F899EAIL_open_stream(int a0, int a1, int a2) { return AIL_open_stream(a0, a1, a2); }
int __stdcall Rva009F89A4AIL_allocate_3D_sample_handle(int a0) { return AIL_allocate_3D_sample_handle(a0); }
int __stdcall Rva009F89AAAIL_set_3D_user_data(int a0, int a1, int a2) { return AIL_set_3D_user_data(a0, a1, a2); }
int __stdcall Rva009F89B0AIL_init_sample(int a0) { return AIL_init_sample(a0); }
int __stdcall Rva009F89B6AIL_allocate_sample_handle(int a0) { return AIL_allocate_sample_handle(a0); }
int __stdcall Rva009F89BCAIL_set_sample_user_data(int a0, int a1, int a2) { return AIL_set_sample_user_data(a0, a1, a2); }
int __stdcall Rva009F89C2AIL_stream_loop_count(int a0) { return AIL_stream_loop_count(a0); }
int __stdcall Rva009F89C8AIL_shutdown(void) { return AIL_shutdown(); }
int __stdcall Rva009F89CEAIL_quick_shutdown(void) { return AIL_quick_shutdown(); }
int __stdcall Rva009F89D4AIL_release_timer_handle(int a0) { return AIL_release_timer_handle(a0); }
int __stdcall Rva009F89DAAIL_set_3D_rolloff_factor(int a0, int a1) { return AIL_set_3D_rolloff_factor(a0, a1); }
int __stdcall Rva009F89E0AIL_last_error(void) { return AIL_last_error(); }
int __stdcall Rva009F89E6AIL_open_3D_provider(int a0) { return AIL_open_3D_provider(a0); }
int __stdcall Rva009F89ECAIL_get_DirectSound_info(int a0, int a1, int a2) { return AIL_get_DirectSound_info(a0, a1, a2); }
int __stdcall Rva009F89F2AIL_start_stream(int a0) { return AIL_start_stream(a0); }
int __stdcall Rva009F89F8AIL_set_stream_loop_count(int a0, int a1) { return AIL_set_stream_loop_count(a0, a1); }
int __stdcall Rva009F89FEAIL_set_stream_ms_position(int a0, int a1) { return AIL_set_stream_ms_position(a0, a1); }
int __stdcall Rva009F8A04AIL_set_3D_sample_volume(int a0, int a1) { return AIL_set_3D_sample_volume(a0, a1); }
int __stdcall Rva009F8A0AAIL_set_stream_volume_pan(int a0, int a1, int a2) { return AIL_set_stream_volume_pan(a0, a1, a2); }
int __stdcall Rva009F8A10AIL_stream_volume_pan(int a0, int a1, int a2) { return AIL_stream_volume_pan(a0, a1, a2); }
int __stdcall Rva009F8A16AIL_set_sample_volume_pan(int a0, int a1, int a2) { return AIL_set_sample_volume_pan(a0, a1, a2); }
int __stdcall Rva009F8A1CAIL_sample_volume_pan(int a0, int a1, int a2) { return AIL_sample_volume_pan(a0, a1, a2); }
int __stdcall Rva009F8A22AIL_set_filter_sample_preference(int a0, int a1, int a2) { return AIL_set_filter_sample_preference(a0, a1, a2); }
int __stdcall Rva009F8A28AIL_set_sample_processor(int a0, int a1, int a2) { return AIL_set_sample_processor(a0, a1, a2); }
int __stdcall Rva009F8A2EAIL_set_sample_playback_rate(int a0, int a1) { return AIL_set_sample_playback_rate(a0, a1); }
int __stdcall Rva009F8A34AIL_sample_playback_rate(int a0) { return AIL_sample_playback_rate(a0); }
int __stdcall Rva009F8A3AAIL_set_3D_sample_occlusion(int a0, int a1) { return AIL_set_3D_sample_occlusion(a0, a1); }
int __stdcall Rva009F8A40AIL_set_3D_sample_playback_rate(int a0, int a1) { return AIL_set_3D_sample_playback_rate(a0, a1); }
int __stdcall Rva009F8A46AIL_3D_sample_playback_rate(int a0) { return AIL_3D_sample_playback_rate(a0); }
int __stdcall Rva009F8A4CAIL_start_sample(int a0) { return AIL_start_sample(a0); }
int __stdcall Rva009F8A52AIL_set_sample_file(int a0, int a1, int a2) { return AIL_set_sample_file(a0, a1, a2); }
int __stdcall Rva009F8A58AIL_set_3D_sample_distances(int a0, int a1, int a2) { return AIL_set_3D_sample_distances(a0, a1, a2); }
int __stdcall Rva009F8A5EAIL_start_3D_sample(int a0) { return AIL_start_3D_sample(a0); }
int __stdcall Rva009F8A64AIL_set_3D_sample_loop_count(int a0, int a1) { return AIL_set_3D_sample_loop_count(a0, a1); }
int __stdcall Rva009F8A6AAIL_set_3D_sample_file(int a0, int a1) { return AIL_set_3D_sample_file(a0, a1); }
int __stdcall Rva009F8A70AIL_quick_set_volume(int a0, int a1, int a2) { return AIL_quick_set_volume(a0, a1, a2); }
int __stdcall Rva009F8A76AIL_quick_load_and_play(int a0, int a1, int a2) { return AIL_quick_load_and_play(a0, a1, a2); }
int __stdcall Rva009F8A7CAIL_3D_sample_offset(int a0) { return AIL_3D_sample_offset(a0); }
int __stdcall Rva009F8A82AIL_set_timer_period(int a0, int a1) { return AIL_set_timer_period(a0, a1); }
int __stdcall Rva009F8A88AIL_register_timer(int a0) { return AIL_register_timer(a0); }
int __stdcall Rva009F8A8EAIL_quick_handles(int a0, int a1, int a2) { return AIL_quick_handles(a0, a1, a2); }
int __stdcall Rva009F8A94AIL_quick_startup(int a0, int a1, int a2, int a3, int a4) { return AIL_quick_startup(a0, a1, a2, a3, a4); }
int __stdcall Rva009F8A9AAIL_startup(void) { return AIL_startup(); }
int __stdcall Rva009F9B7CInitCommonControls(void) { return InitCommonControls(); }

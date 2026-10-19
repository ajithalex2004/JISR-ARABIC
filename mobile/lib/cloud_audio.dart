import 'dart:async';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';

import 'api_service.dart';
import 'playback_words.dart';

/// Plays Arabic with the server's cloud voice (the same audio the web app uses).
///
/// Phones often have no Arabic text-to-speech voice installed, so relying on the
/// device alone plays nothing. The server returns a cached MP3 for any text; the
/// caller falls back to on-device speech only when this returns false.
class CloudArabicAudio {
  CloudArabicAudio(this.api);

  final ApiService api;
  final AudioPlayer _player = AudioPlayer();
  StreamSubscription<void>? _completion;
  StreamSubscription<Duration>? _position;
  int _playback = 0;
  bool _contextSet = false;

  /// Absolute MP3 URL from the `/api/audio/synthesize` response, or null.
  static String? audioUrlFrom(dynamic metadata, String baseUrl) {
    if (metadata is! Map) return null;
    final raw = metadata['audio_url'];
    if (raw is! String || raw.trim().isEmpty) return null;
    if (raw.startsWith('http://') || raw.startsWith('https://')) return raw;
    final base = baseUrl.endsWith('/') ? baseUrl.substring(0, baseUrl.length - 1) : baseUrl;
    return raw.startsWith('/') ? '$base$raw' : '$base/$raw';
  }

  /// The player's rate for the app's speed setting (1.0, 0.6, 0.3); players refuse rates below 0.5.
  static double playbackRateFor(double speed) => speed.clamp(0.5, 2.0).toDouble();

  Future<String?> resolve(String text) async {
    try {
      final metadata = await api.get(
        '/api/audio/synthesize',
        query: {'text': text, 'speed': '1.0', 'lang': 'ar-SA'},
        timeout: const Duration(seconds: 10),
        useCache: true,
      );
      return audioUrlFrom(metadata, api.baseUrl);
    } catch (e) {
      debugPrint('Cloud audio unavailable: $e');
      return null;
    }
  }

  Future<void> _ensureAudioContext() async {
    if (_contextSet) return;
    _contextSet = true;
    try {
      // Play through the speaker even when an iPhone's silent switch is on.
      await AudioPlayer.global.setAudioContext(AudioContextConfig(respectSilence: false).build());
    } catch (e) {
      debugPrint('Audio context not set: $e');
    }
  }

  /// Plays [text] [repeats] times at [speed]. Returns false if the cloud voice
  /// couldn't be played (no network, server error), so the caller can fall back.
  Future<bool> play(String text, {required double speed, required int repeats, required VoidCallback onDone}) async {
    final id = ++_playback;
    await _completion?.cancel();
    await _position?.cancel();
    final url = await resolve(text);
    if (url == null || id != _playback) return false;
    await _ensureAudioContext();

    var remaining = repeats < 1 ? 1 : repeats;
    // Estimate the spoken word from the clip's progress, for word-by-word highlighting.
    final words = playbackWords(text);
    Duration? duration;
    _position = _player.onPositionChanged.listen((position) async {
      if (id != _playback) return;
      duration ??= await _player.getDuration();
      final total = duration;
      if (total != null && id == _playback) {
        PlaybackProgress.update(text, estimateWordIndex(words, position, total));
      }
    });
    _completion = _player.onPlayerComplete.listen((_) async {
      if (id != _playback) return;
      remaining--;
      if (remaining > 0) {
        await Future<void>.delayed(const Duration(milliseconds: 350));
        if (id != _playback) return;
        await _player.seek(Duration.zero);
        await _player.resume();
      } else {
        PlaybackProgress.clear();
        onDone();
      }
    });
    try {
      await _player.play(UrlSource(url));
      await _player.setPlaybackRate(playbackRateFor(speed));
      return id == _playback;
    } catch (e) {
      debugPrint('Cloud audio playback failed: $e');
      await _completion?.cancel();
      await _position?.cancel();
      return false;
    }
  }

  Future<void> stop() async {
    _playback++;
    await _completion?.cancel();
    await _position?.cancel();
    PlaybackProgress.clear();
    try {
      await _player.stop();
    } catch (_) {}
  }

  Future<void> dispose() async {
    await stop();
    await _player.dispose();
  }
}

import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/cloud_audio.dart';

void main() {
  group('CloudArabicAudio.audioUrlFrom', () {
    const base = 'https://api.jisrarabic.com';

    test('joins a relative cache path onto the API host', () {
      expect(
        CloudArabicAudio.audioUrlFrom({'audio_url': '/api/audio/cache/abc.mp3'}, base),
        'https://api.jisrarabic.com/api/audio/cache/abc.mp3',
      );
      expect(
        CloudArabicAudio.audioUrlFrom({'audio_url': '/api/audio/cache/abc.mp3'}, '$base/'),
        'https://api.jisrarabic.com/api/audio/cache/abc.mp3',
      );
    });

    test('keeps an absolute URL as is', () {
      expect(
        CloudArabicAudio.audioUrlFrom({'audio_url': 'https://cdn.example.org/a.mp3'}, base),
        'https://cdn.example.org/a.mp3',
      );
    });

    test('returns null when the server has no audio', () {
      expect(CloudArabicAudio.audioUrlFrom({'audio_url': null}, base), isNull);
      expect(CloudArabicAudio.audioUrlFrom({'audio_url': ''}, base), isNull);
      expect(CloudArabicAudio.audioUrlFrom({}, base), isNull);
      expect(CloudArabicAudio.audioUrlFrom('not json', base), isNull);
      expect(CloudArabicAudio.audioUrlFrom(null, base), isNull);
    });
  });

  test('playback rate follows the speed setting within what players support', () {
    expect(CloudArabicAudio.playbackRateFor(1.0), 1.0);
    expect(CloudArabicAudio.playbackRateFor(0.6), 0.6);
    expect(CloudArabicAudio.playbackRateFor(0.3), 0.5);
  });
}

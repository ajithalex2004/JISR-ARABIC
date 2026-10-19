import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/speech_practice.dart';

void main() {
  group('pickArabicLocale', () {
    test('prefers the UAE variant, then Saudi', () {
      expect(pickArabicLocale(['en_US', 'ar_SA', 'ar_AE']), 'ar_AE');
      expect(pickArabicLocale(['en-US', 'ar-SA', 'ar-JO']), 'ar-SA');
    });
    test('falls back to any Arabic locale', () {
      expect(pickArabicLocale(['fr_FR', 'ar_JO']), 'ar_JO');
    });
    test('is null when the phone has no Arabic recognition', () {
      expect(pickArabicLocale(['en_US', 'hi_IN']), isNull);
      expect(pickArabicLocale(const []), isNull);
    });
  });

  group('buildSpeechEvaluation', () {
    test('sends what the child said, not the target sentence', () {
      final body = buildSpeechEvaluation(
        targetPhrase: 'أُحِبُّ اللُّغَةَ العَرَبِيَّةَ',
        transcript: '  احب اللغه  ',
        childId: 'c1',
        lessonId: 'lesson_01',
      )!;
      expect(body['spoken_text'], 'احب اللغه');
      expect(body['target_phrase'], 'أُحِبُّ اللُّغَةَ العَرَبِيَّةَ');
      expect(body['child_id'], 'c1');
    });
    test('scores nothing when nothing was heard', () {
      expect(buildSpeechEvaluation(targetPhrase: 'مرحبا', transcript: '   '), isNull);
    });
  });

  group('buildRecordingEvaluation', () {
    test('sends the recording for a signed-in learner', () {
      final body = buildRecordingEvaluation(targetPhrase: 'مرحبا', audioBase64: 'UklGRg==', childId: 'c1')!;
      expect(body['audio_base64'], 'UklGRg==');
      expect(body['audio_mime_type'], 'audio/wav');
      expect(body.containsKey('spoken_text'), isFalse);
    });
    test('needs a learner and some audio', () {
      expect(buildRecordingEvaluation(targetPhrase: 'مرحبا', audioBase64: 'UklGRg=='), isNull);
      expect(buildRecordingEvaluation(targetPhrase: 'مرحبا', audioBase64: '', childId: 'c1'), isNull);
    });
  });
}

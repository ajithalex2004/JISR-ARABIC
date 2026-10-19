import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/playback_words.dart';
import 'package:mobile/widgets/aligned_sentence.dart';

void main() {
  tearDown(PlaybackProgress.clear);

  test('estimateWordIndex moves through the words as the clip plays', () {
    final words = playbackWords('هُنَاكَ أَنْوَاعٌ مُخْتَلِفَةٌ لِلْكُرَةِ.');
    const total = Duration(seconds: 4);
    expect(estimateWordIndex(words, Duration.zero, total), 0);
    expect(estimateWordIndex(words, const Duration(milliseconds: 3990), total), 3);
    final seen = [for (var ms = 0; ms <= 4000; ms += 100) estimateWordIndex(words, Duration(milliseconds: ms), total)];
    expect(seen.toSet(), {0, 1, 2, 3});
    for (var i = 1; i < seen.length; i++) {
      expect(seen[i] >= seen[i - 1], isTrue); // never goes backwards
    }
    expect(estimateWordIndex(words, Duration.zero, Duration.zero), -1);
  });

  test('wordIndexAtChar maps device speech offsets to words', () {
    const text = 'الحِصَانُ  سَرِيعٌ جِدًّا';
    expect(wordIndexAtChar(text, 0), 0);
    expect(wordIndexAtChar(text, text.indexOf('سَرِيعٌ')), 1);
    expect(wordIndexAtChar(text, text.indexOf('جِدًّا')), 2);
  });

  test('localWordIndex finds the spoken word inside a line of the played paragraph', () {
    const paragraph = 'قَبْلَ الاسْتِمَاعِ:\n١ - أَتَأَمَّلُ الصُّورَةَ.';
    const line = '١ - أَتَأَمَّلُ الصُّورَةَ.';
    // Played words: 0 قَبْلَ, 1 الاسْتِمَاعِ:, 2 ١, 3 -, 4 أَتَأَمَّلُ, 5 الصُّورَةَ.
    expect(localWordIndex(paragraph, 4, line), 2);
    expect(localWordIndex(paragraph, 0, line), -1); // spoken word is outside this line
    expect(localWordIndex(paragraph, 5, line), 3);
    expect(localWordIndex('مَرْحَبًا', 0, line), -1); // different text
  });

  test('isSpokenWord uses the position, or a single tapped word', () {
    const text = 'الحِصَانُ سَرِيعٌ.';
    expect(isSpokenWord(const SpokenWord(text, 1), text, 1, 'سَرِيعٌ.', ''), isTrue);
    expect(isSpokenWord(const SpokenWord(text, 1), text, 0, 'الحِصَانُ', ''), isFalse);
    expect(isSpokenWord(const SpokenWord('الحِصَانُ', 0), text, 0, 'الحِصَانُ', ''), isTrue);
    expect(isSpokenWord(null, text, 0, 'الحِصَانُ', 'الحِصَانُ'), isTrue);
  });

  testWidgets('AlignedSentenceView lights up the spoken word and its English while it plays', (tester) async {
    const ar = 'الحِصَانُ سَرِيعٌ.';
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: AlignedSentenceView(
          ar: ar,
          en: 'The horse is fast.',
          chunks: AlignmentChunk.listFromJson([
            {'ar': [0], 'en': [0, 1]},
            {'ar': [1], 'en': [3]},
          ])!,
        ),
      ),
    ));
    Color? background(String text) {
      final container = tester.widget<Container>(
        find.ancestor(of: find.text(text), matching: find.byType(Container)).first,
      );
      return (container.decoration as BoxDecoration).color;
    }

    expect(background('fast.'), Colors.transparent);
    PlaybackProgress.update(ar, 1);
    await tester.pump();
    expect(background('سَرِيعٌ.'), isNot(Colors.transparent));
    expect(background('fast.'), isNot(Colors.transparent));
    expect(background('horse'), Colors.transparent);

    PlaybackProgress.clear();
    await tester.pump();
    expect(background('fast.'), Colors.transparent);
  });
}

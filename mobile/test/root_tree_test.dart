import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/widgets/root_tree_sheet.dart';

const _family = {
  'root': 'د-و-ر',
  'roots': ['د-و-ر'],
  'borrowed': false,
  'note_en': null,
  'letters': ['د', 'و', 'ر'],
  'core_meaning_en': 'turning, going round',
  'curriculum_words': [
    {'word_ar': 'مُسْتَدِيرٌ', 'meaning_en': 'Round / circular', 'lesson_id': 'lesson_01_ball_games',
     'lesson_title_en': 'Ball Games', 'lesson_title_ar': 'ألعاب الكرة', 'grade': 5, 'term': 1},
  ],
  'family': [
    {'word_ar': 'دَائِرَةٌ', 'meaning_en': 'circle', 'pattern': 'فَاعِلَة', 'kind': 'noun'},
  ],
  'family_source': 'ai',
};

void main() {
  test('root letters are found, ignoring prefixes and vowel marks', () {
    expect(rootLetterPositions('المَلْعَبُ', 'ل-ع-ب'), [3, 4, 5]);
    expect(rootLetterPositions('مَكْتَبَةٌ', 'ك-ت-ب'), [1, 2, 3]);
    expect(rootLetterPositions('الكُرَةُ', 'ك-ر-و'), [2, 3]);
    expect(rootLetterPositions('المَهَامُّ', 'ه-م-م'), [3, 5]);
    expect(rootLetterPositions('مَدْرَسَةٌ', 'ك-ت-ب'), isNull);
  });

  test('rootSpans colours only the root letters and keeps every character', () {
    final spans = rootSpans('مُسْتَدِيرٌ', 'د-و-ر', Colors.green);
    expect(spans.map((s) => s.text).join(), 'مُسْتَدِيرٌ');
    expect(spans.where((s) => s.style?.color == Colors.green).map((s) => s.text).join(), 'دِيرٌ');
  });

  test('RootFamily parses the API response', () {
    final family = RootFamily.fromJson(Map<String, dynamic>.from(_family));
    expect(family.letters, ['د', 'و', 'ر']);
    expect(family.lessonWords.single.lessonTitleEn, 'Ball Games');
    expect(family.family.single.pattern, 'فَاعِلَة');
    expect(family.familySource, 'ai');
  });

  testWidgets('RootTreeView shows lesson words, family words and plays audio on tap', (tester) async {
    final spoken = <String>[];
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: RootTreeView(
          family: RootFamily.fromJson(Map<String, dynamic>.from(_family)),
          word: 'مُسْتَدِيرٌ',
          onVocalize: spoken.add,
        ),
      ),
    ));
    expect(find.text('IN YOUR LESSONS'), findsOneWidget);
    expect(find.text('Class 5 · Term 1 · Ball Games'), findsOneWidget);
    expect(find.text('Noun · pattern فَاعِلَة'), findsOneWidget);
    await tester.tap(find.text('circle'));
    expect(spoken, ['دَائِرَةٌ']);
  });

  testWidgets('RootTreeView explains borrowed words', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: RootTreeView(
          family: RootFamily.fromJson({
            'root': null, 'roots': [], 'borrowed': true,
            'note_en': "Borrowed from English 'film', so it has no Arabic root.",
            'letters': [], 'curriculum_words': [], 'family': [], 'family_source': 'none',
          }),
          word: 'فِيلْمٌ',
          onVocalize: (_) {},
        ),
      ),
    ));
    expect(find.text('Borrowed word: no Arabic root'), findsOneWidget);
    expect(find.textContaining('film'), findsOneWidget);
  });
}

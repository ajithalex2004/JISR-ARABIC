import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/widgets/homework_helper.dart';

void main() {
  test('picked files are sent with the right type', () {
    expect(homeworkMimeFor('Worksheet.PDF'), 'application/pdf');
    expect(homeworkMimeFor('hw.docx'), docxMime);
    expect(homeworkMimeFor('photo.png'), 'image/png');
    expect(homeworkMimeFor('IMG_001.jpg'), 'image/jpeg');
  });

  test('a scan reply is read with its answers', () {
    final scan = HomeworkScan.fromJson({
      'scan_id': 'abc',
      'is_homework': true,
      'title_en': 'Colours',
      'questions': [
        {'number': '1', 'question_ar': 'مَا لَوْنُ السَّمَاءِ؟', 'question_en': 'What colour is the sky?',
         'asks_en': 'Write the colour.', 'hint_en': 'Think of colour words.', 'hint_ar': 'تَذَكَّرِ الأَلْوَانَ.',
         'answer': 'أَزْرَقُ', 'answer_en': 'Blue.'},
      ],
    });
    expect(scan.isHomework, isTrue);
    expect(scan.questions.single.questionEn, 'What colour is the sky?');
    expect(scan.questions.single.answer, 'أَزْرَقُ');
  });

  testWidgets('the hint and the answer stay hidden until the student asks for them', (tester) async {
    const scan = HomeworkScan('abc', true, 'Colours', [
      HomeworkQuestion(number: '1', questionAr: 'مَا لَوْنُ السَّمَاءِ؟', questionEn: 'What colour is the sky?',
          asksEn: 'Write the colour.', hintEn: 'Think of colour words.', hintAr: 'تَذَكَّرِ الأَلْوَانَ.',
          answer: 'أَزْرَقُ', answerEn: 'Blue.'),
    ]);
    await tester.pumpWidget(const MaterialApp(home: Scaffold(body: HomeworkHelperView(initialScan: scan))));
    expect(find.textContaining('What colour is the sky?'), findsOneWidget);
    expect(find.text('Think of colour words.'), findsNothing);
    await tester.tap(find.text('Stuck? Show a hint'));
    await tester.pump();
    expect(find.text('Think of colour words.'), findsOneWidget);
    expect(find.text('Blue.'), findsNothing);
    await tester.ensureVisible(find.text('Show the answer'));
    await tester.tap(find.text('Show the answer'));
    await tester.pump();
    expect(find.text('أَزْرَقُ'), findsOneWidget);
    expect(find.text('Blue.'), findsOneWidget);
  });
}

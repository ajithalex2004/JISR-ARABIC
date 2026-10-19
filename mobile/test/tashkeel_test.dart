import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/widgets/interactive_arabic_text.dart';
import 'package:mobile/tashkeel.dart';

void main() {
  test('stripTashkeel removes vowel marks but keeps letters and hamza', () {
    expect(stripTashkeel('العَرَبِيَّةُ تَجْمَعُنَا'), 'العربية تجمعنا');
    expect(stripTashkeel('كِتَابٌ'), 'كتاب');
    expect(stripTashkeel('هٰذَا'), 'هذا');
    expect(stripTashkeel('أَنَا'), 'أنا');
    expect(stripTashkeel('سُؤَالٌ؟'), 'سؤال؟');
    expect(stripTashkeel('Hello'), 'Hello');
  });

  test('TashkeelState.display follows the toggle', () {
    expect(TashkeelState.showVowels, isTrue);
    expect(TashkeelState.display('بَيْتٌ'), 'بَيْتٌ');
    TashkeelState.toggle();
    expect(TashkeelState.display('بَيْتٌ'), 'بيت');
    TashkeelState.toggle();
    expect(TashkeelState.display('بَيْتٌ'), 'بَيْتٌ');
  });

  testWidgets('InteractiveArabicText hides and restores vowels when toggled', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(body: InteractiveArabicText(text: 'كِتَابٌ جَمِيلٌ')),
    ));
    expect(find.text('كِتَابٌ'), findsOneWidget);

    TashkeelState.toggle();
    await tester.pump();
    expect(find.text('كتاب'), findsOneWidget);
    expect(find.text('كِتَابٌ'), findsNothing);

    TashkeelState.toggle();
    await tester.pump();
    expect(find.text('كِتَابٌ'), findsOneWidget);
  });
}

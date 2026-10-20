import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/arabic_setup.dart';

void main() {
  test('Arabic letters prove the keyboard works', () {
    expect(typedArabic('مرحبا'), isTrue);
    expect(typedArabic('mrhba'), isFalse);
  });

  test('offered until finished, and not while put off', () {
    final now = DateTime(2026, 10, 20);
    expect(shouldOfferArabicSetup(now: now), isTrue);
    expect(shouldOfferArabicSetup(done: '2026-10-01', now: now), isFalse);
    expect(shouldOfferArabicSetup(snoozeUntil: '2026-10-22T00:00:00', now: now), isFalse);
    expect(shouldOfferArabicSetup(snoozeUntil: '2026-10-19T00:00:00', now: now), isTrue);
  });

  testWidgets('guides a phone without Arabic, and confirms the typing test', (tester) async {
    bool? result;
    await tester.pumpWidget(MaterialApp(home: Builder(builder: (context) => TextButton(
      onPressed: () async => result = await showDialog<bool>(
          context: context, builder: (_) => ArabicSetupDialog(ios: false, voiceCheck: Future.value(false))),
      child: const Text('open'),
    ))));
    await tester.tap(find.text('open'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Gboard'), findsOneWidget);
    expect(find.textContaining('No Arabic voice on this phone yet'), findsOneWidget);
    await tester.enterText(find.byKey(const Key('arabic-keyboard-test')), 'mrhba');
    await tester.pump();
    expect(find.textContaining('Those are English letters'), findsOneWidget);
    await tester.enterText(find.byKey(const Key('arabic-keyboard-test')), 'مرحبا');
    await tester.pump();
    expect(find.text('1. Arabic keyboard · works!'), findsOneWidget);
    await tester.ensureVisible(find.text('All set'));
    await tester.tap(find.text('All set'));
    await tester.pumpAndSettle();
    expect(result, isTrue);
  });
}

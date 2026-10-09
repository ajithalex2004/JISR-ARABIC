import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/main.dart';

void main() {
  testWidgets('JISR Arabic App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const JisrArabicApp());

    // Verify that brand title is rendered.
    expect(find.text('JISR '), findsOneWidget);
    expect(find.text('جسر'), findsOneWidget);
  });
}

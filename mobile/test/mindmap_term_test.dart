import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/screens/mindmap_screen.dart';

class _FakeApi {
  final List<int> terms = [];
  Future<dynamic> mindmaps({int grade = 5, int term = 1, String? token}) async {
    terms.add(term);
    return null; // keep the built-in chapters
  }
}

void main() {
  testWidgets('mind maps load the term selected in the app, not always Term 1', (tester) async {
    tester.view.physicalSize = const Size(900, 3000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    final api = _FakeApi();
    Widget screen(int term) => MaterialApp(
          home: MindmapsScreen(isArabic: false, initialGrade: 3, term: term, api: api, onBack: () {}),
        );
    await tester.pumpWidget(screen(2));
    await tester.pump();
    expect(api.terms, [2]);
    await tester.pumpWidget(screen(3));
    await tester.pump();
    expect(api.terms, [2, 3]);
  });
}

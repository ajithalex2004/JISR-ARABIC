import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/api_service.dart';
import 'package:mobile/screens/learning_views.dart';

// Trimmed copies of what the server sends (GET /api/modules/malazim?grade=3, /api/modules/capsules?grade=3).
final _booklet = {
  'success': true,
  'booklet': {
    'lesson_id': 'lesson_g3_t1_ch01',
    'study_mode': {
      'sections': [
        {
          'section_id': 'sec_g3_t1_ch01_01_reading',
          'title_ar': 'نص الدرس',
          'title_en': '1. Lesson Text: Tales of Courage & Patience',
          'content_ar': 'يتناول الدرس',
          'content_en': 'Chapter 1 of Term 1 explores the lesson.',
          'key_takeaways_ar': ['الفكرة المحورية'],
          'key_takeaways_en': ['Core theme'],
          // The booklet carries no answer: the server checks it.
          'inline_exercise': {
            'question_ar': 'ما عنوان الدرس؟',
            'question_en': 'What is the title of the lesson covered in this booklet?',
            'options': ['حكايات الشجاعة', 'ألعاب الكرة', 'رحلة إلى البحر'],
            'options_en': ['Tales of Courage & Patience', 'Ball Games', 'A Trip to the Sea'],
          },
        },
      ],
    },
    'quick_review_mode': {
      'high_yield_summary': [
        {'bullet_ar': 'موضوع الدرس', 'bullet_en': "Lesson theme: 'Tales of Courage & Patience'."},
      ],
      'essential_formulas': [],
      'exam_pitfall_warnings': [
        {'warning_ar': 'انتبه', 'warning_en': 'Pay attention to case endings.'},
      ],
    },
  },
};

final _capsules = {
  'success': true,
  'grade': 3,
  'count': 1,
  'capsules': [
    {
      'id': 'capsule_g3_t1_01',
      'title_ar': 'المفردات والفهم',
      'title_en': 'Tales of Courage & Patience: Vocabulary & Comprehension',
      'duration_minutes': 3,
      'summary_ar': 'أبرز الأفكار',
      'summary_en': 'Key ideas.',
    },
  ],
};

ApiService _api(List<http.Request> seen) => ApiService(
      baseUrl: 'http://test',
      client: MockClient((request) async {
        seen.add(request);
        final path = request.url.path;
        final body = path.endsWith('/check')
            ? {'is_correct': (jsonDecode(request.body) as Map)['answer'] == 0, 'correct_index': 0,
               'explanation_ar': 'صحيح', 'explanation_en': 'Correct: the lesson is Tales of Courage.'}
            : path.contains('malazim') ? _booklet : _capsules;
        return http.Response(jsonEncode(body), 200, headers: {'content-type': 'application/json'});
      }),
    );

void _tallScreen(WidgetTester tester) {
  tester.view.physicalSize = const Size(900, 8000);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);
}

void main() {
  test('the server booklet and capsule shapes are read', () {
    final parsed = MalazimView.parseBooklet(_booklet);
    expect(parsed['lessonId'], 'lesson_g3_t1_ch01');
    final sections = parsed['sections'] as List<Map<String, dynamic>>;
    expect(sections.single['id'], 'sec_g3_t1_ch01_01_reading');
    expect(sections.single['options_en'], hasLength(3));
    expect((parsed['quickReview'] as Map)['exam_pitfall_warnings'], hasLength(1));
    expect(CapsulesView.parseCapsules(_capsules).single['titleEn'], startsWith('Tales of Courage'));
    // A bare list still works; anything else gives nothing rather than another class's samples.
    expect(CapsulesView.parseCapsules(_capsules['capsules']), hasLength(1));
    expect(CapsulesView.parseCapsules(null), isEmpty);
    expect(MalazimView.parseBooklet({'error': 'x'})['sections'], isEmpty);
  });

  testWidgets('study notes show the class\'s own booklet and check answers on the server', (tester) async {
    _tallScreen(tester);
    final seen = <http.Request>[];
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: MalazimView(grade: 3, api: _api(seen)))));
    await tester.pumpAndSettle();
    expect(find.text('1. Lesson Text: Tales of Courage & Patience'), findsOneWidget);
    expect(find.textContaining('Football'), findsNothing);

    await tester.tap(find.text('Tales of Courage & Patience'));
    await tester.pump();
    await tester.tap(find.text('تحقق من الإجابة (Check Answer)'));
    await tester.pumpAndSettle();
    final check = seen.last;
    expect(check.method, 'POST');
    expect(check.url.path, '/api/modules/malazim/lesson_g3_t1_ch01/check');
    expect(jsonDecode(check.body), containsPair('section_id', 'sec_g3_t1_ch01_01_reading'));
    expect(find.text('إجابة صحيحة! (Correct)'), findsOneWidget);
    expect(find.text('Correct: the lesson is Tales of Courage.'), findsOneWidget);
  });

  testWidgets('the 15-minute review comes from the server, not football facts', (tester) async {
    _tallScreen(tester);
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: MalazimView(grade: 3, api: _api([])))));
    await tester.pumpAndSettle();
    await tester.tap(find.text('15-Minute Quick Notes'));
    await tester.pumpAndSettle();
    expect(find.text("Lesson theme: 'Tales of Courage & Patience'."), findsOneWidget);
    expect(find.text('Pay attention to case endings.'), findsOneWidget);
    expect(find.textContaining('11 players'), findsNothing);
  });

  testWidgets('with nothing from the server, no other class\'s samples are shown', (tester) async {
    _tallScreen(tester);
    await tester.pumpWidget(const MaterialApp(home: Scaffold(body: MalazimView(grade: 2))));
    await tester.pumpAndSettle();
    expect(find.textContaining("couldn't be loaded"), findsOneWidget);
    expect(find.textContaining('Ball'), findsNothing);
  });

  testWidgets('capsules show the class\'s own capsules', (tester) async {
    _tallScreen(tester);
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: CapsulesView(grade: 3, api: _api([]), completedCapsules: const {}, onCapsuleCompleted: (_) {}),
      ),
    ));
    await tester.pumpAndSettle();
    expect(find.text('Tales of Courage & Patience: Vocabulary & Comprehension'), findsOneWidget);
    expect(find.text('0 / 1 منجزة 🏅'), findsOneWidget);
    expect(find.textContaining('Inna'), findsNothing);
  });
}

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/models/curriculum_models.dart';
import 'package:mobile/screens/catalogue_screen.dart';

Map<String, dynamic> _lesson(int order, String titleEn, {bool free = false, String status = 'published'}) => {
      'id': 'g3_t1_$order',
      'lesson_order': order,
      'title_ar': 'عائلتي',
      'title_en': titleEn,
      'unit_title_ar': 'الوحدة الأولى',
      'unit_title_en': 'Unit 1',
      'start_page': 8,
      'is_first_chapter_demo': free,
      'is_accessible': free,
      'status': status,
    };

Widget _screen(List<CurriculumLessonItem> lessons, {int grade = 3, int term = 1}) => MaterialApp(
      home: Scaffold(
        body: CatalogueScreen(
          lessons: lessons,
          remoteCapsules: const [],
          activeChild: null,
          currentGrade: grade,
          currentTerm: term,
          learningDataLoading: false,
          isArabic: false,
          onSelectGrade: (_) {},
          onSelectLessonMode: (_, __) {},
          onModeSelected: (_) {},
          onOpenAskFahim: () {},
          onOpenPaywall: () {},
        ),
      ),
    );

void main() {
  test('only the server flag makes a chapter free, not lesson order 1', () {
    expect(CurriculumLessonItem.fromMap(_lesson(1, 'My Family', free: true)).isFirstChapterDemo, isTrue);
    // Chapter 1 of Term 2 or 3 comes with the flag off: it must not show as free.
    expect(CurriculumLessonItem.fromMap(_lesson(1, 'My Family')).isFirstChapterDemo, isFalse);
    expect(CurriculumLessonItem.fromMap(_lesson(1, 'My Family', free: true, status: 'coming_soon')).isFirstChapterDemo,
        isFalse);
  });

  testWidgets('featured card shows the class\'s own first chapter, not Ball Games', (tester) async {
    final lessons = [_lesson(1, 'My Family', free: true), _lesson(2, 'My School')]
        .map(CurriculumLessonItem.fromMap)
        .toList();
    await tester.pumpWidget(_screen(lessons));
    expect(find.text('عائلتي (My Family)'), findsOneWidget);
    expect(find.text('Class 3 · Term 1 · Chapter 1'), findsOneWidget);
    expect(find.text('Free (مجاني)'), findsOneWidget);
    expect(find.textContaining('Ball Games'), findsNothing);
  });

  testWidgets('a Term 2 first chapter is not labelled free', (tester) async {
    final lessons = [CurriculumLessonItem.fromMap(_lesson(1, 'Our Planet'))];
    await tester.pumpWidget(_screen(lessons, term: 2));
    expect(find.text('Class 3 · Term 2 · Chapter 1'), findsOneWidget);
    expect(find.text('Free (مجاني)'), findsNothing);
    expect(find.text('Subscription (يحتاج اشتراك)'), findsOneWidget);
  });
}

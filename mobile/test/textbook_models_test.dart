import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/models/curriculum_models.dart';

void main() {
  group('Textbook Page Counts & Editions Verification', () {
    test('Grade 1 page counts', () {
      expect(getTextbookPageCount(1, 1), 112);
      expect(getTextbookPageCount(1, 2), 99);
      expect(getTextbookPageCount(1, 3), 93);
    });

    test('Grade 2 page counts', () {
      expect(getTextbookPageCount(2, 1), 112);
      expect(getTextbookPageCount(2, 2), 74);
      expect(getTextbookPageCount(2, 3), 68);
    });

    test('Grade 3 page counts', () {
      expect(getTextbookPageCount(3, 1), 112);
      expect(getTextbookPageCount(3, 2), 71);
      expect(getTextbookPageCount(3, 3), 47);
    });

    test('Grade 4 page counts', () {
      expect(getTextbookPageCount(4, 1), 112);
      expect(getTextbookPageCount(4, 2), 72);
      expect(getTextbookPageCount(4, 3), 68);
    });

    test('Grade 5 page counts', () {
      expect(getTextbookPageCount(5, 1), 112);
      expect(getTextbookPageCount(5, 2), 72);
      expect(getTextbookPageCount(5, 3), 46);
    });

    test('Grade 6 page counts', () {
      expect(getTextbookPageCount(6, 1), 116);
      expect(getTextbookPageCount(6, 2), 72);
      expect(getTextbookPageCount(6, 3), 67);
    });

    test('Grade 7 page counts', () {
      expect(getTextbookPageCount(7, 1), 112);
      expect(getTextbookPageCount(7, 2), 73);
      expect(getTextbookPageCount(7, 3), 68);
    });

    test('Grade 8 page counts', () {
      expect(getTextbookPageCount(8, 1), 51);
      expect(getTextbookPageCount(8, 2), 72);
      expect(getTextbookPageCount(8, 3), 67);
    });

    test('Grade 9 page counts', () {
      expect(getTextbookPageCount(9, 1), 100);
      expect(getTextbookPageCount(9, 2), 73);
      expect(getTextbookPageCount(9, 3), 67);
    });

    test('Grade 10 page counts', () {
      expect(getTextbookPageCount(10, 1), 63);
      expect(getTextbookPageCount(10, 2), 71);
      expect(getTextbookPageCount(10, 3), 67);
    });
  });
}

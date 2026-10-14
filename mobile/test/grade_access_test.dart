import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/grade_access.dart';

void main() {
  final child = {'id': 'c1', 'name': 'Ann Maria', 'default_grade': 6, 'entitled_grades': [7, 6]};

  test('students see only their own grade, even with other paid grades', () {
    expect(allowedGrades({'role': 'learner'}, child), [6]);
  });

  test('parents see the child\'s registered and paid-for grades', () {
    expect(allowedGrades({'role': 'parent'}, child), [6, 7]);
    expect(allowedGrades({'role': 'parent'}, {'default_grade': 4}), [4]);
  });

  test('admins and signed-out visitors see every grade', () {
    expect(allowedGrades({'role': 'admin'}, child), hasLength(12));
    expect(allowedGrades(null, null), hasLength(12));
  });
}

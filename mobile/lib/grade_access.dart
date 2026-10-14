/// Which grades the app may show, matching the server's entitlement rules:
/// students see only their own grade; parents see the selected child's registered
/// and paid-for grades (`entitled_grades`); admins and signed-out visitors see all.
/// Any other grade has to be unlocked (paid) before its lessons open.
List<int> allowedGrades(Map<String, dynamic>? user, Map<String, dynamic>? child) {
  const all = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
  final role = user?['role']?.toString();
  if (user == null || role == 'admin') return all;

  final defaultGrade = child?['default_grade'];
  final ownGrade = defaultGrade is int ? defaultGrade : int.tryParse('${defaultGrade ?? ''}');
  if (role == 'learner') return ownGrade != null ? [ownGrade] : all;

  final entitled = (child?['entitled_grades'] as List?)
      ?.map((g) => g is int ? g : int.tryParse('$g'))
      .whereType<int>()
      .toSet()
      .toList();
  if (entitled != null && entitled.isNotEmpty) return entitled..sort();
  return ownGrade != null ? [ownGrade] : all;
}

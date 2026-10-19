/// Helpers for the "say the sentence" speaking practice.
///
/// The score must come from what the child actually said: the request carries the recognised
/// transcript, never the target sentence, and nothing is scored when nothing was heard.
library;

/// The device's Arabic recognition locale, preferring UAE/Gulf variants, or null if it has none.
String? pickArabicLocale(Iterable<String> localeIds) {
  final arabic = localeIds.where((id) => id.toLowerCase().replaceAll('-', '_').startsWith('ar')).toList();
  if (arabic.isEmpty) return null;
  for (final preferred in const ['ar_ae', 'ar_sa', 'ar_eg']) {
    for (final id in arabic) {
      if (id.toLowerCase().replaceAll('-', '_') == preferred) return id;
    }
  }
  return arabic.first;
}

/// Body for `/api/audio/evaluate-speech`, or null when there is nothing to score.
Map<String, dynamic>? buildSpeechEvaluation({
  required String targetPhrase,
  required String transcript,
  String? childId,
  String? lessonId,
}) {
  final spoken = transcript.trim();
  if (spoken.isEmpty) return null;
  return {
    if (childId != null && childId.isNotEmpty) 'child_id': childId,
    if (lessonId != null && lessonId.isNotEmpty) 'lesson_id': lessonId,
    'target_phrase': targetPhrase,
    'spoken_text': spoken,
  };
}

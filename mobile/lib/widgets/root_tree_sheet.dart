import 'package:flutter/material.dart';

import '../api_service.dart';

/// Root Tree Explorer for the mobile app: the root's letters, the words from the learner's
/// lessons that share it, and AI-suggested relatives (GET /api/curriculum/root-family).

class RootLessonWord {
  final String wordAr;
  final String meaningEn;
  final String lessonTitleEn;
  final int? grade;
  final int? term;

  const RootLessonWord(this.wordAr, this.meaningEn, this.lessonTitleEn, this.grade, this.term);
}

class RootFamilyWord {
  final String wordAr;
  final String meaningEn;
  final String? pattern;
  final String kind;

  const RootFamilyWord(this.wordAr, this.meaningEn, this.pattern, this.kind);
}

class RootFamily {
  final String? root;
  final List<String> roots;
  final bool borrowed;
  final String? noteEn;
  final List<String> letters;
  final String? coreMeaningEn;
  final List<RootLessonWord> lessonWords;
  final List<RootFamilyWord> family;
  final String familySource;

  const RootFamily({
    this.root,
    this.roots = const [],
    this.borrowed = false,
    this.noteEn,
    this.letters = const [],
    this.coreMeaningEn,
    this.lessonWords = const [],
    this.family = const [],
    this.familySource = 'none',
  });

  factory RootFamily.fromJson(Map<String, dynamic> json) {
    String? str(Object? v) => (v == null || v.toString().isEmpty) ? null : v.toString();
    List<Map> maps(Object? v) => (v as List? ?? const []).whereType<Map>().toList();
    return RootFamily(
      root: str(json['root']),
      roots: (json['roots'] as List? ?? const []).map((e) => e.toString()).toList(),
      borrowed: json['borrowed'] == true,
      noteEn: str(json['note_en']),
      letters: (json['letters'] as List? ?? const []).map((e) => e.toString()).toList(),
      coreMeaningEn: str(json['core_meaning_en']),
      lessonWords: maps(json['curriculum_words'])
          .map((w) => RootLessonWord(
                w['word_ar']?.toString() ?? '',
                w['meaning_en']?.toString() ?? '',
                w['lesson_title_en']?.toString() ?? '',
                w['grade'] is int ? w['grade'] as int : null,
                w['term'] is int ? w['term'] as int : null,
              ))
          .toList(),
      family: maps(json['family'])
          .map((w) => RootFamilyWord(
                w['word_ar']?.toString() ?? '',
                w['meaning_en']?.toString() ?? '',
                str(w['pattern']),
                w['kind']?.toString() ?? 'other',
              ))
          .toList(),
      familySource: json['family_source']?.toString() ?? 'none',
    );
  }
}

final RegExp _mark = RegExp(r'[ً-ْٖ-ٰٟـ]');
const _hamza = 'أإآءؤئ';
const _weak = 'اوىي';

bool _sameLetter(String letter, String rootLetter) {
  if (letter == rootLetter) return true;
  if (_hamza.contains(rootLetter) || rootLetter == 'ا') return _hamza.contains(letter) || letter == 'ا';
  if (_weak.contains(rootLetter)) return _weak.contains(letter) || _hamza.contains(letter);
  return false;
}

/// Indexes, among the word's letters (vowel marks ignored), of the root's letters; null if absent.
/// Mirrors root_letter_positions in backend/modules/curriculum/roots.py.
List<int>? rootLetterPositions(String word, String root) {
  final letters = word.runes.map(String.fromCharCode).where((c) => !_mark.hasMatch(c)).toList();
  final rootLetters = root.split('-');

  List<int>? match(int i, int end) {
    if (i < 0) return [];
    final target = rootLetters[i];
    final candidates = [
      for (var j = end - 1; j >= 0; j--) if (letters[j] == target) j,
      for (var j = end - 1; j >= 0; j--) if (letters[j] != target && _sameLetter(letters[j], target)) j,
    ];
    for (final j in candidates) {
      final rest = match(i - 1, j);
      if (rest != null) return [...rest, j];
    }
    final doubled = i + 1 < rootLetters.length && rootLetters[i + 1] == target;
    return _weak.contains(target) || doubled ? match(i - 1, end) : null;
  }

  return match(rootLetters.length - 1, letters.length);
}

/// The phrase as text spans, with the root letters of the first matching word in [rootColor].
/// Only the colour changes between spans, so Arabic letters keep joining.
List<TextSpan> rootSpans(String phrase, String? root, Color rootColor) {
  if (root == null) return [TextSpan(text: phrase)];
  final spans = <TextSpan>[];
  var done = false;
  for (final part in phrase.split(RegExp(r'(?=\s)|(?<=\s)'))) {
    final positions = !done && part.trim().isNotEmpty ? rootLetterPositions(part, root) : null;
    if (positions == null || positions.isEmpty) {
      spans.add(TextSpan(text: part));
      continue;
    }
    done = true;
    final wanted = positions.toSet();
    var index = -1;
    final buffer = StringBuffer();
    bool? current;
    void flush() {
      if (buffer.isEmpty) return;
      spans.add(TextSpan(text: buffer.toString(), style: current == true ? TextStyle(color: rootColor) : null));
      buffer.clear();
    }

    for (final ch in part.runes.map(String.fromCharCode)) {
      if (!_mark.hasMatch(ch)) index++;
      final isRoot = wanted.contains(index);
      if (current != null && current != isRoot) flush();
      current = isRoot;
      buffer.write(ch);
    }
    flush();
  }
  return spans;
}

const _kindLabels = {
  'verb': 'Verb',
  'noun': 'Noun',
  'adjective': 'Describing word',
  'doer': 'The one who does it',
  'object': 'The thing it is done to',
  'place': 'Place',
  'instrument': 'Tool',
  'plural': 'Plural',
};

/// Opens the Root Tree Explorer as a bottom sheet for a vocabulary card.
Future<void> showRootTreeSheet(
  BuildContext context, {
  required String root,
  required String word,
  required void Function(String) onVocalize,
  ApiService? api,
}) {
  final request = (api ?? ApiService()).get(
    '/api/curriculum/root-family',
    query: {if (root.isNotEmpty) 'root': root, if (word.isNotEmpty) 'word': word},
    timeout: const Duration(seconds: 20),
    useCache: true,
  );
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.white,
    shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
    builder: (context) => DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.75,
      maxChildSize: 0.95,
      builder: (context, controller) => FutureBuilder<dynamic>(
        future: request,
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return const Padding(
              padding: EdgeInsets.all(24),
              child: Text("We couldn't load this root family. Check your connection and try again."),
            );
          }
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          final family = RootFamily.fromJson(Map<String, dynamic>.from(snapshot.data as Map));
          return RootTreeView(family: family, word: word, onVocalize: onVocalize, controller: controller);
        },
      ),
    ),
  );
}

class RootTreeView extends StatelessWidget {
  final RootFamily family;
  final String word;
  final void Function(String) onVocalize;
  final ScrollController? controller;

  const RootTreeView({
    super.key,
    required this.family,
    required this.word,
    required this.onVocalize,
    this.controller,
  });

  static const _plum = Color(0xFF2A1548);
  static const _gold = Color(0xFFFCD34D);
  static const _emerald = Color(0xFF059669);
  static const _violet = Color(0xFF7C3AED);

  Widget _wordTile({
    required String wordAr,
    required String meaning,
    required String subtitle,
    required Color accent,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Expanded(
            child: Material(
              color: accent.withValues(alpha: 0.06),
              shape: RoundedRectangleBorder(side: BorderSide(color: accent.withValues(alpha: 0.35))),
              child: InkWell(
                onTap: () => onVocalize(wordAr),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(meaning, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                            Text(subtitle, style: TextStyle(fontSize: 11, color: accent)),
                          ],
                        ),
                      ),
                      Text.rich(
                        TextSpan(children: rootSpans(wordAr, family.root, accent)),
                        textDirection: TextDirection.rtl,
                        style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                      ),
                      const SizedBox(width: 6),
                      Icon(Icons.volume_up_rounded, size: 18, color: accent),
                    ],
                  ),
                ),
              ),
            ),
          ),
          // Twig into the trunk on the right.
          Container(width: 14, height: 2, color: _gold),
        ],
      ),
    );
  }

  Widget _heading(IconData icon, String text, Color color) => Padding(
        padding: const EdgeInsets.only(bottom: 8, top: 4),
        child: Row(children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 6),
          Text(text, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 0.8, color: color)),
        ]),
      );

  @override
  Widget build(BuildContext context) {
    final children = <Widget>[
      Center(
        child: Container(
          width: 40, height: 4, margin: const EdgeInsets.only(bottom: 12),
          decoration: BoxDecoration(color: const Color(0xFFCBD5E1), borderRadius: BorderRadius.circular(2)),
        ),
      ),
      const Text('Root Tree Explorer · شجرة الجذر',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: _plum)),
      const Text('Words that share a root share a meaning.',
          style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
      const SizedBox(height: 16),
    ];

    if (family.borrowed) {
      children.addAll([
        Center(child: Text(word, textDirection: TextDirection.rtl,
            style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold))),
        const SizedBox(height: 8),
        const Text('Borrowed word: no Arabic root',
            style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF92400E))),
        if (family.noteEn != null) Text(family.noteEn!, style: const TextStyle(fontSize: 13)),
      ]);
    } else {
      children.addAll([
        Directionality(
          textDirection: TextDirection.rtl,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              for (final letter in family.letters)
                Container(
                  width: 56, height: 56, margin: const EdgeInsets.symmetric(horizontal: 4),
                  alignment: Alignment.center,
                  color: _plum,
                  child: Text(letter, style: const TextStyle(fontSize: 30, fontWeight: FontWeight.bold, color: _gold)),
                ),
            ],
          ),
        ),
        if (family.coreMeaningEn != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text('Core idea: ${family.coreMeaningEn}', textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
          ),
        if (family.noteEn != null)
          Text(family.noteEn!, textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
        const SizedBox(height: 16),
        Stack(
          children: [
            Positioned(
              right: 0, top: 0, bottom: 0,
              child: Container(width: 3, color: _gold),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (family.lessonWords.isNotEmpty) ...[
                  _heading(Icons.menu_book_rounded, 'IN YOUR LESSONS', _emerald),
                  for (final w in family.lessonWords)
                    _wordTile(
                      wordAr: w.wordAr,
                      meaning: w.meaningEn,
                      subtitle: [
                        if (w.grade != null) 'Class ${w.grade}',
                        if (w.term != null) 'Term ${w.term}',
                        w.lessonTitleEn,
                      ].join(' · '),
                      accent: _emerald,
                    ),
                ],
                if (family.family.isNotEmpty) ...[
                  _heading(Icons.auto_awesome_rounded, 'MORE WORDS FROM THIS ROOT', _violet),
                  for (final w in family.family)
                    _wordTile(
                      wordAr: w.wordAr,
                      meaning: w.meaningEn,
                      subtitle: [_kindLabels[w.kind] ?? 'Related word', if (w.pattern != null) 'pattern ${w.pattern}']
                          .join(' · '),
                      accent: _violet,
                    ),
                  const Padding(
                    padding: EdgeInsets.only(right: 16),
                    child: Text('Suggested by AI and checked to contain the root letters. Not yet reviewed by a teacher.',
                        style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                  ),
                ],
                if (family.familySource == 'unavailable')
                  const Text('More words from this root will appear here soon.',
                      style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
              ],
            ),
          ],
        ),
      ]);
    }

    return ListView(
      controller: controller,
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 32),
      children: children,
    );
  }
}

import 'package:flutter/material.dart';

import '../api_service.dart';
import '../playback_words.dart';
import '../tashkeel.dart';

/// Arabic–English matching highlights (POST /api/curriculum/alignments): which words of a
/// sentence match which words of its translation. Word indexes count whitespace-separated words.

class AlignmentChunk {
  final List<int> ar;
  final List<int> en;

  const AlignmentChunk(this.ar, this.en);

  static List<AlignmentChunk>? listFromJson(Object? json) {
    if (json is! List || json.isEmpty) return null;
    final chunks = <AlignmentChunk>[];
    for (final item in json) {
      if (item is! Map) return null;
      final ar =
          (item['ar'] as List?)?.whereType<int>().toList() ?? const <int>[];
      final en =
          (item['en'] as List?)?.whereType<int>().toList() ?? const <int>[];
      if (ar.isEmpty || en.isEmpty) return null;
      chunks.add(AlignmentChunk(ar, en));
    }
    return chunks;
  }
}

List<String> splitWords(String text) =>
    text.split(RegExp(r'\s+')).where((w) => w.isNotEmpty).toList();

/// Alignments fetched so far. Widgets rebuild on [revision] when new ones arrive.
class AlignmentStore {
  AlignmentStore._();

  static final ValueNotifier<int> revision = ValueNotifier<int>(0);
  static final Map<String, List<AlignmentChunk>> _known = {};
  static final Set<String> _requested = {};

  static String _key(String ar, String en) => '${ar.trim()}\u0000${en.trim()}';

  static List<AlignmentChunk>? lookup(String ar, String en) =>
      _known[_key(ar, en)];

  static final Set<String> _requestedPages = {};

  /// Fetches the matches for a textbook page's lines (signed-in users); true if any arrived.
  static Future<bool> requestPage(
    ApiService api,
    int pdfPage,
    String? editionId, {
    String? token,
  }) async {
    final pageKey = '$editionId/$pdfPage';
    if (!_requestedPages.add(pageKey)) return false;
    try {
      final data = await api.get(
        '/api/curriculum/page-alignments/$pdfPage',
        query: {'edition_id': ?editionId},
        token: token,
        timeout: const Duration(seconds: 45),
      );
      final lines = data is Map ? data['lines'] : null;
      if (lines is! List) return false;
      var added = false;
      for (final line in lines.whereType<Map>()) {
        final chunks = AlignmentChunk.listFromJson(line['chunks']);
        final ar = line['ar']?.toString() ?? '';
        final en = line['en']?.toString() ?? '';
        if (chunks != null && ar.isNotEmpty && en.isNotEmpty) {
          _known[_key(ar, en)] = chunks;
          added = true;
        }
      }
      if (added) revision.value++;
      return added;
    } catch (_) {
      _requestedPages.remove(pageKey);
      return false;
    }
  }

  /// Fetches alignments for pairs not yet asked about in this session; true if any arrived.
  static Future<bool> request(
    ApiService api,
    List<MapEntry<String, String>> pairs,
  ) async {
    final wanted = <MapEntry<String, String>>[];
    for (final p in pairs) {
      final key = _key(p.key, p.value);
      if (p.key.trim().isEmpty || p.value.trim().isEmpty || _requested.contains(key)) {
        continue;
      }
      _requested.add(key);
      wanted.add(p);
    }
    if (wanted.isEmpty) return false;
    final batch = wanted.take(40).toList();
    try {
      final data = await api.post(
        '/api/curriculum/alignments',
        body: {
          'pairs': [
            for (final p in batch) {'ar': p.key, 'en': p.value},
          ],
        },
        timeout: const Duration(seconds: 30),
      );
      final list = data is Map ? data['alignments'] : null;
      if (list is! List) return false;
      var added = false;
      for (var i = 0; i < batch.length && i < list.length; i++) {
        final chunks = AlignmentChunk.listFromJson(list[i]);
        if (chunks != null) {
          _known[_key(batch[i].key, batch[i].value)] = chunks;
          added = true;
        }
      }
      if (added) revision.value++;
      return added;
    } catch (_) {
      // No highlighting is the fallback; let a later visit try again.
      for (final p in batch) {
        _requested.remove(_key(p.key, p.value));
      }
      return false;
    }
  }
}

/// An Arabic sentence above its English translation; tapping a word on either side
/// highlights the matching words on both.
class AlignedSentenceView extends StatefulWidget {
  final String ar;
  final String en;
  final List<AlignmentChunk> chunks;
  final void Function(String word)? onVocalize;
  final TextStyle? arStyle;
  final bool showNote;

  const AlignedSentenceView({
    super.key,
    required this.ar,
    required this.en,
    required this.chunks,
    this.onVocalize,
    this.arStyle,
    this.showNote = true,
  });

  @override
  State<AlignedSentenceView> createState() => _AlignedSentenceViewState();
}

class _AlignedSentenceViewState extends State<AlignedSentenceView> {
  int? _active;

  static const _highlight = Color(0xFFE0F2FE);
  static const _highlightBorder = Color(0xFF0284C7);
  static const _playing = Color(0xFFFDE68A);
  static const _playingBorder = Color(0xFFD97706);

  int _chunkOfAr(int i) => widget.chunks.indexWhere((c) => c.ar.contains(i));
  int _chunkOfEn(int i) => widget.chunks.indexWhere((c) => c.en.contains(i));

  Widget _word(
    String text,
    bool matched,
    VoidCallback? onTap,
    TextStyle style, {
    bool arabic = false,
    bool playing = false,
  }) {
    final lit = playing && !matched;
    return InkWell(
      borderRadius: BorderRadius.circular(6),
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: arabic ? 4 : 2, vertical: 1),
        decoration: BoxDecoration(
          color: matched ? _highlight : (lit ? _playing : Colors.transparent),
          borderRadius: BorderRadius.circular(6),
          border: Border(
            bottom: BorderSide(
              color: matched
                  ? _highlightBorder
                  : lit
                  ? _playingBorder
                  : (onTap != null && !arabic
                        ? const Color(0xFFCBD5E1)
                        : Colors.transparent),
              width: matched || lit ? 2 : 1,
            ),
          ),
        ),
        child: Text(
          text,
          style: matched
              ? style.copyWith(color: const Color(0xFF0C4A6E))
              : style,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final current =
        _active != null && _active! >= 0 && _active! < widget.chunks.length
        ? widget.chunks[_active!]
        : null;
    final arWords = splitWords(widget.ar);
    final enWords = splitWords(widget.en);
    final arStyle =
        widget.arStyle ??
        const TextStyle(
          fontSize: 17,
          fontWeight: FontWeight.bold,
          color: Color(0xFF1E293B),
          height: 1.8,
        );
    const enStyle = TextStyle(
      fontSize: 13,
      color: Color(0xFF475569),
      height: 1.5,
    );

    return ValueListenableBuilder<SpokenWord?>(
      valueListenable: PlaybackProgress.notifier,
      builder: (context, spoken, _) {
        // While this sentence plays, the spoken Arabic word and its English match light up.
        final spokenIndex = spoken?.indexIn(widget.ar) ?? -1;
        final playingChunk = spokenIndex >= 0 ? _chunkOfAr(spokenIndex) : -1;
        final playing = playingChunk >= 0 ? widget.chunks[playingChunk] : null;
        return ValueListenableBuilder<bool>(
          valueListenable: TashkeelState.notifier,
          builder: (context, _, _) => Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Directionality(
                textDirection: TextDirection.rtl,
                child: Wrap(
                  spacing: 2,
                  runSpacing: 4,
                  children: [
                    for (var i = 0; i < arWords.length; i++)
                      _word(
                        TashkeelState.display(arWords[i]),
                        current?.ar.contains(i) ?? false,
                        () {
                          setState(() => _active = _chunkOfAr(i));
                          widget.onVocalize?.call(
                            arWords[i].replaceAll(
                              RegExp(r'[؟!\.,،؛:\x27"()\[\]\-—]'),
                              '',
                            ),
                          );
                        },
                        arStyle,
                        arabic: true,
                        playing: i == spokenIndex,
                      ),
                  ],
                ),
              ),
              const Divider(height: 20),
              Wrap(
                spacing: 3,
                runSpacing: 4,
                children: [
                  for (var i = 0; i < enWords.length; i++)
                    _word(
                      enWords[i],
                      current?.en.contains(i) ?? false,
                      _chunkOfEn(i) >= 0
                          ? () => setState(() => _active = _chunkOfEn(i))
                          : null,
                      enStyle,
                      playing: playing?.en.contains(i) ?? false,
                    ),
                ],
              ),
              if (widget.showNote) ...[
                const SizedBox(height: 4),
                const Text(
                  'Tap a word to see its match. Matches suggested by AI.',
                  style: TextStyle(fontSize: 10, color: Color(0xFF94A3B8)),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}

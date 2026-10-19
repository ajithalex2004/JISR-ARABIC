import 'package:flutter/foundation.dart';

/// Which word of a sentence is being spoken, for word-by-word highlighting while audio plays.
///
/// The cloud voice gives no word timings, so the position is estimated from playback progress:
/// each word gets time in proportion to its letters, with a short pause after punctuation.
/// Mirrors frontend/src/services/playbackWords.ts.

final RegExp _marks = RegExp(r'[ً-ٰٟـ]');
final RegExp _letters = RegExp(r'[\p{L}\p{N}]', unicode: true);
final RegExp _pause = RegExp(r'[.،,؛;:؟?!]$');

List<String> playbackWords(String text) => text.split(RegExp(r'\s+')).where((w) => w.isNotEmpty).toList();

int _letterCount(String word) => _letters.allMatches(word.replaceAll(_marks, '')).length;

/// Index of the word being spoken at [position] of [duration], or -1 before it starts.
int estimateWordIndex(List<String> words, Duration position, Duration duration) {
  if (words.isEmpty || duration <= Duration.zero || position < Duration.zero) return -1;
  final total = duration.inMilliseconds / 1000.0;
  final at = position.inMilliseconds / 1000.0;
  // Synthesized clips start and end with a little silence.
  final lead = total * 0.05 < 0.12 ? total * 0.05 : 0.12;
  final tail = total * 0.05 < 0.15 ? total * 0.05 : 0.15;
  final span = total - lead - tail;
  final progress = ((at - lead) / (span < 0.01 ? 0.01 : span)).clamp(0.0, 1.0);
  final weights = [for (final w in words) (_letterCount(w) < 1 ? 1 : _letterCount(w)) + (_pause.hasMatch(w) ? 2 : 0)];
  var elapsed = progress * weights.fold<int>(0, (a, b) => a + b);
  for (var i = 0; i < weights.length; i++) {
    if (elapsed < weights[i]) return i;
    elapsed -= weights[i];
  }
  return words.length - 1;
}

/// Word index for a character offset into [text] (device speech progress callbacks).
int wordIndexAtChar(String text, int charIndex) {
  var index = -1;
  var inWord = false;
  for (var i = 0; i < text.length && i <= charIndex; i++) {
    final isSpace = text[i].trim().isEmpty;
    if (!isSpace && !inWord) index++;
    inWord = !isSpace;
  }
  return index < 0 ? 0 : index;
}

String _normalize(String word) => _letters.allMatches(word.replaceAll(_marks, '')).map((m) => m.group(0)).join();

/// The spoken word's index within [text] when [text] is the played text or part of it
/// (a line of a played paragraph); -1 otherwise. Punctuation-only words are skipped on both sides.
int localWordIndex(String playedText, int playedIndex, String text) {
  if (playedIndex < 0 || playedText.isEmpty || text.isEmpty) return -1;
  final played = [
    for (final (i, w) in playbackWords(playedText).indexed)
      if (_normalize(w).isNotEmpty) (key: _normalize(w), i: i),
  ];
  final own = [
    for (final (i, w) in playbackWords(text).indexed)
      if (_normalize(w).isNotEmpty) (key: _normalize(w), i: i),
  ];
  if (own.isEmpty || own.length > played.length) return -1;
  final spoken = played.indexWhere((w) => w.i >= playedIndex);
  if (spoken < 0) return -1;
  for (var start = 0; start + own.length <= played.length; start++) {
    var same = true;
    for (var k = 0; k < own.length && same; k++) {
      same = played[start + k].key == own[k].key;
    }
    if (same) {
      final offset = spoken - start;
      return offset >= 0 && offset < own.length ? own[offset].i : -1;
    }
  }
  return -1;
}

/// The text being spoken and the position of the spoken word in it.
class SpokenWord {
  final String text;
  final int index;

  const SpokenWord(this.text, this.index);

  /// The spoken word's index within [own], or -1 (see [localWordIndex]).
  int indexIn(String own) => localWordIndex(text, index, own);
}

/// Shared playback position; null when nothing is playing.
class PlaybackProgress {
  PlaybackProgress._();

  static final ValueNotifier<SpokenWord?> notifier = ValueNotifier<SpokenWord?>(null);

  static void update(String text, int index) {
    final current = notifier.value;
    if (current != null && current.text == text && current.index == index) return;
    notifier.value = SpokenWord(text, index);
  }

  static void clear() => notifier.value = null;
}

String _clean(String word) => word.replaceAll(RegExp(r'[؟!\.,،؛:\x27"()\[\]\-—/\\«»<>]'), '').trim();

/// Whether word [index] (of the whitespace-separated words of [text]) is being spoken.
/// With no playback position yet, falls back to matching [activeWord], the first word played.
bool isSpokenWord(SpokenWord? spoken, String text, int index, String word, String activeWord) {
  if (spoken != null) {
    final local = spoken.indexIn(text);
    if (local >= 0) return local == index;
    final played = playbackWords(spoken.text);
    // A single word played on its own (a tapped word) lights up wherever it appears.
    return played.length == 1 && _clean(word).isNotEmpty && _clean(word) == _clean(played.first);
  }
  final clean = _clean(word);
  return activeWord.isNotEmpty && clean.isNotEmpty && (clean == activeWord || word.contains(activeWord));
}

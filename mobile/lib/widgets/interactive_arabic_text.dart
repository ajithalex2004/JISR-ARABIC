import 'dart:async';

import 'package:flutter/material.dart';
import '../api_service.dart';
import '../arabic_dict.dart';
import '../arab_english_service.dart';
import '../tashkeel.dart';

/// Normalize Arabic text by removing tashkeel diacritics, punctuation, and unifying Alef variants.
String normalizeArabic(String text) {
  if (text.isEmpty) return '';
  return text
      .replaceAll(RegExp(r'[\u064B-\u065F\u0670\u0640]'), '')
      .replaceAll(RegExp(r'[؟!\.,،؛:\x27"()\[\]\-—/\\«»<>]'), '')
      .replaceAll(RegExp(r'[إأآ]'), 'ا')
      .trim();
}

/// Lookup Arabic word translation with root stemming, prefix stripping, and suffix stripping.
String lookupArabicWord(String rawWord, [int depth = 0]) {
  String clean = rawWord.replaceAll(RegExp(r'[\u064B-\u065F\u0670\u0640]'), '');
  clean = clean.replaceAll(RegExp(r'[؟!\.,،؛:\x27"()\[\]\-—/\\«»<>]'), '').trim();
  if (clean.isEmpty) return '';

  if (kArabicMobileDict.containsKey(clean)) {
    return kArabicMobileDict[clean]!;
  }

  final norm = normalizeArabic(clean);
  if (kArabicMobileDict.containsKey(norm)) {
    return kArabicMobileDict[norm]!;
  }

  if (depth > 2) return '';

  const suffixes = [
    'ها', 'هم', 'هما', 'هن', 'كم', 'نا', 'ي', 'ك', 'ه', 'ون', 'ين', 'ات', 'ة', 'ان', 'تان', 'تين', 'ية', 'ا'
  ];
  for (final s in suffixes) {
    if (norm.endsWith(s) && norm.length > s.length + 2) {
      final stem = norm.substring(0, norm.length - s.length);
      if (stem.endsWith('ت')) {
        final stemTaa = '${stem.substring(0, stem.length - 1)}ة';
        if (kArabicMobileDict.containsKey(stemTaa)) {
          return kArabicMobileDict[stemTaa]!;
        }
        final subTaa = lookupArabicWord(stemTaa, depth + 1);
        if (subTaa.isNotEmpty && !subTaa.contains(RegExp(r'[\u0600-\u06FF]'))) {
          return subTaa;
        }
      }
      if (kArabicMobileDict.containsKey(stem)) {
        return kArabicMobileDict[stem]!;
      }
      final subStem = lookupArabicWord(stem, depth + 1);
      if (subStem.isNotEmpty && !subStem.contains(RegExp(r'[\u0600-\u06FF]'))) {
        return subStem;
      }
    }
  }

  const prefixes = [
    MapEntry('ولل', 'and for the'),
    MapEntry('وبال', 'and with the'),
    MapEntry('وكال', 'and like the'),
    MapEntry('وفال', 'and so the'),
    MapEntry('وال', 'and the'),
    MapEntry('فال', 'so the'),
    MapEntry('بال', 'with the'),
    MapEntry('كال', 'like the'),
    MapEntry('لل', 'for the'),
    MapEntry('ال', 'the'),
    MapEntry('و', 'and'),
    MapEntry('ف', 'so'),
    MapEntry('ب', 'with'),
    MapEntry('ل', 'for'),
    MapEntry('ك', 'like'),
    MapEntry('س', 'will'),
  ];

  for (final p in prefixes) {
    if (norm.startsWith(p.key) && norm.length > p.key.length + 2) {
      final rem = norm.substring(p.key.length);
      if (kArabicMobileDict.containsKey(rem)) {
        final baseTrans = kArabicMobileDict[rem]!;
        if (baseTrans.toLowerCase().startsWith('the ') && p.value.endsWith('the')) {
          return '${p.value.replaceAll(RegExp(r'the$'), '').trim()} $baseTrans'.trim();
        }
        return '${p.value} $baseTrans'.trim();
      }
      final subRem = lookupArabicWord(rem, depth + 1);
      if (subRem.isNotEmpty && !subRem.contains(RegExp(r'[\u0600-\u06FF]'))) {
        return '${p.value} $subRem'.trim();
      }
    }
  }

  // Not in the dictionary: an empty result tells callers to use WordGloss, and makes
  // the affix-stripping recursion above treat it as a miss.
  return '';
}

/// Meanings for words missing from [kArabicMobileDict], fetched from the backend
/// (/api/curriculum/word-gloss, which uses the surrounding passage as context).
/// Widgets rebuild on [revision] so a tooltip fills in once its meaning arrives.
class WordGloss {
  static const loadingText = 'Looking up meaning…';
  static const unavailableText = 'Meaning not available';

  static final ValueNotifier<int> revision = ValueNotifier<int>(0);
  static final Map<String, String?> _results = {};
  static final Map<String, Future<String?>> _pending = {};
  static ApiService api = ApiService();

  static String _clean(String word) =>
      word.replaceAll(RegExp(r'[؟!\.,،؛:\x27"()\[\]\-—/\\«»<>]'), '').trim();

  static String _key(String word, String context) =>
      '${_clean(word)}\u0000${context.replaceAll(RegExp(r'\s+'), ' ').trim()}';

  /// Text to show right now: dictionary meaning, fetched meaning, or a status message.
  static String meaning(String word, String context) {
    final local = lookupArabicWord(word);
    if (local.isNotEmpty) return local;
    final key = _key(word, context);
    if (_results.containsKey(key)) return _results[key] ?? unavailableText;
    return loadingText;
  }

  /// Fetches the meaning if the dictionary lacks it; resolves to the text to display.
  static Future<String> ensure(String word, String context) async {
    final local = lookupArabicWord(word);
    if (local.isNotEmpty) return local;
    final key = _key(word, context);
    if (_results.containsKey(key)) return _results[key] ?? unavailableText;

    final ctx = context.replaceAll(RegExp(r'\s+'), ' ').trim();
    final request = _pending[key] ??= _fetch(
      _clean(word),
      ctx.length > 300 ? ctx.substring(0, 300) : ctx,
    );
    final result = await request;
    _pending.remove(key);
    _results[key] = result;
    revision.value++;
    if (result == null) {
      // Don't pin a network failure for the whole session; a later tap can retry.
      Timer(const Duration(seconds: 30), () => _results.remove(key));
    }
    return result ?? unavailableText;
  }

  static Future<String?> _fetch(String word, String context) async {
    try {
      final data = await api.get(
        '/api/curriculum/word-gloss',
        query: {'word': word, if (context.isNotEmpty) 'context': context},
        timeout: const Duration(seconds: 10),
      );
      final translation = data is Map ? (data['translation'] ?? '').toString().trim() : '';
      if (translation.isEmpty || RegExp(r'[\u0600-\u06FF]').hasMatch(translation)) return null;
      return translation;
    } catch (_) {
      return null;
    }
  }
}

/// A shared, interactive Arabic text widget that parses Arabic text into individual
/// word chips with rich tooltips (meaning + "Click to Pronounce") and native audio pronunciation on tap.
class InteractiveArabicText extends StatelessWidget {
  final String text;
  final TextStyle? style;
  final TextAlign textAlign;
  final Function(String)? onVocalize;
  final String activeWord;
  final bool showChips;
  final bool showSnackBarOnTap;

  const InteractiveArabicText({
    super.key,
    required this.text,
    this.style,
    this.textAlign = TextAlign.right,
    this.onVocalize,
    this.activeWord = '',
    this.showChips = true,
    this.showSnackBarOnTap = true,
  });

  @override
  Widget build(BuildContext context) {
    if (text.trim().isEmpty) return const SizedBox.shrink();

    final words = text.split(RegExp(r'\s+')).where((w) => w.trim().isNotEmpty).toList();

    return ValueListenableBuilder<int>(
      valueListenable: WordGloss.revision,
      builder: (context, _, _) => ValueListenableBuilder<bool>(
      valueListenable: TashkeelState.notifier,
      builder: (context, _, _) => ValueListenableBuilder<bool>(
      valueListenable: ArabEnglishState.notifier,
      builder: (context, isArabEnglishOn, _) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: Wrap(
        alignment: textAlign == TextAlign.right
            ? WrapAlignment.end
            : textAlign == TextAlign.center
                ? WrapAlignment.center
                : WrapAlignment.start,
        crossAxisAlignment: WrapCrossAlignment.center,
        spacing: 3,
        runSpacing: 5,
        children: words.map((word) {
          final cleanWord = word.replaceAll(RegExp(r'[؟!\.,،؛:\x27"()\[\]\-—/\\«»<>]'), '').trim();
          final translation = WordGloss.meaning(word, text);
          final isPlaying = activeWord.isNotEmpty &&
              cleanWord.isNotEmpty &&
              (cleanWord == activeWord || word.contains(activeWord));

          final arabEn = ArabEnglishHelper.transliterate(cleanWord);
          final tooltipMessage = cleanWord.isNotEmpty
              ? (ArabEnglishState.isEnabled && arabEn.isNotEmpty
                  ? '$cleanWord\n🗣️ $arabEn\n🇬🇧 $translation\n\n🔊 Click to Pronounce (انقر للاستماع)'
                  : '$cleanWord\n🇬🇧 $translation\n\n🔊 Click to Pronounce (انقر للاستماع)')
              : word;

          return Tooltip(
            message: tooltipMessage,
            onTriggered: () => WordGloss.ensure(word, text),
            preferBelow: false,
            verticalOffset: 16,
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF2A1548),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFB197FC), width: 1.2),
              boxShadow: const [
                BoxShadow(color: Colors.black38, blurRadius: 10, offset: Offset(0, 4)),
              ],
            ),
            textStyle: const TextStyle(
              color: Colors.white,
              fontSize: 12.5,
              fontWeight: FontWeight.bold,
              height: 1.4,
            ),
            child: InkWell(
              borderRadius: BorderRadius.circular(8),
              onTap: () {
                if (cleanWord.isNotEmpty && onVocalize != null) {
                  onVocalize!(cleanWord);
                }
                if (showSnackBarOnTap && cleanWord.isNotEmpty) {
                  WordGloss.ensure(word, text).then((translation) {
                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context).hideCurrentSnackBar();
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      backgroundColor: const Color(0xFF2A1548),
                      duration: const Duration(milliseconds: 2200),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                        side: const BorderSide(color: Color(0xFFB197FC), width: 1.2),
                      ),
                      content: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.volume_up, color: Color(0xFFFDE68A), size: 18),
                              const SizedBox(width: 8),
                              Flexible(
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    if (ArabEnglishState.isEnabled && arabEn.isNotEmpty)
                                      Text(
                                        '🗣️ $arabEn',
                                        style: const TextStyle(
                                          color: Color(0xFFFDE68A),
                                          fontWeight: FontWeight.w700,
                                          fontSize: 11.5,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    Text(
                                      translation,
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 13,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(width: 8),
                          Text(
                            word,
                            style: const TextStyle(
                              color: Color(0xFFFDE68A),
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                  });
                }
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                padding: showChips
                    ? const EdgeInsets.symmetric(horizontal: 5, vertical: 2)
                    : const EdgeInsets.symmetric(horizontal: 2, vertical: 1),
                decoration: BoxDecoration(
                  color: isPlaying
                      ? const Color(0xFFFDE68A)
                      : showChips
                          ? const Color(0xFFF8FAFC)
                          : Colors.transparent,
                  borderRadius: BorderRadius.circular(7),
                  border: showChips
                      ? Border.all(
                          color: isPlaying
                              ? const Color(0xFFF59E0B)
                              : const Color(0xFFE2E8F0),
                          width: 1,
                        )
                      : null,
                  boxShadow: isPlaying
                      ? const [
                          BoxShadow(
                            color: Color(0x33D97706),
                            blurRadius: 4,
                            offset: Offset(0, 1),
                          )
                        ]
                      : null,
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Text(
                      TashkeelState.display(word),
                      style: (style ??
                              const TextStyle(
                                fontSize: 13.5,
                                height: 1.5,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF0F172A),
                              ))
                          .copyWith(
                        color: isPlaying
                            ? const Color(0xFF78350F)
                            : (style?.color ?? const Color(0xFF0F172A)),
                        fontWeight: isPlaying ? FontWeight.w900 : style?.fontWeight,
                      ),
                    ),
                    if (isArabEnglishOn && arabEn.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 1.5),
                        child: Text(
                          arabEn,
                          style: TextStyle(
                            fontSize: ((style?.fontSize ?? 13.5) * 0.65).clamp(9.0, 11.5),
                            fontWeight: FontWeight.w700,
                            color: isPlaying ? const Color(0xFF78350F) : const Color(0xFF4338CA),
                            height: 1.1,
                            letterSpacing: 0.15,
                          ),
                          textDirection: TextDirection.ltr,
                        ),
                      ),
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  },
),
),
);
  }
}

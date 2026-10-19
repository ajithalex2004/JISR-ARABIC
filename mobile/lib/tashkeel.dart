import 'package:flutter/material.dart';

// Harakat, tanween, shadda, sukun, extra combining vowels, superscript alef and Quranic
// annotation marks. Hamza/madda combining marks (U+0653–U+0655) are spelling, so they stay.
final RegExp _tashkeel = RegExp(
  r'[ً-ْٖ-ٰٟۖ-ۜ۟-۪ۤۧۨ-ۭ]',
);

/// Removes vowel marks for display; letters, hamza, punctuation and spacing are untouched.
String stripTashkeel(String text) => text.replaceAll(_tashkeel, '');

/// Whether Arabic is shown with its vowel marks. Off lets a child practise reading Arabic
/// as it is usually written; audio and tooltips keep the vowelled text, so a tap reveals it.
class TashkeelState {
  TashkeelState._();

  static final ValueNotifier<bool> notifier = ValueNotifier<bool>(true);

  static bool get showVowels => notifier.value;

  static void toggle() => notifier.value = !notifier.value;

  /// [text] as it should be displayed under the current setting.
  static String display(String text) => notifier.value ? text : stripTashkeel(text);
}

/// Pill switch for vowel marks. The label demonstrates the setting: vowelled when on.
class TashkeelToggleSwitch extends StatelessWidget {
  const TashkeelToggleSwitch({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: TashkeelState.notifier,
      builder: (context, isOn, _) {
        const activeColor = Color(0xFF047857);
        return Tooltip(
          message: isOn
              ? 'Vowel marks: ON. Turn off to practise reading without them.'
              : 'Vowel marks: OFF. Tap a word to reveal its vowels.',
          child: Semantics(
            toggled: isOn,
            label: 'Show vowel marks',
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: TashkeelState.toggle,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isOn ? activeColor.withValues(alpha: 0.15) : const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isOn ? activeColor : const Color(0xFFCBD5E1),
                    width: 1.2,
                  ),
                ),
                child: Text(
                  isOn ? 'تَشْكِيل ON' : 'تشكيل OFF',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: isOn ? activeColor : const Color(0xFF64748B),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

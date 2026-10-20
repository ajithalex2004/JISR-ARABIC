import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';

/// First sign-in on a phone: check it can type and speak Arabic, and guide the student to turn
/// it on in Settings when it can't. The keyboard can't be listed by apps, so the student types a
/// word in a test box; the voice is detected from the speech engine's languages.
/// Mirrors frontend/src/services/arabicSetup.ts.

const String arabicSetupDoneKey = 'arabic_setup_done';
const String arabicSetupSnoozeKey = 'arabic_setup_snooze_until';
const Duration arabicSetupSnooze = Duration(days: 3);

final RegExp _arabicLetter = RegExp(r'[ء-ي]');

bool typedArabic(String text) => _arabicLetter.hasMatch(text);

/// Offer the setup: never finished on this device, and not put off recently.
bool shouldOfferArabicSetup({String? done, String? snoozeUntil, DateTime? now}) {
  if (done != null && done.isNotEmpty) return false;
  final until = DateTime.tryParse(snoozeUntil ?? '');
  return until == null || (now ?? DateTime.now()).isAfter(until);
}

/// Whether the phone's speech engine has an Arabic voice.
Future<bool> hasArabicTtsVoice(FlutterTts tts) async {
  try {
    final languages = await tts.getLanguages;
    if (languages is List && languages.any((l) => l.toString().toLowerCase().startsWith('ar'))) return true;
    for (final code in const ['ar-SA', 'ar-AE', 'ar']) {
      if (await tts.isLanguageAvailable(code) == true) return true;
    }
  } catch (_) {}
  return false;
}

class ArabicSetupGuide {
  final String name;
  final List<String> keyboard;
  final String switchKeys;
  final List<String> voice;

  const ArabicSetupGuide(this.name, this.keyboard, this.switchKeys, this.voice);
}

const ArabicSetupGuide androidGuide = ArabicSetupGuide(
  'Android',
  [
    'Open Settings → System → Languages & input → On-screen keyboard → Gboard → Languages.',
    'Tap Add keyboard, choose Arabic, then Done.',
  ],
  'On the keyboard, tap the 🌐 globe key (or hold the space bar) to switch to Arabic.',
  [
    'Open Settings → System → Languages & input → Text-to-speech output.',
    'Tap ⚙ next to Speech Services by Google → Install voice data → Arabic, and download it.',
  ],
);

const ArabicSetupGuide iosGuide = ArabicSetupGuide(
  'iPhone / iPad',
  [
    'Open Settings → General → Keyboard → Keyboards.',
    'Tap Add New Keyboard… and choose Arabic.',
  ],
  'On the keyboard, tap the 🌐 globe key to switch to Arabic.',
  [
    'Open Settings → Accessibility → Spoken Content → Voices.',
    'Tap Arabic and download a voice (e.g. Majed).',
  ],
);

/// Pops `true` when the student finished ("All set"), `false` for "Remind me later".
class ArabicSetupDialog extends StatefulWidget {
  final bool ios;
  final Future<bool> voiceCheck;
  final VoidCallback? onTestVoice;

  const ArabicSetupDialog({super.key, required this.ios, required this.voiceCheck, this.onTestVoice});

  @override
  State<ArabicSetupDialog> createState() => _ArabicSetupDialogState();
}

class _ArabicSetupDialogState extends State<ArabicSetupDialog> {
  final _typed = TextEditingController();
  bool? _voice;

  @override
  void initState() {
    super.initState();
    widget.voiceCheck.then((found) {
      if (mounted) setState(() => _voice = found);
    });
  }

  @override
  void dispose() {
    _typed.dispose();
    super.dispose();
  }

  Widget _steps(List<String> steps) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (var i = 0; i < steps.length; i++)
            Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Text('${i + 1}. ${steps[i]}', style: const TextStyle(fontSize: 13)),
            ),
        ],
      );

  Widget _section({required bool ok, required String title, required List<Widget> children}) => Container(
        margin: const EdgeInsets.only(top: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: ok ? const Color(0xFFECFDF5) : Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: ok ? const Color(0xFF6EE7B7) : const Color(0xFFE2E8F0)),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Row(children: [
            Icon(ok ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded,
                color: ok ? const Color(0xFF059669) : const Color(0xFFD97706), size: 20),
            const SizedBox(width: 6),
            Expanded(child: Text(title, style: const TextStyle(fontWeight: FontWeight.bold))),
          ]),
          const SizedBox(height: 6),
          ...children,
        ]),
      );

  @override
  Widget build(BuildContext context) {
    final guide = widget.ios ? iosGuide : androidGuide;
    final keyboardOk = typedArabic(_typed.text);
    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 24),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Set up Arabic on this phone · جَهِّزِ العَرَبِيَّةَ',
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.w900)),
              const SizedBox(height: 4),
              Text(
                'To type your answers and hear Arabic clearly, your ${guide.name} needs an Arabic keyboard and voice. '
                'It takes two minutes.',
                style: const TextStyle(fontSize: 13, color: Color(0xFF475569)),
              ),
              _section(ok: keyboardOk, title: keyboardOk ? '1. Arabic keyboard · works!' : '1. Arabic keyboard', children: [
                if (!keyboardOk) ...[
                  _steps(guide.keyboard),
                  Text('Then: ${guide.switchKeys}', style: const TextStyle(fontSize: 13)),
                  const SizedBox(height: 8),
                ],
                TextField(
                  key: const Key('arabic-keyboard-test'),
                  controller: _typed,
                  textDirection: TextDirection.rtl,
                  onChanged: (_) => setState(() {}),
                  decoration: const InputDecoration(
                    labelText: 'Test it: switch to Arabic and type مرحبا',
                    border: OutlineInputBorder(),
                    isDense: true,
                  ),
                ),
                if (_typed.text.isNotEmpty && !keyboardOk)
                  const Padding(
                    padding: EdgeInsets.only(top: 4),
                    child: Text('Those are English letters. Switch your keyboard to Arabic first.',
                        style: TextStyle(fontSize: 12, color: Color(0xFF92400E))),
                  ),
              ]),
              _section(
                ok: _voice == true,
                title: _voice == true ? '2. Arabic voice · found!' : '2. Arabic voice (recommended)',
                children: [
                  if (_voice == null) const LinearProgressIndicator(),
                  if (_voice == false) ...[
                    const Text(
                      'No Arabic voice on this phone yet. Fahim uses the online Arabic voice meanwhile, '
                      'but a phone voice reads words instantly, even offline.',
                      style: TextStyle(fontSize: 13),
                    ),
                    const SizedBox(height: 6),
                    _steps(guide.voice),
                  ],
                  if (widget.onTestVoice != null)
                    Align(
                      alignment: Alignment.centerLeft,
                      child: TextButton.icon(
                        onPressed: widget.onTestVoice,
                        icon: const Icon(Icons.volume_up_rounded, size: 18),
                        label: const Text('Test the voice'),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 14),
              Wrap(
                alignment: WrapAlignment.end,
                spacing: 8,
                runSpacing: 8,
                children: [
                  OutlinedButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Remind me later')),
                  FilledButton(
                    onPressed: () => Navigator.of(context).pop(true),
                    child: Text(keyboardOk ? 'All set' : "I've done this"),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

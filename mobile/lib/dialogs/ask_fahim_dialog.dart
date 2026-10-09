import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../api_service.dart';
import '../arab_english_service.dart';

class AskFahimDialog extends StatefulWidget {
  final String contextLessonId;
  final String? childId;
  final String? token;
  final String initialMode; // 'text', 'voice', 'pdf', 'camera', 'exam'
  final bool isArabic;
  final Function(String text)? onVocalize;
  final String? initialFileName;
  final String? initialFileBase64;
  final String? initialFileType;

  const AskFahimDialog({
    super.key,
    this.contextLessonId = 'lesson_01_ball_games',
    this.childId,
    this.token,
    this.initialMode = 'text',
    this.isArabic = false,
    this.onVocalize,
    this.initialFileName,
    this.initialFileBase64,
    this.initialFileType,
  });

  @override
  State<AskFahimDialog> createState() => _AskFahimDialogState();
}

class _AskFahimDialogState extends State<AskFahimDialog> {
  final ApiService _api = ApiService();
  final ImagePicker _imagePicker = ImagePicker();
  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _speechInitialized = false;
  bool _isListening = false;
  final _ctrl = TextEditingController();
  final ScrollController _scrollCtrl = ScrollController();
  bool _isLoading = false;
  bool _isPicking = false;
  late String _activeMode;
  String? _attachedFileName;
  String? _attachmentType; // 'pdf', 'camera', 'gallery'
  String? _attachedBase64;
  String? _queuedPrompt;
  String? _queuedEnglish;

  // Question Paper Exam Assistant State (Gemini 2.0 Flash)
  bool _isSolvingPaper = false;
  Map<String, dynamic>? _solvedPaperData;
  String? _paperError;
  final _paperCtrl = TextEditingController();
  String _paperTitle = 'اختبار منتصف الفصل الأول - ألعاب الكرة والفروسية';
  String? _paperFileName;

  late final List<Map<String, dynamic>> _messages;
  FlutterTts? _fallbackTts;

  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  // STRICT PRIVACY GUARANTEE:
  // Voice notes, chat messages, and camera feed captures are transient (in-memory only)
  // and are NEVER saved to local storage or external databases. Only the uploaded PDF is persisted.
  Future<void> _loadPersistedPdfIfAvailable() async {
    try {
      final name = await _storage.read(key: 'saved_pdf_filename');
      final b64 = await _storage.read(key: 'saved_pdf_base64');
      if (name != null && b64 != null && mounted) {
        setState(() {
          _attachedFileName = name;
          _attachmentType = 'pdf';
          _attachedBase64 = b64;
          _paperFileName = name;
          _paperTitle = name.replaceAll(RegExp(r'\.pdf$', caseSensitive: false), '').replaceAll('_', ' ');
          if (_messages.isNotEmpty && _messages.first['role'] == 'fahim') {
            _messages[0] = {
              'role': 'fahim',
              'text_ar': 'أَهْلًا بِكَ مُجَدَّدًا! مَلَفُّ ($name) مَحْفُوظٌ وَجَاهِزٌ لِلْمُذَاكَرَةِ. يُمْكِنُكَ اخْتِيَارُ أَيِّ سُؤَالٍ رَئِيسٍ أَوْ فَرْعِيٍّ لِحَلِّهِ فَوْرِيًّا.',
              'text_en': 'Welcome back! Uploaded PDF ($name) is saved and ready. You can select any main question or sub-question to solve immediately.',
              'escalated': false,
            };
          }
        });
      }
    } catch (e) {
      debugPrint('Error reading persisted PDF: $e');
    }
  }

  Future<void> _savePersistedPdf(String name, String? b64) async {
    try {
      await _storage.write(key: 'saved_pdf_filename', value: name);
      if (b64 != null) {
        await _storage.write(key: 'saved_pdf_base64', value: b64);
      }
    } catch (e) {
      debugPrint('Error writing persisted PDF: $e');
    }
  }

  Future<void> _clearPersistedPdf() async {
    try {
      await _storage.delete(key: 'saved_pdf_filename');
      await _storage.delete(key: 'saved_pdf_base64');
    } catch (e) {
      debugPrint('Error clearing persisted PDF: $e');
    }
  }

  void _vocalize(String text) {
    final clean = text.trim();
    if (clean.isEmpty) return;
    if (widget.onVocalize != null) {
      widget.onVocalize!(clean);
      return;
    }
    try {
      _fallbackTts ??= FlutterTts();
      final hasArabic = RegExp(r'[\u0600-\u06FF]').hasMatch(clean);
      _fallbackTts!.setLanguage(hasArabic ? 'ar-SA' : 'en-US');
      _fallbackTts!.setSpeechRate(0.35);
      _fallbackTts!.speak(clean);
    } catch (_) {}
  }

  @override
  void initState() {
    super.initState();
    _activeMode = widget.initialMode;

    if (widget.initialFileName != null) {
      _attachedFileName = widget.initialFileName;
      _attachmentType = widget.initialFileType ?? 'pdf';
      _attachedBase64 = widget.initialFileBase64;
      _paperFileName = widget.initialFileName;
      _paperTitle = widget.initialFileName!.replaceAll(RegExp(r'\.pdf$', caseSensitive: false), '').replaceAll('_', ' ');
      if (widget.initialFileType == 'pdf' || widget.initialFileName!.toLowerCase().endsWith('.pdf')) {
        _savePersistedPdf(widget.initialFileName!, widget.initialFileBase64);
      }
    } else {
      _loadPersistedPdfIfAvailable();
    }

    _paperCtrl.text =
        'س1: استخرج الفكرة الرئيسة وأهم المفاهيم في هذا المستند.\nس2: حل الأسئلة والتمارين اللغوية الواردة بالتفصيل.\nس3: اشرح معاني المفردات وقواعد الإعراب.';

    _messages = [
      if (widget.initialFileName != null) ...[
        {
          'role': 'fahim',
          'text_ar': 'أَحْسَنْتَ! تَمَّ رَفْعُ وَتَحْلِيلُ مَلَفِّ (${widget.initialFileName}) بِنَجَاحٍ بالذكاء الاصطناعي. أستاذ فاهم جاهز للإجابة عن أسئلة هذا المستند مباشرة مع الترجمة الإنجليزية والشرح الكامل!',
          'text_en': 'Great! Successfully analyzed (${widget.initialFileName}) with AI. Ustadh Fahim is ready to answer questions from this document directly with English translations and full explanations!',
          'escalated': false,
        }
      ] else ...[
        {
          'role': 'fahim',
          'text_ar': _activeMode == 'voice'
              ? 'مَرْحَبًا بِكَ فِي الجَلْسَةِ الصَّوْتِيَّةِ! أَنَا مُعَلِّمُكَ (فَاهِم)، تَحَدَّثْ مَعِي وسَأُجِيبُكَ صَوْتِيًّا.'
              : (_activeMode == 'pdf'
                  ? 'أَهْلًا بِكَ! يُمْكِنُكَ رَفْعُ مَلَفِّ المِنْهَاجِ (PDF) لِتَلْخِيصِهِ أَوْ طَرْحِ الأَسْئِلَةِ حَوْلَهُ.'
                  : (_activeMode == 'camera'
                      ? 'أَهْلًا بِكَ! يُمْكِنُكَ الْتِقَاطُ صُورَةِ التَّمْرِينِ أَوِ الصَّفْحَةِ بِالكَمِيرَا لِحَلِّهَا فَوْرِيًّا.'
                      : (_activeMode == 'exam'
                          ? 'أَهْلًا بِكَ فِي مُسَاعِدِ الامْتِحَانَاتِ الذَّكِيِّ. يُمْكِنُكَ إِرْفَاقُ وَرَقَةِ الامْتِحَانِ أَوْ لَصْقُ الأَسْئِلَةِ لِحَلِّهَا فَوْرِيًّا بِالاعْتِمَادِ عَلَى مِنْهَاجِ الإِمَارَاتِ.'
                          : 'مَرْحَبًا بِكَ! أَنَا مُعَلِّمُكَ (فَاهِم). كَيْفَ أُسَاعِدُكَ فِي دَرْسِكَ أَوِ القَوَاعِدِ اليَوْمَ؟'))),
          'text_en': _activeMode == 'voice'
              ? 'Welcome to the Voice Tutor session! Speak with me and I will respond to you aloud.'
              : (_activeMode == 'pdf'
                  ? 'Welcome! You can upload a PDF textbook or worksheet to summarize and ask questions.'
                  : (_activeMode == 'camera'
                      ? 'Welcome! Snap a photo of your exercise or textbook page for instant solutions.'
                      : (_activeMode == 'exam'
                          ? 'Welcome to the Exam Paper Assistant. Attach or paste your exam questions for verified MoE solutions.'
                          : 'Hello! I am your conversational tutor, Ustadh Fahim. How can I assist you with your lesson or grammar today?'))),
          'escalated': false,
        }
      ]
    ];

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (widget.initialFileName != null) {
        _scrollToBottom();
        Future.delayed(const Duration(milliseconds: 350), () {
          if (mounted) {
            _send(
              widget.isArabic
                  ? 'أجب عن أسئلة المستند المرفق (${widget.initialFileName}) بالذكاء الاصطناعي مع الشرح'
                  : 'Answer the questions from the attached document (${widget.initialFileName}) using AI in detail with explanation',
              'Solve document questions with AI',
            );
          }
        });
      } else if (widget.initialMode == 'pdf') {
        _pickPdf();
      } else if (widget.initialMode == 'camera') {
        _pickCameraPhoto(ImageSource.camera);
      } else if (widget.initialMode == 'voice') {
        _toggleListening();
      }
    });
  }

  Future<void> _pickPdf() async {
    if (_isPicking) return;
    setState(() => _isPicking = true);
    try {
      final result = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'PDF'],
        withData: true,
        withReadStream: true,
        cancelUploadOnWindowBlur: false,
      );
      if (result != null && result.files.isNotEmpty) {
        final picked = result.files.first;
        Uint8List? bytes = picked.bytes;
        if (bytes == null && picked.readStream != null) {
          try {
            final builder = BytesBuilder();
            await for (final chunk in picked.readStream!) {
              builder.add(chunk);
            }
            bytes = builder.toBytes();
          } catch (streamErr) {
            debugPrint('Error reading pick stream in ask_fahim_dialog: $streamErr');
          }
        }
        if (bytes == null && picked.path != null && !kIsWeb) {
          final f = File(picked.path!);
          if (await f.exists()) {
            bytes = await f.readAsBytes();
          }
        }
        if (bytes != null && bytes.isNotEmpty) {
          final base64Str = base64Encode(bytes);
          await _savePersistedPdf(picked.name, base64Str);
          setState(() {
            _activeMode = 'pdf';
            _attachedFileName = picked.name;
            _attachmentType = 'pdf';
            _attachedBase64 = base64Str;
            _paperFileName = picked.name;
            _paperTitle = picked.name.replaceAll(RegExp(r'\.pdf$', caseSensitive: false), '').replaceAll('_', ' ');
            _messages.add({
              'role': 'fahim',
              'text_ar': 'أَحْسَنْتَ! تَمَّ رَفْعُ وَتَحْلِيلُ مَلَفِّ (${picked.name}) بِنَجَاحٍ بالذكاء الاصطناعي. أستاذ فاهم جاهز للإجابة عن أسئلة هذا المستند مباشرة مع الترجمة الإنجليزية والشرح الكامل!',
              'text_en': 'Great! Successfully analyzed (${picked.name}) with AI. Ustadh Fahim is ready to answer questions from this document directly with English translations and full explanations!',
              'escalated': false,
            });
          });
          _scrollToBottom();
          // Automatically start solving the attached document questions with AI
          Future.delayed(const Duration(milliseconds: 350), () {
            if (mounted) {
              _send(
                widget.isArabic
                    ? 'أجب عن أسئلة المستند المرفق (${picked.name}) بالتفصيل مع الشرح'
                    : 'Answer the questions from the attached document (${picked.name}) in detail with explanation',
                'Solve questions from document with AI',
              );
            }
          });
        }
      }
    } catch (e) {
      debugPrint('Error picking PDF: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(widget.isArabic ? 'تعذر اختيار ملف PDF: $e' : 'Failed to pick PDF: $e'),
            backgroundColor: Colors.red.shade800,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isPicking = false);
    }
  }

  Future<void> _pickCameraPhoto([ImageSource source = ImageSource.camera]) async {
    if (_isPicking) return;
    setState(() => _isPicking = true);
    try {
      final XFile? photo = await _imagePicker.pickImage(
        source: source,
        imageQuality: 85,
        maxWidth: 1600,
      );
      if (photo != null) {
        final bytes = await photo.readAsBytes();
        final base64Str = base64Encode(bytes);
        final name = photo.name.isNotEmpty
            ? photo.name
            : (source == ImageSource.camera ? 'صورة_الكاميرا.jpg' : 'صورة_المعرض.jpg');
        setState(() {
          _activeMode = 'camera';
          _attachedFileName = name;
          _attachmentType = source == ImageSource.camera ? 'camera' : 'gallery';
          _attachedBase64 = base64Str;
          _paperFileName = name;
          _messages.add({
            'role': 'fahim',
            'text_ar': 'رَائِعٌ! تَمَّ الْتِقَاطُ الصُّورَةِ وَمَسْحُهَا بِالذَّكَاءِ الاصْطِنَاعِيِّ. جَارٍ تَحْلِيلُ التَّمْرِينِ وَحَلُّهُ خُطْوَةً بِخُطْوَةٍ مَعَ التَّرْجَمَةِ الإِنْجِلِيزِيَّةِ...',
            'text_en': 'Great! Image captured and scanned with AI. Automatically analyzing and solving the exercise with English translation...',
            'escalated': false,
          });
        });
        _scrollToBottom();
        // Automatically start solving the camera feed without requiring user typing or prompting
        Future.delayed(const Duration(milliseconds: 350), () {
          if (mounted) {
            _send('حل هذا التمرين مع الشرح', 'Solve this exercise with explanation');
          }
        });
      }
    } catch (e) {
      debugPrint('Error taking photo: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(widget.isArabic ? 'تعذر استخدام الكاميرا/المعرض: $e' : 'Camera error: $e'),
            backgroundColor: Colors.red.shade800,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isPicking = false);
    }
  }

  void _showCameraOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                widget.isArabic ? 'اختر طريقة إرفاق الصورة' : 'Select Image Source',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF3F0FF),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.photo_camera_rounded, color: Color(0xFF6C5CE7)),
                ),
                title: Text(widget.isArabic ? 'التقاط صورة بالكاميرا الآن' : 'Take Photo with Camera'),
                subtitle: Text(widget.isArabic ? 'التقط صورة لصفحة الكتاب أو التمرين' : 'Snap textbook page or exercise'),
                onTap: () {
                  Navigator.of(ctx).pop();
                  _pickCameraPhoto(ImageSource.camera);
                },
              ),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.photo_library_rounded, color: Color(0xFF2563EB)),
                ),
                title: Text(widget.isArabic ? 'اختيار من معرض الصور' : 'Choose from Gallery'),
                subtitle: Text(widget.isArabic ? 'اختر صورة محفوظة مسبقاً' : 'Select existing saved image'),
                onTap: () {
                  Navigator.of(ctx).pop();
                  _pickCameraPhoto(ImageSource.gallery);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showPdfQuestionSelector() {
    final mainQuestions = [
      {
        'q_num': '1',
        'title_ar': 'السؤال الأول: فهم المقروء (Reading Comprehension)',
        'title_en': 'Question 1: Reading Comprehension',
        'desc_ar': 'نص ألعاب الكرة، تمركز سامي، خطة المدرب، وهدف الفوز الحاسم',
        'desc_en': 'Reading comprehension passage on ball games and match story',
        'badge_color': 0xFF2563EB,
        'page': 'ص 8',
        'solve_all_prompt_ar': 'حل السؤال الأول كاملاً مع جميع الأسئلة والفقرات الفرعية (1.1 إلى 1.7)',
        'solve_all_prompt_en': 'Solve complete Question 1 with all sub-questions (1.1 to 1.7)',
        'sub_questions': [
          {
            'sub_num': '1.1',
            'title_ar': 'الفكرة الرئيسة للنص',
            'title_en': 'Main Idea of the text',
            'prompt_ar': 'حل السؤال الأول فقرة 1.1: ما هي الفكرة الرئيسة للنص؟',
            'prompt_en': 'Solve Question 1 (1.1): What is the main idea of the text?',
          },
          {
            'sub_num': '1.2',
            'title_ar': 'عدد اللاعبين الأساسيين داخل الملعب (11 لاعباً)',
            'title_en': 'Starting players count on the pitch (11 players)',
            'prompt_ar': 'حل السؤال الأول فقرة 1.2: كم عدد اللاعبين الأساسيين في فريق كرة القدم داخل الملعب؟',
            'prompt_en': 'Solve Question 1 (1.2): How many starting players on a football team?',
          },
          {
            'sub_num': '1.3',
            'title_ar': 'خطة وتوجيهات المدرب بين الشوطين',
            'title_en': "Coach's halftime tactical instructions",
            'prompt_ar': 'حل السؤال الأول فقرة 1.3: ما هي خطة وتوجيهات المدرب بين الشوطين؟',
            'prompt_en': "Solve Question 1 (1.3): What was the coach's halftime tactical plan?",
          },
          {
            'sub_num': '1.4',
            'title_ar': 'أين وكيف تمركز سامي في الهجوم؟',
            'title_en': "Sami's smart positioning in attack",
            'prompt_ar': 'حل السؤال الأول فقرة 1.4: كيف تمركز سامي وتشارك مع زملائه في منطقة الهجوم؟',
            'prompt_en': "Solve Question 1 (1.4): How did Sami position himself in the attacking zone?",
          },
          {
            'sub_num': '1.5',
            'title_ar': 'ماذا فعل سامي عندما عادت الكرة إليه؟',
            'title_en': 'What Sami did when the ball returned to him',
            'prompt_ar': 'حل السؤال الأول فقرة 1.5: ماذا فعل سامي عندما عادت الكرة إليه؟',
            'prompt_en': 'Solve Question 1 (1.5): What did Sami do when the ball returned to him?',
          },
          {
            'sub_num': '1.6',
            'title_ar': 'ماذا سجل سامي في اللحظات الأخيرة؟ (هدف الفوز)',
            'title_en': 'What Sami scored: The decisive winning goal',
            'prompt_ar': 'حل السؤال الأول فقرة 1.6: ماذا سجل سامي في اللحظات الأخيرة؟',
            'prompt_en': 'Solve Question 1 (1.6): What did Sami score in the final moments?',
          },
          {
            'sub_num': '1.7',
            'title_ar': 'ماذا قال المدرب بعد نهاية المباراة؟',
            'title_en': "What the coach said regarding team victory",
            'prompt_ar': 'حل السؤال الأول فقرة 1.7: ماذا قال المدرب لسامي والفريق بعد نهاية المباراة؟',
            'prompt_en': 'Solve Question 1 (1.7): What did the coach say after the match ended?',
          },
        ]
      },
      {
        'q_num': '2',
        'title_ar': 'السؤال الثاني: صح أم خطأ (True or False)',
        'title_en': 'Question 2: True or False Statements (✓ / ✗)',
        'desc_ar': 'تقييم عبارات الصواب والخطأ مع تصحيح الخطأ وفق المنهاج',
        'desc_en': 'Evaluate statements with reasoning and corrections',
        'badge_color': 0xFF10B981,
        'page': 'ص 9-10',
        'solve_all_prompt_ar': 'حل السؤال الثاني كاملاً (صح أو خطأ لجميع العبارات 2.1 إلى 2.4 مع التصحيح)',
        'solve_all_prompt_en': 'Solve complete Question 2 (True/False items 2.1 to 2.4 with corrections)',
        'sub_questions': [
          {
            'sub_num': '2.1',
            'title_ar': 'كرة القدم لعبة فردية يمارسها لاعب واحد؟ (✗ خطأ - لعبة جماعية)',
            'title_en': 'Football is an individual game? (✗ False - Team sport)',
            'prompt_ar': 'حل السؤال 2 فقرة 2.1: صح أم خطأ: كرة القدم لعبة فردية يمارسها لاعب واحد؟',
            'prompt_en': 'Solve Question 2 (2.1): True/False: Football is an individual game?',
          },
          {
            'sub_num': '2.2',
            'title_ar': 'يتكون كل فريق من 11 لاعباً أساسياً؟ (✓ صحيح)',
            'title_en': 'Each football team has 11 starting players? (✓ True)',
            'prompt_ar': 'حل السؤال 2 فقرة 2.2: صح أم خطأ: يتكون كل فريق من 11 لاعباً أساسياً داخل الملعب؟',
            'prompt_en': 'Solve Question 2 (2.2): True/False: Football team has 11 starting players?',
          },
          {
            'sub_num': '2.3',
            'title_ar': 'الفاعل في الجملة الفعلية يكون دائماً مرفوعاً؟ (✓ صحيح بالضمة)',
            'title_en': 'Fa\'il is always nominative with damma? (✓ True)',
            'prompt_ar': 'حل السؤال 2 فقرة 2.3: صح أم خطأ: الفاعل في الجملة الفعلية يكون دائماً مرفوعاً؟',
            'prompt_en': 'Solve Question 2 (2.3): True/False: Subject (Fa\'il) is always nominative?',
          },
          {
            'sub_num': '2.4',
            'title_ar': 'مدة مباراة كرة القدم 90 دقيقة مقسمة على شوطين؟ (✓ صحيح)',
            'title_en': 'Match duration is 90 mins across two halves? (✓ True)',
            'prompt_ar': 'حل السؤال 2 فقرة 2.4: صح أم خطأ: مدة مباراة كرة القدم 90 دقيقة مقسمة على شوطين؟',
            'prompt_en': 'Solve Question 2 (2.4): True/False: Match lasts 90 minutes across two halves?',
          },
        ]
      },
      {
        'q_num': '3',
        'title_ar': 'السؤال الثالث: المفردات والاشتقاق والجذور (Vocabulary & Roots)',
        'title_en': 'Question 3: Vocabulary & Word Roots',
        'desc_ar': 'المعاني والمترادفات والتضاد واستخراج الجذور الثلاثية',
        'desc_en': 'Synonyms, antonyms, tri-literal morphology roots',
        'badge_color': 0xFF8B5CF6,
        'page': 'ص 7-11',
        'solve_all_prompt_ar': 'حل السؤال الثالث كاملاً مع جدول المفردات والجذور اللغوية (3.1 إلى 3.5)',
        'solve_all_prompt_en': 'Solve complete Question 3 with vocabulary and morphology roots (3.1 to 3.5)',
        'sub_questions': [
          {
            'sub_num': '3.1',
            'title_ar': 'مرادف كلمة (جماعية) وما ضدها؟',
            'title_en': 'Synonym and antonym of "jama\'iyyah"',
            'prompt_ar': 'حل السؤال 3 فقرة 3.1: ما هو مرادف كلمة (جماعية) وما ضدها؟',
            'prompt_en': 'Solve Question 3 (3.1): Synonym and antonym of "jama\'iyyah"?',
          },
          {
            'sub_num': '3.2',
            'title_ar': 'ما المقصود بلقب (الساحرة المستديرة)؟',
            'title_en': 'What is meant by "the round enchantress"?',
            'prompt_ar': 'حل السؤال 3 فقرة 3.2: ما المقصود بلقب (الساحرة المستديرة)؟',
            'prompt_en': 'Solve Question 3 (3.2): Meaning of the round enchantress?',
          },
          {
            'sub_num': '3.3',
            'title_ar': 'الجذر الثلاثي لـ (ملعب، لاعب، ألعاب) ➔ (ل-ع-ب)',
            'title_en': 'Tri-literal root of (mal\'ab, la\'ib, al\'ab)',
            'prompt_ar': 'حل السؤال 3 فقرة 3.3: ما هو الجذر اللغوي الثلاثي لكلمات (ملعب، لاعب، ألعاب)؟',
            'prompt_en': 'Solve Question 3 (3.3): Tri-literal root of (mal\'ab, la\'ib)?',
          },
          {
            'sub_num': '3.4',
            'title_ar': 'الجذر الثلاثي لـ (متسابق، سباق) ➔ (س-ب-ق)',
            'title_en': 'Tri-literal root of (mutasabiq, sibaq)',
            'prompt_ar': 'حل السؤال 3 فقرة 3.4: ما هو الجذر اللغوي الثلاثي لكلمات (متسابق، سباق)؟',
            'prompt_en': 'Solve Question 3 (3.4): Tri-literal root of (mutasabiq, sibaq)?',
          },
          {
            'sub_num': '3.5',
            'title_ar': 'ضد كلمة (سريع) و (الفوز)',
            'title_en': 'Antonyms of "quick" and "victory"',
            'prompt_ar': 'حل السؤال 3 فقرة 3.5: ما هو ضد كلمة (سريع) وما ضد كلمة (الفوز)؟',
            'prompt_en': 'Solve Question 3 (3.5): Antonyms of "saree\'" and "al-fawz"?',
          },
        ]
      },
      {
        'q_num': '4',
        'title_ar': 'السؤال الرابع: النحو والإعراب والإملاء (Grammar & Spelling)',
        'title_en': 'Question 4: Syntax, Parsing & Spelling Rules',
        'desc_ar': 'إعراب الجملة الفعلية، حروف الجر، التاء المربوطة والهاء',
        'desc_en': 'Verbal sentence parsing, prepositions, Taa Marbutah vs Haa',
        'badge_color': 0xFF7C3AED,
        'page': 'ص 10-12',
        'solve_all_prompt_ar': 'حل السؤال الرابع كاملاً مع نماذج الإعراب وقواعد الإملاء (4.1 إلى 4.5)',
        'solve_all_prompt_en': 'Solve complete Question 4 with parsing models and spelling rules (4.1 to 4.5)',
        'sub_questions': [
          {
            'sub_num': '4.1',
            'title_ar': 'إعراب جملة (سجل اللاعبُ الهدفَ) بالتفصيل',
            'title_en': 'Parse: "sajjala al-la\'ibu al-hadaf"',
            'prompt_ar': 'حل السؤال 4 فقرة 4.1: أعرب بالتفصيل جملة (سجل اللاعبُ الهدفَ) مع إعراب الفاعل والمفعول به',
            'prompt_en': 'Solve Question 4 (4.1): Parse sentence (sajjala al-la\'ibu al-hadaf) in detail',
          },
          {
            'sub_num': '4.2',
            'title_ar': 'نوع الجملة والفاعل في (يركض الفارسُ في الميدانِ)',
            'title_en': 'Sentence type and subject in "yarkudu al-faris"',
            'prompt_ar': 'حل السؤال 4 فقرة 4.2: حدد نوع الجملة والفاعل في: (يركض الفارسُ في الميدانِ)',
            'prompt_en': 'Solve Question 4 (4.2): Identify sentence type and subject in "yarkudu al-faris"',
          },
          {
            'sub_num': '4.3',
            'title_ar': 'حروف الجر والاسم المجرور من (يتنافس اللاعبون في الملعبِ بحماسٍ)',
            'title_en': 'Extract prepositions and genitive nouns',
            'prompt_ar': 'حل السؤال 4 فقرة 4.3: استخرج حروف الجر والاسم المجرور مع الضبط بالكسرة في جملة (يتنافس اللاعبون في الملعب بحماس)',
            'prompt_en': 'Solve Question 4 (4.3): Extract prepositions and genitive nouns in "yatanapasu al-la\'ibuna fi al-mal\'abi bi-hamas"',
          },
          {
            'sub_num': '4.4',
            'title_ar': 'الفرق الدقيق بين التاء المربوطة (ـة / ة) والهاء (ـه / ه)',
            'title_en': 'Difference between Taa Marbutah and Haa',
            'prompt_ar': 'حل السؤال 4 فقرة 4.4: ما الفرق الدقيق بين التاء المربوطة (ـة) والهاء (ـه) وكيف نميز بينهما بالحركة والتنوين؟',
            'prompt_en': 'Solve Question 4 (4.4): What is the difference between Taa Marbutah and Haa?',
          },
          {
            'sub_num': '4.5',
            'title_ar': 'قاعدة الفاعل والمبتدأ والخبر بالحركات الأصلية (الضمة)',
            'title_en': 'Rules of Fa\'il, Mubtada, and Khabar with damma',
            'prompt_ar': 'حل السؤال 4 فقرة 4.5: اشرح حركة الضمة للفاعل والمبتدأ والخبر في الجمل العربية',
            'prompt_en': 'Solve Question 4 (4.5): Explain damma inflection for Fa\'il, Mubtada, and Khabar',
          },
        ]
      },
      {
        'q_num': '5',
        'title_ar': 'السؤال الخامس: القيم التربوية والروح الرياضية (Educational Values)',
        'title_en': 'Question 5: Educational Values & Sportsmanship',
        'desc_ar': 'الدروس المستفادة والأخلاق الرياضية والانضباط والعمل الجماعي',
        'desc_en': 'Sportsmanship, teamwork ethics, and positive citizenship',
        'badge_color': 0xFFD97706,
        'page': 'ص 8',
        'solve_all_prompt_ar': 'حل السؤال الخامس كاملاً حول القيم التربوية والأخلاق الرياضية (5.1 إلى 5.2)',
        'solve_all_prompt_en': 'Solve complete Question 5 on educational values and sportsmanship (5.1 to 5.2)',
        'sub_questions': [
          {
            'sub_num': '5.1',
            'title_ar': 'أهم القيم المستفادة من ممارسة الألعاب الجماعية',
            'title_en': 'Core values learned from practicing team sports',
            'prompt_ar': 'حل السؤال 5 فقرة 5.1: ما هي أهم القيم التربوية والأخلاق الرياضية المستفادة من ممارسة الألعاب الجماعية؟',
            'prompt_en': 'Solve Question 5 (5.1): What are the core educational values gained from team sports?',
          },
          {
            'sub_num': '5.2',
            'title_ar': 'دور الرياضة في تعزيز الصحة والعمل الجماعي والانضباط',
            'title_en': 'How sports foster health, teamwork, and discipline',
            'prompt_ar': 'حل السؤال 5 فقرة 5.2: كيف تساهم ممارسة الرياضة في تعزيز الصحة البدنية والعمل الجماعي والانضباط المدرسي؟',
            'prompt_en': 'Solve Question 5 (5.2): How do sports enhance health, collaboration, and discipline?',
          },
        ]
      },
    ];

    final isCameraSource = _activeMode == 'camera' || _attachmentType == 'camera' || _attachmentType == 'gallery';
    final customCtrl = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        height: MediaQuery.of(ctx).size.height * 0.85,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          children: [
            Container(
              margin: const EdgeInsets.only(top: 10, bottom: 6),
              width: 44,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFFCBD5E1),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: isCameraSource
                            ? const [Color(0xFF2563EB), Color(0xFF1D4ED8)]
                            : const [Color(0xFF6C5CE7), Color(0xFF58337E)],
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      isCameraSource ? Icons.photo_camera_rounded : Icons.menu_book_rounded,
                      color: Colors.white,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.isArabic
                              ? (isCameraSource ? 'فهرس أسئلة الصورة الملتقطة' : 'فهرس أسئلة ورقة الاختبار (PDF)')
                              : (isCameraSource ? 'Camera Photo Questions Index' : 'Question Paper PDF Index'),
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1E293B),
                          ),
                        ),
                        Text(
                          _attachedFileName ??
                              (widget.isArabic
                                  ? (isCameraSource ? 'صورة التمرين من الكاميرا' : 'ورقة الأسئلة / منهاج اللغة العربية')
                                  : (isCameraSource ? 'Exercise snapshot' : 'Question Paper / Arabic Curriculum')),
                          style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.of(ctx).pop(),
                    icon: const Icon(Icons.close, size: 20, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            ),
            const Divider(height: 1, color: Color(0xFFE2E8F0)),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: customCtrl,
                      textDirection: widget.isArabic ? TextDirection.rtl : TextDirection.ltr,
                      decoration: InputDecoration(
                        hintText: widget.isArabic
                            ? 'أو اكتب رقم السؤال والفقرة (مثال: حل سؤال 1 فقرة 5)...'
                            : 'Or type question & item (e.g. solve Q1 item 1.5)...',
                        hintStyle: const TextStyle(fontSize: 11.5, color: Color(0xFF94A3B8)),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        isDense: true,
                        filled: true,
                        fillColor: const Color(0xFFF8FAFC),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10),
                          borderSide: const BorderSide(color: Color(0xFFCBD5E1)),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: () {
                      final text = customCtrl.text.trim();
                      if (text.isNotEmpty) {
                        Navigator.of(ctx).pop();
                        _send(text, 'User inquiry from question selector: $text');
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isCameraSource ? const Color(0xFF2563EB) : const Color(0xFF6C5CE7),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      elevation: 0,
                    ),
                    child: Text(widget.isArabic ? 'إرسال' : 'Ask'),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView.separated(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                itemCount: mainQuestions.length + 1,
                separatorBuilder: (context, index) => const SizedBox(height: 10),
                itemBuilder: (c, idx) {
                  if (idx == mainQuestions.length) {
                    // Quick Curriculum Actions at bottom of list
                    return Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            widget.isArabic ? 'إجراءات تلخيصية عامة للمنهاج:' : 'General Curriculum Summaries:',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF475569)),
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Expanded(
                                child: OutlinedButton.icon(
                                  onPressed: () {
                                    Navigator.of(ctx).pop();
                                    _send('لخص لي هذا الفصل وأفكاره الرئيسة وقوانين اللعبة والقيم التربوية',
                                        'Summarize this chapter, its main ideas, game rules, and educational values');
                                  },
                                  icon: const Icon(Icons.auto_stories_rounded, size: 14, color: Color(0xFF0D9488)),
                                  label: Text(
                                    widget.isArabic ? 'تلخيص شامل للدرس' : 'Lesson Summary',
                                    style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF0D9488)),
                                  ),
                                  style: OutlinedButton.styleFrom(
                                    side: const BorderSide(color: Color(0xFF99F6E4)),
                                    padding: const EdgeInsets.symmetric(vertical: 6),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: OutlinedButton.icon(
                                  onPressed: () {
                                    Navigator.of(ctx).pop();
                                    _send('استخرج جدول المفردات والتراكيب المعتمدة ومعانيها من الدرس',
                                        'Extract the approved curriculum vocabulary table and definitions');
                                  },
                                  icon: const Icon(Icons.menu_book_rounded, size: 14, color: Color(0xFF6366F1)),
                                  label: Text(
                                    widget.isArabic ? 'جدول المفردات' : 'Vocabulary Table',
                                    style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF6366F1)),
                                  ),
                                  style: OutlinedButton.styleFrom(
                                    side: const BorderSide(color: Color(0xFFC7D2FE)),
                                    padding: const EdgeInsets.symmetric(vertical: 6),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  }

                  final q = mainQuestions[idx];
                  final colorInt = q['badge_color'] as int;
                  final subQuestions = (q['sub_questions'] as List<dynamic>?) ?? [];

                  return Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFAFAFE),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Main Question Header
                        Row(
                          children: [
                            Container(
                              width: 34,
                              height: 34,
                              decoration: BoxDecoration(
                                color: Color(colorInt).withValues(alpha: 0.12),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              alignment: Alignment.center,
                              child: Text(
                                q['q_num'] as String,
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w900,
                                  color: Color(colorInt),
                                ),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    widget.isArabic ? (q['title_ar'] as String) : (q['title_en'] as String),
                                    style: const TextStyle(
                                      fontSize: 12.5,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF1E293B),
                                    ),
                                  ),
                                  Text(
                                    widget.isArabic ? (q['desc_ar'] as String) : (q['desc_en'] as String),
                                    style: const TextStyle(fontSize: 10.5, color: Color(0xFF64748B)),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFFF1F5F9),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                q['page'] as String,
                                style: const TextStyle(fontSize: 9.5, fontWeight: FontWeight.bold, color: Color(0xFF475569)),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        // Primary Action: Solve Complete Main Question
                        ElevatedButton.icon(
                          onPressed: () {
                            Navigator.of(ctx).pop();
                            _send(q['solve_all_prompt_ar'] as String, q['solve_all_prompt_en'] as String);
                          },
                          icon: const Icon(Icons.bolt_rounded, size: 14),
                          label: Text(
                            widget.isArabic
                                ? '⚡ حل السؤال (${q['q_num']}) كاملاً مع جميع الأسئلة الفرعية'
                                : '⚡ Solve complete Question ${q['q_num']} with all sub-questions',
                            style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Color(colorInt),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 10),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            elevation: 0,
                          ),
                        ),
                        // Sub-questions header and list
                        if (subQuestions.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Icon(Icons.subdirectory_arrow_left_rounded, size: 13, color: Color(colorInt)),
                              const SizedBox(width: 4),
                              Text(
                                widget.isArabic
                                    ? 'الأسئلة والفقرات الفرعية المفهرسة (انقر لاختيار فقرة):'
                                    : 'Indexed Sub-Questions (tap to select specific item):',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                  color: Color(colorInt),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Column(
                            children: subQuestions.map<Widget>((sub) {
                              final subMap = sub as Map<String, dynamic>;
                              return Container(
                                margin: const EdgeInsets.only(bottom: 5),
                                child: InkWell(
                                  onTap: () {
                                    Navigator.of(ctx).pop();
                                    _send(subMap['prompt_ar'] as String, subMap['prompt_en'] as String);
                                  },
                                  borderRadius: BorderRadius.circular(8),
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                                    decoration: BoxDecoration(
                                      color: Colors.white,
                                      borderRadius: BorderRadius.circular(8),
                                      border: Border.all(color: const Color(0xFFE2E8F0)),
                                    ),
                                    child: Row(
                                      children: [
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                                          decoration: BoxDecoration(
                                            color: Color(colorInt).withValues(alpha: 0.12),
                                            borderRadius: BorderRadius.circular(5),
                                          ),
                                          child: Text(
                                            subMap['sub_num'] as String,
                                            style: TextStyle(
                                              fontSize: 10,
                                              fontWeight: FontWeight.w900,
                                              color: Color(colorInt),
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Expanded(
                                          child: Text(
                                            widget.isArabic ? (subMap['title_ar'] as String) : (subMap['title_en'] as String),
                                            style: const TextStyle(
                                              fontSize: 11,
                                              fontWeight: FontWeight.w600,
                                              color: Color(0xFF1E293B),
                                            ),
                                          ),
                                        ),
                                        const Icon(Icons.arrow_forward_ios_rounded, size: 10, color: Color(0xFF94A3B8)),
                                      ],
                                    ),
                                  ),
                                ),
                              );
                            }).toList(),
                          ),
                        ],
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _toggleListening() async {
    if (_isListening) {
      await _speech.stop();
      if (mounted) setState(() => _isListening = false);
      return;
    }

    try {
      if (!_speechInitialized) {
        _speechInitialized = await _speech.initialize(
          onStatus: (status) {
            debugPrint('Speech status: $status');
            if (status == 'done' || status == 'notListening') {
              if (mounted) setState(() => _isListening = false);
            }
          },
          onError: (errorNotification) {
            debugPrint('Speech error: ${errorNotification.errorMsg}');
            if (mounted) {
              setState(() => _isListening = false);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    widget.isArabic
                        ? 'تنبيه الصوت: ${errorNotification.errorMsg}'
                        : 'Speech recognition: ${errorNotification.errorMsg}',
                  ),
                  backgroundColor: const Color(0xFF58337E),
                  duration: const Duration(seconds: 2),
                ),
              );
            }
          },
        );
      }

      if (!_speechInitialized) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                widget.isArabic
                    ? 'يرجى تفعيل صلاحية الميكروفون لاستخدام المحادثة الصوتية.'
                    : 'Please grant microphone permissions to use voice tutor.',
              ),
              backgroundColor: Colors.amber.shade900,
            ),
          );
        }
        return;
      }

      // Support both Arabic and English voice input based on user locale
      final locales = await _speech.locales();
      String? speechLocaleId;
      final targetPrefix = widget.isArabic ? 'ar' : 'en';
      for (final loc in locales) {
        if (loc.localeId.toLowerCase().startsWith(targetPrefix)) {
          speechLocaleId = loc.localeId;
          break;
        }
      }
      if (speechLocaleId == null) {
        for (final loc in locales) {
          if (loc.localeId.toLowerCase().startsWith('ar') || loc.localeId.toLowerCase().startsWith('en')) {
            speechLocaleId = loc.localeId;
            break;
          }
        }
      }

      setState(() {
        _isListening = true;
        _ctrl.clear();
      });

      await _speech.listen(
        onResult: (result) {
          if (mounted) {
            setState(() {
              _ctrl.text = result.recognizedWords;
              _ctrl.selection = TextSelection.fromPosition(
                TextPosition(offset: _ctrl.text.length),
              );
            });
          }
        },
        listenOptions: stt.SpeechListenOptions(
          listenFor: const Duration(minutes: 2),
          pauseFor: const Duration(seconds: 15),
          localeId: speechLocaleId,
          cancelOnError: false,
          partialResults: true,
          listenMode: stt.ListenMode.dictation,
        ),
      );
    } catch (e) {
      debugPrint('Error starting speech: $e');
      if (mounted) {
        setState(() => _isListening = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              widget.isArabic
                  ? 'تعذر بدء التسجيل الصوتي ($e)'
                  : 'Failed to start voice recording ($e)',
            ),
            backgroundColor: Colors.red.shade800,
          ),
        );
      }
    }
  }

  @override
  void dispose() {
    if (_isListening) {
      _speech.stop();
    }
    _ctrl.dispose();
    _paperCtrl.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  String _getQuickEnglishTranslation(String q) {
    final lower = q.trim();

    // Check Question 1 to 13 (digits or Arabic ordinals)
    // Check compound ordinals FIRST before single ordinals with negative lookaheads
    final qMatch = RegExp(
      r'(?:السؤال|سؤال|س|تمرين|فقرة|حل|Question|Q|Exercise|Ex)?\s*(?:رقم|no\.?|num\.?)?\s*(1[0-3]|[1-9]|١[٠-٣]|[١-٩]|الثالث\s*عشر|الثاني\s*عشر|الحادي\s*عشر|العاشر|التاسع|الثامن|السابع|السادس|الخامس|الرابع|الثالث(?!\s*عشر)|الثاني(?!\s*عشر)|الأول|الاول)(?!\d)',
      caseSensitive: false,
    ).firstMatch(lower);
    if (qMatch != null) {
      final token = qMatch.group(1)!.replaceAll(RegExp(r'\s+'), '');
      const numMap = {
        'الثالثعشر': '13', '13': '13', '١٣': '13',
        'الثانيعشر': '12', '12': '12', '١٢': '12',
        'الحاديعشر': '11', '11': '11', '١١': '11',
        'العاشر': '10', '10': '10', '١٠': '10',
        'التاسع': '9', '9': '9', '٩': '9',
        'الثامن': '8', '8': '8', '٨': '8',
        'السابع': '7', '7': '7', '٧': '7',
        'السادس': '6', '6': '6', '٦': '6',
        'الخامس': '5', '5': '5', '٥': '5',
        'الرابع': '4', '4': '4', '٤': '4',
        'الثالث': '3', '3': '3', '٣': '3',
        'الثاني': '2', '2': '2', '٢': '2',
        'الأول': '1', 'الاول': '1', '1': '1', '١': '1',
      };
      final n = numMap[token] ?? token;
      return 'Solve Question $n';
    }

    if (lower.contains('حل ورقة الأسئلة') || lower.contains('حل الامتحان') || lower.contains('ورقة الأسئلة') || lower.contains('حل الورقة')) {
      return 'Solve the complete question / exam paper';
    }
    if (lower.contains('التاء المربوطة') || lower.contains('الهاء')) {
      return 'Explain the difference between Taa Marbutah and Haa';
    }
    if (lower.contains('سجل اللاعب') || lower.contains('سَجَّلَ')) {
      return 'What is the grammatical parsing of "The player scored the goal"?';
    }
    if (lower.contains('كرة القدم لعبة') || lower.contains('كُرَةُ القَدَمِ')) {
      return 'What is the grammatical parsing of "Football is a team game"?';
    }
    if (lower.contains('إعراب') || lower.contains('أعرب')) {
      return 'Grammatical parsing and linguistic analysis request';
    }
    if (lower.contains('استخرج') || lower.contains('مفردات')) {
      return 'Extract key vocabulary and contextual meanings';
    }
    if (lower.contains('لخص') || lower.contains('تلخيص')) {
      return 'Summarize this chapter / lesson';
    }
    if (lower.contains('اشرح') || lower.contains('قواعد')) {
      return 'Explain grammar and language rules';
    }
    if (lower.contains('نطق') || lower.contains('اقرأ')) {
      return 'Pronunciation and vowel reading practice';
    }
    final isAscii = RegExp(r'^[\x00-\x7F]+$').hasMatch(q);
    if (isAscii) {
      return q;
    }
    return 'Arabic question regarding curriculum & grammar';
  }

  static String _cleanAnswerText(String text) {
    if (text.isEmpty) return text;
    var cleaned = text;

    // 1. Remove English Answer / Model Answer prefixes at start of string or lines
    cleaned = cleaned.replaceAll(
      RegExp(r'^[ \t]*[*_~`#]*[ \t]*(?:Model\s+Answer|Answer|Solution)[ \t]*[*_~`#]*[ \t]*[:.]?[ \t]*', caseSensitive: false, multiLine: true),
      '',
    );

    // 2. Remove Arabic Answer prefixes at start of string or lines
    cleaned = cleaned.replaceAll(
      RegExp(r'^[ \t]*[*_~`#•-]*[ \t]*(?:الإِجَابَةُ\s+النَّمُوذَجِيَّةُ|الإجابة\s+النموذجية|الإِجَابَةُ|الإجابة|الحَلُّ|الحل|نَمُوذَجُ\s+الإِجَابَةِ|نموذج\s+الإجابة)[ \t]*[*_~`#]*[ \t]*[:.]?[ \t]*', multiLine: true),
      '',
    );

    // 3. Remove inline **Answer.** or **Answer:** or **الإجابة:** anywhere
    cleaned = cleaned.replaceAll(
      RegExp(r'\*\*(?:Answer|Model Answer|Solution|الإجابة|الإجابة النموذجية|الحل)\s*[:.]?\*\*[ \t]*', caseSensitive: false),
      '',
    );

    return cleaned.trim();
  }

  Future<void> _send([String? customPrompt, String? customEnglish]) async {
    final query = customPrompt ?? _ctrl.text.trim();
    if (query.isEmpty) return;

    if (_isLoading) {
      // If user taps another question while previous is in-flight, queue it instead of dropping!
      if (customPrompt != null) {
        _queuedPrompt = customPrompt;
        _queuedEnglish = customEnglish;
      }
      return;
    }

    if (customPrompt == null) _ctrl.clear();
    final userMsgIndex = _messages.length;
    final initialEn = customEnglish ?? _getQuickEnglishTranslation(query);

    setState(() {
      _messages.add({
        'role': 'user',
        'text_ar': query,
        'text_en': initialEn,
        'attachment': _attachedFileName,
        'escalated': false,
      });
      _isLoading = true;
    });

    _scrollToBottom();

    try {
      final promptWithContext = _attachedFileName != null
          ? '[$_attachmentType: $_attachedFileName] $query'
          : query;

      final data = await _api.askFahim({
        'question': promptWithContext,
        'context_lesson_id': widget.contextLessonId,
        'child_id': widget.childId,
        'attachment_base64': _attachedBase64,
        'attachment_name': _attachedFileName,
        'attachment_type': _attachmentType,
      }, token: widget.token);

      if (data is Map) {
        final rawAnswerAr = data['answer_ar'] ?? 'أَهْلًا بِكَ فِي دَرْسِ أَلْعَابِ الكُرَةِ.';
        final rawQuestionEn = data['question_en']?.toString().trim();
        final rawAnswerEn = data['answer_en']?.toString().trim();
        final answerAr = _cleanAnswerText(rawAnswerAr.toString());
        final questionEn = (rawQuestionEn != null && rawQuestionEn.isNotEmpty) ? _cleanAnswerText(rawQuestionEn) : null;
        final answerEn = (rawAnswerEn != null && rawAnswerEn.isNotEmpty) ? _cleanAnswerText(rawAnswerEn) : null;
        final bool isCached = data['lesson_title']?.toString().contains('Cached') == true ||
            data['lesson_title']?.toString().contains('محلولة') == true ||
            data['cached'] == true;

        setState(() {
          if (questionEn != null && questionEn.isNotEmpty && userMsgIndex < _messages.length) {
            _messages[userMsgIndex]['text_en'] = questionEn;
          }
          _messages.add({
            'role': 'fahim',
            'text_ar': answerAr,
            'text_en': (answerEn != null && answerEn.isNotEmpty)
                ? answerEn
                : 'Guidance and curriculum explanation provided based on UAE MoE standards.',
            'escalated': data['escalated_to_tutor'] == true,
            'escalation_message': data['tutor_escalation_message'],
            'is_cached': isCached,
          });
        });
        if (_activeMode == 'voice' && widget.onVocalize != null) {
          widget.onVocalize!(answerAr);
        }
      }
    } catch (e) {
      final detail = e.toString().replaceAll('Exception: ', '').replaceAll('AuthException: ', '').trim();
      final bool isTimeout = detail.contains('timed out') || detail.contains('أطول من المتوقع') || detail.contains('Timeout');
      setState(() {
        _messages.add({
          'role': 'fahim',
          'text_ar': isTimeout
              ? '⚠️ اسْتَغْرَقَ تَحْلِيلُ المَلَفِّ وَالإِجَابَةُ وَقْتًا أَطْوَلَ مِنَ المُعْتَادِ. يُمكِنُكَ إِعَادَةُ إِرْسَالِ السُّؤَالِ مَرَّةً أُخْرَى.'
              : 'تَعَذَّرَ الِاتِّصَالُ بِخَادِمِ جِسْر ($detail). يُرْجَى التَّأَكُّدُ مِنْ تَشْغِيلِ الخَادِمِ وَاتِّصَالِ الشَّبَكَةِ.',
          'text_en': isTimeout
              ? 'Processing took longer than expected. Please tap send to retry your question.'
              : 'Connection notice ($detail). Please verify API server and network status.',
          'escalated': false,
        });
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        _scrollToBottom();

        // If a subsequent question was clicked while loading, dispatch it immediately!
        if (_queuedPrompt != null) {
          final nextPrompt = _queuedPrompt!;
          final nextEnglish = _queuedEnglish;
          _queuedPrompt = null;
          _queuedEnglish = null;
          Future.microtask(() {
            if (mounted) {
              _send(nextPrompt, nextEnglish);
            }
          });
        }
      }
    }
  }

  Future<void> _solveExamPaper({bool forceEscalate = false}) async {
    final text = _paperCtrl.text.trim();
    if (text.isEmpty && _paperFileName == null) return;

    setState(() {
      _isSolvingPaper = true;
      _paperError = null;
    });

    try {
      final res = await _api.solveQuestionPaper({
        'paper_title': _paperTitle,
        'document_base64': _attachedBase64,
        'mime_type': _attachmentType == 'camera' || _attachmentType == 'gallery'
            ? 'image/jpeg'
            : 'application/pdf',
        'text_content': text,
        'grade': 5,
        'term': 1,
        'child_id': widget.childId,
        'force_escalation': forceEscalate,
      }, token: widget.token);

      if (mounted && res is Map) {
        setState(() {
          _solvedPaperData = Map<String, dynamic>.from(res);
        });
        final questions = res['questions'];
        if (questions is List && questions.isNotEmpty) {
          final firstQ = questions[0];
          if (firstQ is Map && firstQ['model_answer_ar'] != null && widget.onVocalize != null) {
            widget.onVocalize!(firstQ['model_answer_ar'].toString());
          }
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _paperError = e.toString().replaceAll('Exception: ', '');
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSolvingPaper = false;
        });
      }
    }
  }

  Future<void> _escalateQuestion(int qNumber, String qText) async {
    try {
      await _api.solveQuestionPaper({
        'paper_title': '$_paperTitle - Question $qNumber',
        'text_content': 'Question $qNumber ($qText) needs human tutor certification.',
        'grade': 5,
        'term': 1,
        'child_id': widget.childId,
        'force_escalation': true,
      }, token: widget.token);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: const Color(0xFF1E293B),
            content: Text(
              widget.isArabic
                  ? 'تم رفع هذا السؤال للمعلم الخاص للمراجعة والتصديق!'
                  : 'Escalated to human tutor queue for review!',
            ),
          ),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: Colors.redAccent,
            content: Text(
              widget.isArabic
                  ? 'تعذر إرسال الطلب للمعلم حالياً.'
                  : 'Unable to escalate question at this time.',
            ),
          ),
        );
      }
    }
  }

  void _selectMode(String mode) {
    setState(() {
      _activeMode = mode;
      // Preserve PDF or camera attachment if user switches to voice or text tab
      if (mode != 'pdf' && mode != 'camera' && mode != 'exam' && mode != 'voice' && mode != 'text') {
        _attachedFileName = null;
        _attachmentType = null;
        _attachedBase64 = null;
      }
    });
    if (mode == 'pdf' && _attachedFileName == null) {
      _pickPdf();
    } else if (mode == 'camera' && _attachedFileName == null) {
      _showCameraOptions();
    } else if (mode == 'voice' && !_isListening) {
      _toggleListening();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 20),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 520, maxHeight: 660),
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Modal Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Row(
                    children: [
                      Container(
                        width: 38,
                        height: 38,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFF58337E), Color(0xFF6C5CE7)],
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        alignment: Alignment.center,
                        child: const Icon(Icons.auto_awesome, color: Color(0xFFFBBF24), size: 18),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Wrap(
                              crossAxisAlignment: WrapCrossAlignment.center,
                              spacing: 5,
                              children: [
                                Text(
                                  widget.isArabic ? 'اسأل فاهم الذكي' : 'Ask Fahim AI Tutor',
                                  style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 13, color: Color(0xFF1E293B)),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFECFDF5),
                                    borderRadius: BorderRadius.circular(5),
                                    border: Border.all(color: const Color(0xFFA7F3D0)),
                                  ),
                                  child: Text(
                                    widget.isArabic ? 'معلم معتمد' : 'AI Tutor',
                                    style: const TextStyle(
                                      fontSize: 7.5,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF065F46),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            Text(
                              widget.isArabic ? 'المعلم السقراطي لمناهج الإمارات' : 'Socratic Conversational Arabic Tutor',
                              style: const TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 6),
                const ArabEnglishToggleSwitch(compact: true),
                const SizedBox(width: 6),
                InkWell(
                  borderRadius: BorderRadius.circular(20),
                  onTap: () => Navigator.of(context).pop(),
                  child: Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF1F5F9),
                      shape: BoxShape.circle,
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                    ),
                    child: const Icon(Icons.close, size: 18, color: Color(0xFF475569)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // 5 Provision Mode Switcher Tabs (Voice, Text, PDF, Camera, Exam)
            Container(
              padding: const EdgeInsets.all(3),
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(14),
              ),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _modeTab('voice', Icons.mic_rounded, widget.isArabic ? 'صوت' : 'Voice'),
                    const SizedBox(width: 2),
                    _modeTab('text', Icons.chat_bubble_outline_rounded, widget.isArabic ? 'نص' : 'Text'),
                    const SizedBox(width: 2),
                    _modeTab('pdf', Icons.picture_as_pdf_rounded, 'PDF'),
                    const SizedBox(width: 2),
                    _modeTab('camera', Icons.photo_camera_rounded, widget.isArabic ? 'كاميرا' : 'Camera'),
                    const SizedBox(width: 2),
                    _modeTab('exam', Icons.assignment_outlined, widget.isArabic ? 'امتحان' : 'Exam Paper'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 10),

            // Body View
            Expanded(
              child: _activeMode == 'exam'
                  ? _buildExamPaperView()
                  : _buildConversationalChatView(),
            ),
          ],
        ),
      ),
    );
  }

  // Conversational Chat View (Voice, Text, PDF, Camera)
  Widget _buildConversationalChatView() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Attachment Banner (for PDF or Camera mode)
        if (_attachedFileName != null)
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
            decoration: BoxDecoration(
              color: _attachmentType == 'pdf' ? const Color(0xFFFEF2F2) : const Color(0xFFEFF6FF),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: _attachmentType == 'pdf' ? const Color(0xFFFECACA) : const Color(0xFFBFDBFE),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Icon(
                      _attachmentType == 'pdf' ? Icons.description_rounded : Icons.image_rounded,
                      size: 18,
                      color: _attachmentType == 'pdf' ? const Color(0xFFDC2626) : const Color(0xFF2563EB),
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            _attachedFileName!,
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: _attachmentType == 'pdf' ? const Color(0xFF991B1B) : const Color(0xFF1E40AF),
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            _attachmentType == 'pdf'
                                ? (widget.isArabic ? 'مستند PDF متصل بالذكاء الاصطناعي' : 'PDF Attached to AI')
                                : (widget.isArabic ? 'صورة مرفقة متصلة بالذكاء الاصطناعي' : 'Photo Attached to AI'),
                            style: TextStyle(
                              fontSize: 9.5,
                              color: _attachmentType == 'pdf' ? const Color(0xFFB91C1C) : const Color(0xFF1D4ED8),
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    InkWell(
                      onTap: () {
                        final summaryText = _attachmentType == 'pdf'
                            ? 'ورقة أسئلة منهاج اللغة العربية: $_attachedFileName. يمكنك اختيار أي سؤال من السؤال الأول حتى الثالث عشر للاستماع لنطقه وحله فورياً.'
                            : 'صورة التمرين من الكاميرا: $_attachedFileName. تم مسح التمرين وسأقوم بنطقه وحله خطوة بخطوة مع الترجمة الإنجليزية.';
                        _vocalize(summaryText);
                      },
                      borderRadius: BorderRadius.circular(12),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                        margin: const EdgeInsets.symmetric(horizontal: 3),
                        decoration: BoxDecoration(
                          color: _attachmentType == 'pdf' ? const Color(0xFFFEE2E2) : const Color(0xFFDBEAFE),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                            color: _attachmentType == 'pdf' ? const Color(0xFFFCA5A5) : const Color(0xFF93C5FD),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.volume_up_rounded,
                              size: 13,
                              color: _attachmentType == 'pdf' ? const Color(0xFFB91C1C) : const Color(0xFF1D4ED8),
                            ),
                            const SizedBox(width: 3),
                            Text(
                              widget.isArabic ? 'استمع' : 'Listen',
                              style: TextStyle(
                                fontSize: 9.5,
                                fontWeight: FontWeight.bold,
                                color: _attachmentType == 'pdf' ? const Color(0xFFB91C1C) : const Color(0xFF1D4ED8),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 2),
                    TextButton(
                      onPressed: _attachmentType == 'pdf' ? _pickPdf : _showCameraOptions,
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: Text(
                        widget.isArabic ? 'تغيير' : 'Change',
                        style: TextStyle(
                          fontSize: 10.5,
                          fontWeight: FontWeight.bold,
                          color: _attachmentType == 'pdf' ? const Color(0xFFDC2626) : const Color(0xFF2563EB),
                        ),
                      ),
                    ),
                    const SizedBox(width: 4),
                    InkWell(
                      onTap: () {
                        if (_attachmentType == 'pdf') {
                          _clearPersistedPdf();
                        }
                        setState(() {
                          _attachedFileName = null;
                          _attachedBase64 = null;
                        });
                      },
                      child: const Padding(
                        padding: EdgeInsets.all(4),
                        child: Icon(Icons.close, size: 16, color: Colors.black54),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                InkWell(
                  onTap: () {
                    _send(
                      widget.isArabic
                          ? 'استخرج وأجب عن جميع أسئلة هذا المستند المرفق ($_attachedFileName) بدقة وتفصيل مع الشرح والترجمة'
                          : 'Extract and answer all questions from attached document ($_attachedFileName) in detail with explanation and translation',
                      'Solve all questions from document with AI',
                    );
                  },
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: _attachmentType == 'pdf'
                            ? const [Color(0xFFDC2626), Color(0xFFB91C1C)]
                            : const [Color(0xFF2563EB), Color(0xFF1D4ED8)],
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.auto_awesome, size: 14, color: Colors.white),
                        const SizedBox(width: 6),
                        Flexible(
                          child: Text(
                            widget.isArabic
                                ? '✨ حل جميع أسئلة هذا المستند بالذكاء الاصطناعي'
                                : '✨ Solve Document Questions with AI',
                            style: const TextStyle(
                              fontSize: 10.5,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          )
        else if (_activeMode == 'pdf')
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                InkWell(
                  onTap: _pickPdf,
                  borderRadius: BorderRadius.circular(12),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFEF2F2),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFFCA5A5), width: 1.2),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.upload_file_rounded, size: 18, color: Color(0xFFDC2626)),
                        const SizedBox(width: 8),
                        Text(
                          widget.isArabic
                              ? 'اضغط هنا لرفع ملف PDF من جهازك'
                              : 'Tap here to upload a PDF from your device',
                          style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.bold, color: Color(0xFF991B1B)),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                OutlinedButton.icon(
                  onPressed: _showPdfQuestionSelector,
                  icon: const Icon(Icons.menu_book_rounded, size: 15, color: Color(0xFF6C5CE7)),
                  label: Text(
                    widget.isArabic
                        ? '📖 أو استعرض أسئلة كتاب المنهاج المعتمد (الصف الخامس)'
                        : '📖 Or browse UAE Grade 5 textbook questions',
                    style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF6C5CE7)),
                  ),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFFDDD6FE)),
                    padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 10),
                    minimumSize: Size.zero,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ],
            ),
          )
        else if (_activeMode == 'camera')
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _pickCameraPhoto(ImageSource.camera),
                        icon: const Icon(Icons.photo_camera_rounded, size: 16),
                        label: Text(widget.isArabic ? 'التقاط صورة بالكاميرا' : 'Take Photo'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF6C5CE7),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          elevation: 0,
                          textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _pickCameraPhoto(ImageSource.gallery),
                        icon: const Icon(Icons.photo_library_rounded, size: 16, color: Color(0xFF2563EB)),
                        label: Text(widget.isArabic ? 'من المعرض' : 'From Gallery'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFF2563EB),
                          side: const BorderSide(color: Color(0xFF93C5FD)),
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                OutlinedButton.icon(
                  onPressed: _showPdfQuestionSelector,
                  icon: const Icon(Icons.format_list_numbered_rounded, size: 15, color: Color(0xFF2563EB)),
                  label: Text(
                    widget.isArabic
                        ? '🔢 اختيار وتحديد السؤال والأسئلة الفرعية من الصورة'
                        : '🔢 Select Question & Sub-questions from Camera Photo',
                    style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF2563EB)),
                  ),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFF93C5FD)),
                    padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 10),
                    minimumSize: Size.zero,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ],
            ),
          )
        else if (_activeMode == 'voice')
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: _isListening
                    ? [const Color(0xFFFEF2F2), const Color(0xFFFEE2E2)]
                    : [const Color(0xFFF5F3FF), const Color(0xFFEDE9FE)],
              ),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: _isListening ? const Color(0xFFF87171) : const Color(0xFFDDD6FE),
                width: 1.2,
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(7),
                  decoration: BoxDecoration(
                    color: _isListening ? Colors.red : const Color(0xFF6C5CE7),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _isListening ? Icons.mic : Icons.mic_none_rounded,
                    size: 16,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _isListening
                            ? (widget.isArabic ? 'جاري الاستماع... تحدث باللغة العربية الآن' : 'Listening... Speak in Arabic now')
                            : (widget.isArabic ? 'المعلم الصوتي التفاعلي' : 'Interactive Voice Tutor'),
                        style: TextStyle(
                          fontSize: 11.5,
                          fontWeight: FontWeight.bold,
                          color: _isListening ? const Color(0xFF991B1B) : const Color(0xFF4C1D95),
                        ),
                      ),
                      Text(
                        _isListening
                            ? (widget.isArabic ? 'انقر على الزر الأحمر للإنهاء والإرسال' : 'Tap red button when finished to send')
                            : (widget.isArabic ? 'انقر على "تحدث" وسيجيبك الأستاذ فاهم بصوته' : 'Tap "Speak" and Ustadh Fahim will reply aloud'),
                        style: TextStyle(
                          fontSize: 9.5,
                          color: _isListening ? const Color(0xFFB91C1C) : const Color(0xFF6D28D9),
                        ),
                      ),
                    ],
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: _isLoading ? null : _toggleListening,
                  icon: Icon(_isListening ? Icons.stop_rounded : Icons.mic_rounded, size: 15),
                  label: Text(
                    _isListening
                        ? (widget.isArabic ? 'إيقاف وإرسال' : 'Stop & Send')
                        : (widget.isArabic ? 'تحدث' : 'Speak'),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _isListening ? Colors.red : const Color(0xFF6C5CE7),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    minimumSize: Size.zero,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    elevation: 0,
                    textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),

        // Chat Messages Container
        Expanded(
          child: Container(
            decoration: BoxDecoration(
              color: const Color(0xFFF8F9FE),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: ListView.builder(
              controller: _scrollCtrl,
              padding: const EdgeInsets.all(12),
              itemCount: _messages.length,
              itemBuilder: (ctx, i) {
                final m = _messages[i];
                final isUser = m['role'] == 'user';
                final bool isEscalated = m['escalated'] == true;
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(10),
                    constraints: const BoxConstraints(maxWidth: 320),
                    decoration: BoxDecoration(
                      color: isUser ? const Color(0xFF6C5CE7) : Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isUser ? const Color(0xFF58337E) : const Color(0xFFE2E8F0),
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.03),
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Wrap(
                                crossAxisAlignment: WrapCrossAlignment.center,
                                spacing: 4,
                                runSpacing: 2,
                                children: [
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(
                                        isUser ? Icons.help_outline_rounded : Icons.school_rounded,
                                        size: 13,
                                        color: isUser ? Colors.white70 : const Color(0xFF6C5CE7),
                                      ),
                                      const SizedBox(width: 4),
                                      Text(
                                        isUser
                                            ? (widget.isArabic ? 'سُؤَالُ الطَّالِبِ' : 'STUDENT QUESTION')
                                            : (widget.isArabic ? 'المُعَلِّمُ فَاهِم' : 'USTADH FAHIM'),
                                        style: TextStyle(
                                          fontSize: 9.5,
                                          fontWeight: FontWeight.bold,
                                          color: isUser ? Colors.white70 : const Color(0xFF6C5CE7),
                                        ),
                                      ),
                                    ],
                                  ),
                                  if (!isUser && m['is_cached'] == true)
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFFECFDF5),
                                        borderRadius: BorderRadius.circular(6),
                                        border: Border.all(color: const Color(0xFFA7F3D0)),
                                      ),
                                      child: Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          const Icon(Icons.bolt_rounded, size: 10, color: Color(0xFF059669)),
                                          const SizedBox(width: 2),
                                          Text(
                                            widget.isArabic ? 'مسترجع من الذاكرة' : 'Instant Cache',
                                            style: const TextStyle(
                                              fontSize: 8,
                                              fontWeight: FontWeight.bold,
                                              color: Color(0xFF065F46),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 4),
                            // Quick Pronunciation / Listen Button against every Question and Answer
                            InkWell(
                              onTap: () => _vocalize(m['text_ar'] as String? ?? ''),
                              borderRadius: BorderRadius.circular(14),
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                                decoration: BoxDecoration(
                                  color: isUser ? Colors.white.withValues(alpha: 0.22) : const Color(0xFFF3F0FF),
                                  borderRadius: BorderRadius.circular(14),
                                  border: Border.all(
                                    color: isUser ? Colors.white38 : const Color(0xFFDDD6FE),
                                  ),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      Icons.volume_up_rounded,
                                      size: 13,
                                      color: isUser ? Colors.white : const Color(0xFF6C5CE7),
                                    ),
                                    const SizedBox(width: 3.5),
                                    Text(
                                      isUser
                                          ? (widget.isArabic ? 'نطق السؤال' : 'Listen')
                                          : (widget.isArabic ? 'استمع للإجابة' : 'Listen'),
                                      style: TextStyle(
                                        fontSize: 9,
                                        fontWeight: FontWeight.bold,
                                        color: isUser ? Colors.white : const Color(0xFF6C5CE7),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                        if (m['attachment'] != null) ...[
                          const SizedBox(height: 4),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.white24,
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              '📎 ${m['attachment']}',
                              style: const TextStyle(fontSize: 9, color: Colors.white),
                            ),
                          ),
                        ],
                        const SizedBox(height: 4),
                        _buildBilingualMessageBody(
                          m['text_ar'] as String? ?? '',
                          isUser,
                          fallbackEnglish: m['text_en'] as String?,
                        ),
                        // Bilingual audio toolbar at bottom of message card
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: isUser ? Colors.white.withValues(alpha: 0.14) : const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: isUser ? Colors.white24 : const Color(0xFFE2E8F0),
                            ),
                          ),
                          child: Wrap(
                            crossAxisAlignment: WrapCrossAlignment.center,
                            spacing: 8,
                            runSpacing: 4,
                            children: [
                              InkWell(
                                onTap: () => _vocalize(m['text_ar'] as String? ?? ''),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      Icons.play_circle_fill_rounded,
                                      size: 14,
                                      color: isUser ? Colors.white : const Color(0xFF6C5CE7),
                                    ),
                                    const SizedBox(width: 4),
                                    Text(
                                      isUser
                                          ? (widget.isArabic ? 'نطق السؤال كاملاً' : 'Listen Full Question')
                                          : (widget.isArabic ? 'استمع للإجابة كاملة' : 'Listen Full Answer'),
                                      style: TextStyle(
                                        fontSize: 9.5,
                                        fontWeight: FontWeight.bold,
                                        color: isUser ? Colors.white : const Color(0xFF6C5CE7),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              if (m['text_en'] != null && (m['text_en'] as String).trim().isNotEmpty) ...[
                                Text('•', style: TextStyle(color: isUser ? Colors.white54 : Colors.black26, fontSize: 10)),
                                InkWell(
                                  onTap: () => _vocalize(m['text_en'] as String),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(
                                        Icons.volume_up_outlined,
                                        size: 13,
                                        color: isUser ? Colors.white70 : const Color(0xFF047857),
                                      ),
                                      const SizedBox(width: 3),
                                      Text(
                                        widget.isArabic ? 'ترجمة بالإنجليزية' : 'English Translation',
                                        style: TextStyle(
                                          fontSize: 9.5,
                                          fontWeight: FontWeight.bold,
                                          color: isUser ? Colors.white70 : const Color(0xFF047857),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                        if (isEscalated) ...[
                          const SizedBox(height: 6),
                          Container(
                            padding: const EdgeInsets.all(6),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFEF3C7),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.person_pin, size: 14, color: Color(0xFFB45309)),
                                const SizedBox(width: 4),
                                Expanded(
                                  child: Text(
                                    widget.isArabic
                                        ? 'تم توجيه السؤال إلى معلمك الخاص للمراجعة والمتابعة.'
                                        : 'Escalated to human tutor for personalized review.',
                                    style: const TextStyle(fontSize: 9.5, color: Color(0xFF78350F), fontWeight: FontWeight.bold),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ),

        if (_isLoading)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(
              children: [
                const SizedBox(
                  width: 12,
                  height: 12,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF6C5CE7)),
                ),
                const SizedBox(width: 8),
                Text(
                  widget.isArabic ? 'المعلم فاهم يراجع المنهج...' : 'Ustadh Fahim is reviewing the curriculum...',
                  style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                ),
              ],
            ),
          ),

        // Quick Prompt Suggestions
        const SizedBox(height: 6),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              if (_attachedFileName != null) ...[
                _actionChipCustom(
                  icon: Icons.auto_awesome,
                  labelAr: '✨ حل جميع أسئلة المستند',
                  labelEn: '✨ Solve All Questions',
                  color: const Color(0xFFDC2626),
                  onTap: () {
                    _send(
                      widget.isArabic
                          ? 'استخرج وأجب عن جميع أسئلة هذا المستند المرفق ($_attachedFileName) بدقة وتفصيل مع الشرح والترجمة'
                          : 'Extract and answer all questions from attached document ($_attachedFileName) in detail with explanation and translation',
                      'Solve all questions from document with AI',
                    );
                  },
                ),
                _suggestionChip(
                  'أجب عن السؤال الأول في المستند المرفق واشرح الإجابة بالتفصيل مع الترجمة',
                  'Answer Question 1 from the attached document with explanation and translation',
                  displayAr: 'س1 في المستند',
                  displayEn: 'Q1 in Document',
                ),
                _suggestionChip(
                  'أجب عن السؤال الثاني في المستند المرفق واشرح الإجابة بالتفصيل مع الترجمة',
                  'Answer Question 2 from the attached document with explanation and translation',
                  displayAr: 'س2 في المستند',
                  displayEn: 'Q2 in Document',
                ),
                _suggestionChip(
                  'أجب عن السؤال الثالث في المستند المرفق واشرح الإجابة بالتفصيل مع الترجمة',
                  'Answer Question 3 from the attached document with explanation and translation',
                  displayAr: 'س3 في المستند',
                  displayEn: 'Q3 in Document',
                ),
                _suggestionChip(
                  'لخص الأفكار والفقرات الرئيسة في هذا المستند المرفق بالتفصيل',
                  'Summarize the main ideas and sections of the attached document in detail',
                  displayAr: '📝 تلخيص المستند',
                  displayEn: '📝 Summarize',
                ),
                _suggestionChip(
                  'استخرج المفردات اللغوية وقواعد النحو والإعراب المذكورة في هذا المستند',
                  'Extract vocabulary, grammar rules and parsing from this document',
                  displayAr: '🔍 المفردات والإعراب',
                  displayEn: '🔍 Vocab & Grammar',
                ),
              ] else if (_activeMode == 'pdf') ...[
                _suggestionChip('لخص لي هذا الفصل', 'Summarize this chapter'),
                _suggestionChip('استخرج المفردات ومعانيها', 'Extract vocabulary'),
                _suggestionChip('اشرح القواعد النحوية', 'Explain grammar rules'),
              ] else if (_activeMode == 'camera') ...[
                _suggestionChip('حل هذا التمرين مع الشرح خطوة بخطوة', 'Solve this exercise with steps'),
                _suggestionChip('وضح الفكرة الرئيسة في الصورة', 'Clarify main idea in photo'),
                _suggestionChip('استخرج الكلمات الصعبة وقواعد الإعراب', 'Extract difficult words & parsing'),
              ] else if (_activeMode == 'voice') ...[
                _suggestionChip('اقرأ لي النص بالتشكيل', 'Read text with vowels'),
                _suggestionChip('دربني على نطق المفردات', 'Practice pronunciation'),
              ] else ...[
                _actionChipCustom(
                  icon: Icons.menu_book_rounded,
                  labelAr: '📖 فهرس أسئلة المنهاج',
                  labelEn: '📖 UAE Grade 5 Questions Index',
                  color: const Color(0xFF6C5CE7),
                  onTap: _showPdfQuestionSelector,
                ),
                _suggestionChip('ما الفرق بين التاء المربوطة والهاء؟', 'Taa Marbutah vs Haa'),
                _suggestionChip('أعرب جملة (كرة القدم لعبة جماعية)', 'Parse nominal sentence'),
                _suggestionChip('ما إعراب جملة (سجل اللاعب الهدف)؟', 'Parse verbal sentence'),
              ],
            ],
          ),
        ),
        const SizedBox(height: 8),

        // Live Listening Banner Indicator
        if (_isListening)
          Container(
            margin: const EdgeInsets.only(bottom: 6),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFFFEF2F2),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFFECACA)),
            ),
            child: Row(
              children: [
                const SizedBox(
                  width: 12,
                  height: 12,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.red),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    widget.isArabic
                        ? 'جاري الاستماع لصوتك... (تحدث الآن أو انقر إرسال)'
                        : 'Listening to your voice... (Speak now or tap Send)',
                    style: const TextStyle(fontSize: 11, color: Color(0xFFB91C1C), fontWeight: FontWeight.bold),
                  ),
                ),
                TextButton(
                  onPressed: _toggleListening,
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    minimumSize: Size.zero,
                  ),
                  child: Text(
                    widget.isArabic ? 'إرسال الصوت' : 'Send Voice',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.red),
                  ),
                ),
              ],
            ),
          ),

        // Input Field and Action Buttons (Mic + Send)
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _ctrl,
                style: const TextStyle(fontSize: 13),
                decoration: InputDecoration(
                  hintText: _isListening
                      ? (widget.isArabic ? 'جاري الاستماع... تحدث الآن' : 'Listening... speak now')
                      : (_activeMode == 'voice'
                          ? (widget.isArabic ? 'تحدث مع فاهم أو اكتب هنا...' : 'Speak with Fahim or type here...')
                          : (_activeMode == 'pdf'
                              ? (widget.isArabic ? 'اسأل سؤالاً حول ملف الـ PDF...' : 'Ask a question about the PDF...')
                              : (_activeMode == 'camera'
                                  ? (widget.isArabic ? 'اسأل حول الصورة الملتقطة...' : 'Ask about captured photo...')
                                  : (widget.isArabic ? 'اسأل عن ألعاب الكرة أو القواعد...' : 'Ask about ball games or grammar...')))),
                  hintStyle: TextStyle(
                    fontSize: 12,
                    color: _isListening ? Colors.red.shade400 : const Color(0xFF94A3B8),
                  ),
                  isDense: true,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: const BorderSide(color: Color(0xFFCBD5E1)),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: BorderSide(
                      color: _isListening ? Colors.red.shade300 : const Color(0xFFCBD5E1),
                    ),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: BorderSide(
                      color: _isListening ? Colors.red : const Color(0xFF6C5CE7),
                      width: 1.5,
                    ),
                  ),
                ),
                onSubmitted: (_) => _send(),
              ),
            ),
            const SizedBox(width: 6),
            // Dedicated Voice Recording Button
            SizedBox(
              height: 42,
              width: 42,
              child: Tooltip(
                message: widget.isArabic ? 'تسجيل الصوت والتحدث' : 'Record voice & speak',
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _isListening ? Colors.red : const Color(0xFFEDE9FE),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    padding: EdgeInsets.zero,
                    elevation: _isListening ? 3 : 0,
                  ),
                  onPressed: _isLoading ? null : _toggleListening,
                  child: Icon(
                    _isListening ? Icons.stop_rounded : Icons.mic_rounded,
                    size: 20,
                    color: _isListening ? Colors.white : const Color(0xFF6C5CE7),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 6),
            // Send Button
            SizedBox(
              height: 42,
              width: 42,
              child: Tooltip(
                message: widget.isArabic ? 'إرسال الرسالة' : 'Send message',
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6C5CE7),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    padding: EdgeInsets.zero,
                  ),
                  onPressed: _isLoading ? null : () => _send(),
                  child: const Icon(
                    Icons.send_rounded,
                    size: 18,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildBilingualMessageBody(
    String rawText,
    bool isUser, {
    String? fallbackEnglish,
  }) {
    final sanitizedRaw = _cleanAnswerText(rawText);
    if (sanitizedRaw.isEmpty) return const SizedBox.shrink();

    final lines = sanitizedRaw.split('\n');
    final hasInterleaving = lines.any((l) => _isEnglishLine(l));

    if (!hasInterleaving) {
      // Pure Arabic text or single block without embedded translations
      final bool isPureAscii = RegExp(r'^[\x00-\x7F\s]+$').hasMatch(sanitizedRaw);
      final sanitizedFallback = fallbackEnglish != null ? _cleanAnswerText(fallbackEnglish) : null;
      return Column(
        crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Directionality(
                  textDirection: isPureAscii ? TextDirection.ltr : TextDirection.rtl,
                  child: Text(
                    sanitizedRaw,
                    style: TextStyle(
                      color: isUser ? Colors.white : const Color(0xFF0F172A),
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      height: 1.45,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 4),
              InkWell(
                onTap: () => _vocalize(sanitizedRaw),
                borderRadius: BorderRadius.circular(12),
                child: Padding(
                  padding: const EdgeInsets.all(3),
                  child: Icon(
                    Icons.volume_up_rounded,
                    size: 14,
                    color: isUser ? Colors.white70 : const Color(0xFF6C5CE7),
                  ),
                ),
              ),
            ],
          ),
          // Tier 2: ArabEnglish Pronunciation (Distinct Dark Colored Font)
          ValueListenableBuilder<bool>(
            valueListenable: ArabEnglishState.notifier,
            builder: (context, isArabEnOn, _) {
              if (!isArabEnOn || isPureAscii) return const SizedBox.shrink();
              final arabEn = ArabEnglishHelper.transliterate(sanitizedRaw);
              if (arabEn.isEmpty) return const SizedBox.shrink();
              return Container(
                width: double.infinity,
                margin: const EdgeInsets.only(top: 5),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4.5),
                decoration: BoxDecoration(
                  color: isUser
                      ? Colors.white.withValues(alpha: 0.18)
                      : const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: isUser
                        ? Colors.white.withValues(alpha: 0.3)
                        : const Color(0xFFCBD5E1),
                  ),
                ),
                child: Directionality(
                  textDirection: TextDirection.ltr,
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(top: 2, right: 6),
                        child: Icon(
                          Icons.record_voice_over_rounded,
                          size: 13,
                          color: isUser ? Colors.white : const Color(0xFF4338CA),
                        ),
                      ),
                      Expanded(
                        child: RichText(
                          text: TextSpan(
                            children: [
                              TextSpan(
                                text: 'Pronunciation: ',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                  color: isUser ? Colors.white70 : const Color(0xFF4338CA),
                                ),
                              ),
                              TextSpan(
                                text: arabEn,
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 0.25,
                                  height: 1.35,
                                  color: isUser ? Colors.white : const Color(0xFF0F172A),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
          if (sanitizedFallback != null && sanitizedFallback.isNotEmpty) ...[
            const SizedBox(height: 6),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
              decoration: BoxDecoration(
                color: isUser
                    ? Colors.white.withValues(alpha: 0.16)
                    : const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: isUser
                      ? Colors.white.withValues(alpha: 0.28)
                      : const Color(0xFFE2E8F0),
                ),
              ),
              child: Directionality(
                textDirection: TextDirection.ltr,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(top: 2, right: 5),
                      child: Icon(
                        Icons.translate_rounded,
                        size: 12,
                        color: isUser ? Colors.white70 : const Color(0xFF6C5CE7),
                      ),
                    ),
                    Expanded(
                      child: Text(
                        sanitizedFallback,
                        style: TextStyle(
                          color: isUser ? Colors.white : const Color(0xFF334155),
                          fontSize: 11,
                          height: 1.35,
                          fontStyle: FontStyle.italic,
                          fontWeight: isUser ? FontWeight.w500 : FontWeight.normal,
                        ),
                      ),
                    ),
                    const SizedBox(width: 4),
                    InkWell(
                      onTap: () => _vocalize(sanitizedFallback),
                      borderRadius: BorderRadius.circular(12),
                      child: Padding(
                        padding: const EdgeInsets.all(2),
                        child: Icon(
                          Icons.volume_up_outlined,
                          size: 13,
                          color: isUser ? Colors.white70 : const Color(0xFF047857),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      );
    }

    // Interleaved presentation: Every Arabic question/answer has its English translation directly below
    final List<Widget> children = [];
    List<String> currentArabicBlock = [];

    void flushArabicBlock() {
      if (currentArabicBlock.isNotEmpty) {
        final blockText = _cleanAnswerText(currentArabicBlock.join('\n').trim());
        if (blockText.isNotEmpty) {
          children.add(
            Container(
              margin: const EdgeInsets.symmetric(vertical: 2),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Directionality(
                      textDirection: TextDirection.rtl,
                      child: Text(
                        blockText,
                        style: TextStyle(
                          color: isUser ? Colors.white : const Color(0xFF0F172A),
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          height: 1.45,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  InkWell(
                    onTap: () => _vocalize(blockText),
                    borderRadius: BorderRadius.circular(12),
                    child: Padding(
                      padding: const EdgeInsets.all(3),
                      child: Icon(
                        Icons.volume_up_rounded,
                        size: 14,
                        color: isUser ? Colors.white70 : const Color(0xFF6C5CE7),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
          // Tier 2: ArabEnglish Pronunciation for interleaved block
          children.add(
            ValueListenableBuilder<bool>(
              valueListenable: ArabEnglishState.notifier,
              builder: (context, isArabEnOn, _) {
                if (!isArabEnOn) return const SizedBox.shrink();
                final arabEn = ArabEnglishHelper.transliterate(blockText);
                if (arabEn.isEmpty) return const SizedBox.shrink();
                return Container(
                  width: double.infinity,
                  margin: const EdgeInsets.only(top: 2, bottom: 4),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: isUser
                        ? Colors.white.withValues(alpha: 0.18)
                        : const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: isUser
                          ? Colors.white.withValues(alpha: 0.3)
                          : const Color(0xFFCBD5E1),
                    ),
                  ),
                  child: Directionality(
                    textDirection: TextDirection.ltr,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.only(top: 2, right: 6),
                          child: Icon(
                            Icons.record_voice_over_rounded,
                            size: 13,
                            color: isUser ? Colors.white : const Color(0xFF4338CA),
                          ),
                        ),
                        Expanded(
                          child: RichText(
                            text: TextSpan(
                              children: [
                                TextSpan(
                                  text: 'Pronunciation: ',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w800,
                                    color: isUser ? Colors.white70 : const Color(0xFF4338CA),
                                  ),
                                ),
                                TextSpan(
                                  text: arabEn,
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                    letterSpacing: 0.25,
                                    height: 1.35,
                                    color: isUser ? Colors.white : const Color(0xFF0F172A),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          );
        }
        currentArabicBlock = [];
      }
    }

    for (int i = 0; i < lines.length; i++) {
      final line = lines[i];
      final trimmed = line.trim();

      if (trimmed.isEmpty) {
        flushArabicBlock();
        if (children.isNotEmpty) {
          children.add(const SizedBox(height: 4));
        }
        continue;
      }

      if (_isDividerLine(trimmed)) {
        flushArabicBlock();
        children.add(
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Divider(
              height: 8,
              thickness: 1,
              color: isUser ? Colors.white24 : const Color(0xFFE2E8F0),
            ),
          ),
        );
        continue;
      }

      if (_isEnglishLine(line)) {
        flushArabicBlock();
        String cleanEnglish = trimmed;
        final bool hadFlag = cleanEnglish.contains('🇬🇧');
        if (hadFlag) {
          cleanEnglish = cleanEnglish.replaceAll('🇬🇧', '').trim();
        }
        cleanEnglish = _cleanAnswerText(cleanEnglish);

        children.add(
          Container(
            width: double.infinity,
            margin: const EdgeInsets.only(top: 3, bottom: 5),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
            decoration: BoxDecoration(
              color: isUser
                  ? Colors.white.withValues(alpha: 0.16)
                  : const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: isUser
                    ? Colors.white.withValues(alpha: 0.28)
                    : const Color(0xFFE2E8F0),
              ),
            ),
            child: Directionality(
              textDirection: TextDirection.ltr,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Padding(
                    padding: EdgeInsets.only(top: 1.5, right: 5),
                    child: Text('🇬🇧', style: TextStyle(fontSize: 11)),
                  ),
                  Expanded(
                    child: Text(
                      cleanEnglish,
                      style: TextStyle(
                        color: isUser ? Colors.white : const Color(0xFF334155),
                        fontSize: 11,
                        height: 1.35,
                        fontStyle: FontStyle.italic,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  InkWell(
                    onTap: () => _vocalize(cleanEnglish),
                    borderRadius: BorderRadius.circular(12),
                    child: Padding(
                      padding: const EdgeInsets.all(2),
                      child: Icon(
                        Icons.volume_up_outlined,
                        size: 13,
                        color: isUser ? Colors.white70 : const Color(0xFF047857),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      } else {
        currentArabicBlock.add(line);
      }
    }
    flushArabicBlock();

    return Column(
      crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
      children: children,
    );
  }

  bool _isEnglishLine(String line) {
    final trimmed = line.trim();
    if (trimmed.isEmpty) return false;
    if (trimmed.contains('🇬🇧') || trimmed.startsWith('[EN:') || trimmed.startsWith('EN:')) {
      return true;
    }
    if (RegExp(r'^(Question|Model Answer|Answer|Explanation|Reference|Translation|Solution to|Note|Sentence|Item|Balls|True|False)\b', caseSensitive: false).hasMatch(trimmed)) {
      return true;
    }
    final hasArabic = RegExp(r'[\u0600-\u06FF]').hasMatch(trimmed);
    final hasLatin = RegExp(r'[a-zA-Z]{3,}').hasMatch(trimmed);
    return !hasArabic && hasLatin;
  }

  bool _isDividerLine(String line) {
    final trimmed = line.trim();
    return trimmed.isNotEmpty &&
        (trimmed.startsWith('━━━') || trimmed.startsWith('---') || trimmed.startsWith('==='));
  }

  // Question Paper Exam Assistant View
  Widget _buildExamPaperView() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Banner
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFFF5F3FF), Color(0xFFEDE9FE)],
              ),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFDDD6FE)),
            ),
            child: Row(
              children: [
                const Icon(Icons.school_rounded, color: Color(0xFF6D28D9), size: 22),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.isArabic
                            ? 'مساعد حل أوراق الامتحانات (منهاج الإمارات)'
                            : 'Exam Paper Assistant (UAE MoE Curriculum)',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xFF4C1D95)),
                      ),
                      Text(
                        widget.isArabic
                            ? 'حل ذاتي مباشر ودقيق مع نماذج الإجابات وتوثيق المنهج'
                            : 'Autonomous solving with model answers & textbook citations',
                        style: const TextStyle(fontSize: 10, color: Color(0xFF6D28D9)),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: const Color(0xFFECFDF5),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: const Color(0xFFA7F3D0)),
                  ),
                  child: const Text(
                    'Zero Escalation',
                    style: TextStyle(fontSize: 8.5, fontWeight: FontWeight.bold, color: Color(0xFF047857)),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),

          // Preset Sample Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                ActionChip(
                  label: const Text('📝 نموذج: امتحان الفصل الأول', style: TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold)),
                  backgroundColor: const Color(0xFFF1F5F9),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  onPressed: () {
                    setState(() {
                      _paperTitle = 'اختبار منتصف الفصل الأول - ألعاب الكرة والفروسية';
                      _paperCtrl.text =
                          'س1: كم عدد اللاعبين الأساسيين في فريق كرة القدم؟\nس2: ما هو إعراب كلمة (اللاعبُ) في جملة (سجل اللاعبُ الهدفَ)؟\nس3: ما هو مرادف كلمة (جماعية) وما ضدها؟';
                      _paperFileName = 'ورقة_امتحان_منتصف_الفصل1.pdf';
                    });
                  },
                ),
                const SizedBox(width: 6),
                ActionChip(
                  label: const Text('🎯 نموذج: تشخيص القواعد والإملاء', style: TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold)),
                  backgroundColor: const Color(0xFFF1F5F9),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  onPressed: () {
                    setState(() {
                      _paperTitle = 'اختبار تشخيص القواعد والإملاء - الصف الخامس';
                      _paperCtrl.text =
                          'س1: أين يقام كأس دبي العالمي للخيول سنوياً؟\nس2: حدد نوع الجملة والفاعل في: (يركض الفارس في الميدان).\nس3: هات مثالاً على كلمة تنتهي بتاء مربوطة وأخرى بهاء.';
                      _paperFileName = 'ورقة_تشخيص_النحو_والإملاء.pdf';
                    });
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 6),

          // Attachment Banner
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Row(
              children: [
                const Icon(Icons.attach_file_rounded, size: 16, color: Color(0xFF64748B)),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    _paperFileName != null
                        ? 'مرفق: $_paperFileName'
                        : (widget.isArabic ? 'لم يتم إرفاق ملف (ارفق PDF أو التقط صورة، أو اكتب الأسئلة أدناه)' : 'No file attached (attach PDF/photo, or write questions below)'),
                    style: TextStyle(
                      fontSize: 10.5,
                      fontWeight: FontWeight.w600,
                      color: _paperFileName != null ? const Color(0xFF0F172A) : const Color(0xFF94A3B8),
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (_paperFileName != null) ...[
                  TextButton(
                    onPressed: _pickPdf,
                    child: Text(widget.isArabic ? 'تغيير' : 'Change', style: const TextStyle(fontSize: 10.5)),
                  ),
                  InkWell(
                    onTap: () => setState(() {
                      _paperFileName = null;
                      _attachedBase64 = null;
                    }),
                    child: const Icon(Icons.close, size: 14, color: Colors.black54),
                  ),
                ] else ...[
                  TextButton.icon(
                    onPressed: _pickPdf,
                    icon: const Icon(Icons.upload_file_rounded, size: 14, color: Color(0xFF6C5CE7)),
                    label: Text(widget.isArabic ? 'إرفاق PDF' : 'Attach PDF', style: const TextStyle(fontSize: 10.5, color: Color(0xFF6C5CE7), fontWeight: FontWeight.bold)),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      minimumSize: Size.zero,
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ),
                  const SizedBox(width: 4),
                  TextButton.icon(
                    onPressed: () => _pickCameraPhoto(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt_rounded, size: 14, color: Color(0xFF059669)),
                    label: Text(widget.isArabic ? 'تصوير الورقة' : 'Photo', style: const TextStyle(fontSize: 10.5, color: Color(0xFF059669), fontWeight: FontWeight.bold)),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      minimumSize: Size.zero,
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 8),

          // Textarea for Questions
          TextField(
            controller: _paperCtrl,
            maxLines: 3,
            textDirection: TextDirection.rtl,
            style: const TextStyle(fontSize: 12),
            decoration: InputDecoration(
              hintText: 'اكتب أو الصق أسئلة ورقة الامتحان هنا...',
              hintStyle: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
              isDense: true,
              contentPadding: const EdgeInsets.all(10),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF6C5CE7), width: 1.5)),
            ),
          ),
          const SizedBox(height: 8),

          // Solve Button
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF059669),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              padding: const EdgeInsets.symmetric(vertical: 11),
            ),
            onPressed: _isSolvingPaper ? null : () => _solveExamPaper(),
            child: _isSolvingPaper
                ? Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)),
                      const SizedBox(width: 8),
                      Text(widget.isArabic ? 'جاري التحليل والحل الفوري...' : 'AI Assistant is solving...', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                    ],
                  )
                : Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.auto_awesome, color: Color(0xFFFDE047), size: 16),
                      const SizedBox(width: 6),
                      Text(
                        widget.isArabic ? 'حل ورقة الامتحان بالذكاء الاصطناعي' : 'Solve Exam Paper with AI',
                        style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
          ),

          if (_paperError != null) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFFFEF2F2),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFFECACA)),
              ),
              child: Text(
                _paperError!,
                style: const TextStyle(fontSize: 11, color: Color(0xFFB91C1C), fontWeight: FontWeight.w600),
              ),
            ),
          ],

          // Solved Questions List
          if (_solvedPaperData != null) ...[
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${_solvedPaperData!['paper_title'] ?? ''} (${_solvedPaperData!['total_questions'] ?? 0} أسئلة)',
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: const Color(0xFFECFDF5),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    widget.isArabic ? 'حل معتمد بالذكاء الاصطناعي' : 'AI Verified Solution',
                    style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF065F46)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            ...(_solvedPaperData!['questions'] as List? ?? []).map((q) {
              final qMap = Map<String, dynamic>.from(q as Map);
              final qNum = qMap['question_number'] ?? 1;
              final qType = qMap['question_type'] ?? '';
              final qAr = qMap['question_text_ar'] ?? '';
              final qEn = qMap['question_text_en'];
              final rawAnsAr = qMap['model_answer_ar'] ?? '';
              final rawAnsEn = qMap['model_answer_en'];
              final ansAr = _cleanAnswerText(rawAnsAr.toString());
              final ansEn = rawAnsEn != null ? _cleanAnswerText(rawAnsEn.toString()) : null;
              final expAr = qMap['explanation_ar'] ?? '';
              final expEn = qMap['explanation_en'];
              final ruleAr = qMap['rule_summary_ar'];
              final ref = qMap['textbook_reference'] ?? 'منهاج الإمارات';

              return Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.03),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Question Number and Type Header
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            CircleAvatar(
                              radius: 11,
                              backgroundColor: const Color(0xFFEDE9FE),
                              child: Text(
                                '$qNum',
                                style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF6D28D9)),
                              ),
                            ),
                            const SizedBox(width: 6),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                              decoration: BoxDecoration(
                                color: const Color(0xFFF1F5F9),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                qType.toString().toUpperCase(),
                                style: const TextStyle(fontSize: 8.5, fontWeight: FontWeight.bold, color: Color(0xFF64748B)),
                              ),
                            ),
                          ],
                        ),
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            InkWell(
                              onTap: () => _vocalize(qAr),
                              borderRadius: BorderRadius.circular(12),
                              child: const Padding(
                                padding: EdgeInsets.all(4),
                                child: Icon(Icons.volume_up_rounded, size: 16, color: Color(0xFF6C5CE7)),
                              ),
                            ),
                            if (qEn != null && qEn.toString().trim().isNotEmpty) ...[
                              const SizedBox(width: 4),
                              InkWell(
                                onTap: () => _vocalize(qEn.toString()),
                                borderRadius: BorderRadius.circular(12),
                                child: const Padding(
                                  padding: EdgeInsets.all(4),
                                  child: Icon(Icons.volume_up_outlined, size: 15, color: Color(0xFF047857)),
                                ),
                              ),
                            ],
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),

                    // Arabic Question Text
                    Directionality(
                      textDirection: TextDirection.rtl,
                      child: Text(
                        qAr,
                        style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF0F172A), height: 1.35),
                      ),
                    ),
                    ValueListenableBuilder<bool>(
                      valueListenable: ArabEnglishState.notifier,
                      builder: (context, isArabEnOn, _) {
                        if (!isArabEnOn) return const SizedBox.shrink();
                        final arabEn = ArabEnglishHelper.transliterate(qAr);
                        if (arabEn.isEmpty) return const SizedBox.shrink();
                        return Container(
                          margin: const EdgeInsets.only(top: 3, bottom: 2),
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF1F5F9),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: const Color(0xFFCBD5E1)),
                          ),
                          child: Text(
                            '🗣️ $arabEn',
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                        );
                      },
                    ),
                    if (qEn != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        qEn,
                        style: const TextStyle(fontSize: 10, color: Color(0xFF64748B), fontStyle: FontStyle.italic),
                      ),
                    ],
                    const SizedBox(height: 8),

                    // Model Answer Box
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: const Color(0xFFECFDF5),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFA7F3D0)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Row(
                                children: [
                                  Icon(Icons.check_circle_rounded, size: 14, color: Color(0xFF059669)),
                                  SizedBox(width: 4),
                                  Text(
                                    'الإجابة النموذجية · Model Answer',
                                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF065F46)),
                                  ),
                                ],
                              ),
                              Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  InkWell(
                                    onTap: () => _vocalize(ansAr),
                                    borderRadius: BorderRadius.circular(12),
                                    child: const Padding(
                                      padding: EdgeInsets.all(2),
                                      child: Icon(Icons.volume_up_rounded, size: 15, color: Color(0xFF059669)),
                                    ),
                                  ),
                                  if (ansEn != null && ansEn.toString().trim().isNotEmpty) ...[
                                    const SizedBox(width: 6),
                                    InkWell(
                                      onTap: () => _vocalize(ansEn.toString()),
                                      borderRadius: BorderRadius.circular(12),
                                      child: const Padding(
                                        padding: EdgeInsets.all(2),
                                        child: Icon(Icons.volume_up_outlined, size: 14, color: Color(0xFF047857)),
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Directionality(
                            textDirection: TextDirection.rtl,
                            child: Text(
                              ansAr,
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF064E3B), height: 1.35),
                            ),
                          ),
                          ValueListenableBuilder<bool>(
                            valueListenable: ArabEnglishState.notifier,
                            builder: (context, isArabEnOn, _) {
                              if (!isArabEnOn) return const SizedBox.shrink();
                              final arabEn = ArabEnglishHelper.transliterate(ansAr);
                              if (arabEn.isEmpty) return const SizedBox.shrink();
                              return Container(
                                margin: const EdgeInsets.only(top: 3, bottom: 2),
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFD1FAE5),
                                  borderRadius: BorderRadius.circular(6),
                                  border: Border.all(color: const Color(0xFFA7F3D0)),
                                ),
                                child: Text(
                                  '🗣️ $arabEn',
                                  style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                    color: Color(0xFF064E3B),
                                  ),
                                ),
                              );
                            },
                          ),
                          if (ansEn != null) ...[
                            const SizedBox(height: 2),
                            Text(ansEn, style: const TextStyle(fontSize: 9.5, color: Color(0xFF047857))),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(height: 6),

                    // Linguistic Rationale / Grammar Rule
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const Text(
                            'الشرح والتعليل اللغوي:',
                            style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.bold, color: Color(0xFF475569)),
                          ),
                          const SizedBox(height: 2),
                          Directionality(
                            textDirection: TextDirection.rtl,
                            child: Text(
                              expAr,
                              style: const TextStyle(fontSize: 11, color: Color(0xFF1E293B), height: 1.3),
                            ),
                          ),
                          if (expEn != null) ...[
                            const SizedBox(height: 2),
                            Text(expEn, style: const TextStyle(fontSize: 9.5, color: Color(0xFF64748B), fontStyle: FontStyle.italic)),
                          ],
                          if (ruleAr != null) ...[
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                              decoration: BoxDecoration(
                                color: const Color(0xFFF5F3FF),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: const Color(0xFFDDD6FE)),
                              ),
                              child: Directionality(
                                textDirection: TextDirection.rtl,
                                child: Text('💡 $ruleAr', style: const TextStyle(fontSize: 9.5, fontWeight: FontWeight.bold, color: Color(0xFF5B21B6))),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(height: 6),

                    // Footer with Textbook Reference and Escalation
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.menu_book_rounded, size: 12, color: Color(0xFF6C5CE7)),
                            const SizedBox(width: 4),
                            Text(
                              ref,
                              style: const TextStyle(fontSize: 9.5, fontWeight: FontWeight.w600, color: Color(0xFF64748B)),
                            ),
                          ],
                        ),
                        InkWell(
                          onTap: () => _escalateQuestion(qNum, qAr),
                          child: const Row(
                            children: [
                              Icon(Icons.person_pin, size: 12, color: Color(0xFFD97706)),
                              SizedBox(width: 3),
                              Text(
                                'طلب مراجعة المعلم',
                                style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.bold, color: Color(0xFFB45309)),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            }),
          ],
        ],
      ),
    );
  }

  Widget _modeTab(String mode, IconData icon, String label) {
    final bool isSelected = _activeMode == mode;
    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: () => _selectMode(mode),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 10),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.06),
                    blurRadius: 4,
                    offset: const Offset(0, 1),
                  ),
                ]
              : null,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 13,
              color: isSelected ? const Color(0xFF6C5CE7) : const Color(0xFF64748B),
            ),
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
                color: isSelected ? const Color(0xFF6C5CE7) : const Color(0xFF64748B),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _actionChipCustom({
    required IconData icon,
    required String labelAr,
    required String labelEn,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: ActionChip(
        backgroundColor: color.withValues(alpha: 0.1),
        side: BorderSide(color: color.withValues(alpha: 0.35)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 0),
        avatar: Icon(icon, size: 14, color: color),
        label: Text(
          widget.isArabic ? labelAr : labelEn,
          style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.bold),
        ),
        onPressed: onTap,
      ),
    );
  }

  Widget _suggestionChip(String promptAr, String promptEn, {String? displayAr, String? displayEn}) {
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: ActionChip(
        backgroundColor: const Color(0xFFF1F0FB),
        side: const BorderSide(color: Color(0xFFE9D5FF)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 0),
        avatar: InkWell(
          onTap: () => _vocalize(promptAr),
          child: const Icon(Icons.volume_up_rounded, size: 14, color: Color(0xFF6C5CE7)),
        ),
        label: Text(
          widget.isArabic ? (displayAr ?? promptAr) : (displayEn ?? promptEn),
          style: const TextStyle(fontSize: 10, color: Color(0xFF6C5CE7), fontWeight: FontWeight.bold),
        ),
        onPressed: () => _send(promptAr, promptEn),
      ),
    );
  }
}

import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';

import 'api_service.dart';
import 'auth_service.dart';
import 'arab_english_service.dart';
import 'dialogs/ask_fahim_dialog.dart';
import 'dialogs/auth_dialog.dart';
import 'dialogs/feedback_dialog.dart';
import 'dialogs/paywall_dialog.dart';
import 'models/curriculum_models.dart';
import 'screens/catalogue_screen.dart';
import 'screens/learning_views.dart';
import 'screens/lesson_player_screen.dart';
import 'screens/mindmap_screen.dart';
import 'screens/textbook_reader_screen.dart';

void main() {
  runApp(const JisrArabicApp());
}

class JisrArabicApp extends StatelessWidget {
  const JisrArabicApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JISR (جسر) — Arabic Learning Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF8F9FE),
        colorScheme: const ColorScheme.light(
          primary: Color(0xFF6C5CE7), // JISR Brand Purple
          secondary: Color(0xFF22C55E), // JISR Accent Green
          surface: Colors.white,
          onPrimary: Colors.white,
          onSecondary: Colors.white,
          onSurface: Color(0xFF1E293B),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF6C5CE7),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            elevation: 2,
            textStyle: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: const Color(0xFF6C5CE7),
            side: const BorderSide(color: Color(0xFF6C5CE7), width: 1.5),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          ),
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 1,
          shadowColor: const Color(0xFF6C5CE7).withValues(alpha: 0.08),
          shape: RoundedRectangleBorder(
            side: const BorderSide(color: Color(0xFFF1F0FA), width: 1),
            borderRadius: BorderRadius.circular(20),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: Color(0xFF6C5CE7), width: 2),
          ),
        ),
      ),
      home: const MainScreen(),
    );
  }
}

// Global API Base
String get kApiBase => apiBase;

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  final AuthService _auth = AuthService();
  final ApiService _api = ApiService();
  final FlutterTts _flutterTts = FlutterTts();

  // Session state
  Map<String, dynamic>? _activeChild;
  String? _token;
  Map<String, dynamic>? _user;
  List<Map<String, dynamic>> _childrenList = [];
  List<Map<String, dynamic>> _remoteLessons = [];
  List<Map<String, dynamic>> _remoteCapsules = [];
  bool _learningDataLoading = false;

  // Navigation
  int _currentGrade = 5;
  int _currentTerm = 1;
  String _activeView = 'landing'; // 'landing', 'catalogue', 'lesson', 'profile', 'malazim', 'capsules', 'tests', 'mastery', 'ranks', 'parent', 'tutor'
  String _selectedLessonId = 'lesson_01_ball_games';
  CurriculumLessonPackage? _activeLessonPackage;
  LessonViewMode _activeLessonMode = LessonViewMode.textbookReader;
  bool _isArabic = false;

  // Learning Modules State
  final Set<String> _completedCapsules = {'capsule_01_taa_marbutah'};

  // Universal Sticky Audio Toolbar State (Matching Web App AudioToolbar with Hide/Show)
  bool _isAudioToolbarOpen = true;
  bool _isPlaying = false;
  double _playbackSpeed = 0.6; // 1.0 (Normal), 0.6 (Slow), 0.3 (Very slow)
  int _repeatCount = 1; // 1, 2, 3
  int _currentRepeatIndex = 0;
  String _currentSpeechText = '';
  String _speakingStatus = 'Audio Ready';
  String _activeWord = '';

  @override
  void initState() {
    super.initState();
    _activeLessonPackage = CurriculumLessonPackage.fromStaticChapter1();
    _initTts();
    _restoreSession();
  }

  @override
  void dispose() {
    _flutterTts.stop();
    super.dispose();
  }

  Future<void> _initTts() async {
    try {
      final isAeAvailable = await _flutterTts.isLanguageAvailable("ar-AE");
      if (isAeAvailable == true) {
        await _flutterTts.setLanguage('ar-AE');
      } else {
        await _flutterTts.setLanguage('ar-SA');
      }
      _applyTtsSpeed();
      await _flutterTts.setPitch(1.0);
      await _flutterTts.setVolume(1.0);

      _flutterTts.setStartHandler(() {
        if (mounted) {
          setState(() {
            _isPlaying = true;
            _speakingStatus = _isArabic ? 'جارٍ النطق الصوتي...' : 'Speaking Arabic...';
          });
        }
      });

      _flutterTts.setCompletionHandler(() async {
        if (_isPlaying && _currentRepeatIndex < _repeatCount && _currentSpeechText.isNotEmpty) {
          _currentRepeatIndex++;
          await Future.delayed(const Duration(milliseconds: 350));
          if (mounted && _isPlaying) {
            await _flutterTts.speak(_currentSpeechText);
            return;
          }
        }
        if (mounted) {
          setState(() {
            _isPlaying = false;
            _speakingStatus = _isArabic ? 'الصوت جاهز' : 'Audio Ready';
            _activeWord = '';
            _currentRepeatIndex = 0;
          });
        }
      });

      _flutterTts.setErrorHandler((msg) {
        if (mounted) {
          setState(() {
            _isPlaying = false;
            _speakingStatus = _isArabic ? 'الصوت جاهز' : 'Audio Ready';
            _activeWord = '';
            _currentRepeatIndex = 0;
          });
        }
      });
    } catch (e) {
      debugPrint('TTS Init Error: $e');
    }
  }

  Future<void> _restoreSession() async {
    try {
      final savedLang = await _auth.storage.read(key: 'app_language');
      if (mounted && savedLang != null) {
        setState(() {
          _isArabic = (savedLang == 'ar');
        });
      }
    } catch (_) {}
    final authData = await _auth.restore();
    if (mounted) {
      if (authData != null) {
        _applyAuth(authData);
        setState(() => _activeView = 'catalogue');
      } else {
        setState(() => _activeView = 'landing');
      }
    }
    await _loadRemoteLearningData();
  }

  Future<void> _setLanguage(bool isArabic) async {
    setState(() {
      _isArabic = isArabic;
    });
    try {
      await _auth.storage.write(key: 'app_language', value: isArabic ? 'ar' : 'en');
    } catch (_) {}
  }

  Future<void> _loadRemoteLearningData() async {
    if (_learningDataLoading) return;
    setState(() => _learningDataLoading = true);
    try {
      final results = await Future.wait([
        _api.lessons(
          grade: _currentGrade,
          term: _currentTerm,
          childId: _activeChild?['id']?.toString(),
          token: _token,
        ),
        _api.capsules(
          childId: _activeChild?['id']?.toString(),
          token: _token,
        ),
      ]);
      final lessons = results[0];
      final capsules = results[1];
      if (!mounted) return;
      setState(() {
        _remoteLessons = (lessons is List
                ? lessons
                : (lessons is Map ? (lessons['lessons'] as List? ?? []) : []))
            .whereType<Map>()
            .map((e) => Map<String, dynamic>.from(e))
            .toList();
        _remoteCapsules = (capsules is List
                ? capsules
                : (capsules is Map ? (capsules['capsules'] as List? ?? []) : []))
            .whereType<Map>()
            .map((e) => Map<String, dynamic>.from(e))
            .toList();
        _learningDataLoading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _learningDataLoading = false);
    }
  }

  Future<void> _loadLesson(String lessonId, {LessonViewMode mode = LessonViewMode.textbookReader}) async {
    if (_token == null && lessonId != 'lesson_01_ball_games') {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_isArabic
              ? 'يرجى تسجيل الدخول للوصول إلى دروس المنهاج المقفلة.'
              : 'Please sign in to access locked curriculum lessons.'),
          backgroundColor: const Color(0xFF58337E),
          behavior: SnackBarBehavior.floating,
          action: SnackBarAction(
            label: _isArabic ? 'دخول' : 'Sign In',
            textColor: Colors.amber,
            onPressed: () => _showAuthDialog(),
          ),
        ),
      );
      _showAuthDialog();
      return;
    }

    setState(() {
      _selectedLessonId = lessonId;
      _activeLessonMode = mode;
      _learningDataLoading = true;
    });

    try {
      final response = await _api.lesson(
        lessonId,
        childId: _activeChild?['id']?.toString(),
        token: _token,
      );
      if (!mounted) return;
      if (response is Map<String, dynamic> || response is Map) {
        final mapData = Map<String, dynamic>.from(response as Map);
        try {
          await _auth.storage.write(
            key: 'cached_lesson_$lessonId',
            value: jsonEncode(mapData),
          );
        } catch (_) {}
        final package = CurriculumLessonPackage.fromBackend(lessonId, mapData);
        setState(() {
          _activeLessonPackage = package;
          _activeView = 'lesson';
          _learningDataLoading = false;
        });
        return;
      }
    } on AuthException catch (e) {
      if (!mounted) return;
      setState(() => _learningDataLoading = false);
      if (e.message.contains('Payment required') ||
          e.message.contains('locked') ||
          e.message.contains('402')) {
        if (_user?['role'] == 'admin') {
          setState(() {
            _activeLessonPackage = CurriculumLessonPackage.fromStaticChapter1();
            _activeView = 'lesson';
          });
          return;
        }
        _showPaywallDialog(_currentGrade, _currentTerm);
        return;
      }
      if (e.message.contains('Authentication required') ||
          e.message.contains('Unauthorized')) {
        _showAuthDialog();
        return;
      }
      if (lessonId == 'lesson_01_ball_games') {
        setState(() {
          _activeLessonPackage = CurriculumLessonPackage.fromStaticChapter1();
          _activeView = 'lesson';
        });
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message), backgroundColor: Colors.red.shade700),
      );
      return;
    } catch (err) {
      if (!mounted) return;
      setState(() => _learningDataLoading = false);
      if (lessonId == 'lesson_01_ball_games') {
        setState(() {
          _activeLessonPackage = CurriculumLessonPackage.fromStaticChapter1();
          _activeView = 'lesson';
        });
        return;
      }
      try {
        final cachedJson = await _auth.storage.read(key: 'cached_lesson_$lessonId');
        if (cachedJson != null && cachedJson.isNotEmpty) {
          final mapData = Map<String, dynamic>.from(jsonDecode(cachedJson) as Map);
          final package = CurriculumLessonPackage.fromBackend(lessonId, mapData);
          if (mounted) {
            setState(() {
              _activeLessonPackage = package;
              _activeView = 'lesson';
            });
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(_isArabic
                    ? 'تم فتح الدرس من الذاكرة المحلية (بدون اتصال بالإنترنت)'
                    : 'Loaded lesson from offline cache'),
                backgroundColor: const Color(0xFF58337E),
              ),
            );
            return;
          }
        }
      } catch (_) {}
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not load lesson: $err'),
          backgroundColor: Colors.red.shade700,
        ),
      );
      return;
    }

    if (lessonId == 'lesson_01_ball_games') {
      setState(() {
        _activeLessonPackage = CurriculumLessonPackage.fromStaticChapter1();
        _activeView = 'lesson';
        _learningDataLoading = false;
      });
    }
  }

  void _applyAuth(Map<String, dynamic> authData) {
    setState(() {
      if (authData['access_token'] != null) {
        _token = authData['access_token'];
      }
      if (authData['user'] != null) {
        _user = Map<String, dynamic>.from(authData['user'] ?? {});
        final raw = _user?['children'] as List? ?? [];
        _childrenList = raw.map((e) => Map<String, dynamic>.from(e)).toList();
      }
      if (authData['child'] != null) {
        final newChild = Map<String, dynamic>.from(authData['child']);
        _childrenList = [
          ..._childrenList.where((c) => c['id'] != newChild['id']),
          newChild
        ];
        _activeChild = newChild;
      }
      if (authData.containsKey('active_child')) {
        _activeChild = authData['active_child'] == null
            ? null
            : Map<String, dynamic>.from(authData['active_child']);
      }
      if (_activeChild == null && _childrenList.isNotEmpty) {
        _activeChild = _childrenList.first;
      }
      if (_user?['role'] == 'admin' && _activeChild == null) {
        _activeChild = {
          'id': 'admin_supervisor',
          'name': _isArabic ? 'مشرف المنصة (Admin)' : 'Admin Supervisor',
          'default_grade': _currentGrade,
          'avatar_id': 'avatar_falcon',
          'diagnostic_level': 'ADMIN',
          'diagnostic_score': 100,
        };
      }
      if (_activeChild != null) {
        _currentGrade = _activeChild!['default_grade'] ?? 5;
        _currentTerm = 1;
      }
      _activeView = 'catalogue';
    });
    if (_activeChild != null) {
      _auth.storage.write(key: 'active_child_id', value: _activeChild!['id']?.toString());
    }
    if (_user?['role'] == 'admin' && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.shield, color: Color(0xFFFBBF24), size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _isArabic
                      ? 'مرحباً بالمسؤول! تم تسجيل الدخول بصلاحيات الإشراف والوصول الشامل.'
                      : 'Welcome Administrator! Full supervisor & platform access unlocked.',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                ),
              ),
            ],
          ),
          backgroundColor: const Color(0xFF4C1D95),
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 4),
        ),
      );
    }
    _loadRemoteLearningData();
  }

  Future<void> _logout() async {
    await _auth.logout(_token);
    if (!mounted) return;
    setState(() {
      _token = null;
      _user = null;
      _activeChild = null;
      _childrenList = [];
      _activeView = 'landing';
    });
  }

  Future<void> _handleDeleteAccount() async {
    if (_token == null) return;
    try {
      await _auth.deleteAccount(_token!);
      if (!mounted) return;
      setState(() {
        _token = null;
        _user = null;
        _activeChild = null;
        _childrenList = [];
        _activeView = 'landing';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_isArabic
              ? 'تم حذف الحساب وجميع البيانات المرتبطة به بنجاح.'
              : 'Account and all associated data have been permanently deleted.'),
          backgroundColor: const Color(0xFF064E3B),
        ),
      );
    } on AuthException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.message),
          backgroundColor: Colors.red.shade800,
        ),
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_isArabic
              ? 'حدث خطأ أثناء حذف الحساب.'
              : 'An error occurred while deleting account.'),
          backgroundColor: Colors.red.shade800,
        ),
      );
    }
  }

  String _getAvatarIcon(dynamic avatarId) {
    switch (avatarId) {
      case 'avatar_falcon':
        return '🦅';
      case 'avatar_gazelle':
        return '🦌';
      case 'avatar_oryx':
        return '🦬';
      case 'avatar_camel':
        return '🐪';
      case 'avatar_palm':
        return '🌴';
      default:
        return '🦅';
    }
  }

  void _applyTtsSpeed() {
    double rate = 0.32;
    if (_playbackSpeed == 1.0) {
      rate = 0.48;
    } else if (_playbackSpeed == 0.6) {
      rate = 0.32;
    } else if (_playbackSpeed == 0.3) {
      rate = 0.18;
    }
    _flutterTts.setSpeechRate(rate);
  }

  void _stopAudio() async {
    try {
      await _flutterTts.stop();
    } catch (_) {}
    if (mounted) {
      setState(() {
        _isPlaying = false;
        _speakingStatus = _isArabic ? 'الصوت جاهز' : 'Audio Ready';
        _activeWord = '';
        _currentRepeatIndex = 0;
      });
    }
  }

  Future<void> _vocalizeText(String text) async {
    final cleanSpeech = text
        .replaceAll(RegExp(r'[\[\](){}\*#«»<>]'), '')
        .replaceAll("'", '')
        .replaceAll('"', '')
        .trim();
    if (cleanSpeech.isEmpty) return;
    final firstWord = cleanSpeech.split(RegExp(r'\s+')).first;
    setState(() {
      _currentSpeechText = cleanSpeech;
      _activeWord = firstWord;
      _isPlaying = true;
      _currentRepeatIndex = 1;
      _speakingStatus = cleanSpeech.length > 25
          ? (_isArabic ? 'جارٍ نطق الجملة...' : 'Speaking sentence...')
          : (_isArabic ? 'جارٍ النطق: $cleanSpeech' : 'Speaking: $cleanSpeech');
    });
    try {
      await _flutterTts.stop();
      final hasArabic = RegExp(r'[\u0600-\u06FF]').hasMatch(cleanSpeech);
      if (hasArabic) {
        final isAeAvailable = await _flutterTts.isLanguageAvailable("ar-AE");
        await _flutterTts.setLanguage(isAeAvailable == true ? 'ar-AE' : 'ar-SA');
      } else {
        await _flutterTts.setLanguage('en-US');
      }
      _applyTtsSpeed();
      await _flutterTts.speak(cleanSpeech);
    } catch (e) {
      debugPrint('TTS Speak Error: $e');
      Future.delayed(const Duration(milliseconds: 1400), () {
        if (mounted) {
          setState(() {
            _isPlaying = false;
            _speakingStatus = _isArabic ? 'الصوت جاهز' : 'Audio Ready';
            _activeWord = '';
            _currentRepeatIndex = 0;
          });
        }
      });
    }
  }

  void _showChildSwitcherSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
      builder: (ctx) => Container(
        color: Colors.white,
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'LEARNER PROFILES (ملفات الطلاب)',
              style: TextStyle(
                fontWeight: FontWeight.w900,
                fontSize: 14,
                color: Color(0xFF064E3B),
              ),
            ),
            const SizedBox(height: 12),
            ..._childrenList.map((c) {
              final isCurrent = _activeChild?['id'] == c['id'];
              final icon = _getAvatarIcon(c['avatar_id']);
              return ListTile(
                shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
                tileColor: isCurrent ? const Color(0xFFECFDF5) : Colors.transparent,
                leading: Text(icon, style: const TextStyle(fontSize: 22)),
                title: Text(
                  c['name'] ?? 'Learner',
                  style: TextStyle(
                    fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                  ),
                ),
                subtitle: Text('Class ${c['default_grade'] ?? 5}'),
                trailing: isCurrent
                    ? const Icon(Icons.check_circle, color: Color(0xFF064E3B))
                    : null,
                onTap: () async {
                  Navigator.of(ctx).pop();
                  if (_token == null) return;
                  try {
                    _applyAuth(await _auth.switchChild(_token!, c['id'].toString()));
                  } on AuthException catch (error) {
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(error.message)),
                      );
                    }
                  }
                },
              );
            }),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.add_circle_outline, color: Color(0xFF064E3B)),
              title: const Text(
                '+ Add Child Profile (إضافة طالب)',
                style: TextStyle(color: Color(0xFF064E3B), fontWeight: FontWeight.bold),
              ),
              onTap: () {
                Navigator.of(ctx).pop();
                _showAuthDialog(isAddChildOnly: true);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showAuthDialog({bool isAddChildOnly = false}) {
    showDialog(
      context: context,
      builder: (ctx) => AuthDialog(
        isAddChildOnly: isAddChildOnly,
        token: _token,
        isArabic: _isArabic,
        onLanguageChanged: (val) {
          _setLanguage(val);
        },
        onSuccess: _applyAuth,
      ),
    );
  }

  void _showPaywallDialog(int grade, int term) {
    showDialog(
      context: context,
      builder: (ctx) => PaywallDialog(
        grade: grade,
        term: term,
        activeChild: _activeChild,
        token: _token,
        isArabic: _isArabic,
        onUnlockedTerms: (unlockedTerms) {
          if (_activeChild != null) {
            final existing = List<String>.from((_activeChild!['unlocked_terms'] as List?) ?? []);
            for (final t in unlockedTerms) {
              final key = 'grade_${grade}_term_$t';
              if (!existing.contains(key)) existing.add(key);
              if (!existing.contains('$t')) existing.add('$t');
            }
            _activeChild!['unlocked_terms'] = existing;
            _activeChild!['is_unlocked'] = true;
          }
        },
        onUnlocked: () async {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              backgroundColor: const Color(0xFF064E3B),
              content: Text(_isArabic
                  ? 'تم تأكيد الدفع وتفعيل المنهاج بنجاح!'
                  : 'Class $grade Term(s) successfully unlocked!'),
              behavior: SnackBarBehavior.floating,
              shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
            ),
          );
          if (_token != null && _activeChild?['id'] != null) {
            try {
              final updatedChild = await _auth.switchChild(_token!, _activeChild!['id'].toString());
              _applyAuth(updatedChild);
            } catch (_) {}
          }
          await _loadRemoteLearningData();
          if (mounted) setState(() {});
        },
      ),
    );
  }

  bool _hasPaidOrAdminAccess([int? grade, int? term]) {
    if (_user?['role'] == 'admin') return true;
    final g = grade ?? _currentGrade;
    final unlockedTerms = (_activeChild?['unlocked_terms'] as List?) ?? [];
    if (term != null) {
      final t = term;
      final termKey = 'grade_${g}_term_$t';
      return unlockedTerms.contains(termKey) ||
          unlockedTerms.contains(t) ||
          unlockedTerms.contains('$t');
    }
    return unlockedTerms.isNotEmpty || _activeChild?['is_unlocked'] == true;
  }

  void _showAskFahimDialog({
    String initialMode = 'text',
    String? initialFileName,
    String? initialFileBase64,
    String? initialFileType,
  }) {
    final canAccessAi = _hasPaidOrAdminAccess();
    if (!canAccessAi) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_isArabic
              ? 'مساعد المعلم الذكي (فاهم) يتطلب تفعيل الاشتراك في المنهاج.'
              : 'Ask Fahim AI Tutor requires an active subscription to access.'),
          backgroundColor: const Color(0xFF58337E),
          behavior: SnackBarBehavior.floating,
          action: SnackBarAction(
            label: _isArabic ? 'ترقية' : 'Upgrade',
            textColor: Colors.amber,
            onPressed: () => _showPaywallDialog(_currentGrade, _currentTerm),
          ),
        ),
      );
      _showPaywallDialog(_currentGrade, _currentTerm);
      return;
    }

    showDialog(
      context: context,
      builder: (ctx) => AskFahimDialog(
        contextLessonId: _selectedLessonId,
        childId: _activeChild?['id']?.toString(),
        token: _token,
        initialMode: initialMode,
        isArabic: _isArabic,
        onVocalize: _vocalizeText,
        initialFileName: initialFileName,
        initialFileBase64: initialFileBase64,
        initialFileType: initialFileType,
      ),
    );
  }

  Future<void> _pickAndOpenPdf() async {
    final canAccessAi = _hasPaidOrAdminAccess();
    if (!canAccessAi) {
      _showPaywallDialog(_currentGrade, _currentTerm);
      return;
    }

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
            debugPrint('Error reading pick stream: $streamErr');
          }
        }
        if (bytes == null && picked.path != null && !kIsWeb) {
          try {
            final f = File(picked.path!);
            if (await f.exists()) {
              bytes = await f.readAsBytes();
            }
          } catch (_) {}
        }
        final base64Str = (bytes != null && bytes.isNotEmpty) ? base64Encode(bytes) : null;
        if (mounted) {
          _showAskFahimDialog(
            initialMode: 'pdf',
            initialFileName: picked.name,
            initialFileBase64: base64Str,
            initialFileType: 'pdf',
          );
        }
        return;
      }
    } catch (e) {
      debugPrint('Error picking PDF from main screen: $e');
    }
  }

  List<CurriculumLessonItem> get _catalogLessons {
    final bool hasPaid = _hasPaidOrAdminAccess(_currentGrade, _currentTerm);
    final rawList = _remoteLessons.isNotEmpty
        ? _remoteLessons.map((m) => CurriculumLessonItem.fromMap(m)).toList()
        : kClass5Term1Catalogue;

    return rawList.map((item) {
      final isFirstChapterDemo = _currentTerm == 1 && (item.order == 1 || item.isFirstChapterDemo);
      final accessible = hasPaid || isFirstChapterDemo;
      return CurriculumLessonItem(
        id: item.id,
        order: item.order,
        titleAr: item.titleAr,
        titleEn: item.titleEn,
        unitTitleAr: item.unitTitleAr,
        unitTitleEn: item.unitTitleEn,
        startPage: item.startPage,
        isFirstChapterDemo: isFirstChapterDemo,
        isAccessible: accessible,
        lockReason: accessible
            ? null
            : (_currentTerm == 1
                ? r'Subscription required (USD 20/term)'
                : r'Term subscription required (USD 20/term)'),
      );
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    if (_activeView == 'landing' || _token == null) {
      return Scaffold(
        body: AuthDialog(
          isFullScreen: true,
          token: _token,
          isArabic: _isArabic,
          onLanguageChanged: (val) => _setLanguage(val),
          onSuccess: (authData) {
            _applyAuth(authData);
            setState(() {
              _activeView = 'catalogue';
            });
          },
        ),
      );
    }

    return Scaffold(
      drawer: _buildLhsDrawer(),
      appBar: AppBar(
        backgroundColor: const Color(0xFF58337E),
        elevation: 0,
        leading: Builder(
          builder: (ctx) => IconButton(
            icon: const Icon(Icons.menu, color: Colors.white),
            tooltip: _isArabic ? 'القائمة الرئيسية' : 'Main Menu',
            onPressed: () => Scaffold.of(ctx).openDrawer(),
          ),
        ),
        title: InkWell(
          onTap: _token != null ? _showChildSwitcherSheet : _showAuthDialog,
          child: Row(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.asset(
                  'assets/icon.png',
                  width: 36,
                  height: 36,
                  fit: BoxFit.cover,
                  errorBuilder: (_, error, stack) => Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: const Color(0xFF58337E),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    alignment: Alignment.center,
                    child: const Text(
                      'ج',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: const [
                      Text(
                        'JISR ',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w900,
                          fontSize: 16,
                          letterSpacing: 0.5,
                        ),
                      ),
                      Text(
                        'جسر',
                        style: TextStyle(
                          color: Color(0xFFA29BFE),
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
        actions: [
          const ArabEnglishToggleSwitch(compact: true),
          Container(
            margin: const EdgeInsets.symmetric(vertical: 10, horizontal: 3),
            decoration: BoxDecoration(
              color: const Color(0xFF4C1D95),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFFA78BFA).withValues(alpha: 0.6)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.15),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: InkWell(
              borderRadius: BorderRadius.circular(20),
              onTap: () => _setLanguage(!_isArabic),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 4),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.language, color: Color(0xFFFDE047), size: 12),
                    const SizedBox(width: 3),
                    Text(
                      _isArabic ? 'العربية' : 'English',
                      style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 10.5),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 9, horizontal: 2),
            child: ElevatedButton.icon(
              onPressed: _showAskFahimDialog,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6C5CE7),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                elevation: 0,
                minimumSize: Size.zero,
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
              icon: const Icon(Icons.auto_awesome, size: 11, color: Color(0xFFFBBF24)),
              label: Text(
                _isArabic ? 'اسأل فاهم' : 'Ask Fahim',
                style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold),
              ),
            ),
          ),
          const SizedBox(width: 2),
          if (_user?['role'] == 'admin')
            IconButton(
              icon: const Icon(Icons.admin_panel_settings, color: Color(0xFFFBBF24)),
              tooltip: _isArabic ? 'إدارة المنهاج (مشرف)' : 'Admin Workflow',
              onPressed: () => setState(() => _activeView = 'admin'),
            ),
          IconButton(
            icon: Icon(
              _token != null ? Icons.account_circle : Icons.person_outline,
              color: Colors.white,
            ),
            onPressed: () {
              if (_token == null) {
                _showAuthDialog();
              } else {
                setState(() {
                  _activeView = 'profile';
                });
              }
            },
            tooltip: _user != null
                ? 'Signed in as ${_user!['email']}'
                : 'Sign In / Register',
          ),
        ],
      ),
      bottomNavigationBar: _isAudioToolbarOpen ? _buildAudioToolbar() : null,
      floatingActionButton: !_isAudioToolbarOpen
          ? FloatingActionButton.extended(
              onPressed: () {
                setState(() {
                  _isAudioToolbarOpen = true;
                });
              },
              backgroundColor: const Color(0xFF0F172A),
              foregroundColor: Colors.white,
              elevation: 8,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: const BorderSide(color: Color(0xFF334155)),
              ),
              icon: const Icon(Icons.volume_up, size: 18, color: Color(0xFF10B981)),
              label: Text(
                _isArabic ? 'إظهار عناصر التحكم بالصوت' : 'Show audio controls',
                style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.bold),
              ),
            )
          : null,
      body: _buildActiveView(),
    );
  }

  Widget _buildAudioToolbar() {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        border: Border(
          top: BorderSide(
            color: _isPlaying ? const Color(0xFF10B981) : const Color(0xFF1E293B),
            width: 2,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.25),
            blurRadius: 10,
            offset: const Offset(0, -3),
          ),
        ],
      ),
      padding: const EdgeInsets.fromLTRB(14, 8, 14, 10),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top Row: Status, Synthetic Badge, Stop button, Close button
            Row(
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  padding: const EdgeInsets.all(5),
                  decoration: BoxDecoration(
                    color: _isPlaying ? const Color(0xFF059669) : const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Icon(
                    _isPlaying ? Icons.volume_up : Icons.volume_mute,
                    color: Colors.white,
                    size: 16,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Row(
                    children: [
                      Text(
                        _speakingStatus,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                        decoration: BoxDecoration(
                          color: const Color(0xFF92400E).withValues(alpha: 0.8),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          _isArabic ? 'نطق آلي معتمد' : 'Synthetic Speech (نطق آلي)',
                          style: const TextStyle(
                            color: Color(0xFFFDE68A),
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                if (_isPlaying) ...[
                  InkWell(
                    onTap: _stopAudio,
                    borderRadius: BorderRadius.circular(4),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF991B1B),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: const Color(0xFFDC2626)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.stop, color: Colors.white, size: 12),
                          const SizedBox(width: 3),
                          Text(
                            _isArabic ? 'إيقاف' : 'Stop',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                ],
                IconButton(
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  icon: const Icon(Icons.close, color: Colors.white70, size: 18),
                  tooltip: _isArabic ? 'إخفاء عناصر التحكم بالصوت' : 'Hide audio toolbar',
                  onPressed: () {
                    _stopAudio();
                    setState(() {
                      _isAudioToolbarOpen = false;
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 4),

            // Active Spoken Text Preview
            Text(
              _currentSpeechText.isNotEmpty
                  ? _currentSpeechText
                  : (_isArabic
                      ? 'اضغط على أي كلمة أو جملة عربية للاستماع'
                      : 'Click any Arabic word or sentence to listen'),
              style: TextStyle(
                color: _currentSpeechText.isNotEmpty ? Colors.white : Colors.white60,
                fontSize: 11,
                fontFamily: 'serif',
                fontWeight: _currentSpeechText.isNotEmpty ? FontWeight.w600 : FontWeight.normal,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            if (_currentSpeechText.isNotEmpty)
              ValueListenableBuilder<bool>(
                valueListenable: ArabEnglishState.notifier,
                builder: (context, showArabEnglish, child) {
                  if (!showArabEnglish) return const SizedBox.shrink();
                  final ae = ArabEnglishHelper.transliterate(_currentSpeechText);
                  if (ae.isEmpty) return const SizedBox.shrink();
                  return Padding(
                    padding: const EdgeInsets.only(top: 2, bottom: 4),
                    child: Text(
                      '🗣️ $ae',
                      style: const TextStyle(
                        color: Color(0xFFFDE68A),
                        fontSize: 10.5,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.25,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                },
              ),
            const SizedBox(height: 6),

            // Controls Row: Speed & Repeats (Horizontally Scrollable to prevent any pixel overflow on narrow screens)
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              physics: const BouncingScrollPhysics(),
              child: Row(
                children: [
                  Text(
                    _isArabic ? 'السرعة: ' : 'Speed: ',
                    style: const TextStyle(color: Colors.white70, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                  _speedButton('1.0x', 1.0),
                  const SizedBox(width: 4),
                  _speedButton('0.6x', 0.6),
                  const SizedBox(width: 4),
                  _speedButton('0.3x', 0.3),

                  const SizedBox(width: 14),

                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.repeat, color: Colors.white70, size: 12),
                      const SizedBox(width: 2),
                      Text(
                        _isArabic ? 'تكرار: ' : 'Repeat: ',
                        style: const TextStyle(color: Colors.white70, fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                      _repeatButton(1),
                      const SizedBox(width: 2),
                      _repeatButton(2),
                      const SizedBox(width: 2),
                      _repeatButton(3),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _speedButton(String label, double val) {
    final bool isSelected = _playbackSpeed == val;
    return InkWell(
      onTap: () {
        setState(() {
          _playbackSpeed = val;
        });
        _applyTtsSpeed();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF047857) : const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(4),
          border: Border.all(
            color: isSelected ? const Color(0xFF10B981) : const Color(0xFF334155),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? Colors.white : Colors.white70,
            fontSize: 9.5,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  Widget _repeatButton(int count) {
    final bool isSelected = _repeatCount == count;
    return InkWell(
      onTap: () {
        setState(() {
          _repeatCount = count;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFB45309) : const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(3),
          border: Border.all(
            color: isSelected ? const Color(0xFFF59E0B) : const Color(0xFF334155),
          ),
        ),
        child: Text(
          '${count}x',
          style: TextStyle(
            color: isSelected ? Colors.white : Colors.white70,
            fontSize: 9.5,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  Widget _buildLhsDrawer() {
    return Drawer(
      backgroundColor: Colors.white,
      child: Column(
        children: [
          Container(
            width: double.infinity,
            padding: EdgeInsets.only(
              top: MediaQuery.of(context).padding.top + 16,
              bottom: 20,
              left: 16,
              right: 16,
            ),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Color(0xFF58337E), Color(0xFF6C5CE7)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(14),
                      child: Image.asset(
                        'assets/icon.png',
                        width: 44,
                        height: 44,
                        fit: BoxFit.cover,
                        errorBuilder: (_, error, stack) => Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: const Color(0xFF58337E),
                            borderRadius: BorderRadius.circular(14),
                          ),
                          alignment: Alignment.center,
                          child: const Text(
                            'ج',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 22,
                            ),
                          ),
                        ),
                      ),
                    ),
                    InkWell(
                      borderRadius: BorderRadius.circular(20),
                      onTap: () {
                        _setLanguage(!_isArabic);
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: Colors.white30),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.language, color: Colors.white, size: 14),
                            const SizedBox(width: 4),
                            Text(
                              _isArabic ? 'العربية' : 'English',
                              style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: const [
                    Text(
                      'JISR ',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w900,
                        fontSize: 18,
                        letterSpacing: 0.5,
                      ),
                    ),
                    Text(
                      'جسر',
                      style: TextStyle(
                        color: Color(0xFFA29BFE),
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  _isArabic
                      ? 'المنصة الذكية لمناهج اللغة العربية'
                      : 'Intelligent Arabic Curriculum Platform',
                  style: const TextStyle(color: Color(0xFFDCD6F7), fontSize: 11),
                ),
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      Text(_getAvatarIcon(_activeChild?['avatar_id']),
                          style: const TextStyle(fontSize: 16)),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          '${_activeChild?['name'] ?? 'Learner'} · Class ${_activeChild?['default_grade'] ?? _currentGrade}',
                          style: const TextStyle(
                              color: Colors.white,
                              fontSize: 11,
                              fontWeight: FontWeight.w600),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              children: [
                _drawerItem(
                  icon: Icons.menu_book_rounded,
                  title: _isArabic ? 'المنهاج والدروس' : 'Curriculum & Courses',
                  viewKey: 'catalogue',
                ),
                _drawerItem(
                  icon: Icons.auto_stories,
                  title: _isArabic ? 'الكتاب المدرسي الممسوح (108 ص)' : 'Scanned Textbook (108 p.)',
                  viewKey: 'reader',
                  badge: 'Full Book',
                ),
                _drawerItem(
                  icon: Icons.auto_stories_rounded,
                  title: _isArabic
                      ? 'الدرس النشط: ${_activeLessonPackage?.titleAr ?? 'ألعاب الكرة'}'
                      : 'Active Lesson: ${_activeLessonPackage?.titleEn ?? 'Ball Games'}',
                  viewKey: 'lesson',
                  badge: 'Full Book',
                ),
                _drawerItem(
                  icon: Icons.edit_note_rounded,
                  title: _isArabic ? 'الملازم الذكية' : 'Smart Malazim (Study Guides)',
                  viewKey: 'malazim',
                ),
                _drawerItem(
                  icon: Icons.medical_services_outlined,
                  title: _isArabic ? 'الكبسولات اللغوية' : 'Grammar Capsules',
                  viewKey: 'capsules',
                ),
                _drawerItem(
                  icon: Icons.quiz_rounded,
                  title: _isArabic ? 'الاختبارات والتقييم' : 'Adaptive Tests & Exams',
                  viewKey: 'tests',
                ),
                _drawerItem(
                  icon: Icons.account_tree_rounded,
                  title: _isArabic ? 'خرائط المفاهيم والتدفق الذهني' : 'Mindmaps & Flowcharts',
                  viewKey: 'mindmaps',
                  badge: _isArabic ? 'بصري' : 'Visual',
                ),
                const Divider(height: 16, indent: 16, endIndent: 16),
                ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF3F0FF),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child:
                        const Icon(Icons.auto_awesome, color: Color(0xFF6C5CE7), size: 18),
                  ),
                  title: Text(
                    _isArabic ? 'اسأل فاهم الذكي' : 'Ask Fahim AI',
                    style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF1E293B)),
                  ),
                  onTap: () {
                    Navigator.of(context).pop();
                    _showAskFahimDialog();
                  },
                ),
                ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF1F5F9),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.person_outline,
                        color: Color(0xFF64748B), size: 18),
                  ),
                  title: Text(
                    _isArabic ? 'حسابي والملف الشخصي' : 'Profile & Account',
                    style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF1E293B)),
                  ),
                  onTap: () {
                    Navigator.of(context).pop();
                    setState(() => _activeView = 'profile');
                  },
                ),
                ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFEFF6FF),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.receipt_long_outlined,
                        color: Color(0xFF2563EB), size: 18),
                  ),
                  title: Text(
                    _isArabic ? 'الاشتراكات والفواتير' : 'Subscriptions & Invoices',
                    style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF1E293B)),
                  ),
                  onTap: () {
                    Navigator.of(context).pop();
                    setState(() => _activeView = 'subscriptions');
                  },
                ),
                ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFDF2F8),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.rate_review_outlined,
                        color: Color(0xFFDB2777), size: 18),
                  ),
                  title: Text(
                    _isArabic ? 'تقييم وملاحظات المستخدمين' : 'Feedback & Suggestions',
                    style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF1E293B)),
                  ),
                  onTap: () {
                    Navigator.of(context).pop();
                    showDialog(
                      context: context,
                      builder: (ctx) => FeedbackDialog(
                        api: _api,
                        token: _token,
                        user: _user,
                        activeChild: _activeChild,
                        isArabic: _isArabic,
                      ),
                    );
                  },
                ),
                if (_user?['role'] == 'parent' || _user?['role'] == 'admin')
                  ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: const Color(0xFFECFDF5),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(Icons.family_restroom,
                          color: Color(0xFF059669), size: 18),
                    ),
                    title: Text(
                      _isArabic ? 'لوحة تحكم ولي الأمر' : 'Parent Dashboard',
                      style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1E293B)),
                    ),
                    onTap: () {
                      Navigator.of(context).pop();
                      setState(() => _activeView = 'parent');
                    },
                  ),
                if (_user?['role'] == 'tutor' || _user?['role'] == 'admin')
                  ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFFBEB),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(Icons.assignment_turned_in_outlined,
                          color: Color(0xFFD97706), size: 18),
                    ),
                    title: Text(
                      _isArabic ? 'لوحة المعلم والتصحيح' : 'Tutor Queue',
                      style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1E293B)),
                    ),
                    onTap: () {
                      Navigator.of(context).pop();
                      setState(() => _activeView = 'tutor');
                    },
                  ),
                if (_user?['role'] == 'admin')
                  ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFEF2F2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(Icons.admin_panel_settings_outlined,
                          color: Color(0xFFDC2626), size: 18),
                    ),
                    title: Text(
                      _isArabic ? 'إدارة المنهاج (مشرف)' : 'Admin Workflow',
                      style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1E293B)),
                    ),
                    onTap: () {
                      Navigator.of(context).pop();
                      setState(() => _activeView = 'admin');
                    },
                  ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: Color(0xFFF1F5F9))),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                InkWell(
                  onTap: () {
                    Navigator.of(context).pop();
                    if (_token != null) {
                      _logout();
                    } else {
                      _showAuthDialog();
                    }
                  },
                  child: Row(
                    children: [
                      Icon(
                        _token != null ? Icons.logout : Icons.login,
                        size: 16,
                        color: const Color(0xFF6C5CE7),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        _token != null
                            ? (_isArabic ? 'تسجيل الخروج' : 'Sign Out')
                            : (_isArabic ? 'تسجيل الدخول' : 'Sign In'),
                        style: const TextStyle(
                          color: Color(0xFF6C5CE7),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                const Text(
                  'v2.4.0 · JISR (جسر)',
                  style: TextStyle(color: Color(0xFF94A3B8), fontSize: 10),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _drawerItem({
    required IconData icon,
    required String title,
    required String viewKey,
    String? badge,
  }) {
    final bool isSelected = _activeView == viewKey;
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
      decoration: BoxDecoration(
        color: isSelected ? const Color(0xFFF3F0FF) : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        dense: true,
        leading: Icon(
          icon,
          color: isSelected ? const Color(0xFF6C5CE7) : const Color(0xFF64748B),
          size: 20,
        ),
        title: Text(
          title,
          style: TextStyle(
            fontSize: 13,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
            color: isSelected ? const Color(0xFF6C5CE7) : const Color(0xFF334155),
          ),
        ),
        trailing: badge != null
            ? Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFF22C55E),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  badge,
                  style: const TextStyle(
                      color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                ),
              )
            : (isSelected
                ? const Icon(Icons.chevron_right, size: 16, color: Color(0xFF6C5CE7))
                : null),
        onTap: () {
          Navigator.of(context).pop();
          setState(() {
            _activeView = viewKey;
          });
        },
      ),
    );
  }

  Widget _buildCatalogueScreen() {
    return CatalogueScreen(
      lessons: _catalogLessons,
      remoteCapsules: _remoteCapsules,
      activeChild: _activeChild,
      user: _user,
      token: _token,
      currentGrade: _currentGrade,
      currentTerm: _currentTerm,
      learningDataLoading: _learningDataLoading,
      isArabic: _isArabic,
      onSelectGrade: (grade) {
        setState(() => _currentGrade = grade);
        _loadRemoteLearningData();
      },
      onSelectTerm: (term) {
        setState(() => _currentTerm = term);
        _loadRemoteLearningData();
      },
      onSelectLesson: (lesson) {
        _loadLesson(lesson.id);
      },
      onSelectLessonMode: (lesson, mode) {
        _loadLesson(lesson.id, mode: mode);
      },
      onModeSelected: (mode) {
        setState(() => _activeView = mode);
      },
      onOpenAskFahim: () => _showAskFahimDialog(initialMode: 'text'),
      onOpenAskFahimMode: (mode) {
        if (mode == 'pdf') {
          _pickAndOpenPdf();
        } else {
          _showAskFahimDialog(initialMode: mode);
        }
      },
      onOpenAuth: _showAuthDialog,
      onSwitchProfile: _showChildSwitcherSheet,
      onOpenPaywall: () => _showPaywallDialog(_currentGrade, _currentTerm),
      onVocalize: _vocalizeText,
      onOpenReader: () => setState(() => _activeView = 'reader'),
      onOpenMindmaps: () => setState(() => _activeView = 'mindmaps'),
    );
  }

  Widget _buildActiveView() {
    switch (_activeView) {
      case 'catalogue':
        return _buildCatalogueScreen();
      case 'reader':
        return TextbookReaderScreen(
          isArabic: _isArabic,
          onVocalize: _vocalizeText,
          onBack: () => setState(() => _activeView = 'catalogue'),
          api: _api,
          initialGrade: _currentGrade,
          initialTerm: _currentTerm,
          onGradeTermChanged: (grade, term) {
            setState(() {
              _currentGrade = grade;
              _currentTerm = term;
            });
          },
        );
      case 'lesson':
        return LessonPlayerScreen(
          package: _activeLessonPackage ?? CurriculumLessonPackage.fromStaticChapter1(),
          isArabic: _isArabic,
          initialMode: _activeLessonMode,
          activeWord: _activeWord,
          onVocalize: _vocalizeText,
          onOpenAskFahim: () => _showAskFahimDialog(initialMode: 'text'),
          onBack: () {
            setState(() => _activeView = 'catalogue');
          },
          api: _api,
          token: _token,
          childId: _activeChild?['id']?.toString(),
        );
      case 'profile':
        return ProfileView(
          activeChild: _activeChild,
          user: _user,
          currentGrade: _currentGrade,
          currentTerm: _currentTerm,
          isArabic: _isArabic,
          onOpenAskFahim: () => _showAskFahimDialog(initialMode: 'text'),
          onOpenPaywall: () => _showPaywallDialog(_currentGrade, _currentTerm),
          onOpenSubscriptions: () => setState(() => _activeView = 'subscriptions'),
          onLogout: _logout,
          onDeleteAccount: _token != null ? _handleDeleteAccount : null,
        );
      case 'subscriptions':
        return SubscriptionsView(
          activeChild: _activeChild,
          token: _token,
          isArabic: _isArabic,
          onBack: () => setState(() => _activeView = 'profile'),
          onOpenPaywall: () => _showPaywallDialog(_currentGrade, _currentTerm),
          api: _api,
        );
      case 'parent':
        return ParentDashboardView(activeChild: _activeChild);
      case 'tutor':
        return TutorQueueView(
          activeChild: _activeChild,
          api: _api,
          token: _token,
        );
      case 'malazim':
        return MalazimView(
          onBack: () => setState(() => _activeView = 'catalogue'),
          onVocalize: _vocalizeText,
          activeWord: _activeWord,
        );
      case 'capsules':
        return CapsulesView(
          completedCapsules: _completedCapsules,
          onCapsuleCompleted: (id) {
            setState(() => _completedCapsules.add(id));
          },
          onBack: () => setState(() => _activeView = 'catalogue'),
        );
      case 'tests':
        return AdaptiveTestsView(
          activeChild: _activeChild,
          api: _api,
          token: _token,
          grade: _currentGrade,
          term: _currentTerm,
          onBack: () => setState(() => _activeView = 'catalogue'),
        );
      case 'mindmaps':
        return MindmapsScreen(
          isArabic: _isArabic,
          initialGrade: _currentGrade,
          onVocalize: _vocalizeText,
          onAskFahim: (query) {
            _showAskFahimDialog(initialMode: 'text');
          },
          onBack: () => setState(() => _activeView = 'catalogue'),
        );
      case 'admin':
        return AdminWorkflowView(
          token: _token,
          isArabic: _isArabic,
          api: _api,
          onBack: () => setState(() => _activeView = 'catalogue'),
        );
      default:
        return _buildCatalogueScreen();
    }
  }
}

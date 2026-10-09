import 'package:flutter/material.dart';

import '../api_service.dart';
import '../arab_english_service.dart';
import '../auth_service.dart';
import '../chapter1_data.dart';
import '../models/curriculum_models.dart';

/// Full-featured Scanned Textbook Reader for the UAE MoE Arabic Curriculum
/// Supporting all 10 grades (Grades 1-10) and all terms (Terms 1-3)
/// with authentic Google Cloud Vision OCR, paragraph-by-paragraph TTS audio,
/// split / text / image view modes, full-screen zoom, and chapter jumping.
class TextbookReaderScreen extends StatefulWidget {
  final bool isArabic;
  final Function(String text) onVocalize;
  final VoidCallback onBack;
  final ApiService? api;
  final int initialGrade;
  final int initialTerm;
  final int initialPage;
  final void Function(int grade, int term)? onGradeTermChanged;

  const TextbookReaderScreen({
    super.key,
    required this.isArabic,
    required this.onVocalize,
    required this.onBack,
    this.api,
    this.initialGrade = 5,
    this.initialTerm = 1,
    this.initialPage = 8,
    this.onGradeTermChanged,
  });

  @override
  State<TextbookReaderScreen> createState() => _TextbookReaderScreenState();
}

class _TextbookReaderScreenState extends State<TextbookReaderScreen> {
  late int _currentGrade;
  late int _currentTerm;
  late int _currentPdfPage;
  String _viewMode = 'split'; // 'image', 'split', 'text'
  bool _loadingOcr = false;
  Map<String, dynamic>? _remoteOcrData;
  List<Map<String, dynamic>> _remoteLessons = [];
  bool _loadingLessons = false;

  int get totalBookPages => getTextbookPageCount(_currentGrade, _currentTerm);
  String get _currentEditionId => 'moe_gr${_currentGrade}_vol${_currentTerm}_2023';

  static const List<Map<String, dynamic>> _chapterJumps = [
    {'chapter': 0, 'pdf': 6, 'print': 4, 'titleAr': 'الغلاف والوحدة الأولى', 'titleEn': 'Unit 1 Cover'},
    {'chapter': 0, 'pdf': 7, 'print': 5, 'titleAr': 'فهرس الموضوعات', 'titleEn': 'Table of Contents'},
    {'chapter': 1, 'pdf': 8, 'print': 6, 'titleAr': 'الدرس 1: ألعاب الكرة', 'titleEn': 'Ch 1: Ball Games'},
    {'chapter': 2, 'pdf': 18, 'print': 16, 'titleAr': 'الدرس 2: ركوب الخيل', 'titleEn': 'Ch 2: Horse Riding'},
    {'chapter': 3, 'pdf': 28, 'print': 26, 'titleAr': 'الدرس 3: الجري', 'titleEn': 'Ch 3: Running'},
    {'chapter': 4, 'pdf': 38, 'print': 36, 'titleAr': 'الدرس 4: الفنون', 'titleEn': 'Ch 4: Arts'},
    {'chapter': 5, 'pdf': 48, 'print': 46, 'titleAr': 'الدرس 5: القراءة', 'titleEn': 'Ch 5: Reading'},
    {'chapter': 6, 'pdf': 58, 'print': 56, 'titleAr': 'الدرس 6: في مدرستي', 'titleEn': 'Ch 6: At My School'},
    {'chapter': 7, 'pdf': 68, 'print': 66, 'titleAr': 'الدرس 7: في بيتي', 'titleEn': 'Ch 7: At My Home'},
    {'chapter': 8, 'pdf': 78, 'print': 76, 'titleAr': 'الدرس 8: طعامي', 'titleEn': 'Ch 8: My Food'},
    {'chapter': 9, 'pdf': 88, 'print': 86, 'titleAr': 'الدرس 9: ملابسي', 'titleEn': 'Ch 9: My Clothes'},
    {'chapter': 10, 'pdf': 98, 'print': 96, 'titleAr': 'الدرس 10: وقت المرح', 'titleEn': 'Ch 10: Fun Time'},
  ];

  @override
  void initState() {
    super.initState();
    _currentGrade = widget.initialGrade;
    _currentTerm = widget.initialTerm;
    final maxP = getTextbookPageCount(_currentGrade, _currentTerm);
    _currentPdfPage = widget.initialPage <= maxP ? widget.initialPage : 1;
    _fetchLessons();
    _fetchRemoteOcr(_currentPdfPage);
  }

  Future<void> _fetchLessons() async {
    setState(() => _loadingLessons = true);
    try {
      final res = await (widget.api?.get(
            '/api/curriculum/lessons',
            query: {'grade': '$_currentGrade', 'term': '$_currentTerm'},
          ) ??
          ApiService().get(
            '/api/curriculum/lessons',
            query: {'grade': '$_currentGrade', 'term': '$_currentTerm'},
          ));
      if (mounted && res is List) {
        setState(() {
          _remoteLessons = res.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList();
          _loadingLessons = false;
        });
        return;
      }
    } catch (_) {}
    if (mounted) setState(() => _loadingLessons = false);
  }

  Future<void> _fetchRemoteOcr(int page) async {
    setState(() => _loadingOcr = true);
    try {
      final res = await (widget.api?.get(
            '/api/admin/ocr-page/$page',
            query: {'edition_id': _currentEditionId},
          ) ??
          ApiService().get(
            '/api/admin/ocr-page/$page',
            query: {'edition_id': _currentEditionId},
          ));
      if (mounted && res is Map) {
        setState(() {
          _remoteOcrData = Map<String, dynamic>.from(res);
          _loadingOcr = false;
        });
        return;
      }
    } catch (_) {}
    if (mounted) setState(() => _loadingOcr = false);
  }

  void _changePage(int newPage) {
    if (newPage < 1 || newPage > totalBookPages) return;
    setState(() {
      _currentPdfPage = newPage;
      _remoteOcrData = null;
    });
    _fetchRemoteOcr(newPage);
  }

  void _switchEdition(int grade, int term) {
    if (grade == _currentGrade && term == _currentTerm) return;
    setState(() {
      _currentGrade = grade;
      _currentTerm = term;
      _currentPdfPage = 1;
      _remoteOcrData = null;
      _remoteLessons = [];
    });
    widget.onGradeTermChanged?.call(grade, term);
    _fetchLessons();
    _fetchRemoteOcr(1);
  }

  ChapterPage? get _staticChapterPageData {
    try {
      return kChapter1Pages.firstWhere((p) => p.pdfPage == _currentPdfPage);
    } catch (_) {
      return null;
    }
  }

  List<String> get _currentParagraphsAr {
    if (_remoteOcrData != null && _remoteOcrData!['paragraphs'] is List) {
      final list = (_remoteOcrData!['paragraphs'] as List)
          .map((e) => e?.toString() ?? '')
          .where((s) => s.trim().isNotEmpty)
          .toList();
      if (list.isNotEmpty) return list;
    }
    final st = _staticChapterPageData;
    if (st != null && st.paragraphsAr.isNotEmpty) {
      return st.paragraphsAr;
    }
    return [];
  }

  List<String> get _currentParagraphsEn {
    if (_remoteOcrData != null && _remoteOcrData!['paragraphs_en'] is List) {
      return (_remoteOcrData!['paragraphs_en'] as List)
          .map((e) => e?.toString() ?? '')
          .toList();
    }
    final st = _staticChapterPageData;
    if (st != null && st.paragraphsEn.isNotEmpty) {
      return st.paragraphsEn;
    }
    return [];
  }

  List<Map<String, dynamic>> get _effectiveChapters {
    if (_remoteLessons.isNotEmpty) {
      return _remoteLessons.map((l) {
        final order = l['lesson_order'] is int
            ? l['lesson_order'] as int
            : (int.tryParse(l['lesson_order']?.toString() ?? '1') ?? 1);
        final start = l['start_page'] is int
            ? l['start_page'] as int
            : (int.tryParse(l['start_page']?.toString() ?? '1') ?? 1);
        return {
          'chapter': order,
          'pdf': start,
          'print': start,
          'titleAr': l['title_ar']?.toString() ?? 'الدرس $order',
          'titleEn': l['title_en']?.toString() ?? 'Lesson $order',
        };
      }).toList();
    }
    if (_currentGrade == 5 && _currentTerm == 1) {
      return _chapterJumps;
    }
    final total = totalBookPages;
    final step = (total / 6).ceil().clamp(1, total);
    return List.generate(6, (i) {
      final p = (i * step) + 1;
      final clamped = p > total ? total : p;
      return {
        'chapter': i + 1,
        'pdf': clamped,
        'print': clamped,
        'titleAr': 'الوحدة ${i + 1} (ص $clamped)',
        'titleEn': 'Unit ${i + 1} (p. $clamped)',
      };
    });
  }

  String get _currentTitleAr {
    if (_remoteOcrData != null &&
        _remoteOcrData!['title_ar'] != null &&
        _remoteOcrData!['title_ar'].toString().trim().isNotEmpty) {
      return _remoteOcrData!['title_ar'].toString();
    }
    final st = _staticChapterPageData;
    if (_currentGrade == 5 && _currentTerm == 1 && st != null && st.titleAr.isNotEmpty) return st.titleAr;
    final jump = _effectiveChapters.firstWhere(
      (j) => j['pdf'] == _currentPdfPage,
      orElse: () => {'titleAr': widget.isArabic ? 'كتاب الطالب · صفحة $_currentPdfPage' : 'Student Book · Page $_currentPdfPage'},
    );
    return jump['titleAr'] as String;
  }

  String get _currentTitleEn {
    if (_remoteOcrData != null &&
        _remoteOcrData!['title_en'] != null &&
        _remoteOcrData!['title_en'].toString().trim().isNotEmpty) {
      return _remoteOcrData!['title_en'].toString();
    }
    final st = _staticChapterPageData;
    if (_currentGrade == 5 && _currentTerm == 1 && st != null && st.titleEn.isNotEmpty) return st.titleEn;
    final jump = _effectiveChapters.firstWhere(
      (j) => j['pdf'] == _currentPdfPage,
      orElse: () => {'titleEn': 'Student Book · Page $_currentPdfPage'},
    );
    return jump['titleEn'] as String;
  }

  int get _printedPageNumber {
    if (_remoteOcrData != null && _remoteOcrData!['printed_page'] != null) {
      final p = int.tryParse(_remoteOcrData!['printed_page'].toString());
      if (p != null) return p;
    }
    final st = _staticChapterPageData;
    if (_currentGrade == 5 && _currentTerm == 1 && st != null) return st.printedPage;
    return _currentPdfPage >= 3 ? (_currentPdfPage - 2) : _currentPdfPage;
  }

  void _openFullScreenZoom() {
    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (dialogCtx, setDialogState) {
          final pdfPage = _currentPdfPage;
          final printPage = _printedPageNumber;
          final titleAr = _currentTitleAr;

          return Dialog.fullscreen(
            backgroundColor: Colors.black,
            child: SafeArea(
              child: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.close, color: Colors.white),
                              onPressed: () => Navigator.of(ctx).pop(),
                            ),
                            IconButton(
                              icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 18),
                              tooltip: widget.isArabic ? 'الصفحة السابقة' : 'Previous Page',
                              onPressed: _currentPdfPage > 1
                                  ? () {
                                      _changePage(_currentPdfPage - 1);
                                      setDialogState(() {});
                                    }
                                  : null,
                            ),
                            IconButton(
                              icon: const Icon(Icons.arrow_forward_ios, color: Colors.white, size: 18),
                              tooltip: widget.isArabic ? 'الصفحة التالية' : 'Next Page',
                              onPressed: _currentPdfPage < totalBookPages
                                  ? () {
                                      _changePage(_currentPdfPage + 1);
                                      setDialogState(() {});
                                    }
                                  : null,
                            ),
                          ],
                        ),
                        Expanded(
                          child: Text(
                            'ص $printPage / $totalBookPages (PDF: $pdfPage) · $titleAr',
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.volume_up, color: Colors.white),
                          onPressed: () {
                            final paras = _currentParagraphsAr;
                            if (paras.isNotEmpty) {
                              widget.onVocalize(paras.join(' '));
                            }
                          },
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: InteractiveViewer(
                      minScale: 0.8,
                      maxScale: 5.0,
                      child: Center(
                        child: Image.asset(
                          'assets/pages/page_$pdfPage.png',
                          fit: BoxFit.contain,
                          errorBuilder: (_, error, stack) => Image.network(
                            '${widget.api?.baseUrl ?? apiBase}/api/admin/page-image/$pdfPage?edition_id=$_currentEditionId',
                            fit: BoxFit.contain,
                            errorBuilder: (_, error2, stack2) => const Center(
                              child: Text('Page scan unavailable', style: TextStyle(color: Colors.white70)),
                            ),
                          ),
                        ),
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

  void _showPageJumpDialog() {
    final ctrl = TextEditingController(text: '$_currentPdfPage');
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.bookmark_added, color: Color(0xFF047857)),
            const SizedBox(width: 8),
            Text(widget.isArabic ? 'انتقال سريع إلى صفحة' : 'Jump to Page'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.isArabic
                  ? 'الصف $_currentGrade · الفصل $_currentTerm (من 1 إلى $totalBookPages)'
                  : 'Grade $_currentGrade · Term $_currentTerm (1 to $totalBookPages)',
              style: const TextStyle(fontSize: 12, color: Color(0xFF64748B), fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ctrl,
              keyboardType: TextInputType.number,
              autofocus: true,
              decoration: InputDecoration(
                hintText: '1 - $totalBookPages',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                prefixIcon: const Icon(Icons.menu_book),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(widget.isArabic ? 'إلغاء' : 'Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF047857),
              foregroundColor: Colors.white,
            ),
            onPressed: () {
              final val = int.tryParse(ctrl.text.trim());
              if (val != null && val >= 1 && val <= totalBookPages) {
                Navigator.of(ctx).pop();
                _changePage(val);
              }
            },
            child: Text(widget.isArabic ? 'انتقال' : 'Jump'),
          ),
        ],
      ),
    );
  }

  void _showChapterSelectSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (bottomSheetCtx, setSheetState) {
          final chapters = _effectiveChapters;
          return Container(
            padding: const EdgeInsets.all(16),
            constraints: BoxConstraints(maxHeight: MediaQuery.of(context).size.height * 0.85),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      widget.isArabic
                          ? 'كتاب الطالب · الصف $_currentGrade ($totalBookPages صفحة)'
                          : 'Student Book · Grade $_currentGrade ($totalBookPages p.)',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF064E3B)),
                    ),
                    IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.of(ctx).pop()),
                  ],
                ),
                const SizedBox(height: 8),

                // Grade Switcher (Grades 1 to 10)
                Text(
                  widget.isArabic ? 'اختر الصف الدراسي:' : 'Select Grade:',
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748B)),
                ),
                const SizedBox(height: 6),
                SizedBox(
                  height: 36,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: 10,
                    itemBuilder: (_, i) {
                      final g = i + 1;
                      final isSel = g == _currentGrade;
                      return Padding(
                        padding: const EdgeInsets.only(right: 6),
                        child: ChoiceChip(
                          label: Text(widget.isArabic ? 'الصف $g' : 'Gr $g'),
                          selected: isSel,
                          selectedColor: const Color(0xFF047857),
                          labelStyle: TextStyle(
                            color: isSel ? Colors.white : const Color(0xFF1E293B),
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                          onSelected: (_) {
                            setSheetState(() {
                              _switchEdition(g, _currentTerm);
                            });
                          },
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 10),

                // Term Switcher (Terms 1 to 3)
                Text(
                  widget.isArabic ? 'اختر الفصل الدراسي:' : 'Select Term:',
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748B)),
                ),
                const SizedBox(height: 6),
                Row(
                  children: List.generate(3, (i) {
                    final t = i + 1;
                    final isSel = t == _currentTerm;
                    final tName = widget.isArabic ? 'الفصل $t' : 'Term $t';
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: Text(tName),
                        selected: isSel,
                        selectedColor: const Color(0xFF047857),
                        labelStyle: TextStyle(
                          color: isSel ? Colors.white : const Color(0xFF1E293B),
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                        onSelected: (_) {
                          setSheetState(() {
                            _switchEdition(_currentGrade, t);
                          });
                        },
                      ),
                    );
                  }),
                ),
                const SizedBox(height: 12),
                const Divider(),

                // Direct Page Jump Shortcut
                InkWell(
                  onTap: () {
                    Navigator.of(ctx).pop();
                    _showPageJumpDialog();
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFA7F3D0)),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.dialpad, size: 16, color: Color(0xFF047857)),
                            const SizedBox(width: 8),
                            Text(
                              widget.isArabic
                                  ? 'انتقال مباشر إلى أي صفحة (1 - $totalBookPages)'
                                  : 'Jump to specific page (1 - $totalBookPages)',
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF047857)),
                            ),
                          ],
                        ),
                        const Icon(Icons.arrow_forward_ios, size: 12, color: Color(0xFF047857)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 10),

                // Lessons list
                Expanded(
                  child: (_loadingLessons && chapters.isEmpty)
                      ? const Center(child: CircularProgressIndicator(color: Color(0xFF047857)))
                      : ListView.builder(
                          itemCount: chapters.length,
                          itemBuilder: (context, idx) {
                            final j = chapters[idx];
                            final isCurrent = j['pdf'] == _currentPdfPage;
                            return ListTile(
                              tileColor: isCurrent ? const Color(0xFFECFDF5) : null,
                              leading: CircleAvatar(
                                backgroundColor: isCurrent ? const Color(0xFF047857) : const Color(0xFFF1F5F9),
                                foregroundColor: isCurrent ? Colors.white : const Color(0xFF047857),
                                child: Text('ص ${j['print']}'),
                              ),
                              title: Text(
                                j['titleAr'] as String,
                                style: TextStyle(fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal),
                              ),
                              subtitle: Text(j['titleEn'] as String),
                              trailing: isCurrent ? const Icon(Icons.check, color: Color(0xFF047857)) : null,
                              onTap: () {
                                Navigator.of(ctx).pop();
                                _changePage(j['pdf'] as int);
                              },
                            );
                          },
                        ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final pdfPage = _currentPdfPage;
    final printPage = _printedPageNumber;
    final titleAr = _currentTitleAr;
    final titleEn = _currentTitleEn;
    final paragraphsAr = _currentParagraphsAr;
    final paragraphsEn = _currentParagraphsEn;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: InkWell(
          onTap: _showChapterSelectSheet,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                widget.isArabic
                    ? 'كتاب الوزارة: صف $_currentGrade · ف$_currentTerm ($totalBookPages ص)'
                    : 'Textbook: Gr $_currentGrade · T$_currentTerm ($totalBookPages p.)',
                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              ),
              const SizedBox(width: 4),
              const Icon(Icons.keyboard_arrow_down, size: 18),
            ],
          ),
        ),
        backgroundColor: const Color(0xFF064E3B),
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: widget.onBack,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.dialpad),
            tooltip: widget.isArabic ? 'انتقال لصفحة' : 'Jump to Page',
            onPressed: _showPageJumpDialog,
          ),
          IconButton(
            icon: const Icon(Icons.menu_book),
            tooltip: widget.isArabic ? 'فهرس الفصول والصفوف' : 'Index & Grades',
            onPressed: _showChapterSelectSheet,
          ),
          IconButton(
            icon: const Icon(Icons.fullscreen),
            tooltip: widget.isArabic ? 'تكبير ملء الشاشة' : 'Full Screen Zoom',
            onPressed: _openFullScreenZoom,
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(14),
        children: [
          // Banner
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF064E3B), Color(0xFF047857)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF064E3B).withValues(alpha: 0.2),
                  blurRadius: 8,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      widget.isArabic
                          ? 'كتاب وزارة التربية والتعليم · الصف $_currentGrade (الفصل $_currentTerm)'
                          : 'UAE MoE Student Book · Grade $_currentGrade (Term $_currentTerm)',
                      style: const TextStyle(color: Color(0xFFA7F3D0), fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                    InkWell(
                      onTap: _showPageJumpDialog,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          'ص $printPage / $totalBookPages (PDF: $pdfPage)',
                          style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  titleAr,
                  style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  titleEn,
                  style: const TextStyle(color: Color(0xFFD1FAE5), fontSize: 11),
                ),
                if (_loadingOcr)
                  const Padding(
                    padding: EdgeInsets.only(top: 8),
                    child: LinearProgressIndicator(color: Color(0xFFA7F3D0), backgroundColor: Colors.white10),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // Horizontal Thumbnail / Page Picker Strip
          SizedBox(
            height: 48,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _effectiveChapters.length,
              itemBuilder: (ctx, idx) {
                final item = _effectiveChapters[idx];
                final isSelected = item['pdf'] == _currentPdfPage;
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(12),
                    onTap: () => _changePage(item['pdf'] as int),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: isSelected ? const Color(0xFF047857) : Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: isSelected ? const Color(0xFF047857) : const Color(0xFFE2E8F0),
                        ),
                        boxShadow: isSelected
                            ? [
                                BoxShadow(
                                  color: const Color(0xFF047857).withValues(alpha: 0.25),
                                  blurRadius: 4,
                                  offset: const Offset(0, 2),
                                )
                              ]
                            : null,
                      ),
                      child: Center(
                        child: Text(
                          item['chapter'] == 0 ? item['titleAr'] : 'الدرس ${item['chapter']}',
                          style: TextStyle(
                            color: isSelected ? Colors.white : const Color(0xFF1E293B),
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 12),

          // View Mode Switcher
          Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Row(
              children: [
                _buildModeBtn('split', widget.isArabic ? 'عرض مزدوج' : 'Split View'),
                _buildModeBtn('image', widget.isArabic ? 'الكتاب المصور' : 'Image Only'),
                _buildModeBtn('text', widget.isArabic ? 'النص والترجمة' : 'Text & Audio'),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // 1. Scanned Original Page Image (visible in 'split' or 'image' mode)
          if (_viewMode == 'split' || _viewMode == 'image') ...[
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFE2E8F0)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                children: [
                  // Top Title Bar
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: const BoxDecoration(
                      color: Color(0xFFF8FAFC),
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(16),
                        topRight: Radius.circular(16),
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.picture_as_pdf, color: Color(0xFF047857), size: 16),
                            const SizedBox(width: 6),
                            Text(
                              widget.isArabic ? 'الكتاب الممسوح' : 'Scanned Page',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Color(0xFF0F172A)),
                            ),
                            const SizedBox(width: 8),
                            const ArabEnglishToggleSwitch(compact: true),
                          ],
                        ),
                        Row(
                          children: [
                            // Previous Page Button
                            InkWell(
                              borderRadius: BorderRadius.circular(6),
                              onTap: _currentPdfPage > 1 ? () => _changePage(_currentPdfPage - 1) : null,
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                                decoration: BoxDecoration(
                                  color: _currentPdfPage > 1 ? const Color(0xFFECFDF5) : const Color(0xFFF1F5F9),
                                  borderRadius: BorderRadius.circular(6),
                                  border: Border.all(
                                    color: _currentPdfPage > 1 ? const Color(0xFFA7F3D0) : const Color(0xFFE2E8F0),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    Icon(
                                      Icons.arrow_back,
                                      size: 12,
                                      color: _currentPdfPage > 1 ? const Color(0xFF047857) : const Color(0xFF94A3B8),
                                    ),
                                    const SizedBox(width: 2),
                                    Text(
                                      widget.isArabic ? 'السابقة' : 'Prev',
                                      style: TextStyle(
                                        fontSize: 10,
                                        fontWeight: FontWeight.bold,
                                        color: _currentPdfPage > 1 ? const Color(0xFF047857) : const Color(0xFF94A3B8),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            const SizedBox(width: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: const Color(0xFFE2E8F0)),
                              ),
                              child: Text(
                                'ص $printPage',
                                style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF334155)),
                              ),
                            ),
                            const SizedBox(width: 4),
                            // Next Page Button
                            InkWell(
                              borderRadius: BorderRadius.circular(6),
                              onTap: _currentPdfPage < totalBookPages ? () => _changePage(_currentPdfPage + 1) : null,
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                                decoration: BoxDecoration(
                                  color: _currentPdfPage < totalBookPages ? const Color(0xFFECFDF5) : const Color(0xFFF1F5F9),
                                  borderRadius: BorderRadius.circular(6),
                                  border: Border.all(
                                    color: _currentPdfPage < totalBookPages ? const Color(0xFFA7F3D0) : const Color(0xFFE2E8F0),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    Text(
                                      widget.isArabic ? 'التالية' : 'Next',
                                      style: TextStyle(
                                        fontSize: 10,
                                        fontWeight: FontWeight.bold,
                                        color: _currentPdfPage < totalBookPages ? const Color(0xFF047857) : const Color(0xFF94A3B8),
                                      ),
                                    ),
                                    const SizedBox(width: 2),
                                    Icon(
                                      Icons.arrow_forward,
                                      size: 12,
                                      color: _currentPdfPage < totalBookPages ? const Color(0xFF047857) : const Color(0xFF94A3B8),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            const SizedBox(width: 6),
                            InkWell(
                              onTap: _openFullScreenZoom,
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF047857),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.zoom_in, size: 13, color: Colors.white),
                                    const SizedBox(width: 2),
                                    Text(
                                      widget.isArabic ? 'تكبير' : 'Zoom',
                                      style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  // Image Container with InteractiveViewer
                  ClipRRect(
                    child: Container(
                      color: const Color(0xFFF1F5F9),
                      height: 380,
                      width: double.infinity,
                      child: InteractiveViewer(
                        minScale: 1.0,
                        maxScale: 3.5,
                        child: Center(
                          child: Image.asset(
                            'assets/pages/page_$pdfPage.png',
                            fit: BoxFit.contain,
                            errorBuilder: (_, error, stack) => Image.network(
                              '${widget.api?.baseUrl ?? apiBase}/api/admin/page-image/$pdfPage?edition_id=$_currentEditionId',
                              fit: BoxFit.contain,
                              errorBuilder: (_, error2, stack2) => Container(
                                height: 200,
                                alignment: Alignment.center,
                                child: Text(
                                  widget.isArabic ? 'صورة الصفحة قيد المراجعة' : 'Page scan loading / unavailable',
                                  style: const TextStyle(color: Color(0xFF94A3B8)),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),

                  // Bottom Hint with Full Page Audio
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: const BoxDecoration(
                      color: Color(0xFFF1F5F9),
                      borderRadius: BorderRadius.only(
                        bottomLeft: Radius.circular(16),
                        bottomRight: Radius.circular(16),
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          '💡 اسحب بإصبعين للتكبير',
                          style: TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                        ),
                        if (paragraphsAr.isNotEmpty)
                          InkWell(
                            onTap: () => widget.onVocalize(paragraphsAr.join(' ')),
                            child: Row(
                              children: const [
                                Icon(Icons.volume_up, size: 16, color: Color(0xFF047857)),
                                SizedBox(width: 4),
                                Text(
                                  'استمع للصفحة كاملة',
                                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF047857)),
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
          ],

          // 2. Interactive Text Cards (in 'split' or 'text' mode)
          if (_viewMode == 'split' || _viewMode == 'text') ...[
            if (paragraphsAr.isEmpty && !_loadingOcr)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    widget.isArabic
                        ? 'النص التفاعلي قيد المعالجة التحريرية، يمكنك مشاهدة الصفحة المصورة أعلاه.'
                        : 'OCR transcription is being processed for this page. View the scanned page above.',
                    style: const TextStyle(color: Color(0xFF64748B), fontSize: 12),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
            ...List.generate(paragraphsAr.length, (pIdx) {
              final pAr = paragraphsAr[pIdx];
              final pEn = pIdx < paragraphsEn.length ? paragraphsEn[pIdx] : '';
              return Card(
                margin: const EdgeInsets.only(bottom: 10),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                elevation: 0,
                color: Colors.white,
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          IconButton.filledTonal(
                            icon: const Icon(Icons.volume_up, size: 18, color: Color(0xFF047857)),
                            onPressed: () => widget.onVocalize(pAr),
                          ),
                          Text(
                            'فقرة ${pIdx + 1}',
                            style: const TextStyle(fontSize: 10, color: Color(0xFF64748B), fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        pAr,
                        textAlign: TextAlign.right,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1E293B),
                          height: 1.8,
                        ),
                      ),
                      ValueListenableBuilder<bool>(
                        valueListenable: ArabEnglishState.notifier,
                        builder: (context, isArabEnOn, _) {
                          if (!isArabEnOn) return const SizedBox.shrink();
                          final arabEn = ArabEnglishHelper.transliterate(pAr);
                          if (arabEn.isEmpty) return const SizedBox.shrink();
                          return Container(
                            margin: const EdgeInsets.only(top: 6, bottom: 4),
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF1F5F9),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: const Color(0xFFCBD5E1)),
                            ),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Padding(
                                  padding: EdgeInsets.only(top: 2, right: 6),
                                  child: Icon(Icons.record_voice_over_rounded, size: 14, color: Color(0xFF4338CA)),
                                ),
                                Expanded(
                                  child: RichText(
                                    text: TextSpan(
                                      children: [
                                        const TextSpan(
                                          text: 'Pronunciation: ',
                                          style: TextStyle(
                                            fontSize: 10.5,
                                            fontWeight: FontWeight.w800,
                                            color: Color(0xFF4338CA),
                                          ),
                                        ),
                                        TextSpan(
                                          text: arabEn,
                                          style: const TextStyle(
                                            fontSize: 12.5,
                                            fontWeight: FontWeight.w700,
                                            letterSpacing: 0.25,
                                            height: 1.4,
                                            color: Color(0xFF0F172A),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                      if (pEn.isNotEmpty) ...[
                        const Divider(height: 16),
                        Text(
                          pEn,
                          style: const TextStyle(
                            fontSize: 12,
                            color: Color(0xFF64748B),
                            fontStyle: FontStyle.italic,
                            height: 1.4,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              );
            }),
          ],

          // Navigation Page Buttons (Previous / Next across all 108 pages)
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _currentPdfPage > 1 ? () => _changePage(_currentPdfPage - 1) : null,
                  icon: const Icon(Icons.arrow_back, size: 16),
                  label: Text(widget.isArabic ? 'الصفحة السابقة' : 'Previous Page'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF047857),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  onPressed: _currentPdfPage < totalBookPages ? () => _changePage(_currentPdfPage + 1) : null,
                  icon: const Icon(Icons.arrow_forward, size: 16),
                  label: Text(widget.isArabic ? 'الصفحة التالية' : 'Next Page'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildModeBtn(String id, String label) {
    final isSelected = _viewMode == id;
    return Expanded(
      child: InkWell(
        borderRadius: BorderRadius.circular(10),
        onTap: () => setState(() => _viewMode = id),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF047857) : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: isSelected ? Colors.white : const Color(0xFF475569),
            ),
          ),
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';

import '../models/curriculum_models.dart';

/// CatalogueScreen for Mobile incorporating the Web App Home Page Layout:
/// 1. Top Hero Gradient Banner with UAE MoE Badges & Curriculum Mastery Gauge
/// 2. Official Scanned Textbook Reader Showcase (108 MoE Textbook Pages with Audio)
/// 3. Featured Showcase: Complete Chapter 1 - Ball Games with 4 Curriculum Pillars
/// 4. 10 Core Capabilities Quick Hub (Ask Fahim, Mastery Matrix, Ranks, Exam Sim)
/// 5. Grade Switcher (Class 1 to Class 12)
/// 6. Full Syllabus: All 10 Term 1 Lessons grouped by Unit 1 & Unit 2 with LPAR & Book access
class CatalogueScreen extends StatelessWidget {
  final List<CurriculumLessonItem> lessons;
  final List<Map<String, dynamic>> remoteCapsules;
  final Map<String, dynamic>? activeChild;
  final Map<String, dynamic>? user;
  final String? token;
  final int currentGrade;
  final int currentTerm;
  final bool learningDataLoading;
  final bool isArabic;
  final ValueChanged<int> onSelectGrade;
  final ValueChanged<int>? onSelectTerm;
  final ValueChanged<CurriculumLessonItem>? onSelectLesson;
  final Function(CurriculumLessonItem lesson, LessonViewMode mode) onSelectLessonMode;
  final ValueChanged<String> onModeSelected;
  final VoidCallback onOpenAskFahim;
  final Function(String mode)? onOpenAskFahimMode;
  final VoidCallback onOpenPaywall;
  final Function(String text)? onVocalize;
  final VoidCallback? onOpenReader;
  final VoidCallback? onOpenAuth;
  final VoidCallback? onSwitchProfile;
  final VoidCallback? onOpenMindmaps;

  const CatalogueScreen({
    super.key,
    required this.lessons,
    required this.remoteCapsules,
    required this.activeChild,
    this.user,
    this.token,
    required this.currentGrade,
    this.currentTerm = 1,
    required this.learningDataLoading,
    required this.isArabic,
    required this.onSelectGrade,
    this.onSelectTerm,
    this.onSelectLesson,
    required this.onSelectLessonMode,
    required this.onModeSelected,
    required this.onOpenAskFahim,
    this.onOpenAskFahimMode,
    required this.onOpenPaywall,
    this.onVocalize,
    this.onOpenReader,
    this.onOpenAuth,
    this.onSwitchProfile,
    this.onOpenMindmaps,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveLessons = lessons.isNotEmpty
        ? lessons
        : (currentGrade == 5 && currentTerm == 1 ? kClass5Term1Catalogue : <CurriculumLessonItem>[]);
    final halfLen = effectiveLessons.isNotEmpty ? (effectiveLessons.length / 2).ceil() : 5;
    final unit1Lessons = effectiveLessons.where((l) => l.order <= halfLen).toList();
    final unit2Lessons = effectiveLessons.where((l) => l.order > halfLen).toList();
    final firstLesson = effectiveLessons.isNotEmpty ? effectiveLessons.first : null;

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      children: [
        if (learningDataLoading)
          const Padding(
            padding: EdgeInsets.only(bottom: 8),
            child: LinearProgressIndicator(minHeight: 2.5, color: Color(0xFF6C5CE7)),
          ),

        // =====================================================================
        // A. WELCOME WIDGET (Student Name, Transferred Avatar, Demo Class)
        // =====================================================================
        _buildWelcomeWidget(context),

        // =====================================================================
        // B. ASK FAHIM MULTIMODAL WIDGET (Voice, Text, PDF, Camera Photo)
        // =====================================================================
        _buildAskFahimMultimodalWidget(context),

        // =====================================================================
        // NEW: MINDMAPS & FLOWCHARTS SHOWCASE CARD (Visual Learning on Landing Page)
        // =====================================================================
        _buildMindmapsShowcaseCard(context),

        // =====================================================================
        // C. CURRICULUM & COURSE NAVIGATION MENU
        // =====================================================================
        _buildCurriculumAndCourseMenu(context, effectiveLessons),

        // =====================================================================
        // 1. TOP HERO GRADIENT BANNER (1:1 from Web CatalogueView lines 84-150)
        // =====================================================================
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF58337E), Color(0xFF6C5CE7), Color(0xFF4A154B)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF58337E).withValues(alpha: 0.35),
                blurRadius: 16,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Badges Row
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.18),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'Grade $currentGrade · Term 1',
                      style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.25),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      '${effectiveLessons.length} Chapters',
                      style: const TextStyle(color: Color(0xFFDCD6F7), fontSize: 10, fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Title in Bold Arabic
              const Text(
                'مِنْهَاجُ اللُّغَةِ العَرَبِيَّةِ (العَرَبِيَّةُ تَجْمَعُنَا)',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 21,
                  fontWeight: FontWeight.w900,
                  height: 1.3,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                isArabic
                    ? 'المنهاج المتكامل للناطقين باللغة العربية وغير الناطقين بها. كتاب تفاعلي، ترجمة صوتية للمفردات، ملازم ذكية واختبارات تكيفية.'
                    : 'Modern Standard Arabic for Non-Native & Native Learners. Interactive textbook, word-level audio translations, smart study booklets, and adaptive quizzes.',
                style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 11.5, height: 1.4),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // =====================================================================
        // 2. SCANNED TEXTBOOK READER QUICK ACCESS (108 Pages with Audio)
        // =====================================================================
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF064E3B), Color(0xFF047857)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF064E3B).withValues(alpha: 0.25),
                blurRadius: 10,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.auto_stories, color: Colors.white, size: 24),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            isArabic ? 'الكتاب المدرسي الممسوح الأصلي' : 'Original Scanned Textbook',
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12.5),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                          decoration: BoxDecoration(
                            color: const Color(0xFF22C55E),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            '${getTextbookPageCount(currentGrade, currentTerm)} ص',
                            style: const TextStyle(color: Colors.white, fontSize: 8.5, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      isArabic
                          ? 'تصفح كتاب الوزارة المعتمد (${getTextbookPageCount(currentGrade, currentTerm)} صفحة) مع الاستماع الصوتي'
                          : 'Read all ${getTextbookPageCount(currentGrade, currentTerm)} MoE pages with native TTS audio & zoom',
                      style: const TextStyle(color: Color(0xFFA7F3D0), fontSize: 10),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: () {
                  if (onOpenReader != null) {
                    onOpenReader!();
                  } else {
                    onModeSelected('reader');
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: const Color(0xFF064E3B),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                  elevation: 0,
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: Text(
                  isArabic ? 'فتح الكتاب' : 'Read Book',
                  style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // =====================================================================
        // 3. FEATURED SHOWCASE: COMPLETE CHAPTER 1 - BALL GAMES (أَلْعَابُ الكُرَةِ)
        // (1:1 from Web CatalogueView lines 152-329)
        // =====================================================================
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: const Color(0xFFE2E8F0)),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF6C5CE7).withValues(alpha: 0.06),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Accent Gradient Line
                Container(
                  height: 4,
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Color(0xFF6C5CE7), Color(0xFF22C55E), Color(0xFF58337E)],
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Badges
                      Wrap(
                        spacing: 6,
                        runSpacing: 4,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFFECFDF5),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: const [
                                Icon(Icons.stars, size: 12, color: Color(0xFF047857)),
                                SizedBox(width: 4),
                                Text(
                                  'الفصل الأول · نشط الآن (Active)',
                                  style: TextStyle(color: Color(0xFF047857), fontSize: 10, fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF3F0FF),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Text(
                              'الوحدة الأولى · ص 6 - 15',
                              style: TextStyle(color: Color(0xFF6C5CE7), fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFEF3C7),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Text(
                              'مجاني بالكامل (Free Access)',
                              style: TextStyle(color: Color(0xFFB45309), fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),

                      // Chapter Title & Reading Text Subtitle
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: const [
                                Text(
                                  'أَلْعَابُ الكُرَةِ (Ball Games)',
                                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF58337E)),
                                ),
                                SizedBox(height: 2),
                                Text(
                                  'النص القرائي: السَّاحِرَةُ المُسْتَدِيرَةُ (The Round Sorceress / Football)',
                                  style: TextStyle(fontSize: 11, color: Color(0xFF64748B), fontWeight: FontWeight.w500),
                                ),
                              ],
                            ),
                          ),
                          // Quick Stats
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF8FAFC),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: const Color(0xFFE2E8F0)),
                            ),
                            child: Row(
                              children: [
                                _buildMiniStat('8', 'مفردات'),
                                const SizedBox(width: 8),
                                Container(width: 1, height: 16, color: const Color(0xFFCBD5E1)),
                                const SizedBox(width: 8),
                                _buildMiniStat('2', 'قواعد'),
                                const SizedBox(width: 8),
                                Container(width: 1, height: 16, color: const Color(0xFFCBD5E1)),
                                const SizedBox(width: 8),
                                _buildMiniStat('10', 'أسئلة'),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),

                      // Interactive Passage Preview Box
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFCFAFF),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFFEDE9FE)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(
                                  children: const [
                                    Icon(Icons.menu_book, size: 14, color: Color(0xFF6C5CE7)),
                                    SizedBox(width: 6),
                                    Text(
                                      'معاينة النص القرائي (Passage Preview)',
                                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF58337E)),
                                    ),
                                  ],
                                ),
                                InkWell(
                                  onTap: () {
                                    if (onVocalize != null) {
                                      onVocalize!('كُرَةُ القَدَمِ هِيَ اللُّعْبَةُ الأَكْثَرُ شَعْبِيَّةً فِي العَالَمِ. يُحِبُّهَا الكِبَارُ وَالصِّغَارُ، حَيْثُ يَتَنَافَسُ فِي المَلْعَبِ فَرِيقَانِ كَبِيرَانِ لِتَسْجِيلِ الهَدَفِ فِي شِبَاكِ حَارِسِ المَرْمَى.');
                                    }
                                  },
                                  child: Row(
                                    children: const [
                                      Icon(Icons.volume_up, size: 14, color: Color(0xFF6C5CE7)),
                                      SizedBox(width: 4),
                                      Text(
                                        'استمع للنص',
                                        style: TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF6C5CE7)),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              '«كُرَةُ القَدَمِ هِيَ اللُّعْبَةُ الأَكْثَرُ شَعْبِيَّةً فِي العَالَمِ. يُحِبُّهَا الكِبَارُ وَالصِّغَارُ، حَيْثُ يَتَنَافَسُ فِي المَلْعَبِ فَرِيقَانِ كَبِيرَانِ لِتَسْجِيلِ الهَدَفِ فِي شِبَاكِ حَارِسِ المَرْمَى.»',
                              textAlign: TextAlign.right,
                              style: TextStyle(
                                fontSize: 14.5,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1E293B),
                                height: 1.8,
                              ),
                            ),
                            const SizedBox(height: 4),
                            const Text(
                              '"Football is the most popular game in the world. Both young and old love it, where two large teams compete on the pitch to score goals into the goalkeeper\'s net."',
                              style: TextStyle(fontSize: 10.5, fontStyle: FontStyle.italic, color: Color(0xFF64748B)),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),

                      // 4 INTERACTIVE CURRICULUM PILLARS (Clean 2x2 Grid)
                      GridView.count(
                        crossAxisCount: 2,
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        crossAxisSpacing: 10,
                        mainAxisSpacing: 10,
                        childAspectRatio: 1.35,
                        children: [
                          _buildPillarCard(
                            number: '1',
                            titleAr: 'قراءة الدرس والنص',
                            titleEn: 'Interactive Reading',
                            subtitle: 'نص تفاعلي وترجمة صوتية',
                            icon: Icons.menu_book_rounded,
                            color: const Color(0xFF3B82F6),
                            bg: const Color(0xFFEFF6FF),
                            onTap: firstLesson != null
                                ? () => onSelectLessonMode(firstLesson, LessonViewMode.textbookReader)
                                : null,
                          ),
                          _buildPillarCard(
                            number: '2',
                            titleAr: 'الملزمة الذكية',
                            titleEn: 'Smart Study Notes',
                            subtitle: 'ملخص ١٥ دقيقة للمفردات والقواعد',
                            icon: Icons.edit_note_rounded,
                            color: const Color(0xFF10B981),
                            bg: const Color(0xFFECFDF5),
                            onTap: () => onModeSelected('malazim'),
                          ),
                          _buildPillarCard(
                            number: '3',
                            titleAr: 'الكبسولة السريعة',
                            titleEn: '3-Min Capsule',
                            subtitle: 'كبسولة نحوية صوتية سريعة',
                            icon: Icons.access_time_rounded,
                            color: const Color(0xFF8B5CF6),
                            bg: const Color(0xFFF5F3FF),
                            onTap: () => onModeSelected('capsules'),
                          ),
                          _buildPillarCard(
                            number: '4',
                            titleAr: 'اختبار محاكاة الوزارة',
                            titleEn: 'Ministry Mock Exam',
                            subtitle: '١٠ أسئلة تدريبية مع توقيت',
                            icon: Icons.quiz_rounded,
                            color: const Color(0xFFF59E0B),
                            bg: const Color(0xFFFFFBEB),
                            onTap: () => onModeSelected('tests'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 14),

                      // Two Big Action Buttons
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: firstLesson != null
                                  ? () => onSelectLessonMode(firstLesson, LessonViewMode.lparSequence)
                                  : null,
                              icon: const Icon(Icons.play_arrow, size: 16),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF58337E),
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                                elevation: 1,
                              ),
                              label: const Text(
                                'قراءة الدرس كاملاً',
                                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () => onModeSelected('malazim'),
                              icon: const Icon(Icons.book, size: 16, color: Color(0xFF047857)),
                              style: OutlinedButton.styleFrom(
                                backgroundColor: const Color(0xFFECFDF5),
                                foregroundColor: const Color(0xFF047857),
                                side: const BorderSide(color: Color(0xFFA7F3D0)),
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                              ),
                              label: const Text(
                                'ملزمة الفصل الذكية',
                                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 14),

        // =====================================================================
        // 4. QUICK HUB: 10 CORE CAPABILITIES BAR
        // =====================================================================
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildHubChip(
                icon: Icons.auto_awesome,
                labelAr: 'اسأل فاهم',
                labelEn: 'Ask Fahim AI',
                color: const Color(0xFF6C5CE7),
                bg: const Color(0xFFF3F0FF),
                onTap: onOpenAskFahim,
              ),
              const SizedBox(width: 8),
              _buildHubChip(
                icon: Icons.edit_note_rounded,
                labelAr: 'الملازم الذكية',
                labelEn: 'Smart Malazim',
                color: const Color(0xFF2563EB),
                bg: const Color(0xFFDBEAFE),
                onTap: () => onModeSelected('malazim'),
              ),
              const SizedBox(width: 8),
              _buildHubChip(
                icon: Icons.medical_services_outlined,
                labelAr: 'الكبسولات اللغوية',
                labelEn: 'Grammar Capsules',
                color: const Color(0xFF7C3AED),
                bg: const Color(0xFFEDE9FE),
                onTap: () => onModeSelected('capsules'),
              ),
              const SizedBox(width: 8),
              _buildHubChip(
                icon: Icons.account_tree_rounded,
                labelAr: 'خرائط المفاهيم',
                labelEn: 'Mindmaps',
                color: const Color(0xFF0D9488),
                bg: const Color(0xFFCCFBF1),
                onTap: () {
                  if (onOpenMindmaps != null) {
                    onOpenMindmaps!();
                  } else {
                    onModeSelected('mindmaps');
                  }
                },
              ),
              const SizedBox(width: 8),
              _buildHubChip(
                icon: Icons.timer_outlined,
                labelAr: 'محاكي الامتحان',
                labelEn: 'Exam Simulator',
                color: const Color(0xFFEC4899),
                bg: const Color(0xFFFCE7F3),
                onTap: () => onModeSelected('tests'),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),

        // =====================================================================
        // =====================================================================
        // 5. TERM & GRADE PICKER (Class 1 to 12 & Terms 1 to 3)
        // =====================================================================
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              isArabic ? 'اختر الفصل الدراسي:' : 'SELECT TERM (اختر الفصل الدراسي):',
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 0.5),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2.5),
              decoration: BoxDecoration(
                color: const Color(0xFFEDE9FE),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                isArabic ? 'الفصل $currentTerm محدد' : 'Term $currentTerm Selected',
                style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF6C5CE7)),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [1, 2, 3].map((t) {
            final isSel = currentTerm == t;
            final labelAr = t == 1 ? 'الفصل الأول' : (t == 2 ? 'الفصل الثاني' : 'الفصل الثالث');
            final labelEn = 'Term $t';
            return Expanded(
              child: Padding(
                padding: EdgeInsets.only(right: t < 3 ? 6.0 : 0.0),
                child: InkWell(
                  borderRadius: BorderRadius.circular(14),
                  onTap: () => onSelectTerm?.call(t),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      gradient: isSel
                          ? const LinearGradient(colors: [Color(0xFF58337E), Color(0xFF6C5CE7)])
                          : null,
                      color: isSel ? null : Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                        color: isSel ? const Color(0xFF6C5CE7) : const Color(0xFFE2E8F0),
                        width: isSel ? 1.5 : 1.0,
                      ),
                      boxShadow: isSel
                          ? [
                              BoxShadow(
                                color: const Color(0xFF6C5CE7).withValues(alpha: 0.25),
                                blurRadius: 6,
                                offset: const Offset(0, 2),
                              ),
                            ]
                          : null,
                    ),
                    alignment: Alignment.center,
                    child: Text(
                      isArabic ? labelAr : labelEn,
                      style: TextStyle(
                        color: isSel ? Colors.white : const Color(0xFF475569),
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 14),

        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              isArabic ? 'اختر الصف الدراسي:' : 'SELECT GRADE (اختر الصف الدراسي):',
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748B), letterSpacing: 0.5),
            ),
            Text(
              'Grade $currentGrade Selected',
              style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF6C5CE7)),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: List.generate(12, (index) {
              final g = index + 1;
              final isSel = currentGrade == g;
              return Padding(
                padding: const EdgeInsets.only(right: 6),
                child: InkWell(
                  borderRadius: BorderRadius.circular(16),
                  onTap: () => onSelectGrade(g),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                    decoration: BoxDecoration(
                      color: isSel ? const Color(0xFF6C5CE7) : Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isSel ? const Color(0xFF6C5CE7) : const Color(0xFFE2E8F0),
                      ),
                      boxShadow: isSel
                          ? [
                              BoxShadow(
                                color: const Color(0xFF6C5CE7).withValues(alpha: 0.3),
                                blurRadius: 6,
                                offset: const Offset(0, 2),
                              ),
                            ]
                          : null,
                    ),
                    child: Text(
                      'Class $g',
                      style: TextStyle(
                        color: isSel ? Colors.white : const Color(0xFF475569),
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ),
              );
            }),
          ),
        ),
        const SizedBox(height: 20),

        // =====================================================================
        // 6. FULL SYLLABUS: ALL LESSONS FOR SELECTED GRADE & TERM
        // =====================================================================
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isArabic
                        ? 'فهرس فصول المنهاج (الصف $currentGrade · الفصل $currentTerm)'
                        : 'Grade $currentGrade · Term $currentTerm Chapters (${effectiveLessons.length})',
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: Color(0xFF1E293B)),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    isArabic
                        ? 'الدروس الرسمية المعتمدة لمنهاج وزارة التربية والتعليم'
                        : 'Official UAE MoE Approved Curriculum Syllabus',
                    style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            if (user?['role'] == 'admin')
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: const Color(0xFFECFDF5),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFA7F3D0)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.verified, size: 14, color: Color(0xFF059669)),
                    const SizedBox(width: 4),
                    Text(
                      isArabic ? 'وصول المشرف مفعّل' : 'Admin Unlocked',
                      style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF065F46)),
                    ),
                  ],
                ),
              )
            else
              TextButton.icon(
                onPressed: onOpenPaywall,
                icon: const Icon(Icons.lock_open, size: 13, color: Color(0xFF6C5CE7)),
                label: Text(
                  isArabic ? 'فتح الفصل كامل (USD 20)' : r'Unlock (USD 20)',
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF6C5CE7)),
                ),
                style: TextButton.styleFrom(
                  backgroundColor: const Color(0xFFF3F0FF),
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
          ],
        ),
        const SizedBox(height: 14),

        if (unit1Lessons.isNotEmpty) ...[
          _buildUnitHeader(
            unitNumber: '1',
            titleAr: unit1Lessons.first.unitTitleAr.isNotEmpty
                ? 'الوحدة الأولى: ${unit1Lessons.first.unitTitleAr}'
                : 'الوحدة الأولى: المهارات التأسيسية والقراءة',
            titleEn: unit1Lessons.first.unitTitleEn.isNotEmpty
                ? 'Unit 1: ${unit1Lessons.first.unitTitleEn}'
                : 'Unit 1: Foundation Skills & Reading',
            color: const Color(0xFF6C5CE7),
          ),
          const SizedBox(height: 8),
          ...unit1Lessons.map((l) => _buildUnifiedLessonCard(l)),
          const SizedBox(height: 16),
        ],

        if (unit2Lessons.isNotEmpty) ...[
          _buildUnitHeader(
            unitNumber: '2',
            titleAr: unit2Lessons.first.unitTitleAr.isNotEmpty
                ? 'الوحدة الثانية: ${unit2Lessons.first.unitTitleAr}'
                : 'الوحدة الثانية: القواعد اللغوية والتعبير',
            titleEn: unit2Lessons.first.unitTitleEn.isNotEmpty
                ? 'Unit 2: ${unit2Lessons.first.unitTitleEn}'
                : 'Unit 2: Grammar & Expression',
            color: const Color(0xFF10B981),
          ),
          const SizedBox(height: 8),
          ...unit2Lessons.map((l) => _buildUnifiedLessonCard(l)),
        ],
        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildMiniStat(String val, String label) {
    return Column(
      children: [
        Text(val, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w900, color: Color(0xFF58337E))),
        Text(label, style: const TextStyle(fontSize: 8.5, color: Color(0xFF64748B), fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildPillarCard({
    required String number,
    required String titleAr,
    required String titleEn,
    required String subtitle,
    required IconData icon,
    required Color color,
    required Color bg,
    VoidCallback? onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withValues(alpha: 0.2)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(icon, color: color, size: 20),
                Text(
                  number,
                  style: TextStyle(color: color.withValues(alpha: 0.6), fontSize: 13, fontWeight: FontWeight.w900),
                ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  titleAr,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  titleEn,
                  style: TextStyle(fontSize: 9.5, color: color, fontWeight: FontWeight.bold),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  subtitle,
                  style: const TextStyle(fontSize: 8.5, color: Color(0xFF64748B)),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHubChip({
    required IconData icon,
    required String labelAr,
    required String labelEn,
    required Color color,
    required Color bg,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withValues(alpha: 0.25)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(labelAr, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color)),
                Text(labelEn, style: const TextStyle(fontSize: 8.5, color: Color(0xFF64748B))),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUnitHeader({
    required String unitNumber,
    required String titleAr,
    required String titleEn,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 10,
            backgroundColor: color,
            child: Text(unitNumber, style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(titleAr, style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: color)),
                Text(titleEn, style: const TextStyle(fontSize: 9.5, color: Color(0xFF64748B))),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUnifiedLessonCard(CurriculumLessonItem lesson) {
    final isDemo = lesson.isFirstChapterDemo;
    final isUnlocked = lesson.isAccessible;

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: isDemo ? const Color(0xFF6C5CE7) : (isUnlocked ? const Color(0xFF22C55E) : const Color(0xFFF1F0FA)),
          width: isDemo ? 1.5 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header: Lesson Order, Page, Badge
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'الدرس ${lesson.order} (L${lesson.order}) · ص ${lesson.startPage}',
                  style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold, color: Color(0xFF64748B)),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: isDemo
                        ? const Color(0xFFECFDF5)
                        : (isUnlocked ? const Color(0xFFF3F0FF) : const Color(0xFFF1F5F9)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        isDemo
                            ? Icons.stars_rounded
                            : (isUnlocked ? Icons.check_circle_outline : Icons.lock_outline),
                        size: 11,
                        color: isDemo
                            ? const Color(0xFF047857)
                            : (isUnlocked ? const Color(0xFF6C5CE7) : const Color(0xFF64748B)),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        isDemo
                            ? 'مجاني (FREE)'
                            : (isUnlocked ? 'متاح (UNLOCKED)' : 'مغلق (LOCKED)'),
                        style: TextStyle(
                          color: isDemo
                              ? const Color(0xFF047857)
                              : (isUnlocked ? const Color(0xFF6C5CE7) : const Color(0xFF64748B)),
                          fontSize: 9,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),

            // Arabic Title
            Text(
              lesson.titleAr,
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w900,
                color: Color(0xFF58337E),
              ),
            ),
            Text(
              lesson.titleEn,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
            ),
            const SizedBox(height: 12),

            // Dual Action Buttons: Read Book vs Interactive LPAR
            Row(
              children: [
                if (isUnlocked || isDemo) ...[
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => onSelectLessonMode(lesson, LessonViewMode.textbookReader),
                      icon: const Icon(Icons.auto_stories, size: 14),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF58337E),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 9),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        elevation: 0,
                      ),
                      label: Text(
                        isDemo ? 'قراءة الدرس' : 'كتاب الدرس',
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => onSelectLessonMode(lesson, LessonViewMode.lparSequence),
                      icon: const Icon(Icons.play_circle_outline, size: 14, color: Color(0xFF6C5CE7)),
                      style: OutlinedButton.styleFrom(
                        backgroundColor: const Color(0xFFF8F7FF),
                        foregroundColor: const Color(0xFF6C5CE7),
                        side: const BorderSide(color: Color(0xFFDCD6F7)),
                        padding: const EdgeInsets.symmetric(vertical: 9),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      label: const Text(
                        'مسار تفاعلي (LPAR)',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ] else ...[
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: onOpenPaywall,
                      icon: const Icon(Icons.lock, size: 14),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFF1F5F9),
                        foregroundColor: const Color(0xFF64748B),
                        padding: const EdgeInsets.symmetric(vertical: 10),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        elevation: 0,
                      ),
                      label: Text(
                        isArabic ? 'فتح الدرس (USD 20 للفصل)' : r'Unlock Lesson (USD 20/term)',
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _getAvatarIcon(dynamic avatarId) {
    switch (avatarId) {
      case 'avatar_falcon': return '🦅';
      case 'avatar_gazelle': return '🦌';
      case 'avatar_oryx': return '🦬';
      case 'avatar_camel': return '🐪';
      case 'avatar_palm': return '🌴';
      default: return '🦅';
    }
  }

  Widget _buildWelcomeWidget(BuildContext context) {
    final bool isGuest = token == null || activeChild == null;
    final String avatar = isGuest ? '🦅' : _getAvatarIcon(activeChild?['avatar_id']);
    final String studentName = isGuest
        ? (isArabic ? 'الضيف' : 'Guest')
        : (activeChild?['name'] ?? (isArabic ? 'طالب جسر' : 'Learner'));
    final String welcomeGreeting = isArabic
        ? 'مرحباً بك $studentName'
        : 'Welcome $studentName';
    final String classBadge = isGuest
        ? (isArabic ? 'صف تجريبي' : 'Demo Class')
        : (isArabic ? 'الصف ${activeChild?['default_grade'] ?? currentGrade}' : 'Class ${activeChild?['default_grade'] ?? currentGrade}');

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF6C5CE7).withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        children: [
          // Transferred Avatar Icon with gradient background
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF6C5CE7), Color(0xFFA29BFE)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF6C5CE7).withValues(alpha: 0.25),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            alignment: Alignment.center,
            child: Text(avatar, style: const TextStyle(fontSize: 24)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  welcomeGreeting,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w900,
                    color: Color(0xFF1E293B),
                  ),
                ),
                const SizedBox(height: 3),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: isGuest ? const Color(0xFFFEF3C7) : const Color(0xFFECFDF5),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                          color: isGuest ? const Color(0xFFFDE68A) : const Color(0xFFA7F3D0),
                        ),
                      ),
                      child: Text(
                        classBadge,
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: isGuest ? const Color(0xFFB45309) : const Color(0xFF065F46),
                        ),
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      isArabic ? '· الفصل الدراسي الأول' : '· Term 1',
                      style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8)),
                    ),
                  ],
                ),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: isGuest ? onOpenAuth : onSwitchProfile,
            style: ElevatedButton.styleFrom(
              backgroundColor: isGuest ? const Color(0xFF6C5CE7) : const Color(0xFFF1F0FB),
              foregroundColor: isGuest ? Colors.white : const Color(0xFF6C5CE7),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              elevation: 0,
            ),
            child: Text(
              isGuest
                  ? (isArabic ? 'تسجيل الدخول' : 'Sign In')
                  : (isArabic ? 'تبديل الحساب' : 'Switch'),
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAskFahimMultimodalWidget(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF58337E), Color(0xFF6C5CE7)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF58337E).withValues(alpha: 0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    alignment: Alignment.center,
                    child: const Icon(Icons.auto_awesome, color: Color(0xFFFBBF24), size: 20),
                  ),
                  const SizedBox(width: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isArabic ? 'اسأل فاهم (المعلم الذكي)' : 'Ask Fahim (AI Tutor)',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w900,
                          fontSize: 15,
                        ),
                      ),
                      Text(
                        isArabic
                            ? 'المعلم السقراطي الذكي لمناهج الإمارات'
                            : 'Socratic Conversational Arabic Companion',
                        style: const TextStyle(color: Color(0xFFDCD6F7), fontSize: 10.5),
                      ),
                    ],
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFF22C55E),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Text(
                  'AI Active',
                  style: TextStyle(color: Colors.white, fontSize: 9.5, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            isArabic
                ? 'تفاعل صوتياً أو نصياً مع فاهم، أو ارفع مستنداتك وصور تدريبات الكتاب المدرسي:'
                : 'Interact via voice or text, or upload textbook PDFs and camera photos:',
            style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 11),
          ),
          const SizedBox(height: 12),
          // 4 Action Buttons Grid
          Row(
            children: [
              Expanded(
                child: _askFahimTile(
                  icon: Icons.mic_rounded,
                  iconColor: const Color(0xFF10B981),
                  bgColor: Colors.white,
                  title: isArabic ? 'تحدث صوتياً' : 'Voice Tutor',
                  subtitle: isArabic ? 'حوار ناطق' : 'Speak Aloud',
                  onTap: () => onOpenAskFahimMode?.call('voice') ?? onOpenAskFahim(),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _askFahimTile(
                  icon: Icons.chat_bubble_outline_rounded,
                  iconColor: const Color(0xFF6C5CE7),
                  bgColor: Colors.white,
                  title: isArabic ? 'محادثة نصية' : 'Text Chat',
                  subtitle: isArabic ? 'شرح فوري' : 'Ask Anything',
                  onTap: () => onOpenAskFahimMode?.call('text') ?? onOpenAskFahim(),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _askFahimTile(
                  icon: Icons.picture_as_pdf_rounded,
                  iconColor: const Color(0xFFEF4444),
                  bgColor: Colors.white,
                  title: isArabic ? 'رفع ملف PDF' : 'Upload PDF',
                  subtitle: isArabic ? 'تلخيص وشرح' : 'Study Notes',
                  onTap: () => onOpenAskFahimMode?.call('pdf') ?? onOpenAskFahim(),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _askFahimTile(
                  icon: Icons.photo_camera_rounded,
                  iconColor: const Color(0xFFF59E0B),
                  bgColor: Colors.white,
                  title: isArabic ? 'التقاط صورة' : 'Camera Photo',
                  subtitle: isArabic ? 'مسح التدريبات' : 'Scan Exercise',
                  onTap: () => onOpenAskFahimMode?.call('camera') ?? onOpenAskFahim(),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          InkWell(
            onTap: () => onOpenAskFahimMode?.call('exam') ?? onOpenAskFahim(),
            borderRadius: BorderRadius.circular(16),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFEDE9FE), Color(0xFFDDD6FE)],
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFC4B5FD)),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(7),
                    decoration: BoxDecoration(
                      color: const Color(0xFF6C5CE7),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Icon(Icons.assignment_turned_in_rounded, color: Colors.white, size: 18),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              isArabic ? 'مساعد حل أوراق الامتحانات' : 'Exam Paper Assistant',
                              style: const TextStyle(
                                fontSize: 11.5,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF4C1D95),
                              ),
                            ),
                            const SizedBox(width: 6),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                              decoration: BoxDecoration(
                                color: const Color(0xFFECFDF5),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: const Color(0xFFA7F3D0)),
                              ),
                              child: Text(
                                isArabic ? 'المساعد الذكي' : 'AI Assistant',
                                style: const TextStyle(
                                  fontSize: 8,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF047857),
                                ),
                              ),
                            ),
                          ],
                        ),
                        Text(
                          isArabic
                              ? 'حل فوري لأوراق الامتحانات والأسئلة مع نماذج الإجابات وتوثيق المنهج'
                              : 'Autonomous exam solving with model answers & MoE citations',
                          style: const TextStyle(fontSize: 9.5, color: Color(0xFF5B21B6)),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.arrow_forward_ios_rounded, size: 14, color: Color(0xFF6C5CE7)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _askFahimTile({
    required IconData icon,
    required Color iconColor,
    required Color bgColor,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                color: iconColor.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: iconColor, size: 18),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 11.5,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1E293B),
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 9.5, color: Color(0xFF64748B)),
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMindmapsShowcaseCard(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF3B82F6), Color(0xFF6C5CE7), Color(0xFF8B5CF6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF6C5CE7).withValues(alpha: 0.28),
            blurRadius: 14,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Icon(Icons.account_tree_rounded, color: Colors.white, size: 26),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.22),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        isArabic ? 'جديد • دراسة بصرية تفاعلية' : 'NEW • VISUAL MINDMAPS & FLOWCHARTS',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 9.5,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isArabic ? 'خرائط المفاهيم والتدفق الذهني' : 'Mindmaps & Flowcharts',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            isArabic
                ? 'استكشف الدروس عبر خرائط ذهنية شجرية، ومخططات انسيابية دقيقة لقواعد الإعراب (المبتدأ، الخبر، الفاعل، المفعول به) مع الترجمة الإنجليزية الكاملة لكل كلمة!'
                : 'Study lessons easily with interactive concept trees, syntax decision flowcharts (Mubtada, Khabar, Fa\'il, Object), and full English translations under every word!',
            style: const TextStyle(color: Color(0xFFF1F5F9), fontSize: 12, height: 1.4),
          ),
          const SizedBox(height: 14),
          Wrap(
            alignment: WrapAlignment.spaceBetween,
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 8,
            runSpacing: 10,
            children: [
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      isArabic ? 'دروس الصف $currentGrade' : 'Class $currentGrade Lessons',
                      style: const TextStyle(color: Colors.white, fontSize: 10.5, fontWeight: FontWeight.bold),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      isArabic ? 'مخطط الإعراب' : 'Syntax Flowchart',
                      style: const TextStyle(color: Colors.white, fontSize: 10.5, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              ElevatedButton.icon(
                onPressed: () {
                  if (onOpenMindmaps != null) {
                    onOpenMindmaps!();
                  } else {
                    onModeSelected('mindmaps');
                  }
                },
                icon: const Icon(Icons.arrow_forward_rounded, size: 16),
                label: Text(
                  isArabic ? 'فتح الخرائط' : 'Explore Now',
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: const Color(0xFF4338CA),
                  elevation: 0,
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCurriculumAndCourseMenu(BuildContext context, List<CurriculumLessonItem> effectiveLessons) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.apps_rounded, color: Color(0xFF58337E), size: 20),
                  const SizedBox(width: 6),
                  Text(
                    isArabic ? 'المنهاج والدورات التعليمية' : 'Curriculum & Courses',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w900,
                      color: Color(0xFF1E293B),
                    ),
                  ),
                ],
              ),
              Text(
                isArabic ? 'اختر مسار التعلم' : 'Navigation Menu',
                style: const TextStyle(color: Color(0xFF64748B), fontSize: 11, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 10),
          _curriculumMenuCard(
            icon: Icons.menu_book_rounded,
            iconColor: const Color(0xFF6C5CE7),
            iconBg: const Color(0xFFF3F0FF),
            title: isArabic ? 'المنهاج والدروس تفاعلياً (LPAR)' : 'Curriculum & Lessons (LPAR)',
            subtitle: isArabic ? '10 دروس للفصل الدراسي الأول مع الاستماع والتدريب والتطبيق والمراجعة' : '10 Term 1 lessons with Listen, Practice, Apply & Review',
            badge: 'Ch. 1 Active',
            badgeColor: const Color(0xFF22C55E),
            onTap: () {
              if (effectiveLessons.isNotEmpty) {
                onSelectLessonMode(effectiveLessons.first, LessonViewMode.lparSequence);
              }
            },
          ),
          const SizedBox(height: 8),
          _curriculumMenuCard(
            icon: Icons.auto_stories_rounded,
            iconColor: const Color(0xFF047857),
            iconBg: const Color(0xFFECFDF5),
            title: isArabic
                ? 'الكتاب المدرسي الممسوح (${getTextbookPageCount(currentGrade, currentTerm)} صفحة)'
                : 'Scanned MoE Textbook (${getTextbookPageCount(currentGrade, currentTerm)} Pages)',
            subtitle: isArabic
                ? 'تصفح صفحات كتاب الوزارة الأصلي صفحة بصفحة مع تدقيق OCR والاستماع الصوتي'
                : 'All ${getTextbookPageCount(currentGrade, currentTerm)} original textbook pages with TTS vocalization & zoom',
            badge: '${getTextbookPageCount(currentGrade, currentTerm)} Pages',
            badgeColor: const Color(0xFF047857),
            onTap: () {
              if (onOpenReader != null) {
                onOpenReader!();
              } else {
                onModeSelected('reader');
              }
            },
          ),
          const SizedBox(height: 8),
          _curriculumMenuCard(
            icon: Icons.account_tree_rounded,
            iconColor: const Color(0xFF6C5CE7),
            iconBg: const Color(0xFFF3F0FF),
            title: isArabic ? 'خرائط المفاهيم والتدفق الذهني' : 'Mindmaps & Flowcharts',
            subtitle: isArabic
                ? 'خرائط بصرية تفاعلية للدروس، مخططات شجرية للإعراب، وقواعد النحو لجميع الفصول'
                : 'Interactive concept mindmaps for lessons, syntax decision flowcharts & grammar rules tree',
            badge: isArabic ? 'دراسة بصرية' : 'Visual Study',
            badgeColor: const Color(0xFF6C5CE7),
            onTap: () {
              if (onOpenMindmaps != null) {
                onOpenMindmaps!();
              } else {
                onModeSelected('mindmaps');
              }
            },
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _curriculumSquareCard(
                  icon: Icons.edit_note_rounded,
                  iconColor: const Color(0xFF2563EB),
                  iconBg: const Color(0xFFDBEAFE),
                  title: isArabic ? 'الملازم الذكية' : 'Smart Malazim',
                  subtitle: isArabic ? 'مراجعة 15 دقيقة' : '15-Min Notes',
                  onTap: () => onModeSelected('malazim'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _curriculumSquareCard(
                  icon: Icons.medical_services_outlined,
                  iconColor: const Color(0xFF7C3AED),
                  iconBg: const Color(0xFFEDE9FE),
                  title: isArabic ? 'الكبسولات اللغوية' : 'Learning Capsules',
                  subtitle: isArabic ? 'نحو 3-5 دقائق' : '3-5 Min Grammar',
                  onTap: () => onModeSelected('capsules'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          _curriculumMenuCard(
            icon: Icons.quiz_rounded,
            iconColor: const Color(0xFFD97706),
            iconBg: const Color(0xFFFEF3C7),
            title: isArabic ? 'محاكاة الامتحانات والتقييم' : 'MoE Exam Simulator & Assessment',
            subtitle: isArabic ? 'اختبارات وزارية وفق معايير 40/30/20/10 الرسمية مع تصحيح فوري' : 'Standardized MoE blueprint exam simulation with automated scoring',
            badge: 'Exam Blueprint',
            badgeColor: const Color(0xFFD97706),
            onTap: () => onModeSelected('tests'),
          ),
        ],
      ),
    );
  }

  Widget _curriculumMenuCard({
    required IconData icon,
    required Color iconColor,
    required Color iconBg,
    required String title,
    required String subtitle,
    required String badge,
    required Color badgeColor,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFE2E8F0)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.03),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: iconBg,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: iconColor, size: 22),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          title,
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1E293B),
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: badgeColor,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          badge,
                          style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 10.5, color: Color(0xFF64748B)),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 6),
            const Icon(Icons.arrow_forward_ios, size: 14, color: Color(0xFFCBD5E1)),
          ],
        ),
      ),
    );
  }

  Widget _curriculumSquareCard({
    required IconData icon,
    required Color iconColor,
    required Color iconBg,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFE2E8F0)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.03),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: iconBg,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: iconColor, size: 18),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 9.5, color: Color(0xFF64748B)),
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

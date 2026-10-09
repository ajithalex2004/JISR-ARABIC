// ignore_for_file: deprecated_member_use
import 'package:flutter/material.dart';

class OnboardingWizardDialog extends StatefulWidget {
  final Map<String, dynamic> child;
  final Function(Map<String, dynamic> updatedChild) onCompleted;

  const OnboardingWizardDialog({
    super.key,
    required this.child,
    required this.onCompleted,
  });

  @override
  State<OnboardingWizardDialog> createState() => _OnboardingWizardDialogState();
}

class _OnboardingWizardDialogState extends State<OnboardingWizardDialog> {
  int _currentStep = 1;

  // Step 1: Profile & Demographics
  late TextEditingController _nameCtrl;
  late TextEditingController _schoolCtrl;
  String _avatarId = 'avatar_falcon';
  String _gender = 'Boy';
  int _age = 10;
  int _grade = 5;

  // Step 2: Stream & Term
  String _stream = 'MoE / CBSE Arabic (Non-Arabs)';
  int _selectedTerm = 1;
  late TextEditingController _pinCtrl;

  // Step 3: Diagnostic Assessment
  int _activeQIndex = 0;
  final Map<String, int> _answers = {};
  bool _isGrading = false;

  final List<Map<String, dynamic>> _diagnosticQuestions = [
    {
      'id': 'diag_q1',
      'competency': 'Reading Comprehension (فهم المقروء)',
      'passage':
          'يُعَدُّ الصَّقْرُ رَمْزًا أَصِيلًا فِي دَوْلَةِ الْإِمَارَاتِ. يَمْتَازُ بِبَصَرِهِ الْحَادِّ وَسُرْعَتِهِ الْفَائِقَةِ فِي الصَّيْدِ.',
      'question': 'مَا الَّذِي يُمَيِّزُ الصَّقْرَ بِحَسَبِ النَّصِّ؟',
      'options': [
        'لَوْنُهُ الْأَبْيَضُ النَّاصِعُ',
        'بَصَرُهُ الْحَادُّ وَسُرْعَتُهُ الْفَائِقَةُ',
        'حُبُّهُ لِلسِّبَاحَةِ فِي الْبَحْرِ',
        'نَوْمُهُ الطَّوِيلُ فِي النَّهَارِ',
      ],
      'correct': 1,
    },
    {
      'id': 'diag_q2',
      'competency': 'Vocabulary & Context (المفردات والسياق)',
      'passage': null,
      'question':
          'مَا مَعْنَى كَلِمَةِ «مَغْمُورًا» فِي: «كَانَ الطَّالِبُ مَغْمُورًا بِالسَّعَادَةِ»؟',
      'options': [
        'حَزِينًا وَمُتَرَدِّدًا',
        'غَارِقًا وَمَمْلُوءًا بِالْفَرَحِ',
        'خَائِفًا وَمُضْطَرِبًا',
        'نَائِمًا فِي مَكَانِهِ',
      ],
      'correct': 1,
    },
    {
      'id': 'diag_q3',
      'competency': 'Grammar & Syntax (القواعد والتراكيب)',
      'passage': null,
      'question': 'اخْتَرِ الْجُمْلَةَ الاسْمِيَّةَ الصَّحِيحَةَ نَحْوِيًّا:',
      'options': [
        'اَلْأَشْجَارُ مُثْمِرَةٌ',
        'اَلْأَشْجَارَ مُثْمِرَةً',
        'اَلْأَشْجَارِ مُثْمِرٌ',
        'اَلْأَشْجَارُ مُثْمِرٍ',
      ],
      'correct': 0,
    },
    {
      'id': 'diag_q4',
      'competency': 'Grammar & Structure (القواعد والتراكيب)',
      'passage': null,
      'question':
          'أَكْمِلِ الْفَرَاغَ بِالْفِعْلِ الْمُنَاسِبِ: «الطَّالِبَاتُ ________ فِي الْمُسَابَقَةِ.»',
      'options': [
        'شَارَكُوا (مذكر جمع)',
        'شَارَكْنَ (نون النسوة)',
        'شَارَكَتَا (مثنى مؤنث)',
        'يُشَارِكُ (مفرد مذكر)',
      ],
      'correct': 1,
    },
  ];

  // Step 4: Calibrated Results
  double _scorePct = 0.0;
  int _correctCount = 0;
  String _calibratedLevel = 'guided';
  String _levelTitleAr = 'المسار الموجه (متوسط)';
  String _levelSummary =
      'أساس لغوي جيد ومبشر. تم تصميم المسار لتعزيز القواعد والتراكيب ودعم الفهم القرائي مع تلميحات ومساعد جسر الذكي.';

  final List<Map<String, String>> _avatars = [
    {'id': 'avatar_falcon', 'name': 'صقر 🦅'},
    {'id': 'avatar_gazelle', 'name': 'غزال 🦌'},
    {'id': 'avatar_oryx', 'name': 'مها 🦬'},
    {'id': 'avatar_camel', 'name': 'جمل 🐪'},
    {'id': 'avatar_palm', 'name': 'نخلة 🌴'},
  ];

  @override
  void initState() {
    super.initState();
    _nameCtrl = TextEditingController(
        text: widget.child['name'] ?? 'Zayed Al-Nuaimi');
    _schoolCtrl = TextEditingController(
        text: widget.child['school_name'] ??
            'Sunrise International School, Abu Dhabi');
    _avatarId = widget.child['avatar_id'] ?? 'avatar_falcon';
    _gender = widget.child['gender'] ?? 'Boy';
    _age = widget.child['age'] ?? 10;
    _grade = widget.child['default_grade'] ?? 5;
    _stream =
        widget.child['curriculum_stream'] ?? 'MoE / CBSE Arabic (Non-Arabs)';
    _selectedTerm = widget.child['selected_term'] ?? 1;
    _pinCtrl = TextEditingController();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _schoolCtrl.dispose();
    _pinCtrl.dispose();
    super.dispose();
  }

  void _submitDiagnostic() {
    if (_answers.length < _diagnosticQuestions.length) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please answer all questions to calibrate accurately.'),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.zero),
        ),
      );
      return;
    }

    setState(() {
      _isGrading = true;
    });

    Future.delayed(const Duration(milliseconds: 600), () {
      int correct = 0;
      for (final q in _diagnosticQuestions) {
        if (_answers[q['id']] == q['correct']) {
          correct++;
        }
      }
      final pct = (correct / _diagnosticQuestions.length) * 100.0;
      String level = 'guided';
      String titleAr = 'المسار الموجه (متوسط)';
      String summary =
          'أساس لغوي جيد ومبشر. تم تصميم المسار لتعزيز القواعد والتراكيب ودعم الفهم القرائي مع تلميحات ومساعد جسر الذكي.';

      if (pct >= 75.0) {
        level = 'independent';
        titleAr = 'المسار المستقل (متمكن)';
        summary =
            'أداء متميز واستيعاب لغوي متين. تم تخصيص محتوى تفاعلي إثرائي يركز على التطبيقات المتقدمة والطلاقة اللغوية.';
      } else if (pct < 50.0) {
        level = 'foundation';
        titleAr = 'المسار التأسيسي (مبتدئ)';
        summary =
            'مسار داعم وتأسيسي يركز على بناء المفردات خطوة بخطوة، والتراكيب الجملية البسيطة مع نطق صوتي كامل.';
      }

      setState(() {
        _isGrading = false;
        _correctCount = correct;
        _scorePct = pct;
        _calibratedLevel = level;
        _levelTitleAr = titleAr;
        _levelSummary = summary;
        _currentStep = 4;
      });
    });
  }

  void _finishAndSave() {
    final updated = Map<String, dynamic>.from(widget.child);
    updated['name'] = _nameCtrl.text.trim();
    updated['school_name'] = _schoolCtrl.text.trim();
    updated['avatar_id'] = _avatarId;
    updated['gender'] = _gender;
    updated['age'] = _age;
    updated['default_grade'] = _grade;
    updated['curriculum_stream'] = _stream;
    updated['selected_term'] = _selectedTerm;
    updated['access_pin'] = _pinCtrl.text.trim();
    updated['diagnostic_completed'] = true;
    updated['diagnostic_level'] = _calibratedLevel;
    updated['diagnostic_score'] = _scorePct;

    widget.onCompleted(updated);
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
      child: Container(
        width: double.infinity,
        constraints: const BoxConstraints(maxWidth: 500, maxHeight: 680),
        decoration: const BoxDecoration(
          color: Colors.white,
          border: Border.fromBorderSide(
              BorderSide(color: Color(0xFF0F172A), width: 2)),
        ),
        child: Column(
          children: [
            // Top Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: const BoxDecoration(
                color: Color(0xFF064E3B),
                border: Border(
                    bottom:
                        BorderSide(color: Color(0xFF0F172A), width: 1.5)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: const [
                      Icon(Icons.explore, color: Color(0xFFFBBF24), size: 20),
                      SizedBox(width: 8),
                      Text(
                        'JISR ONBOARDING (التهيئة)',
                        style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w900,
                            fontSize: 13),
                      ),
                    ],
                  ),
                  IconButton(
                    icon:
                        const Icon(Icons.close, color: Colors.white, size: 20),
                    onPressed: () => Navigator.of(context).pop(),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ],
              ),
            ),

            // Step Progress Ribbon
            Container(
              decoration: const BoxDecoration(
                color: Color(0xFFF1F5F9),
                border: Border(bottom: BorderSide(color: Color(0xFFCBD5E1))),
              ),
              child: Row(
                children: [
                  _stepItem(1, 'Profile'),
                  _stepItem(2, 'Stream'),
                  _stepItem(3, 'Quiz'),
                  _stepItem(4, 'Roadmap'),
                ],
              ),
            ),

            // Step Body
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: _buildCurrentStep(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _stepItem(int stepNumber, String label) {
    final bool isActive = _currentStep == stepNumber;
    final bool isDone = _currentStep > stepNumber;
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8),
        decoration: BoxDecoration(
          color: isActive ? Colors.white : Colors.transparent,
          border: Border(
            bottom: BorderSide(
              color: isActive
                  ? const Color(0xFF064E3B)
                  : isDone
                      ? const Color(0xFF059669)
                      : Colors.transparent,
              width: 3,
            ),
          ),
        ),
        child: Column(
          children: [
            Text(
              'Step $stepNumber',
              style: TextStyle(
                fontSize: 9,
                fontWeight: FontWeight.bold,
                color: isActive
                    ? const Color(0xFF064E3B)
                    : const Color(0xFF64748B),
              ),
            ),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w900,
                color: isActive
                    ? const Color(0xFF064E3B)
                    : const Color(0xFF334155),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentStep() {
    switch (_currentStep) {
      case 1:
        return _buildStep1Profile();
      case 2:
        return _buildStep2Stream();
      case 3:
        return _buildStep3Diagnostic();
      case 4:
        return _buildStep4Roadmap();
      default:
        return _buildStep1Profile();
    }
  }

  // STEP 1
  Widget _buildStep1Profile() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '1. Student Demographics & Heritage Avatar',
          style: TextStyle(
              fontWeight: FontWeight.w900,
              fontSize: 13,
              color: Color(0xFF064E3B)),
        ),
        const SizedBox(height: 12),

        // Full Name
        const Text('Student Full Name (اسم الطالب):',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        TextField(
          controller: _nameCtrl,
          decoration: const InputDecoration(hintText: 'e.g. Zayed Al-Nuaimi'),
        ),
        const SizedBox(height: 12),

        // Avatar Picker
        const Text('Select Heritage Avatar (الرمز التراثي):',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: _avatars.map((av) {
            final isSel = _avatarId == av['id'];
            return InkWell(
              onTap: () => setState(() => _avatarId = av['id']!),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  color: isSel ? const Color(0xFFECFDF5) : Colors.white,
                  border: Border.all(
                    color: isSel
                        ? const Color(0xFF064E3B)
                        : const Color(0xFFCBD5E1),
                    width: isSel ? 2 : 1,
                  ),
                ),
                child: Text(av['name']!, style: const TextStyle(fontSize: 16)),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 12),

        // Age & Grade
        Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Age (العمر):',
                      style:
                          TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  DropdownButtonFormField<int>(
                    initialValue: _age,
                    decoration: const InputDecoration(),
                    items: List.generate(14, (i) => i + 5)
                        .map((a) =>
                            DropdownMenuItem(value: a, child: Text('$a yrs')))
                        .toList(),
                    onChanged: (v) => setState(() => _age = v ?? 10),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Grade (الصف):',
                      style:
                          TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  DropdownButtonFormField<int>(
                    initialValue: _grade,
                    decoration: const InputDecoration(),
                    items: List.generate(12, (i) => i + 1)
                        .map((g) =>
                            DropdownMenuItem(value: g, child: Text('Class $g')))
                        .toList(),
                    onChanged: (v) => setState(() => _grade = v ?? 5),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // School
        const Text('UAE School Name (المدرسة):',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        TextField(
          controller: _schoolCtrl,
          decoration: const InputDecoration(
              hintText: 'e.g. Sunrise International School, Abu Dhabi'),
        ),
        const SizedBox(height: 20),

        Align(
          alignment: Alignment.centerRight,
          child: ElevatedButton.icon(
            onPressed: () {
              if (_nameCtrl.text.trim().isEmpty) return;
              setState(() => _currentStep = 2);
            },
            icon: const Icon(Icons.arrow_forward, size: 14),
            label: const Text('NEXT: STREAM & TERM'),
          ),
        ),
      ],
    );
  }

  // STEP 2
  Widget _buildStep2Stream() {
    final streams = [
      'MoE / CBSE Arabic (Non-Arabs)',
      'General MoE Stream (المسار العام)',
      'Advanced MoE Stream (المسار المتقدم)',
      'Elite MoE Stream (مسار النخبة)',
      'International Stream (IB / British / American B)',
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '2. Curriculum Stream & Term Selection',
          style: TextStyle(
              fontWeight: FontWeight.w900,
              fontSize: 13,
              color: Color(0xFF064E3B)),
        ),
        const SizedBox(height: 12),

        // Streams List
        const Text('Select Curriculum Alignment:',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        ...streams.map((st) {
          final isSel = _stream == st;
          return Container(
            margin: const EdgeInsets.only(bottom: 6),
            decoration: BoxDecoration(
              color: isSel ? const Color(0xFFECFDF5) : Colors.white,
              border: Border.all(
                  color: isSel
                      ? const Color(0xFF064E3B)
                      : const Color(0xFFCBD5E1),
                  width: isSel ? 2 : 1),
            ),
            child: RadioListTile<String>(
              value: st,
              groupValue: _stream,
              title: Text(st,
                  style: const TextStyle(
                      fontSize: 11, fontWeight: FontWeight.bold)),
              onChanged: (v) => setState(() => _stream = v!),
              contentPadding: const EdgeInsets.symmetric(horizontal: 8),
              dense: true,
            ),
          );
        }),
        const SizedBox(height: 12),

        // Term Picker
        const Text('Select Academic Term:',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        Row(
          children: [1, 2, 3].map((t) {
            final isSel = _selectedTerm == t;
            return Expanded(
              child: Padding(
                padding: const EdgeInsets.only(right: 6),
                child: InkWell(
                  onTap: () => setState(() => _selectedTerm = t),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: isSel ? const Color(0xFF064E3B) : Colors.white,
                      border: Border.all(color: const Color(0xFF064E3B)),
                    ),
                    child: Column(
                      children: [
                        Text(
                          'Term $t',
                          style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                              color: isSel
                                  ? Colors.white
                                  : const Color(0xFF064E3B)),
                        ),
                        if (t == 1)
                          Text('Free Demo',
                              style: TextStyle(
                                  fontSize: 9,
                                  color: isSel
                                      ? const Color(0xFFFBBF24)
                                      : const Color(0xFFB45309))),
                      ],
                    ),
                  ),
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 14),

        // PIN
        const Text('4-Digit Student PIN (رمز الدخول السريع):',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        TextField(
          controller: _pinCtrl,
          maxLength: 4,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(hintText: '1234'),
        ),
        const SizedBox(height: 16),

        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            OutlinedButton(
              onPressed: () => setState(() => _currentStep = 1),
              child: const Text('BACK'),
            ),
            ElevatedButton.icon(
              onPressed: () => setState(() => _currentStep = 3),
              icon: const Icon(Icons.quiz, size: 14),
              label: const Text('START DIAGNOSTIC'),
            ),
          ],
        ),
      ],
    );
  }

  // STEP 3
  Widget _buildStep3Diagnostic() {
    final q = _diagnosticQuestions[_activeQIndex];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              '3. Diagnostic Baseline Assessment',
              style: TextStyle(
                  fontWeight: FontWeight.w900,
                  fontSize: 13,
                  color: Color(0xFF064E3B)),
            ),
            Text(
              'Question ${_activeQIndex + 1} / ${_diagnosticQuestions.length}',
              style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 11,
                  color: Color(0xFFB45309)),
            ),
          ],
        ),
        const SizedBox(height: 10),

        // Competency tag
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: const BoxDecoration(
            color: Color(0xFFF1F5F9),
            border: Border.fromBorderSide(BorderSide(color: Color(0xFFCBD5E1))),
          ),
          child: Text(
            q['competency']!,
            style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: Color(0xFF334155)),
          ),
        ),
        const SizedBox(height: 10),

        if (q['passage'] != null) ...[
          Container(
            padding: const EdgeInsets.all(10),
            decoration: const BoxDecoration(
              color: Color(0xFFFFFBEB),
              border: Border(
                  left: BorderSide(color: Color(0xFFF59E0B), width: 3)),
            ),
            child: Text(
              q['passage']!,
              textDirection: TextDirection.rtl,
              style: const TextStyle(
                  fontSize: 14, height: 1.5, fontWeight: FontWeight.w600),
            ),
          ),
          const SizedBox(height: 10),
        ],

        Text(
          q['question']!,
          textDirection: TextDirection.rtl,
          style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0F172A)),
        ),
        const SizedBox(height: 12),

        // Options
        ...List.generate((q['options'] as List).length, (i) {
          final optText = q['options'][i] as String;
          final isSelected = _answers[q['id']] == i;
          return Container(
            margin: const EdgeInsets.only(bottom: 8),
            decoration: BoxDecoration(
              color: isSelected ? const Color(0xFFECFDF5) : Colors.white,
              border: Border.all(
                  color: isSelected
                      ? const Color(0xFF064E3B)
                      : const Color(0xFFCBD5E1),
                  width: isSelected ? 2 : 1),
            ),
            child: ListTile(
              dense: true,
              leading: Text(String.fromCharCode(65 + i),
                  style: const TextStyle(fontWeight: FontWeight.bold)),
              title: Text(optText,
                  textDirection: TextDirection.rtl,
                  style: const TextStyle(
                      fontSize: 13, fontWeight: FontWeight.bold)),
              trailing: isSelected
                  ? const Icon(Icons.check_circle,
                      color: Color(0xFF064E3B), size: 18)
                  : null,
              onTap: () {
                setState(() {
                  _answers[q['id']] = i;
                });
              },
            ),
          );
        }),

        const SizedBox(height: 14),

        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            OutlinedButton(
              onPressed: _activeQIndex > 0
                  ? () => setState(() => _activeQIndex--)
                  : null,
              child: const Text('PREVIOUS'),
            ),
            if (_activeQIndex < _diagnosticQuestions.length - 1)
              ElevatedButton(
                onPressed: () => setState(() => _activeQIndex++),
                child: const Text('NEXT QUESTION'),
              )
            else
              ElevatedButton.icon(
                onPressed: _isGrading ? null : _submitDiagnostic,
                icon: _isGrading
                    ? const SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.auto_awesome, size: 14),
                label:
                    Text(_isGrading ? 'CALIBRATING...' : 'SUBMIT & CALIBRATE'),
                style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFB45309)),
              ),
          ],
        ),
      ],
    );
  }

  // STEP 4
  Widget _buildStep4Roadmap() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Level Badge Card
        Container(
          padding: const EdgeInsets.all(14),
          decoration: const BoxDecoration(
            color: Color(0xFF064E3B),
            border: Border.fromBorderSide(
                BorderSide(color: Color(0xFF0F172A), width: 2)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'AI CALIBRATED LEVEL · المستوى',
                        style: TextStyle(
                            color: Color(0xFFFBBF24),
                            fontSize: 10,
                            fontWeight: FontWeight.bold),
                      ),
                      Text(
                        _levelTitleAr,
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.w900),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 6),
                    decoration: const BoxDecoration(
                      color: Color(0xFFB45309),
                      border: Border.fromBorderSide(
                          BorderSide(color: Color(0xFFFBBF24))),
                    ),
                    child: Text(
                      '${_scorePct.toInt()}% Score ($_correctCount/${_diagnosticQuestions.length})',
                      style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                _levelSummary,
                style: const TextStyle(
                    color: Colors.white70, fontSize: 11, height: 1.4),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // 4-Week Roadmap Milestones
        const Text(
          'Personalized 4-Week Milestone Roadmap (الخطة الأسبوعية):',
          style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0F172A)),
        ),
        const SizedBox(height: 8),
        _milestoneTile(1, 'Week 1: Core Confidence & Key Vocabulary',
            'نصوص تمهيدية وبنك الكلمات الصوتي'),
        _milestoneTile(2, 'Week 2: Sentence Dynamics & Nominal Agreement',
            'الجملة الاسمية ومطابقة الفعل والفاعل'),
        _milestoneTile(3, 'Week 3: Deep Contextual Comprehension',
            'تحليل نصوص التراث واستخراج الأضداد'),
        _milestoneTile(4, 'Week 4: Applied Expression & Milestone Badge',
            'التعبير الإبداعي واختبار التقييم الشهري'),

        const SizedBox(height: 18),

        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _finishAndSave,
            icon: const Icon(Icons.check_circle, size: 16),
            label: const Text('START LEARNING WITH JISR'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
        ),
      ],
    );
  }

  Widget _milestoneTile(int week, String titleEn, String titleAr) {
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.all(8),
      decoration: const BoxDecoration(
        color: Color(0xFFF8FAFC),
        border: Border.fromBorderSide(BorderSide(color: Color(0xFFE2E8F0))),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: const BoxDecoration(color: Color(0xFF064E3B)),
            child: Text('W$week',
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.bold)),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(titleEn,
                    style: const TextStyle(
                        fontSize: 11, fontWeight: FontWeight.bold)),
                Text(titleAr,
                    textDirection: TextDirection.rtl,
                    style: const TextStyle(
                        fontSize: 10,
                        color: Color(0xFF064E3B),
                        fontWeight: FontWeight.w600)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

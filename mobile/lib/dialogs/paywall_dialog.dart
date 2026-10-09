import 'package:flutter/material.dart';

import '../api_service.dart';

class PaywallDialog extends StatefulWidget {
  final int grade;
  final int term;
  final Map<String, dynamic>? activeChild;
  final VoidCallback onUnlocked;
  final Function(List<int> unlockedTerms)? onUnlockedTerms;
  final String? token;
  final bool isArabic;

  const PaywallDialog({
    super.key,
    required this.grade,
    required this.term,
    required this.activeChild,
    required this.onUnlocked,
    this.onUnlockedTerms,
    this.token,
    this.isArabic = false,
  });

  @override
  State<PaywallDialog> createState() => _PaywallDialogState();
}

class _PaywallDialogState extends State<PaywallDialog> {
  final ApiService _api = ApiService();
  late Set<int> _selectedTerms;
  bool _includeAskFahimAi = true; // Ask Fahim AI default selection: ON
  String _selectedMode = 'card'; // 'card' or 'voucher'
  final TextEditingController _voucherCtrl = TextEditingController();
  bool _isProcessing = false;
  String? _errorMessage;
  String? _successReceipt;
  List<int> _unlockedTermsResult = [];

  @override
  void initState() {
    super.initState();
    // Default selection: Include current term
    _selectedTerms = {widget.term.clamp(1, 3)};
  }

  @override
  void dispose() {
    _voucherCtrl.dispose();
    super.dispose();
  }

  double get _totalUsd {
    final count = _selectedTerms.length;
    if (count >= 3) {
      return 50.0; // 3 Terms together (Full Academic Year): USD 50 (15% discount)
    } else if (count == 2) {
      return 40.0; // 2 * $20
    } else if (count == 1) {
      return 20.0; // 1 * $20
    }
    return 0.0;
  }

  int get _totalAed => (_totalUsd * 3.6725).round();

  void _toggleTerm(int termNumber) {
    setState(() {
      if (_selectedTerms.contains(termNumber)) {
        if (_selectedTerms.length > 1) {
          _selectedTerms.remove(termNumber);
        } else {
          // Keep at least one term selected
          _errorMessage = widget.isArabic
              ? 'يرجى تحديد فصل دراسي واحد على الأقل.'
              : 'Please keep at least one Term selected.';
        }
      } else {
        _selectedTerms.add(termNumber);
        _errorMessage = null;
      }
    });
  }

  void _selectAllTerms() {
    setState(() {
      _selectedTerms = {1, 2, 3};
      _errorMessage = null;
    });
  }

  Future<void> _processCheckout() async {
    final childId = widget.activeChild?['id'];
    if (childId == null) {
      setState(() => _errorMessage = widget.isArabic
          ? 'يرجى اختيار طالب نشط أولاً.'
          : 'Please select an active learner first.');
      return;
    }

    if (_selectedMode == 'card' && _selectedTerms.isEmpty) {
      setState(() => _errorMessage = widget.isArabic
          ? 'يرجى اختيار فصل دراسي واحد على الأقل.'
          : 'Please select at least one Term to unlock.');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      if (_selectedMode == 'voucher') {
        final code = _voucherCtrl.text.trim();
        if (code.isEmpty) {
          setState(() {
            _errorMessage = widget.isArabic
                ? 'يرجى إدخال رمز قسيمة المدرسة.'
                : 'Please enter a school voucher code.';
            _isProcessing = false;
          });
          return;
        }

        final data = await _api.post('/api/payments/redeem-voucher',
            token: widget.token,
            body: {
              'child_id': childId,
              'grade': widget.grade,
              'code': code,
            });
        if (data is Map) {
          final receipt = data['receipt_number'] ?? 'VCH-ACTIVE';
          final unlocked = [1, 2, 3];
          setState(() {
            _successReceipt = receipt;
            _unlockedTermsResult = unlocked;
          });
          widget.onUnlockedTerms?.call(unlocked);
          widget.onUnlocked();
        }
      } else {
        // Multi-term or annual card checkout
        final termsList = _selectedTerms.toList()..sort();
        final isAnnual = termsList.length >= 3;
        final data = await _api.post('/api/payments/checkout',
            token: widget.token,
            body: {
              'child_id': childId,
              'grade': widget.grade,
              'term': termsList.first,
              'terms': termsList,
              'package_type': isAnnual ? 'annual' : 'term',
              'include_ai': _includeAskFahimAi,
              'payment_method': 'card',
              'promo_code': 'JISR100',
            });
        if (data is Map) {
          final receipt = data['receipt_number'] ?? 'JISR-PASS';
          final rawUnlocked = data['unlocked_terms'] as List? ?? termsList;
          final unlocked = rawUnlocked.map((e) => int.tryParse(e.toString()) ?? 1).toList();
          setState(() {
            _successReceipt = receipt;
            _unlockedTermsResult = unlocked;
          });
          widget.onUnlockedTerms?.call(unlocked);
          widget.onUnlocked();
        }
      }
    } catch (e) {
      setState(() => _errorMessage = '${widget.isArabic ? "تعذر إتمام الدفع: " : "Checkout failed: "}$e');
    } finally {
      if (mounted) {
        setState(() => _isProcessing = false);
      }
    }
  }

  Future<void> _restorePurchases() async {
    final childId = widget.activeChild?['id'];
    if (childId == null) {
      setState(() => _errorMessage = widget.isArabic
          ? 'يرجى اختيار طالب نشط أولاً.'
          : 'Please select an active learner first.');
      return;
    }
    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });
    try {
      final terms = await _api.terms(widget.grade, childId: childId, token: widget.token);
      final unlockedList = <int>[];
      if (terms is List) {
        for (final t in terms) {
          if (t is Map && t['is_unlocked'] == true) {
            final tNum = int.tryParse(t['term'].toString());
            if (tNum != null) unlockedList.add(tNum);
          }
        }
      }
      if (unlockedList.isNotEmpty) {
        setState(() {
          _successReceipt = 'RESTORED-TERMS-${unlockedList.join(",")}';
          _unlockedTermsResult = unlockedList;
        });
        widget.onUnlockedTerms?.call(unlockedList);
        widget.onUnlocked();
      } else {
        setState(() {
          _errorMessage = widget.isArabic
              ? 'لم يتم العثور على مشتريات سابقة لهذا المتعلم.'
              : 'No previous purchases found for this learner.';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = widget.isArabic
            ? 'فشلت استعادة المشتريات: $e'
            : 'Failed to restore purchases: $e';
      });
    } finally {
      if (mounted) {
        setState(() => _isProcessing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isAr = widget.isArabic;
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        width: 520,
        constraints: const BoxConstraints(maxHeight: 680),
        padding: const EdgeInsets.all(22),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEF3C7),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(Icons.stars, color: Color(0xFFD97706), size: 20),
                      ),
                      const SizedBox(width: 8),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isAr ? 'ترقية المنهاج والاشتراكات' : 'JISR · CURRICULUM SUBSCRIPTIONS',
                            style: const TextStyle(
                              fontWeight: FontWeight.w900,
                              fontSize: 13,
                              color: Color(0xFFB45309),
                              letterSpacing: 0.5,
                            ),
                          ),
                          Text(
                            isAr
                                ? 'الصف ${widget.grade} · ${widget.activeChild?['name'] ?? 'الطالب'}'
                                : 'Class ${widget.grade} · ${widget.activeChild?['name'] ?? 'Learner'}',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Freemium Notice
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFFECFDF5),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFF10B981)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.check_circle_outline, size: 16, color: Color(0xFF065F46)),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        isAr
                            ? 'الفصل الأول: الدرس الأول (ألعاب الكرة) مجاني بالكامل كعينة تجريبية. اشترك لفتح باقي دروس الفصول ومساعد المعلم الذكي (فاهم).'
                            : 'Chapter 1 (Ball Games / ألعاب الكرة) of Term 1 is 100% Free Demo. Subscribe to unlock subsequent chapters across Terms 1, 2, 3 and Ask Fahim AI.',
                        style: const TextStyle(fontSize: 11, color: Color(0xFF065F46), height: 1.3),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),

              if (_successReceipt != null) ...[
                // Success View
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFECFDF5),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF059669)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.verified, color: Color(0xFF065F46), size: 20),
                          const SizedBox(width: 8),
                          Text(
                            isAr ? 'تم تفعيل الاشتراك بنجاح!' : 'SUBSCRIPTION ACTIVATED!',
                            style: const TextStyle(
                              fontWeight: FontWeight.w900,
                              fontSize: 13,
                              color: Color(0xFF065F46),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '${isAr ? "رقم الإيصال: " : "Receipt: "}$_successReceipt',
                        style: const TextStyle(
                          fontSize: 11.5,
                          fontFamily: 'monospace',
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${isAr ? "الفصول المفعلة: " : "Unlocked Terms: "}Term ${_unlockedTermsResult.join(", Term ")}',
                        style: const TextStyle(
                          fontSize: 11.5,
                          color: Color(0xFF064E3B),
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${isAr ? "مساعد فاهم الذكي: " : "Ask Fahim AI: "} ${isAr ? "مفعل ومتاح للاستخدام" : "Active & Unlocked"}',
                        style: const TextStyle(
                          fontSize: 11,
                          color: Color(0xFF047857),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'UAE FTA TRN: 100458923100003 (5% VAT Inclusive)',
                        style: TextStyle(fontSize: 10, color: Colors.black54),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF064E3B),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: Text(
                      isAr ? 'ابدأ التعلم الآن' : 'Start Learning Now',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                  ),
                ),
              ] else ...[
                // Mode Toggle: Credit Card / Apple Pay vs School Voucher
                Row(
                  children: [
                    Expanded(
                      child: InkWell(
                        onTap: () => setState(() => _selectedMode = 'card'),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          decoration: BoxDecoration(
                            color: _selectedMode == 'card' ? const Color(0xFFF3F0FF) : Colors.white,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: _selectedMode == 'card' ? const Color(0xFF6C5CE7) : const Color(0xFFCBD5E1),
                              width: _selectedMode == 'card' ? 2 : 1,
                            ),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.credit_card,
                                  size: 16,
                                  color: _selectedMode == 'card' ? const Color(0xFF6C5CE7) : Colors.black54),
                              const SizedBox(width: 6),
                              Text(
                                isAr ? 'دفع إلكتروني (بطاقة/أبل باي)' : 'Online Payment (Card/Apple)',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                  color: _selectedMode == 'card' ? const Color(0xFF6C5CE7) : Colors.black87,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: InkWell(
                        onTap: () => setState(() => _selectedMode = 'voucher'),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          decoration: BoxDecoration(
                            color: _selectedMode == 'voucher' ? const Color(0xFFF3F0FF) : Colors.white,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: _selectedMode == 'voucher' ? const Color(0xFF6C5CE7) : const Color(0xFFCBD5E1),
                              width: _selectedMode == 'voucher' ? 2 : 1,
                            ),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.vpn_key,
                                  size: 16,
                                  color: _selectedMode == 'voucher' ? const Color(0xFF6C5CE7) : Colors.black54),
                              const SizedBox(width: 6),
                              Text(
                                isAr ? 'رمز قسيمة المدرسة' : 'School Voucher Pass',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                  color: _selectedMode == 'voucher' ? const Color(0xFF6C5CE7) : Colors.black87,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                if (_selectedMode == 'voucher') ...[
                  TextField(
                    controller: _voucherCtrl,
                    textCapitalization: TextCapitalization.characters,
                    style: const TextStyle(
                      fontSize: 12,
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.bold,
                    ),
                    decoration: InputDecoration(
                      labelText: isAr ? 'رمز قسيمة المدرسة' : 'School Voucher Code',
                      labelStyle: const TextStyle(fontSize: 11),
                      hintText: 'e.g. SUNRISE2026 or ADEK-ARABIC-100',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      isDense: true,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      TextButton(
                        onPressed: () => _voucherCtrl.text = 'SUNRISE2026',
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        ),
                        child: const Text('Use SUNRISE2026', style: TextStyle(fontSize: 11)),
                      ),
                      TextButton(
                        onPressed: () => _voucherCtrl.text = 'ADEK-ARABIC-100',
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        ),
                        child: const Text('Use ADEK-ARABIC-100', style: TextStyle(fontSize: 11)),
                      ),
                    ],
                  ),
                ] else ...[
                  // Term Selection Provision: Term 1, Term 2, Term 3
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        isAr ? 'اختر الفصول الدراسية المطلوبة:' : 'Select Desired Terms:',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1E293B),
                        ),
                      ),
                      TextButton.icon(
                        onPressed: _selectAllTerms,
                        icon: const Icon(Icons.auto_awesome, size: 14, color: Color(0xFF6C5CE7)),
                        label: Text(
                          isAr ? 'تحديد العام بأكمله (خصم 15%)' : 'Full Academic Year (15% OFF)',
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF6C5CE7)),
                        ),
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          visualDensity: VisualDensity.compact,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),

                  // Interactive Term Tiles
                  _buildTermTile(
                    termNumber: 1,
                    titleAr: 'الفصل الدراسي الأول',
                    titleEn: 'Term 1 (Autumn)',
                    descriptionAr: 'الوحدات 1-3 · اختبارات الفصل · ملازم شاملة',
                    descriptionEn: 'Units 1-3 · Exam Models · Smart Malazim',
                  ),
                  const SizedBox(height: 6),
                  _buildTermTile(
                    termNumber: 2,
                    titleAr: 'الفصل الدراسي الثاني',
                    titleEn: 'Term 2 (Winter)',
                    descriptionAr: 'الوحدات 4-7 · كبسولات القواعد · بنك الأسئلة',
                    descriptionEn: 'Units 4-7 · Grammar Capsules · Question Bank',
                  ),
                  const SizedBox(height: 6),
                  _buildTermTile(
                    termNumber: 3,
                    titleAr: 'الفصل الدراسي الثالث',
                    titleEn: 'Term 3 (Spring)',
                    descriptionAr: 'الوحدات 8-10 · مراجعة نهاية العام والتقييم النهائي',
                    descriptionEn: 'Units 8-10 · Year-end Comprehensive Mastery',
                  ),
                  const SizedBox(height: 10),

                  // Ask Fahim AI Tutor Companion (Default Selection: ON)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFBF8FF),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: _includeAskFahimAi ? const Color(0xFF8B5CF6) : const Color(0xFFCBD5E1),
                        width: _includeAskFahimAi ? 1.5 : 1,
                      ),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Checkbox(
                          value: _includeAskFahimAi,
                          activeColor: const Color(0xFF6C5CE7),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                          onChanged: (val) {
                            setState(() => _includeAskFahimAi = val ?? true);
                          },
                        ),
                        const SizedBox(width: 4),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Text(
                                    isAr ? '🤖 مساعد المعلم الذكي (اسأل فاهم)' : '🤖 Ask Fahim AI Tutor Companion',
                                    style: const TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF4C1D95),
                                    ),
                                  ),
                                  const SizedBox(width: 6),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF10B981),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Text(
                                      isAr ? 'مشمول مجاناً' : 'INCLUDED',
                                      style: const TextStyle(
                                        fontSize: 9,
                                        fontWeight: FontWeight.w900,
                                        color: Colors.white,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 2),
                              Text(
                                isAr
                                    ? 'شرح فوري للمفردات، حل أوراق الامتحانات بالكاميرا، وتدريب النطق بالإنجليزية المعربة'
                                    : 'Instant vocabulary explanation, exam paper camera scanner, ArabEnglish pronunciation coach',
                                style: const TextStyle(fontSize: 10, color: Color(0xFF6D28D9)),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Pricing Summary Box
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF8FAFC),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFE2E8F0)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _selectedTerms.length >= 3
                                      ? (isAr ? 'اشتراك العام الأكاديمي الكامل (3 فصول)' : 'Full Academic Year Pass (3 Terms)')
                                      : (isAr
                                          ? 'اشتراك ${_selectedTerms.length} فصل دراسي (Term ${_selectedTerms.join(", ")})'
                                          : 'Subscription for ${_selectedTerms.length} Term(s) (Term ${_selectedTerms.join(", ")})'),
                                  style: const TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF1E293B),
                                  ),
                                ),
                                if (_selectedTerms.length >= 3)
                                  Padding(
                                    padding: const EdgeInsets.only(top: 2),
                                    child: Text(
                                      isAr
                                        ? 'السعر الأصلي: \$60 (خصم 15% متضمن)'
                                        : 'Regular \$60 (15% Special Discount Applied)',
                                      style: const TextStyle(
                                        fontSize: 10.5,
                                        color: Color(0xFF059669),
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFFECFDF5),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: const Color(0xFFA7F3D0)),
                              ),
                              child: Text(
                                'USD ${_totalUsd.toInt()} (AED $_totalAed)',
                                style: const TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w900,
                                  color: Color(0xFF064E3B),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Includes 5% UAE VAT · TRN: 100458923100003',
                          style: TextStyle(fontSize: 10, color: Colors.black54),
                        ),
                      ],
                    ),
                  ),
                ],

                if (_errorMessage != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    _errorMessage!,
                    style: const TextStyle(
                      fontSize: 11,
                      color: Colors.red,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],

                const SizedBox(height: 14),

                // Pay / Redeem Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isProcessing ? null : _processCheckout,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF064E3B),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: _isProcessing
                        ? const SizedBox(
                            height: 16,
                            width: 16,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                          )
                        : Text(
                            _selectedMode == 'voucher'
                                ? (isAr ? 'تفعيل القسيمة وفتح المنهاج' : 'Redeem Voucher & Unlock Curriculum')
                                : (isAr
                                    ? 'دفع USD ${_totalUsd.toInt()} (AED $_totalAed) وتفعيل الفصول المحددة'
                                    : 'Pay USD ${_totalUsd.toInt()} (AED $_totalAed) & Unlock Terms ${_selectedTerms.join(", ")}'),
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12.5),
                          ),
                  ),
                ),
                const SizedBox(height: 8),

                // Restore Purchases
                Center(
                  child: TextButton.icon(
                    onPressed: _isProcessing ? null : _restorePurchases,
                    icon: const Icon(Icons.restore, size: 16, color: Color(0xFF064E3B)),
                    label: Text(
                      isAr ? 'استعادة المشتريات السابقة (Restore)' : 'Restore Previous Purchases',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF064E3B),
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTermTile({
    required int termNumber,
    required String titleAr,
    required String titleEn,
    required String descriptionAr,
    required String descriptionEn,
  }) {
    final isSelected = _selectedTerms.contains(termNumber);
    final isAr = widget.isArabic;
    return InkWell(
      onTap: () => _toggleTerm(termNumber),
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFF0FDF4) : Colors.white,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: isSelected ? const Color(0xFF059669) : const Color(0xFFE2E8F0),
            width: isSelected ? 1.5 : 1,
          ),
        ),
        child: Row(
          children: [
            Checkbox(
              value: isSelected,
              activeColor: const Color(0xFF059669),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
              onChanged: (_) => _toggleTerm(termNumber),
            ),
            const SizedBox(width: 4),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        isAr ? titleAr : titleEn,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: isSelected ? const Color(0xFF064E3B) : const Color(0xFF1E293B),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: isSelected ? const Color(0xFFDCFCE7) : const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          'USD 20 (AED 73.5)',
                          style: TextStyle(
                            fontSize: 10.5,
                            fontWeight: FontWeight.w700,
                            color: isSelected ? const Color(0xFF065F46) : const Color(0xFF475569),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    isAr ? descriptionAr : descriptionEn,
                    style: const TextStyle(fontSize: 10, color: Color(0xFF64748B)),
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

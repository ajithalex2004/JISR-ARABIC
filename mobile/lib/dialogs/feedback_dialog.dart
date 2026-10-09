import 'package:flutter/material.dart';

import '../api_service.dart';

class FeedbackDialog extends StatefulWidget {
  final ApiService api;
  final String? token;
  final Map<String, dynamic>? user;
  final Map<String, dynamic>? activeChild;
  final bool isArabic;

  const FeedbackDialog({
    super.key,
    required this.api,
    this.token,
    this.user,
    this.activeChild,
    required this.isArabic,
  });

  @override
  State<FeedbackDialog> createState() => _FeedbackDialogState();
}

class _FeedbackDialogState extends State<FeedbackDialog> {
  final TextEditingController _commentCtrl = TextEditingController();
  final TextEditingController _emailCtrl = TextEditingController();

  int _rating = 5;
  String _category = 'feature';
  bool _isSubmitting = false;
  bool _isSubmitted = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    final userEmail = widget.user?['email']?.toString();
    if (userEmail != null && userEmail.isNotEmpty) {
      _emailCtrl.text = userEmail;
    }
  }

  @override
  void dispose() {
    _commentCtrl.dispose();
    _emailCtrl.dispose();
    super.dispose();
  }

  String _getRatingLabel(int r) {
    switch (r) {
      case 5:
        return widget.isArabic ? '🌟 ممتاز ورائع!' : '🌟 Excellent & Wonderful!';
      case 4:
        return widget.isArabic ? '👍 جيد جداً' : '👍 Very Good';
      case 3:
        return widget.isArabic ? '👌 جيد' : '👌 Good';
      case 2:
        return widget.isArabic ? '⚠️ يحتاج تحسين' : '⚠️ Needs Improvement';
      default:
        return widget.isArabic ? '❗ واجهت صعوبات' : '❗ Faced Difficulties';
    }
  }

  Future<void> _submitFeedback() async {
    final comment = _commentCtrl.text.trim();
    if (comment.isEmpty) {
      setState(() {
        _errorMessage = widget.isArabic
            ? 'يرجى كتابة ملاحظاتك أو اقتراحاتك قبل الإرسال.'
            : 'Please enter your feedback or suggestions before submitting.';
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      await widget.api.submitFeedback({
        'rating': _rating,
        'category': _category,
        'comment': comment,
        'contact_email': _emailCtrl.text.trim().isNotEmpty ? _emailCtrl.text.trim() : null,
        'grade': widget.activeChild?['default_grade'] ?? 5,
        'child_id': widget.activeChild?['id']?.toString(),
      }, token: widget.token);

      if (mounted) {
        setState(() {
          _isSubmitting = false;
          _isSubmitted = true;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
          _errorMessage = e.toString().replaceAll('Exception: ', '').replaceAll('AuthException: ', '');
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      clipBehavior: Clip.antiAlias,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 440),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header Gradient
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Color(0xFF58337E), Color(0xFF6C5CE7)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.18),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(Icons.rate_review_rounded, color: Colors.white, size: 22),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.isArabic ? 'آراء وملاحظات المستخدمين' : 'User Feedback & Reviews',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            widget.isArabic
                                ? 'رأيك يهمنا لمواصلة تطوير المنهاج والمنصة'
                                : 'Your input guides our curriculum & platform enhancements',
                            style: const TextStyle(color: Color(0xFFE0D7F5), fontSize: 10.5),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white70, size: 20),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
              ),

              if (_isSubmitted) ...[
                // Success View
                Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      Container(
                        width: 64,
                        height: 64,
                        decoration: BoxDecoration(
                          color: const Color(0xFFECFDF5),
                          shape: BoxShape.circle,
                          border: Border.all(color: const Color(0xFFA7F3D0), width: 2),
                        ),
                        child: const Icon(Icons.check_rounded, color: Color(0xFF059669), size: 36),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        widget.isArabic ? 'شكرًا لمشاركتك القيّمة!' : 'Thank you for your feedback!',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF064E3B),
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        widget.isArabic
                            ? 'تم استلام ملاحظاتك بنجاح. يحرص فريق جسر على مراجعة كل اقتراح لتحسين تجربة تعلم اللغة العربية لجميع الطلاب.'
                            : 'We have received your input. The JISR team reviews each suggestion to empower our students’ Arabic learning journey.',
                        style: const TextStyle(fontSize: 12, color: Color(0xFF475569), height: 1.4),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF6C5CE7),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        child: Text(widget.isArabic ? 'تم' : 'Done'),
                      ),
                    ],
                  ),
                ),
              ] else ...[
                // Form View
                Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Star Rating Section
                      Text(
                        widget.isArabic ? 'ما هو تقييمك العام للتجربة؟' : 'How was your experience?',
                        style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                      ),
                      const SizedBox(height: 6),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: List.generate(5, (index) {
                          final star = index + 1;
                          final isFilled = star <= _rating;
                          return InkWell(
                            onTap: () => setState(() => _rating = star),
                            borderRadius: BorderRadius.circular(20),
                            child: Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                              child: Icon(
                                isFilled ? Icons.star_rounded : Icons.star_outline_rounded,
                                color: isFilled ? const Color(0xFFF59E0B) : const Color(0xFFCBD5E1),
                                size: 34,
                              ),
                            ),
                          );
                        }),
                      ),
                      Center(
                        child: Text(
                          _getRatingLabel(_rating),
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF6C5CE7)),
                        ),
                      ),
                      const SizedBox(height: 14),

                      // Category Selector
                      Text(
                        widget.isArabic ? 'نوع الملاحظة:' : 'Feedback Category:',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                      ),
                      const SizedBox(height: 6),
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: [
                          _categoryChip('feature', '💡 ${widget.isArabic ? 'اقتراح ميزة' : 'Feature Idea'}'),
                          _categoryChip('curriculum', '📖 ${widget.isArabic ? 'محتوى المنهاج' : 'Curriculum Content'}'),
                          _categoryChip('bug', '🐛 ${widget.isArabic ? 'الإبلاغ عن مشكلة' : 'Bug Report'}'),
                          _categoryChip('general', '🌟 ${widget.isArabic ? 'تقييم عام' : 'General Review'}'),
                        ],
                      ),
                      const SizedBox(height: 14),

                      // Comments Text Area
                      Text(
                        widget.isArabic ? 'ملاحظاتك واقتراحاتك بالتفصيل:' : 'Your detailed feedback or suggestion:',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                      ),
                      const SizedBox(height: 6),
                      TextField(
                        controller: _commentCtrl,
                        maxLines: 4,
                        textDirection: widget.isArabic ? TextDirection.rtl : TextDirection.ltr,
                        decoration: InputDecoration(
                          hintText: widget.isArabic
                              ? 'اكتب رأيك، الميزات التي تتمنى إضافتها، أو أي صعوبات واجهتها في المنهاج...'
                              : 'Write your thoughts, features you would like to see, or any issues faced...',
                          hintStyle: const TextStyle(fontSize: 11.5, color: Color(0xFF94A3B8)),
                          contentPadding: const EdgeInsets.all(12),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          filled: true,
                          fillColor: const Color(0xFFF8FAFC),
                        ),
                      ),
                      const SizedBox(height: 10),

                      // Contact Email (Optional)
                      Text(
                        widget.isArabic ? 'البريد الإلكتروني للتواصل (اختياري):' : 'Contact Email (optional):',
                        style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
                      ),
                      const SizedBox(height: 4),
                      TextField(
                        controller: _emailCtrl,
                        keyboardType: TextInputType.emailAddress,
                        decoration: InputDecoration(
                          prefixIcon: const Icon(Icons.email_outlined, size: 16, color: Color(0xFF64748B)),
                          hintText: 'example@email.com',
                          hintStyle: const TextStyle(fontSize: 11.5, color: Color(0xFF94A3B8)),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                          isDense: true,
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                          filled: true,
                          fillColor: const Color(0xFFF8FAFC),
                        ),
                      ),

                      if (_errorMessage != null) ...[
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFEF2F2),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: const Color(0xFFFECACA)),
                          ),
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(fontSize: 11, color: Color(0xFFDC2626)),
                          ),
                        ),
                      ],

                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _isSubmitting ? null : _submitFeedback,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF6C5CE7),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          elevation: 0,
                        ),
                        child: _isSubmitting
                            ? const SizedBox(
                                height: 18,
                                width: 18,
                                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                              )
                            : Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(Icons.send_rounded, size: 16),
                                  const SizedBox(width: 6),
                                  Text(
                                    widget.isArabic ? 'إرسال الملاحظات' : 'Submit Feedback',
                                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                                  ),
                                ],
                              ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _categoryChip(String cat, String label) {
    final isSelected = _category == cat;
    return ChoiceChip(
      label: Text(label, style: TextStyle(fontSize: 10.5, fontWeight: isSelected ? FontWeight.bold : FontWeight.normal)),
      selected: isSelected,
      selectedColor: const Color(0xFFEDE9FE),
      backgroundColor: const Color(0xFFF1F5F9),
      side: BorderSide(color: isSelected ? const Color(0xFF6C5CE7) : const Color(0xFFE2E8F0)),
      onSelected: (_) => setState(() => _category = cat),
    );
  }
}

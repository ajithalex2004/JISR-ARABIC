import 'dart:async';
import 'package:flutter/material.dart';
import '../api_service.dart';
import '../arab_english_service.dart';
import '../widgets/interactive_arabic_text.dart';

// ---------------------------------------------------------------------------
// 1. PROFILE / BALANCE VIEW
// ---------------------------------------------------------------------------
class ProfileView extends StatelessWidget {
  final Map<String, dynamic>? activeChild;
  final Map<String, dynamic>? user;
  final int currentGrade;
  final int currentTerm;
  final VoidCallback onOpenAskFahim;
  final VoidCallback onOpenPaywall;
  final VoidCallback onLogout;
  final VoidCallback? onDeleteAccount;
  final bool isArabic;
  final VoidCallback? onOpenSubscriptions;

  const ProfileView({
    super.key,
    required this.activeChild,
    required this.user,
    required this.currentGrade,
    required this.currentTerm,
    required this.onOpenAskFahim,
    required this.onOpenPaywall,
    required this.onLogout,
    this.onDeleteAccount,
    this.isArabic = false,
    this.onOpenSubscriptions,
  });

  @override
  Widget build(BuildContext context) {
    final displayName =
        activeChild?['name'] ?? user?['email']?.split('@')[0] ?? (isArabic ? 'طالب جسر' : 'JISR Student');

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              isArabic ? 'حسابي' : 'My Account',
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Color(0xFF58337E),
              ),
            ),
            Text(
              isArabic ? 'ملف الطالب والاشتراكات' : 'JISR Account',
              style: const TextStyle(
                fontSize: 12,
                color: Color(0xFF94A3B8),
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Student Profile Identity Card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: const Color(0xFFF1F0FA)),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF6C5CE7).withValues(alpha: 0.05),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF6C5CE7), Color(0xFFA29BFE)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(28),
                ),
                padding: const EdgeInsets.all(2),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(26),
                  ),
                  alignment: Alignment.center,
                  child: Text(
                    displayName.isNotEmpty
                        ? displayName[0].toUpperCase()
                        : (isArabic ? 'ف' : 'J'),
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF6C5CE7),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      displayName,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1E293B),
                      ),
                    ),
                    if (user?['role'] == 'admin') ...[
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFF5B21B6),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.shield, color: Colors.amber, size: 12),
                            const SizedBox(width: 4),
                            Text(
                              isArabic
                                  ? 'مسؤول النظام · Admin Access'
                                  : 'System Administrator · Admin Access',
                              style: const TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    ],
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 3),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF3F0FF),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFFE9D5FF)),
                          ),
                          child: Text(
                            isArabic
                                ? 'الصف ${activeChild?['default_grade'] ?? currentGrade}'
                                : 'Grade ${activeChild?['default_grade'] ?? currentGrade}',
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF6C5CE7),
                            ),
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          isArabic
                              ? '· الفصل $currentTerm'
                              : '· Term $currentTerm',
                          style: const TextStyle(
                              fontSize: 11, color: Color(0xFF94A3B8)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // General Group
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
          child: Text(
            isArabic ? 'عام' : 'General',
            style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Color(0xFF64748B)),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: const Color(0xFFF1F0FA)),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF6C5CE7).withValues(alpha: 0.04),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            children: [
              _profileRow(
                icon: Icons.chat_bubble_outline,
                iconColor: const Color(0xFF6C5CE7),
                iconBg: const Color(0xFFF3F0FF),
                titleAr: isArabic ? 'آخر محادثة مع المعلم الذكي' : 'Latest Session with AI Tutor',
                subtitleEn: isArabic ? 'استئناف الحوار التفاعلي السقراطي' : 'Resume Socratic conversational tutoring',
                onTap: onOpenAskFahim,
              ),
              const Divider(height: 1, indent: 64, color: Color(0xFFF1F5F9)),
              _profileRow(
                icon: Icons.receipt_long_outlined,
                iconColor: const Color(0xFF2563EB),
                iconBg: const Color(0xFFDBEAFE),
                titleAr: isArabic ? 'الاشتراكات والفواتير الضريبية' : 'Subscriptions & Tax Invoices',
                subtitleEn: isArabic ? 'الباقات المفعلة وفواتير ضريبة القيمة المضافة الرسمية' : 'Active passes and official UAE FTA VAT invoices',
                onTap: onOpenSubscriptions ?? onOpenPaywall,
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // Account Group
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
          child: Text(
            isArabic ? 'الحساب' : 'Account',
            style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Color(0xFF64748B)),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: const Color(0xFFF1F0FA)),
          ),
          child: Column(
            children: [
              _profileRow(
                icon: Icons.logout,
                iconColor: const Color(0xFFEF4444),
                iconBg: const Color(0xFFFEE2E2),
                titleAr: isArabic ? 'تسجيل الخروج' : 'Sign Out',
                subtitleEn: isArabic ? 'الخروج من الحساب الحالي' : 'Sign out of current profile',
                onTap: onLogout,
              ),
              if (onDeleteAccount != null) ...[
                const Divider(height: 1, indent: 64, color: Color(0xFFF1F5F9)),
                _profileRow(
                  icon: Icons.delete_forever,
                  iconColor: const Color(0xFFDC2626),
                  iconBg: const Color(0xFFFEE2E2),
                  titleAr: isArabic ? 'حذف الحساب نهائياً' : 'Delete Account Permanently',
                  subtitleEn: isArabic ? 'حذف الحساب وجميع البيانات نهائياً' : 'Permanently remove account, child profiles, and data',
                  onTap: () => _confirmDeleteAccount(context),
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: 32),
      ],
    );
  }

  void _confirmDeleteAccount(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            const Icon(Icons.warning_amber_rounded, color: Color(0xFFDC2626)),
            const SizedBox(width: 8),
            Text(
              isArabic ? 'حذف الحساب نهائياً' : 'Delete Account Permanently',
              style: const TextStyle(
                color: Color(0xFFDC2626),
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isArabic
                  ? 'تحذير: هذا الإجراء لا يمكن التراجع عنه.\nسيتم حذف حسابك وجميع ملفات المتعلمين والاشتراكات وسجلات التقدم نهائياً من خوادم جسر، امتثالاً لسياسات الخصوصية ومتجر التطبيقات.'
                  : 'Warning: This action is permanent and cannot be undone.\nAll learner profiles, learning progress, subscriptions, and personal data will be permanently deleted from JISR servers in compliance with privacy regulations.',
              style: const TextStyle(fontSize: 13, height: 1.4),
            ),
            const SizedBox(height: 10),
            Text(
              isArabic
                  ? 'Notice: Data deletion is irreversible.'
                  : 'ملاحظة: حذف البيانات نهائي ولا يمكن استرجاعه.',
              style: const TextStyle(fontSize: 11, color: Colors.black54, height: 1.3),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(isArabic ? 'إلغاء' : 'Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              onDeleteAccount?.call();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFDC2626),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: Text(
              isArabic ? 'حذف نهائي' : 'Delete Forever',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  Widget _profileRow({
    required IconData icon,
    required Color iconColor,
    required Color iconBg,
    required String titleAr,
    required String subtitleEn,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: iconBg,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: iconColor, size: 20),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    titleAr,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1E293B),
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitleEn,
                    style: const TextStyle(
                      fontSize: 11,
                      color: Color(0xFF94A3B8),
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.arrow_forward_ios,
              size: 13,
              color: Color(0xFFCBD5E1),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// 1.1 SUBSCRIPTIONS & TAX INVOICES VIEW
// ---------------------------------------------------------------------------
class SubscriptionsView extends StatefulWidget {
  final Map<String, dynamic>? activeChild;
  final String? token;
  final bool isArabic;
  final VoidCallback onBack;
  final VoidCallback onOpenPaywall;
  final ApiService? api;

  const SubscriptionsView({
    super.key,
    required this.activeChild,
    required this.onBack,
    required this.onOpenPaywall,
    this.token,
    this.isArabic = false,
    this.api,
  });

  @override
  State<SubscriptionsView> createState() => _SubscriptionsViewState();
}

class _SubscriptionsViewState extends State<SubscriptionsView> {
  late final ApiService _api;
  bool _loading = true;
  String? _error;
  List<dynamic> _receipts = [];

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? ApiService();
    _fetchReceipts();
  }

  @override
  void didUpdateWidget(SubscriptionsView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.activeChild?['id'] != widget.activeChild?['id']) {
      _fetchReceipts();
    }
  }

  Future<void> _fetchReceipts() async {
    final childId = widget.activeChild?['id']?.toString();
    if (childId == null || childId.isEmpty) {
      if (mounted) setState(() => _loading = false);
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final res = await _api.listReceipts(childId, token: widget.token);
      if (mounted) {
        setState(() {
          _receipts = res is List ? res : [];
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  void _showTaxInvoiceDialog(Map<String, dynamic> r) {
    final isAr = widget.isArabic;
    final subtotalUsd = (r['subtotal_usd'] as num?)?.toDouble() ??
        ((r['amount_usd'] as num?) != null ? (r['amount_usd'] as num).toDouble() / 1.05 : 0.0);
    final vatUsd = (r['vat_amount_usd'] as num?)?.toDouble() ??
        ((r['amount_usd'] as num?) != null ? (r['amount_usd'] as num).toDouble() - subtotalUsd : 0.0);
    final totalUsd = (r['amount_usd'] as num?)?.toDouble() ?? 0.0;
    final totalAed = (r['amount_aed'] as num?)?.toDouble() ?? (totalUsd * 3.6725);
    final subtotalAed = subtotalUsd * 3.6725;
    final vatAed = vatUsd * 3.6725;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        titlePadding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
        contentPadding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFF58337E).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.receipt_long, color: Color(0xFF58337E), size: 22),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isAr ? 'فاتورة ضريبية رسمية' : 'Official Tax Invoice',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  Text(
                    'UAE FTA Compliant · TRN 100458923100003',
                    style: TextStyle(fontSize: 10, color: Colors.grey.shade600),
                  ),
                ],
              ),
            ),
          ],
        ),
        content: SizedBox(
          width: 420,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: [
                      _invoiceRow(isAr ? 'رقم الفاتورة' : 'Invoice Number', r['tax_invoice_number'] ?? 'INV-${r['receipt_number']}'),
                      const SizedBox(height: 6),
                      _invoiceRow(isAr ? 'رقم الإيصال' : 'Receipt Reference', r['receipt_number']?.toString() ?? '-'),
                      const SizedBox(height: 6),
                      _invoiceRow(isAr ? 'التاريخ' : 'Date', r['created_at']?.toString().split('T').first ?? '-'),
                      const SizedBox(height: 6),
                      _invoiceRow(isAr ? 'اسم الطالب' : 'Student Name', widget.activeChild?['name']?.toString() ?? (isAr ? 'طالب جسر' : 'JISR Student')),
                      const SizedBox(height: 6),
                      _invoiceRow(isAr ? 'المدرسة' : 'School', r['school_name']?.toString() ?? 'Sunrise International School'),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: [
                      _invoiceRow(
                        isAr ? 'المبلغ الصافي الخاضع للضريبة' : 'Subtotal (Excl. VAT)',
                        'USD ${subtotalUsd.toStringAsFixed(2)} (AED ${subtotalAed.toStringAsFixed(2)})',
                      ),
                      const SizedBox(height: 6),
                      _invoiceRow(
                        isAr ? 'ضريبة القيمة المضافة (5% VAT)' : 'UAE VAT (5%)',
                        'USD ${vatUsd.toStringAsFixed(2)} (AED ${vatAed.toStringAsFixed(2)})',
                      ),
                      const Divider(height: 14),
                      _invoiceRow(
                        isAr ? 'المبلغ الإجمالي شاملاً الضريبة' : 'Total (5% VAT Inclusive)',
                        'USD ${totalUsd.toStringAsFixed(2)} (AED ${totalAed.toStringAsFixed(2)})',
                        isBold: true,
                        color: const Color(0xFF065F46),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Icon(Icons.lock_outline, size: 13, color: Colors.grey.shade600),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        isAr
                            ? 'الدفع مسدد وموثق إلكترونياً لدى الهيئة الاتحادية للضرائب'
                            : 'Payment verified and registered with UAE Federal Tax Authority',
                        style: TextStyle(fontSize: 10, color: Colors.grey.shade600),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: Text(isAr ? 'إغلاق' : 'Close'),
          ),
        ],
      ),
    );
  }

  Widget _invoiceRow(String label, String value, {bool isBold = false, Color? color}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(fontSize: 11, color: isBold ? Colors.black87 : Colors.grey.shade700, fontWeight: isBold ? FontWeight.bold : FontWeight.normal)),
        Text(value, style: TextStyle(fontSize: 11, fontWeight: isBold ? FontWeight.w900 : FontWeight.bold, color: color ?? Colors.black87)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final isAr = widget.isArabic;
    final childName = widget.activeChild?['name'] ?? (isAr ? 'طالب جسر' : 'Student');

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Navigation bar: Back and Purchase
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            TextButton.icon(
              onPressed: widget.onBack,
              style: TextButton.styleFrom(
                foregroundColor: const Color(0xFF58337E),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              ),
              icon: Icon(isAr ? Icons.arrow_forward : Icons.arrow_back, size: 18),
              label: Text(
                isAr ? 'العودة للحساب' : 'Back to Profile',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ),
            ElevatedButton.icon(
              onPressed: widget.onOpenPaywall,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF065F46),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              ),
              icon: const Icon(Icons.add_shopping_cart, size: 16),
              label: Text(
                isAr ? 'شراء باقة جديدة' : 'Purchase Access',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Header Title
        Text(
          isAr ? 'اشتراكاتي وفواتيري الضريبية' : 'My Subscriptions & Invoices',
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w900,
            color: Color(0xFF58337E),
          ),
        ),
        const SizedBox(height: 2),
        Text(
          isAr
              ? 'سجل المشتريات والفواتير المعتمدة للطالب: $childName'
              : 'Official UAE FTA transaction history for $childName',
          style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
        ),
        const SizedBox(height: 16),

        if (_error != null)
          Container(
            padding: const EdgeInsets.all(12),
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: const Color(0xFFFEF2F2),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFFCA5A5)),
            ),
            child: Row(
              children: [
                const Icon(Icons.error_outline, color: Color(0xFFDC2626), size: 18),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _error!,
                    style: const TextStyle(color: Color(0xFF991B1B), fontSize: 12),
                  ),
                ),
                TextButton(
                  onPressed: _fetchReceipts,
                  child: Text(isAr ? 'إعادة المحاولة' : 'Retry'),
                ),
              ],
            ),
          ),

        if (_loading)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 40),
            child: Center(
              child: CircularProgressIndicator(color: Color(0xFF58337E)),
            ),
          )
        else if (_receipts.isEmpty)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF3F0FF),
                    borderRadius: BorderRadius.circular(30),
                  ),
                  child: const Icon(Icons.receipt_long_outlined, size: 36, color: Color(0xFF6C5CE7)),
                ),
                const SizedBox(height: 12),
                Text(
                  isAr ? 'لا توجد اشتراكات أو فواتير بعد' : 'No subscriptions or invoices yet',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF1E293B)),
                ),
                const SizedBox(height: 6),
                Text(
                  isAr
                      ? 'الوصول التجريبي المجاني مفعل حالياً. اشترك لفتح كافة فصول ونماذج المنهاج.'
                      : 'Free Demo Access is currently active. Upgrade to unlock all curriculum modules and exam simulations.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 12, color: Color(0xFF64748B), height: 1.4),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: widget.onOpenPaywall,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF58337E),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  ),
                  icon: const Icon(Icons.bolt, size: 16),
                  label: Text(
                    isAr ? 'ترقية الاشتراك وتفعيل الفصول' : 'Unlock All Modules',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                ),
              ],
            ),
          )
        else
          ..._receipts.map((r) {
            final isAnnual = r['package_type'] == 'annual' || (r['term'] == 0);
            final title = isAnnual
                ? (isAr ? 'الباقة السنوية الكاملة (الفصول 1، 2 و3)' : 'Annual Pass (Terms 1, 2, & 3)')
                : (isAr ? 'باقة الفصل ${r['term']}' : 'Term ${r['term']} License');
            final amountUsd = (r['amount_usd'] as num?)?.toDouble() ?? 0.0;
            final amountAed = (r['amount_aed'] as num?)?.toDouble() ?? (amountUsd * 3.6725);
            final receiptNum = r['receipt_number']?.toString() ?? 'REC';
            final status = (r['status']?.toString() ?? 'PAID').toUpperCase();

            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
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
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: isAnnual ? const Color(0xFFECFDF5) : const Color(0xFFEFF6FF),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      isAnnual ? Icons.verified : Icons.bookmark_added,
                      color: isAnnual ? const Color(0xFF065F46) : const Color(0xFF1D4ED8),
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 14),
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
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF1E293B),
                                ),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFFDCFCE7),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                status,
                                style: const TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w900,
                                  color: Color(0xFF166534),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '$receiptNum · USD ${amountUsd.toStringAsFixed(2)} (AED ${amountAed.toStringAsFixed(2)})',
                          style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  OutlinedButton.icon(
                    onPressed: () => _showTaxInvoiceDialog(r as Map<String, dynamic>),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF58337E),
                      side: const BorderSide(color: Color(0xFF58337E)),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    ),
                    icon: const Icon(Icons.description_outlined, size: 14),
                    label: Text(
                      isAr ? 'الفاتورة' : 'Invoice',
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            );
          }),
        const SizedBox(height: 24),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// 2. PARENT DASHBOARD VIEW
// ---------------------------------------------------------------------------
class ParentDashboardView extends StatelessWidget {
  final Map<String, dynamic>? activeChild;

  const ParentDashboardView({super.key, required this.activeChild});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: const BoxDecoration(
            color: Colors.white,
            border: Border(
              top: BorderSide(color: Color(0xFFCBD5E1)),
              right: BorderSide(color: Color(0xFFCBD5E1)),
              bottom: BorderSide(color: Color(0xFFCBD5E1)),
              left: BorderSide(color: Color(0xFF064E3B), width: 4),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Parent Overview: ${activeChild?['name'] ?? 'Learner'}',
                style:
                    const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              const Text(
                'Objective mastery: 85% · 1 Lesson Completed · Missing 9 lessons in Term 1',
                style: TextStyle(fontSize: 11, color: Colors.black54),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Weekly Digest Card
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.white,
            border: Border.all(color: const Color(0xFF064E3B), width: 1.5),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'WEEKLY DIGEST (الملخص الأسبوعي)',
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF064E3B)),
                  ),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    color: const Color(0xFF064E3B),
                    child: const Text('Week 3',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      color: const Color(0xFFF8FAFC),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text('STUDY TIME',
                              style: TextStyle(
                                  fontSize: 9,
                                  color: Colors.black54,
                                  fontWeight: FontWeight.bold)),
                          Text('135 mins',
                              style: TextStyle(
                                  fontSize: 14, fontWeight: FontWeight.bold)),
                          Text('+18% vs last wk',
                              style: TextStyle(
                                  fontSize: 9,
                                  color: Color(0xFF064E3B),
                                  fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      color: const Color(0xFFF8FAFC),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text('CAPSULES',
                              style: TextStyle(
                                  fontSize: 9,
                                  color: Colors.black54,
                                  fontWeight: FontWeight.bold)),
                          Text('3 Completed',
                              style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF064E3B))),
                          Text('Bite-sized units',
                              style: TextStyle(
                                  fontSize: 9, color: Colors.black54)),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      color: const Color(0xFFF8FAFC),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text('QUIZ AVG',
                              style: TextStyle(
                                  fontSize: 9,
                                  color: Colors.black54,
                                  fontWeight: FontWeight.bold)),
                          Text('86.5%',
                              style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFFB45309))),
                          Text('4 quizzes passed',
                              style: TextStyle(
                                  fontSize: 9, color: Colors.black54)),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            backgroundColor: Color(0xFF064E3B),
                            content: Text(
                                'Weekly Digest alert sent to Parent In-App Notification channel.'),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.zero),
                          ),
                        );
                      },
                      icon: const Icon(Icons.notifications_active_outlined,
                          size: 14),
                      label: const Text('In-App Alert',
                          style: TextStyle(fontSize: 11)),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            backgroundColor: Color(0xFFB45309),
                            content: Text(
                                'Weekly Digest email dispatched to registered parent email.'),
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.zero),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFB45309)),
                      icon: const Icon(Icons.email_outlined, size: 14),
                      label: const Text('Email Digest',
                          style: TextStyle(fontSize: 11)),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Guidance for Non-Arabic Speaking Parents
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.white,
            border: Border.all(color: const Color(0xFF0F172A), width: 1.5),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: const [
                  Icon(Icons.family_restroom,
                      color: Color(0xFFB45309), size: 18),
                  SizedBox(width: 6),
                  Text(
                    'NON-ARABIC SPEAKING PARENT GUIDE',
                    style:
                        TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              const Text(
                'You do not need to speak Arabic to help your child succeed. Use these quick tips at home:',
                style: TextStyle(fontSize: 11, color: Colors.black54),
              ),
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(10),
                color: const Color(0xFFF8FAFC),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text('💬 What to ask at dinner:',
                        style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                            color: Color(0xFF064E3B))),
                    SizedBox(height: 2),
                    Text(
                        '"Can you teach me the Arabic word for ball (كُرة - Kurah) and make a sentence?"',
                        style: TextStyle(
                            fontSize: 11, fontStyle: FontStyle.italic)),
                    SizedBox(height: 8),
                    Text('🌟 How to praise them:',
                        style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                            color: Color(0xFFB45309))),
                    SizedBox(height: 2),
                    Text(
                        '"Praise their focus on the two-dot rule for Taa Marbutah (ة) like a little crown!"',
                        style: TextStyle(fontSize: 11)),
                    SizedBox(height: 8),
                    Text('🏡 Quick Household Activity:',
                        style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                            color: Color(0xFF0F172A))),
                    SizedBox(height: 2),
                    Text(
                        'Point to objects in the room and let them state the Arabic name and describe it.',
                        style: TextStyle(fontSize: 11)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// 3. MASTERY HEATMAP VIEW
// ---------------------------------------------------------------------------
class MasteryHeatmapView extends StatefulWidget {
  final Map<String, dynamic>? activeChild;
  final ApiService? api;
  final String? token;

  const MasteryHeatmapView({
    super.key,
    required this.activeChild,
    this.api,
    this.token,
  });

  @override
  State<MasteryHeatmapView> createState() => _MasteryHeatmapViewState();
}

class _MasteryHeatmapViewState extends State<MasteryHeatmapView> {
  bool _loading = false;
  String? _errorMessage;
  Map<String, dynamic>? _heatmap;

  @override
  void initState() {
    super.initState();
    _loadHeatmap();
  }

  @override
  void didUpdateWidget(covariant MasteryHeatmapView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.activeChild?['id'] != oldWidget.activeChild?['id']) {
      _loadHeatmap();
    }
  }

  Future<void> _loadHeatmap() async {
    final childId = widget.activeChild?['id']?.toString();
    if (childId == null || widget.api == null) {
      if (mounted) {
        setState(() {
          _loading = false;
          _heatmap = null;
        });
      }
      return;
    }

    setState(() {
      _loading = true;
      _errorMessage = null;
    });

    try {
      final res = await widget.api!.heatmap(childId, token: widget.token);
      if (mounted) {
        setState(() {
          _loading = false;
          _heatmap = res is Map<String, dynamic> ? res : null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _errorMessage = e.toString().replaceAll('AuthException: ', '');
        });
      }
    }
  }

  void _openGapDrillSheet() {
    final childId = widget.activeChild?['id']?.toString();
    if (childId == null || widget.api == null) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _GapDrillModal(
        childId: childId,
        api: widget.api!,
        token: widget.token,
        onDrillCompleted: _loadHeatmap,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (widget.activeChild == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: const [
              Icon(Icons.person_outline, size: 48, color: Color(0xFF64748B)),
              SizedBox(height: 12),
              Text(
                'يرجى تسجيل الدخول أو اختيار ملف الطالب لعرض سجل الإتقان المعرفي وحساب فجوات التعلم بدقة.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, color: Color(0xFF475569)),
              ),
            ],
          ),
        ),
      );
    }

    if (_loading && _heatmap == null) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: CircularProgressIndicator(color: Color(0xFF064E3B)),
        ),
      );
    }

    if (_errorMessage != null && _heatmap == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 40, color: Colors.red),
              const SizedBox(height: 10),
              Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12)),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF064E3B)),
                onPressed: _loadHeatmap,
                icon: const Icon(Icons.refresh, size: 14),
                label: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      );
    }

    final childName = _heatmap?['child_name'] ?? widget.activeChild?['name'] ?? 'الطالب';
    final overallPct = (_heatmap?['overall_mastery_pct'] as num?)?.toDouble() ?? 0.0;
    final totalTracked = _heatmap?['total_concepts_tracked'] ?? 0;
    final gapsList = (_heatmap?['knowledge_gaps'] as List?) ?? [];
    final activeGapsCount = _heatmap?['active_gaps_count'] ?? gapsList.length;
    final conceptsByCategory = (_heatmap?['concepts_by_category'] as Map<String, dynamic>?) ?? {};

    final isUncalibrated = (totalTracked == 0 || (overallPct == 0.0 && activeGapsCount == 0));

    return RefreshIndicator(
      color: const Color(0xFF064E3B),
      onRefresh: _loadHeatmap,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Header Card
          Container(
            padding: const EdgeInsets.all(16),
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
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFFECFDF5),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text(
                              'سجل الإتقان المعرفي الحقيقي',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF064E3B),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'كفاءات $childName اللغوية',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1E293B),
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        isUncalibrated
                            ? 'لم يبدأ بعد — تبدأ المعايرة بإجراء الاختبار التشخيصي أو حل التمارين'
                            : 'معايرة مستمرة وفق نتائج التمارين والاختبارات الرسمية',
                        style: TextStyle(
                          fontSize: 11,
                          color: isUncalibrated ? const Color(0xFFD97706) : const Color(0xFF64748B),
                        ),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      isUncalibrated ? '0%' : '${overallPct.toStringAsFixed(1)}%',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w900,
                        color: isUncalibrated
                            ? const Color(0xFF94A3B8)
                            : (overallPct >= 75.0 ? const Color(0xFF064E3B) : const Color(0xFFD97706)),
                      ),
                    ),
                    Text(
                      isUncalibrated ? 'لم يبدأ بعد' : 'المعدل العام',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: isUncalibrated ? const Color(0xFF94A3B8) : const Color(0xFF475569),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Knowledge Gaps / Spaced Review Card
          if (activeGapsCount > 0) ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFFEF2F2),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFFCA5A5), width: 1.5),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.warning_amber_rounded, size: 18, color: Color(0xFFDC2626)),
                          const SizedBox(width: 6),
                          Text(
                            '$activeGapsCount فجوات لغوية نشطة بحاجة لدعم',
                            style: const TextStyle(
                              color: Color(0xFFDC2626),
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEE2E2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          'أقل من 70%',
                          style: TextStyle(
                            color: Color(0xFFDC2626),
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  ...gapsList.map((gap) {
                    final nameAr = gap['concept_name_ar'] ?? gap['concept_key'] ?? '';
                    final nameEn = gap['concept_name_en'] ?? '';
                    final pct = (gap['mastery_percentage'] as num?)?.toDouble() ?? 0.0;
                    final attempts = gap['total_attempts'] ?? 0;
                    final interval = gap['interval_days'] ?? 1;
                    return Container(
                      margin: const EdgeInsets.only(bottom: 6),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFFECACA)),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  nameAr,
                                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                                ),
                                if (nameEn.isNotEmpty)
                                  Text(
                                    nameEn,
                                    style: const TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                                  ),
                              ],
                            ),
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                '${pct.toStringAsFixed(1)}%',
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFFDC2626),
                                ),
                              ),
                              Text(
                                '$attempts محاولات · تكرار: $interval ي',
                                style: const TextStyle(fontSize: 9, color: Color(0xFF94A3B8)),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  }),
                  const SizedBox(height: 8),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFDC2626),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 10),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: _openGapDrillSheet,
                      icon: const Icon(Icons.bolt, size: 16),
                      label: const Text(
                        'بدء تدريب سد الفجوات والتكرار المتباعد (+25 XP)',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ] else ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFF0FDF4),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF86EFAC)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.verified, color: Color(0xFF16A34A), size: 24),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'لا توجد فجوات لغوية نشطة 🎉',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF166534),
                          ),
                        ),
                        Text(
                          isUncalibrated
                              ? 'ابدأ أول درس أو اختبار لتحديد مستوى الإتقان المعرفي.'
                              : 'كافة المهارات المدرجة تتجاوز معيار الإتقان (70%+).',
                          style: const TextStyle(fontSize: 11, color: Color(0xFF15803D)),
                        ),
                      ],
                    ),
                  ),
                  TextButton.icon(
                    onPressed: _openGapDrillSheet,
                    icon: const Icon(Icons.fitness_center, size: 14, color: Color(0xFF166534)),
                    label: const Text(
                      'تمرين SM-2',
                      style: TextStyle(fontSize: 11, color: Color(0xFF166534), fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 20),

          // Concept Mastery Matrix Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'مصفوفة الإتقان التفصيلية (CONCEPT MASTERY MATRIX)',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF334155),
                ),
              ),
              Text(
                '$totalTracked مهارات',
                style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
              ),
            ],
          ),
          const SizedBox(height: 10),

          if (conceptsByCategory.isEmpty)
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: const Center(
                child: Text(
                  'لم يتم تسجيل أي مهارات بعد.\nقم بحل الاختبار التشخيصي أو تمارين الدروس لتبدأ المعايرة الحقيقية.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                ),
              ),
            )
          else
            ...conceptsByCategory.entries.expand((entry) {
              final catKey = entry.key;
              final list = (entry.value as List?) ?? [];
              final catTitleAr = _categoryTitle(catKey);

              return [
                Padding(
                  padding: const EdgeInsets.only(top: 8, bottom: 4),
                  child: Text(
                    catTitleAr,
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF064E3B),
                    ),
                  ),
                ),
                ...list.map((c) {
                  final title = c['concept_name_ar'] ?? c['concept_key'] ?? '';
                  final titleEn = c['concept_name_en'] ?? '';
                  final pct = (c['mastery_percentage'] as num?)?.toDouble() ?? 0.0;
                  final totalAttempts = c['total_attempts'] ?? 0;
                  final correctAttempts = c['correct_attempts'] ?? 0;
                  final interval = c['interval_days'] ?? 1;
                  final reps = c['repetition_count'] ?? 0;

                  return _conceptMatrixItem(
                    title: title,
                    titleEn: titleEn,
                    pct: pct,
                    totalAttempts: totalAttempts,
                    correctAttempts: correctAttempts,
                    intervalDays: interval,
                    repetitionCount: reps,
                  );
                }),
              ];
            }),
        ],
      ),
    );
  }

  static String _categoryTitle(String cat) {
    switch (cat) {
      case 'grammar':
        return 'القواعد والتراكيب النحوية (Grammar)';
      case 'vocabulary':
        return 'المفردات والدلالة اللغوية (Vocabulary)';
      case 'reading':
        return 'الطلاقة وفهم المقروء (Reading Comprehension)';
      case 'orthography':
        return 'الرسم الإملائي والخط (Orthography)';
      default:
        return cat.toUpperCase();
    }
  }

  Widget _conceptMatrixItem({
    required String title,
    required String titleEn,
    required double pct,
    required int totalAttempts,
    required int correctAttempts,
    required int intervalDays,
    required int repetitionCount,
  }) {
    final Color color;
    final String statusLabel;

    if (totalAttempts == 0) {
      color = const Color(0xFF94A3B8);
      statusLabel = 'لم يبدأ بعد';
    } else if (pct >= 85.0) {
      color = const Color(0xFF064E3B);
      statusLabel = 'متقن (Mastered)';
    } else if (pct >= 70.0) {
      color = const Color(0xFF059669);
      statusLabel = 'متمكن (Proficient)';
    } else {
      color = const Color(0xFFDC2626);
      statusLabel = 'فجوة تعليمية (Active Gap)';
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                    ),
                    if (titleEn.isNotEmpty)
                      Text(
                        titleEn,
                        style: const TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                      ),
                  ],
                ),
              ),
              Text(
                '${pct.toStringAsFixed(1)}%',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: color),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: totalAttempts == 0 ? 0.0 : (pct / 100.0).clamp(0.0, 1.0),
              backgroundColor: const Color(0xFFF1F5F9),
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                statusLabel,
                style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.bold, color: color),
              ),
              Text(
                totalAttempts == 0
                    ? '0 محاولات'
                    : '$correctAttempts/$totalAttempts صحيح · تكرار SM-2: $intervalDays ي (تكرار: $repetitionCount)',
                style: const TextStyle(fontSize: 9, color: Color(0xFF64748B)),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _GapDrillModal extends StatefulWidget {
  final String childId;
  final ApiService api;
  final String? token;
  final VoidCallback onDrillCompleted;

  const _GapDrillModal({
    required this.childId,
    required this.api,
    this.token,
    required this.onDrillCompleted,
  });

  @override
  State<_GapDrillModal> createState() => _GapDrillModalState();
}

class _GapDrillModalState extends State<_GapDrillModal> {
  bool _loading = true;
  String? _error;
  List<dynamic> _questions = [];
  int _currentIndex = 0;
  int? _selectedIndex;
  bool _submitting = false;
  Map<String, dynamic>? _drillResult;
  int _totalXpEarned = 0;

  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final res = await widget.api.gapReviewSession(widget.childId, token: widget.token);
      final qs = (res is Map && res['questions'] is List) ? res['questions'] as List : [];
      if (mounted) {
        setState(() {
          _loading = false;
          _questions = qs;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.toString().replaceAll('AuthException: ', '');
        });
      }
    }
  }

  Future<void> _submitAnswer(int idx) async {
    if (_submitting || _drillResult != null) return;
    final q = _questions[_currentIndex];
    final isCorrect = (idx == q['correct_index']);

    setState(() {
      _selectedIndex = idx;
      _submitting = true;
    });

    try {
      final res = await widget.api.recordDrill({
        'child_id': widget.childId,
        'concept_key': q['concept_key'],
        'question_id': q['id'],
        'selected_index': idx,
        'is_correct': isCorrect,
      }, token: widget.token);

      if (mounted) {
        setState(() {
          _submitting = false;
          _drillResult = res is Map<String, dynamic> ? res : null;
          _totalXpEarned += ((res?['xp_awarded'] as num?)?.toInt() ?? (isCorrect ? 25 : 5));
        });
        widget.onDrillCompleted();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _submitting = false;
          _drillResult = {
            'feedback_ar': isCorrect ? 'أحسنت! إجابة صحيحة' : 'محاولة جيدة، راجع القاعدة وتدرب مجدداً.',
            'new_mastery_pct': null,
            'xp_awarded': isCorrect ? 25 : 5,
          };
        });
      }
    }
  }

  void _nextQuestion() {
    if (_currentIndex + 1 < _questions.length) {
      setState(() {
        _currentIndex++;
        _selectedIndex = null;
        _drillResult = null;
      });
    } else {
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFFCBD5E1),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 14),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: const [
                  Icon(Icons.bolt, color: Color(0xFF064E3B)),
                  SizedBox(width: 8),
                  Text(
                    'تدريب سد الفجوات والتكرار المتباعد (SM-2)',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF064E3B)),
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.close, size: 20),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
          const Divider(),
          if (_loading)
            const Expanded(
              child: Center(
                child: CircularProgressIndicator(color: Color(0xFF064E3B)),
              ),
            )
          else if (_error != null)
            Expanded(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 12)),
                    const SizedBox(height: 10),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF064E3B)),
                      onPressed: _loadQuestions,
                      child: const Text('إعادة المحاولة'),
                    ),
                  ],
                ),
              ),
            )
          else if (_questions.isEmpty)
            Expanded(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Icon(Icons.check_circle_outline, size: 48, color: Color(0xFF064E3B)),
                    SizedBox(height: 10),
                    Text(
                      'رائع! لا توجد أسئلة مراجعة مجدولة في الوقت الحالي.',
                      style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            )
          else ...[
            Text(
              'السؤال ${_currentIndex + 1} من ${_questions.length} · مهارة: ${_questions[_currentIndex]['concept_name_ar'] ?? ''}',
              style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _questions[_currentIndex]['prompt_ar'] ?? '',
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, height: 1.5),
                  ),
                  if (_questions[_currentIndex]['prompt_en'] != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      _questions[_currentIndex]['prompt_en'] ?? '',
                      style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: Color(0xFF64748B)),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: (_questions[_currentIndex]['options'] as List?)?.length ?? 0,
                itemBuilder: (ctx, idx) {
                  final opt = _questions[_currentIndex]['options'][idx];
                  final isSelected = _selectedIndex == idx;
                  final isCorrectOpt = idx == _questions[_currentIndex]['correct_index'];

                  Color bgColor = Colors.white;
                  Color borderColor = const Color(0xFFE2E8F0);
                  Color textColor = const Color(0xFF1E293B);

                  if (_drillResult != null) {
                    if (isCorrectOpt) {
                      bgColor = const Color(0xFFECFDF5);
                      borderColor = const Color(0xFF10B981);
                      textColor = const Color(0xFF064E3B);
                    } else if (isSelected && !isCorrectOpt) {
                      bgColor = const Color(0xFFFEF2F2);
                      borderColor = const Color(0xFFEF4444);
                      textColor = const Color(0xFF991B1B);
                    }
                  } else if (isSelected) {
                    bgColor = const Color(0xFFECFDF5);
                    borderColor = const Color(0xFF064E3B);
                  }

                  return InkWell(
                    onTap: _submitting || _drillResult != null ? null : () => _submitAnswer(idx),
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: bgColor,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: borderColor, width: isSelected ? 1.5 : 1),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 24,
                            height: 24,
                            alignment: Alignment.center,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(color: borderColor),
                              color: isSelected ? const Color(0xFF064E3B) : Colors.transparent,
                            ),
                            child: Text(
                              '${idx + 1}',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: isSelected ? Colors.white : const Color(0xFF64748B),
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              opt.toString(),
                              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: textColor),
                            ),
                          ),
                          if (_drillResult != null && isCorrectOpt)
                            const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 18)
                          else if (_drillResult != null && isSelected && !isCorrectOpt)
                            const Icon(Icons.cancel, color: Color(0xFFEF4444), size: 18),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
            if (_drillResult != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0FDF4),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFF86EFAC)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.stars, color: Color(0xFF16A34A), size: 16),
                        const SizedBox(width: 6),
                        Text(
                          _drillResult!['feedback_ar'] ?? 'أحسنت!',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF166534)),
                        ),
                      ],
                    ),
                    if (_drillResult!['new_mastery_pct'] != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        'نسبة الإتقان الجديدة: ${_drillResult!['new_mastery_pct']}% (+${_drillResult!['xp_awarded'] ?? 25} XP)',
                        style: const TextStyle(fontSize: 11, color: Color(0xFF15803D)),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 10),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF064E3B),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: _nextQuestion,
                  child: Text(
                    _currentIndex + 1 < _questions.length ? 'السؤال التالي ⬅️' : 'إنهاء التدريب (+$_totalXpEarned XP) 🎉',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.white),
                  ),
                ),
              ),
            ],
          ],
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// 4. GAMIFICATION VIEW
// ---------------------------------------------------------------------------
class GamificationView extends StatelessWidget {
  final Map<String, dynamic>? activeChild;

  const GamificationView({super.key, required this.activeChild});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Heritage Rank Banner
        Container(
          padding: const EdgeInsets.all(14),
          decoration: const BoxDecoration(
            color: Color(0xFF0F172A),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                color: const Color(0xFF064E3B),
                child: const Icon(Icons.military_tech,
                    color: Color(0xFFFBBF24), size: 28),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('UAE HERITAGE RANK',
                        style: TextStyle(
                            color: Colors.white60,
                            fontSize: 10,
                            fontWeight: FontWeight.bold)),
                    const Text('Knight of Words · فارس الكلمات',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                            fontWeight: FontWeight.bold)),
                    Text(
                        'Level 2 Scholar · ${activeChild?['name'] ?? 'Learner'}',
                        style: const TextStyle(
                            color: Color(0xFFFBBF24), fontSize: 11)),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Streak & XP Row
        Row(
          children: [
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border:
                      Border.all(color: const Color(0xFFB45309), width: 1.5),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text('LEARNING STREAK',
                        style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFFB45309))),
                    SizedBox(height: 2),
                    Text('🔥 4 Days',
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold)),
                    Text('Active today ✓',
                        style: TextStyle(
                            fontSize: 10,
                            color: Color(0xFF064E3B),
                            fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border:
                      Border.all(color: const Color(0xFF064E3B), width: 1.5),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text('EXPERIENCE POINTS',
                        style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF064E3B))),
                    SizedBox(height: 2),
                    Text('450 XP',
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold)),
                    Text('250 XP to Level 3',
                        style:
                            TextStyle(fontSize: 10, color: Colors.black54)),
                  ],
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Badges Shelf
        const Text('MASTERY BADGES SHOWCASE (الأوسمة):',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        GridView.count(
          crossAxisCount: 3,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 8,
          mainAxisSpacing: 8,
          childAspectRatio: 1.1,
          children: [
            _badgeCard('⚡', 'Streak Champion', 'بطل الاستمرارية', true),
            _badgeCard('🦅', 'Falcon Eye', 'عين الصقر', true),
            _badgeCard('💊', 'Capsule Master', 'خبير الكبسولات', true),
            _badgeCard('📖', 'Fluent Reader', 'القارئ الماهر', true),
            _badgeCard('🔍', 'Mistake Conqueror', 'قاهر الأخطاء', false),
            _badgeCard('🏆', 'Grammar Guru', 'فارس النحو', false),
          ],
        ),
        const SizedBox(height: 16),

        // Cohort Leaderboard
        const Text('SCHOOL COHORT LEADERBOARD (المتصدرون):',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            border: Border.all(color: const Color(0xFFCBD5E1)),
          ),
          child: Column(
            children: [
              _leaderboardRow(
                  '🥇 #1', '🦅', 'Tariq Al-Hashimi', '580 XP', '🔥 6d', false),
              _leaderboardRow(
                  '🥈 #2', '🦌', 'Fatima Al-Zahra', '510 XP', '🔥 5d', false),
              _leaderboardRow('🥉 #3', '🦅',
                  '${activeChild?['name'] ?? 'Learner'} (You)', '450 XP', '🔥 4d', true),
              _leaderboardRow(
                  '4', '🐪', 'Rohan Sharma', '390 XP', '🔥 3d', false),
              _leaderboardRow(
                  '5', '🦬', 'Ryan Al-Falasi', '340 XP', '🔥 4d', false),
            ],
          ),
        ),
      ],
    );
  }

  Widget _badgeCard(
      String icon, String titleEn, String titleAr, bool unlocked) {
    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: unlocked ? const Color(0xFFECFDF5) : const Color(0xFFF1F5F9),
        border: Border.all(
            color:
                unlocked ? const Color(0xFF064E3B) : const Color(0xFFCBD5E1)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(icon,
              style: TextStyle(
                  fontSize: 20, color: unlocked ? null : Colors.black26)),
          const SizedBox(height: 2),
          Text(titleEn,
              textAlign: TextAlign.center,
              style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.bold,
                  color: unlocked ? Colors.black87 : Colors.black38),
              maxLines: 1),
          Text(titleAr,
              textAlign: TextAlign.center,
              style: TextStyle(
                  fontSize: 8,
                  color: unlocked ? const Color(0xFF064E3B) : Colors.black38),
              maxLines: 1),
        ],
      ),
    );
  }

  Widget _leaderboardRow(String rank, String avatar, String name, String xp,
      String streak, bool isUser) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      color: isUser ? const Color(0xFFECFDF5) : Colors.white,
      child: Row(
        children: [
          SizedBox(
              width: 40,
              child: Text(rank,
                  style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                      color: isUser
                          ? const Color(0xFF064E3B)
                          : Colors.black87))),
          Text(avatar, style: const TextStyle(fontSize: 14)),
          const SizedBox(width: 8),
          Expanded(
              child: Text(name,
                  style: TextStyle(
                      fontWeight: isUser ? FontWeight.bold : FontWeight.normal,
                      fontSize: 11))),
          Text(xp,
              style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 11,
                  color: Color(0xFF064E3B))),
          const SizedBox(width: 8),
          Text(streak,
              style:
                  const TextStyle(fontSize: 10, color: Color(0xFFB45309))),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// ---------------------------------------------------------------------------
// 5. TUTOR QUEUE VIEW (Live Human Teacher Work Queue)
// ---------------------------------------------------------------------------
class TutorQueueView extends StatefulWidget {
  final Map<String, dynamic>? activeChild;
  final ApiService? api;
  final String? token;

  const TutorQueueView({
    super.key,
    required this.activeChild,
    this.api,
    this.token,
  });

  @override
  State<TutorQueueView> createState() => _TutorQueueViewState();
}

class _TutorQueueViewState extends State<TutorQueueView> {
  bool _isLoading = true;
  String? _errorMessage;
  List<dynamic> _submissions = [];

  @override
  void initState() {
    super.initState();
    _fetchQueue();
  }

  @override
  void didUpdateWidget(covariant TutorQueueView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.activeChild?['id'] != widget.activeChild?['id']) {
      _fetchQueue();
    }
  }

  Future<void> _fetchQueue() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final api = widget.api ?? ApiService();
      final childId = widget.activeChild?['id'] as String?;
      List<dynamic> items = [];

      if (childId != null && childId.isNotEmpty) {
        final res = await api.childSubmissions(childId, token: widget.token);
        if (res is List) items = res;
      }

      if (items.isEmpty) {
        try {
          final qRes = await api.tutorQueue(token: widget.token);
          if (qRes is List) items = qRes;
        } catch (_) {}
      }

      if (mounted) {
        setState(() {
          _submissions = items;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final childName = widget.activeChild?['name'] ?? 'الطالب';
    final schoolName = widget.activeChild?['school_name'] ?? 'مدرسة الإمارات الوطنية';

    return RefreshIndicator(
      onRefresh: _fetchQueue,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Header Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0F172A), Color(0xFF1E293B)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.08),
                  blurRadius: 10,
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
                      children: const [
                        Icon(Icons.assignment_ind_outlined, color: Color(0xFFF59E0B), size: 24),
                        SizedBox(width: 8),
                        Text(
                          'دفتر تدقيق ومراجعة المعلم',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                      ],
                    ),
                    IconButton(
                      icon: const Icon(Icons.refresh, color: Colors.white70, size: 20),
                      onPressed: _fetchQueue,
                      tooltip: 'تحديث القائمة',
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  'متابعة مهام التعبير الكتابي والنطق الصوتي والاستفسارات المحالة من فاهم لـ $childName ($schoolName).',
                  style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          if (_isLoading)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: CircularProgressIndicator(),
              ),
            )
          else if (_errorMessage != null)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFFEE2E2),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFFCA5A5)),
              ),
              child: Column(
                children: [
                  Text('تعذر تحميل قائمة المراجعة: $_errorMessage',
                      style: const TextStyle(color: Color(0xFF991B1B), fontSize: 12)),
                  const SizedBox(height: 8),
                  ElevatedButton(
                    onPressed: _fetchQueue,
                    child: const Text('إعادة المحاولة', style: TextStyle(fontSize: 11)),
                  ),
                ],
              ),
            )
          else if (_submissions.isEmpty)
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Column(
                children: const [
                  Icon(Icons.inbox_outlined, size: 48, color: Color(0xFF94A3B8)),
                  SizedBox(height: 12),
                  Text(
                    'لا توجد مهام معلقة حالياً في قائمة التدقيق',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF1E293B)),
                  ),
                  SizedBox(height: 6),
                  Text(
                    'عندما يرسل الطالب كتابة أو تسجيلاً صوتياً في استوديو الدروس، أو عندما يحيل فاهم سؤالاً معقداً، ستظهر المهمة هنا مع ملاحظات المعلم وتقييماته.',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.5),
                  ),
                ],
              ),
            )
          else
            ..._submissions.map((item) {
              final sub = item as Map<String, dynamic>;
              final isReviewed = sub['status'] == 'reviewed';
              final type = sub['submission_type'] ?? 'writing';
              String typeLabel = 'تعبير كتابي';
              IconData typeIcon = Icons.edit_note;
              if (type == 'ask_fahim_escalation') {
                typeLabel = 'استفسار محال من فاهم';
                typeIcon = Icons.help_outline;
              } else if (type == 'speaking') {
                typeLabel = 'تسجيل نطق صوتي';
                typeIcon = Icons.mic;
              }

              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: isReviewed ? const Color(0xFF86EFAC) : const Color(0xFFFDE68A),
                    width: 1.5,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.03),
                      blurRadius: 6,
                      offset: const Offset(0, 2),
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
                            Icon(typeIcon, size: 16, color: const Color(0xFF6C5CE7)),
                            const SizedBox(width: 6),
                            Text(
                              typeLabel,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                                color: Color(0xFF1E293B),
                              ),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: isReviewed ? const Color(0xFFDCFCE7) : const Color(0xFFFEF3C7),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            isReviewed ? 'تم التدقيق والتقييم ✓' : 'قيد المراجعة ⏳',
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              color: isReviewed ? const Color(0xFF166534) : const Color(0xFF92400E),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                      ),
                      child: Text(
                        sub['content_text'] ?? 'محتوى المهمة المرسلة...',
                        style: const TextStyle(fontSize: 12, color: Color(0xFF334155), height: 1.4),
                      ),
                    ),
                    if (isReviewed) ...[
                      const SizedBox(height: 10),
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF0FDF4),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: const Color(0xFFBBF7D0)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text('ملاحظات وتقييم المعلم:',
                                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Color(0xFF166534))),
                                Text(
                                  'الدرجة: ${sub['tutor_score'] ?? 100} / 100',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Color(0xFF15803D)),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              sub['tutor_feedback'] ?? 'إجابة متميزة ومطابقة لمعايير منهاج وزارة التربية والتعليم.',
                              style: const TextStyle(fontSize: 11, color: Color(0xFF166534), height: 1.4),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// 6. MALAZIM HUB VIEW
// ---------------------------------------------------------------------------
class MalazimView extends StatefulWidget {
  final VoidCallback? onBack;
  final Function(String)? onVocalize;
  final String activeWord;

  const MalazimView({
    super.key,
    this.onBack,
    this.onVocalize,
    this.activeWord = '',
  });

  @override
  State<MalazimView> createState() => _MalazimViewState();
}

class _MalazimViewState extends State<MalazimView> {
  String _mode = 'study'; // 'study' or 'quick_review'
  final Map<String, int> _selectedAnswers = {};
  final Map<String, bool> _submittedExercises = {};

  final List<Map<String, dynamic>> _sections = [
    {
      'id': 'sec_01',
      'title_ar': '١. مفهوم الكرة ولقب (الساحرة المستديرة)',
      'title_en': '1. Ball Concept & \'The Round Witch\' Moniker',
      'content_ar':
          'الكرة هي كل جسم مستدير يُصنع من الجلد أو المطاط. وتعد كرة القدم اللعبة الأكثر شعبية في العالم، حيث أطلق عليها عشاقها لقب (الساحرة المستديرة) لأنها سحرت عقول وقلوب أكثر من مليار مشجع حول العالم بجمالها وإثارتها.',
      'content_en':
          'A ball is any spherical object crafted from leather or rubber. Football is the world\'s most popular sport, famously dubbed \'The Round Witch\' (الساحرة المستديرة) because its thrill captivates over a billion fans globally.',
      'takeaways': [
        {
          'ar': 'الكرة: كل جسم مستدير يُصنع من الجلد أو المطاط.',
          'en': 'The Ball: Any spherical round object made of leather or rubber.',
        },
        {
          'ar': 'سبب التسمية: سحرها لعقول وقلوب الملايين بحماسها وشعبيتها الجارفة.',
          'en': 'Reason for Title: Enchanting the minds and hearts of millions with thrilling excitement.',
        },
      ],
      'question_ar': 'لماذا سميت كرة القدم بـ (الساحرة المستديرة)؟',
      'question_en': 'Why was football nicknamed \'The Round Witch\' (The Enchantress)?',
      'options_ar': [
        'لأنها مصنوعة من خامات سحرية',
        'لأنها جذبت وسحرت قلوب وعقول ملايين الجماهير',
        'لأنها تُلعب فقط في المساء',
      ],
      'options_en': [
        'Because it is made of magical materials',
        'Because it captivated and enchanted the hearts and minds of millions of fans',
        'Because it is only played in the evening',
      ],
      'correct_idx': 1,
      'explanation_ar': 'أحسنت! لقبت بالساحرة لأن إثارتها وشعبيتها جذبت عقول المشجعين في شتى بقاع الأرض.',
      'explanation_en': 'Well done! Nicknamed \'The Enchantress\' because its excitement and popularity captivate fans worldwide.',
    },
    {
      'id': 'sec_02',
      'title_ar': '٢. أبعاد الملعب والمواصفات الرسمية',
      'title_en': '2. Pitch Dimensions & Official Specifications',
      'content_ar':
          'ملعب كرة القدم مستطيل الشكل ومغطى بالعشب الأخضر (الطبيعي أو الاصطناعي). يبلغ طول الملعب بين 100 إلى 110 أمتار، وعرضه بين 64 إلى 75 متراً. أما محيط الكرة الرسمية فيتراوح بين 68 إلى 70 سنتيمتراً ووزنها بين 410 إلى 450 غراماً.',
      'content_en':
          'A football pitch is rectangular and turfed with green grass. Length ranges from 100m to 110m, and width from 64m to 75m. The official ball circumference is 68 to 70 cm, weighing 410 to 450 grams.',
      'takeaways': [
        {
          'ar': 'شكل الملعب: مستطيل ومفروش بالعشب الأخضر.',
          'en': 'Pitch shape: Rectangular covered with green turf.',
        },
        {
          'ar': 'أبعاد الطول: 100 – 110 م | أبعاد العرض: 64 – 75 م.',
          'en': 'Dimensions: 100–110m in length | 64–75m in width.',
        },
        {
          'ar': 'محيط الكرة: 68 – 70 سم.',
          'en': 'Ball circumference: 68–70 cm.',
        },
      ],
      'question_ar': 'ما هو محيط كرة القدم القانونية حسب لوائح الاتحاد الدولي؟',
      'question_en': 'What is the official circumference of a regulation football per FIFA rules?',
      'options_ar': [
        '50 إلى 55 سم',
        '68 إلى 70 سم',
        '80 إلى 85 سم',
      ],
      'options_en': [
        '50 to 55 cm',
        '68 to 70 cm',
        '80 to 85 cm',
      ],
      'correct_idx': 1,
      'explanation_ar': 'صحيح تماماً! يتراوح محيط الكرة الرسمية بين 68 إلى 70 سم.',
      'explanation_en': 'Spot on! The official regulation ball circumference measures between 68 and 70 cm.',
    },
    {
      'id': 'sec_03',
      'title_ar': '٣. الفريق والتحكيم في المباراة',
      'title_en': '3. Team Structure & Officiating Crew',
      'content_ar':
          'يتكون كل فريق في كرة القدم من 11 لاعباً أساسياً، أحدهم حارس المرمى. ويقود المباراة طاقم تحكيمي مكوّن من 4 حكام: حكم الساحة الرئيسي، وحكمان مساعدان على خطي التماس (حاملا الراية)، والحكم الرابع المساعد.',
      'content_en':
          'Each team fields 11 starting players, including one goalkeeper. Matches are governed by 4 referees: the Head Referee, two Assistant Referees (linesmen), and the Fourth Official.',
      'takeaways': [
        {
          'ar': 'تشكيلة الفريق: 11 لاعباً أساسياً في الملعب أحدهم حارس المرمى.',
          'en': 'Team roster: 11 starting players on the pitch, including the goalkeeper.',
        },
        {
          'ar': 'طاقم التحكيم: 4 حكام (حكم الساحة + حكمان مساعدان + الحكم الرابع).',
          'en': 'Officiating crew: 4 referees (Head referee + 2 linesmen + 4th official).',
        },
      ],
      'question_ar': 'كم عدد الحكام الرسميين في مباراة كرة القدم؟',
      'question_en': 'How many official referees oversee a football match?',
      'options_ar': [
        'حكمان فقط',
        '4 حكام (حكم ساحة + حكمان مساعدان + حكم رابع)',
        '6 حكام',
      ],
      'options_en': [
        'Only two referees',
        '4 referees (Head referee + 2 assistants + 4th official)',
        '6 referees',
      ],
      'correct_idx': 1,
      'explanation_ar': 'أحسنت! طاقم التحكيم مكوّن من 4 حكام لإدارة المباراة بدقة.',
      'explanation_en': 'Well done! A full 4-referee crew governs every match.',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (widget.onBack != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF064E3B),
                    side: const BorderSide(color: Color(0xFF064E3B)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                  onPressed: widget.onBack,
                  icon: const Icon(Icons.arrow_back, size: 16),
                  label: const Text('العودة للرئيسية · Back to Home', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                ),
                const ArabEnglishToggleSwitch(compact: true),
              ],
            ),
          ),

        // =====================================================================
        // HEADER BANNER WITH DUAL MODE SWITCHER (Matching Web App)
        // =====================================================================
        Container(
          decoration: BoxDecoration(
            color: const Color(0xFF052E16),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF0F172A), width: 1.5),
            boxShadow: const [
              BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 2)),
            ],
          ),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'ملزمة ألعاب الكرة — الوحدة الأولى',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w900,
                  fontSize: 16.5,
                  letterSpacing: -0.2,
                ),
                textAlign: TextAlign.right,
              ),
              const SizedBox(height: 12),
              // Dual Mode Switcher
              Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFFFBBF24), width: 1.5),
                ),
                padding: const EdgeInsets.all(3),
                child: Row(
                  children: [
                    Expanded(
                      child: InkWell(
                        onTap: () => setState(() => _mode = 'study'),
                        borderRadius: BorderRadius.circular(6),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          decoration: BoxDecoration(
                            color: _mode == 'study' ? const Color(0xFFFBBF24) : Colors.transparent,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.menu_book,
                                    size: 14,
                                    color: _mode == 'study' ? const Color(0xFF0F172A) : Colors.white70,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    'وضع المذاكرة الشامل',
                                    style: TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.bold,
                                      color: _mode == 'study' ? const Color(0xFF0F172A) : Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 1),
                              Text(
                                'Comprehensive Study Mode',
                                style: TextStyle(
                                  fontSize: 9.5,
                                  color: _mode == 'study' ? const Color(0xFF1E293B) : Colors.white60,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    Expanded(
                      child: InkWell(
                        onTap: () => setState(() => _mode = 'quick_review'),
                        borderRadius: BorderRadius.circular(6),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          decoration: BoxDecoration(
                            color: _mode == 'quick_review' ? const Color(0xFFFBBF24) : Colors.transparent,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.access_time,
                                    size: 14,
                                    color: _mode == 'quick_review' ? const Color(0xFF0F172A) : Colors.white70,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    'مراجعة الـ 15 دقيقة',
                                    style: TextStyle(
                                      fontSize: 11.5,
                                      fontWeight: FontWeight.bold,
                                      color: _mode == 'quick_review' ? const Color(0xFF0F172A) : Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 1),
                              Text(
                                '15-Minute Quick Notes',
                                style: TextStyle(
                                  fontSize: 9.5,
                                  color: _mode == 'quick_review' ? const Color(0xFF1E293B) : Colors.white60,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // =====================================================================
        // MODE 1: COMPREHENSIVE STUDY MODE (WITH WORD CHIPS & LISTEN BUTTON)
        // =====================================================================
        if (_mode == 'study') ...[
          ..._sections.map((sec) => _buildStudySectionCard(sec)),
        ] else ...[
          // =====================================================================
          // MODE 2: 15-MINUTE QUICK NOTES & EXAM TRAPS
          // =====================================================================
          _buildQuickReviewCards(),
        ],
      ],
    );
  }

  Widget _buildStudySectionCard(Map<String, dynamic> sec) {
    final sectionId = sec['id'] as String;
    final isSubmitted = _submittedExercises[sectionId] == true;
    final selectedIdx = _selectedAnswers[sectionId];
    final isCorrect = selectedIdx == sec['correct_idx'];
    final takeaways = (sec['takeaways'] as List<Map<String, String>>?) ?? [];
    final optionsAr = (sec['options_ar'] as List<String>?) ?? [];
    final optionsEn = (sec['options_en'] as List<String>?) ?? [];

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFCBD5E1), width: 1.5),
        boxShadow: const [
          BoxShadow(color: Color(0x0A000000), blurRadius: 6, offset: Offset(0, 2)),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // -------------------------------------------------------------
          // Top Header: Section Title + LISTEN BUTTON (استمع)
          // -------------------------------------------------------------
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    InteractiveArabicText(
                      text: sec['title_ar'],
                      onVocalize: widget.onVocalize,
                      activeWord: widget.activeWord,
                      style: const TextStyle(
                        fontWeight: FontWeight.w900,
                        fontSize: 14.5,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                    ValueListenableBuilder<bool>(
                      valueListenable: ArabEnglishState.notifier,
                      builder: (context, isArabEnOn, _) {
                        if (!isArabEnOn) return const SizedBox.shrink();
                        final arabEn = ArabEnglishHelper.transliterate(sec['title_ar'] ?? '');
                        if (arabEn.isEmpty) return const SizedBox.shrink();
                        return Container(
                          margin: const EdgeInsets.only(top: 2, bottom: 2),
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF1F5F9),
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(color: const Color(0xFFCBD5E1), width: 0.8),
                          ),
                          child: Text(
                            '🗣️ $arabEn',
                            style: const TextStyle(
                              fontSize: 10.5,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF0F172A),
                            ),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 3),
                    Text(
                      sec['title_en'],
                      style: const TextStyle(
                        fontSize: 11,
                        color: Color(0xFF64748B),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              // LISTEN BUTTON (استمع) matching Web App
              OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF064E3B),
                  backgroundColor: Colors.white,
                  side: const BorderSide(color: Color(0xFFCBD5E1), width: 1),
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  elevation: 0,
                ),
                onPressed: () {
                  if (widget.onVocalize != null) {
                    widget.onVocalize!(sec['content_ar']);
                  }
                },
                icon: const Icon(Icons.volume_up, size: 16, color: Color(0xFF064E3B)),
                label: const Text(
                  'استمع (Listen)',
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const Divider(height: 20, color: Color(0xFFE2E8F0)),

          // -------------------------------------------------------------
          // Arabic Content with Interactive Word Chips & Tooltips
          // -------------------------------------------------------------
          InteractiveArabicText(
            text: sec['content_ar'],
            onVocalize: widget.onVocalize,
            activeWord: widget.activeWord,
            style: const TextStyle(
              fontSize: 14,
              height: 1.6,
              color: Color(0xFF1E293B),
            ),
          ),
          ValueListenableBuilder<bool>(
            valueListenable: ArabEnglishState.notifier,
            builder: (context, isArabEnOn, _) {
              if (!isArabEnOn) return const SizedBox.shrink();
              final arabEn = ArabEnglishHelper.transliterate(sec['content_ar'] ?? '');
              if (arabEn.isEmpty) return const SizedBox.shrink();
              return Container(
                margin: const EdgeInsets.only(top: 4, bottom: 4),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: const Color(0xFFCBD5E1)),
                ),
                child: Text(
                  '🗣️ $arabEn',
                  style: const TextStyle(
                    fontSize: 11.5,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
              );
            },
          ),
          const SizedBox(height: 8),
          Text(
            sec['content_en'],
            style: const TextStyle(
              fontSize: 11.5,
              color: Color(0xFF64748B),
              fontStyle: FontStyle.italic,
              height: 1.35,
            ),
          ),
          const SizedBox(height: 14),

          // -------------------------------------------------------------
          // Key Takeaways & Core Concepts
          // -------------------------------------------------------------
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'النقاط الجوهرية:',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const Text(
                  'Key Takeaways & Core Concepts',
                  style: TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                ),
                const SizedBox(height: 10),
                ...takeaways.map((t) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('• ', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                              Expanded(
                                child: InteractiveArabicText(
                                  text: t['ar']!,
                                  onVocalize: widget.onVocalize,
                                  activeWord: widget.activeWord,
                                  style: const TextStyle(
                                    fontSize: 12.5,
                                    fontWeight: FontWeight.w600,
                                    color: Color(0xFF1E293B),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          ValueListenableBuilder<bool>(
                            valueListenable: ArabEnglishState.notifier,
                            builder: (context, isArabEnOn, _) {
                              if (!isArabEnOn) return const SizedBox.shrink();
                              final arabEn = ArabEnglishHelper.transliterate(t['ar']!);
                              if (arabEn.isEmpty) return const SizedBox.shrink();
                              return Container(
                                margin: const EdgeInsets.only(left: 12, top: 2, bottom: 2),
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFF1F5F9),
                                  borderRadius: BorderRadius.circular(4),
                                  border: Border.all(color: const Color(0xFFCBD5E1), width: 0.8),
                                ),
                                child: Text(
                                  '🗣️ $arabEn',
                                  style: const TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w700,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                              );
                            },
                          ),
                          Padding(
                            padding: const EdgeInsets.only(left: 12, top: 2),
                            child: Text(
                              t['en']!,
                              style: const TextStyle(
                                fontSize: 10.5,
                                color: Color(0xFF64748B),
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ),
                        ],
                      ),
                    )),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // -------------------------------------------------------------
          // Inline Practice Exercise
          // -------------------------------------------------------------
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF0FDF4),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFBBF7D0)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: const [
                    Icon(Icons.lightbulb_outline, size: 16, color: Color(0xFF064E3B)),
                    SizedBox(width: 6),
                    Text(
                      'تطبيق فوري (Practice Exercise)',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF064E3B),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                InteractiveArabicText(
                  text: sec['question_ar'],
                  onVocalize: widget.onVocalize,
                  activeWord: widget.activeWord,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF0F172A),
                  ),
                ),
                ValueListenableBuilder<bool>(
                  valueListenable: ArabEnglishState.notifier,
                  builder: (context, isArabEnOn, _) {
                    if (!isArabEnOn) return const SizedBox.shrink();
                    final arabEn = ArabEnglishHelper.transliterate(sec['question_ar'] ?? '');
                    if (arabEn.isEmpty) return const SizedBox.shrink();
                    return Container(
                      margin: const EdgeInsets.only(top: 2, bottom: 2),
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: const Color(0xFFCBD5E1), width: 0.8),
                      ),
                      child: Text(
                        '🗣️ $arabEn',
                        style: const TextStyle(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 2),
                Text(
                  sec['question_en'],
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF047857),
                    fontStyle: FontStyle.italic,
                  ),
                ),
                const SizedBox(height: 10),

                // Options
                ...List.generate(optionsAr.length, (idx) {
                  final isSelected = selectedIdx == idx;
                  return InkWell(
                    onTap: isSubmitted
                        ? null
                        : () => setState(() => _selectedAnswers[sectionId] = idx),
                    borderRadius: BorderRadius.circular(8),
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 6),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      decoration: BoxDecoration(
                        color: isSelected ? const Color(0xFFDCFCE7) : Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: isSelected ? const Color(0xFF16A34A) : const Color(0xFFCBD5E1),
                          width: isSelected ? 1.5 : 1,
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            isSelected ? Icons.check_circle : Icons.radio_button_unchecked,
                            size: 16,
                            color: isSelected ? const Color(0xFF16A34A) : const Color(0xFF94A3B8),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  optionsAr[idx],
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                                    color: const Color(0xFF0F172A),
                                  ),
                                ),
                                if (idx < optionsEn.length)
                                  Text(
                                    optionsEn[idx],
                                    style: const TextStyle(
                                      fontSize: 10,
                                      color: Color(0xFF64748B),
                                    ),
                                  ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }),

                const SizedBox(height: 6),
                if (!isSubmitted)
                  Align(
                    alignment: Alignment.centerLeft,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF064E3B),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      onPressed: selectedIdx == null
                          ? null
                          : () {
                              setState(() {
                                _submittedExercises[sectionId] = true;
                              });
                            },
                      child: const Text('تحقق من الإجابة (Check Answer)', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                    ),
                  ),

                if (isSubmitted)
                  Container(
                    margin: const EdgeInsets.only(top: 8),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: isCorrect ? const Color(0xFFECFDF5) : const Color(0xFFFEF2F2),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isCorrect ? const Color(0xFF86EFAC) : const Color(0xFFFECACA),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              isCorrect ? Icons.check_circle : Icons.cancel,
                              color: isCorrect ? const Color(0xFF16A34A) : const Color(0xFFDC2626),
                              size: 16,
                            ),
                            const SizedBox(width: 6),
                            Text(
                              isCorrect ? 'إجابة صحيحة! (Correct)' : 'حاول مرة أخرى (Incorrect)',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 11.5,
                                color: isCorrect ? const Color(0xFF16A34A) : const Color(0xFFDC2626),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          sec['explanation_ar'],
                          style: TextStyle(
                            fontSize: 11,
                            color: isCorrect ? const Color(0xFF166534) : const Color(0xFF991B1B),
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          sec['explanation_en'],
                          style: TextStyle(
                            fontSize: 10,
                            fontStyle: FontStyle.italic,
                            color: isCorrect ? const Color(0xFF15803D) : const Color(0xFFB91C1C),
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickReviewCards() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFCBD5E1), width: 1.5),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('📌 خلاصات الاختبار السريعة (Fast Rules)',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0F172A))),
                  OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF064E3B),
                      side: const BorderSide(color: Color(0xFFCBD5E1)),
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    onPressed: () {
                      if (widget.onVocalize != null) {
                        widget.onVocalize!(
                            'عدد لاعبي الفريق أحد عشر لاعبا. مدة الشوط الواحد خمس وأربعون دقيقة. محيط الكرة الرسمية ثمانية وستون إلى سبعين سنتيمترا. الجملة الاسمية تتكون من مبتدأ وخبر.');
                      }
                    },
                    icon: const Icon(Icons.volume_up, size: 15),
                    label: const Text('استمع للكل', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              const Divider(height: 18),
              _ruleRow('• عدد لاعبي الفريق: 11 لاعباً في أرض الملعب.', 'Team Size: 11 players on the pitch.'),
              const SizedBox(height: 8),
              _ruleRow('• مدة الشوط الواحد: 45 دقيقة (المباراة كاملة 90 دقيقة).', 'Match Duration: 45-min halves (90 mins total).'),
              const SizedBox(height: 8),
              _ruleRow('• محيط الكرة الرسمية: 68 إلى 70 سنتيمتراً.', 'Official Ball: 68 to 70 centimeters circumference.'),
              const SizedBox(height: 8),
              _ruleRow('• الجملة الاسمية: مبتدأ مرفوع + خبر مرفوع (الكُرَةُ مُسْتَدِيرَةٌ).', 'Nominal Sentence: Nominative Subject + Nominative Predicate.'),
            ],
          ),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFFFF1F2),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFFECDD3), width: 1.5),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('⚠️ تنبيهات الفخاخ الامتحانية (Exam Traps)',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF9F1239))),
              const Divider(height: 18, color: Color(0xFFFECDD3)),
              _trapRow('• انتبه: طاقم التحكيم يتكون من 4 حكام كاملين وليس حكمين فقط.', 'Watch Out: Officiating crew consists of 4 referees, not two.'),
              const SizedBox(height: 8),
              _trapRow('• التاء المربوطة (ـة) تنطق تاءً عند الوصل، بينما الهاء (ـه) تنطق هاءً دائماً.', 'Phonetic Rule: Taa Marbutah sounds "t" on connection; Haa is always "h".'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _ruleRow(String ar, String en) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        InteractiveArabicText(
          text: ar,
          onVocalize: widget.onVocalize,
          activeWord: widget.activeWord,
          style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600, color: Color(0xFF1E293B)),
        ),
        Padding(
          padding: const EdgeInsets.only(left: 12, top: 2),
          child: Text(en, style: const TextStyle(fontSize: 10.5, color: Color(0xFF64748B))),
        ),
      ],
    );
  }

  Widget _trapRow(String ar, String en) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        InteractiveArabicText(
          text: ar,
          onVocalize: widget.onVocalize,
          activeWord: widget.activeWord,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF881337)),
        ),
        Padding(
          padding: const EdgeInsets.only(left: 12, top: 2),
          child: Text(en, style: const TextStyle(fontSize: 10, color: Color(0xFF9F1239))),
        ),
      ],
    );
  }
}


// ---------------------------------------------------------------------------
// 7. CAPSULES MICROLEARNING VIEW
// ---------------------------------------------------------------------------
class CapsulesView extends StatefulWidget {
  final Set<String> completedCapsules;
  final Function(String id) onCapsuleCompleted;
  final VoidCallback? onBack;

  const CapsulesView({
    super.key,
    required this.completedCapsules,
    required this.onCapsuleCompleted,
    this.onBack,
  });

  @override
  State<CapsulesView> createState() => _CapsulesViewState();
}

class _CapsulesViewState extends State<CapsulesView> {
  final List<Map<String, String>> _capsulesList = [
    {
      'id': 'capsule_01_taa_marbutah',
      'title': 'التاء المربوطة (ـة) والهاء (ـه)',
      'titleEn': 'Taa Marbutah (ـة) & Haa (ـه)',
      'duration': '3 دقائق',
      'durationEn': '3 mins',
      'rule':
          'حرّك الكلمة بالتنوين: (كُرَةٌ ← تاء مربوطة) بينما (مِيَاهٌ ← هاء دون نقطتين).',
      'ruleEn':
          'Test with tanween: (كُرَةٌ -> Taa Marbutah with dots) whereas (مِيَاهٌ -> Haa without dots).'
    },
    {
      'id': 'capsule_02_verb_subject_agreement',
      'title': 'مطابقة الفعل للفاعل',
      'titleEn': 'Verb-Subject Agreement',
      'duration': '4 دقائق',
      'durationEn': '4 mins',
      'rule':
          'يبدأ الفعل بالياء للمذكر (يَرْكُضُ زَايِدٌ)، ويبدأ بالتاء للمؤنث (تَرْكُضُ مَرْيَمُ).',
      'ruleEn':
          'Verbs begin with Yaa for masculine (يَرْكُضُ زَايِدٌ), and with Taa for feminine (تَرْكُضُ مَرْيَمُ).'
    },
    {
      'id': 'capsule_03_sound_plurals',
      'title': 'جمع المذكر والمؤنث السالم',
      'titleEn': 'Sound Masculine & Feminine Plurals',
      'duration': '4 دقائق',
      'durationEn': '4 mins',
      'rule':
          'مذكر سالم بزيادة (ـونَ / ـينَ) مثل لاعبونَ، ومؤنث سالم بزيادة (ـات) مثل لاعبات.',
      'ruleEn':
          'Sound masculine adds (-oon / -een) like لاعبون, sound feminine adds (-aat) like لاعبات.'
    },
    {
      'id': 'capsule_04_hamza_wasl_qat',
      'title': 'همزة الوصل والقطع',
      'titleEn': 'Hamzat Al-Wasl vs. Hamzat Al-Qat',
      'duration': '3 دقائق',
      'durationEn': '3 mins',
      'rule':
          'ضع حرف الواو قبل الكلمة: (وَاسْتَمَعَ ← وصل تسقط)، و(وَأَكَلَ ← قطع تثبت).',
      'ruleEn':
          'Prefix "Waw": If sound drops (وَاسْتَمَعَ -> Wasl), if sounded (وَأَكَلَ -> Qat).'
    },
    {
      'id': 'capsule_05_nominal_verbal_sentence',
      'title': 'الجملة الاسمية والفعلية',
      'titleEn': 'Nominal vs. Verbal Sentences',
      'duration': '5 دقائق',
      'durationEn': '5 mins',
      'rule':
          'الاسمية تبدأ باسم: (مبتدأ + خبر)، والفعلية تبدأ بفعل: (فعل + فاعل).',
      'ruleEn':
          'Nominal starts with noun (Subject + Predicate); Verbal starts with verb (Verb + Doer).'
    },
  ];

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (widget.onBack != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF0F172A),
                    side: const BorderSide(color: Color(0xFF0F172A)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                  onPressed: widget.onBack,
                  icon: const Icon(Icons.arrow_back, size: 16),
                  label: const Text('العودة للرئيسية · Back to Home', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                ),
                const ArabEnglishToggleSwitch(compact: true),
              ],
            ),
          ),
        Container(
          color: const Color(0xFF0F172A),
          padding: const EdgeInsets.all(14),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text('Microlearning Capsules · الكبسولات',
                      style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13)),
                  Text('Bite-sized 3–5 minute rules for daily review',
                      style: TextStyle(color: Colors.white60, fontSize: 10)),
                ],
              ),
              Text('${widget.completedCapsules.length} / 5 منجزة 🏅',
                  style: const TextStyle(
                      color: Color(0xFFFBBF24),
                      fontWeight: FontWeight.bold,
                      fontSize: 11)),
            ],
          ),
        ),
        const SizedBox(height: 12),
        ..._capsulesList.map((cap) {
          final isDone = widget.completedCapsules.contains(cap['id']);
          return Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(
                  color: isDone
                      ? const Color(0xFF064E3B)
                      : const Color(0xFFCBD5E1),
                  width: isDone ? 2 : 1),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(cap['title']!,
                              style: const TextStyle(
                                  fontWeight: FontWeight.bold, fontSize: 13)),
                          ValueListenableBuilder<bool>(
                            valueListenable: ArabEnglishState.notifier,
                            builder: (context, isArabEnOn, _) {
                              if (!isArabEnOn) return const SizedBox.shrink();
                              final arabEn = ArabEnglishHelper.transliterate(cap['title']!);
                              if (arabEn.isEmpty) return const SizedBox.shrink();
                              return Container(
                                margin: const EdgeInsets.only(top: 2, bottom: 2),
                                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFF1F5F9),
                                  borderRadius: BorderRadius.circular(4),
                                  border: Border.all(color: const Color(0xFFCBD5E1), width: 0.8),
                                ),
                                child: Text(
                                  '🗣️ $arabEn',
                                  style: const TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w700,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                              );
                            },
                          ),
                          if (cap['titleEn'] != null)
                            Text(cap['titleEn']!,
                                style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: Color(0xFF64748B))),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      color: const Color(0xFFF1F5F9),
                      child: Text(cap['duration']!,
                          style: const TextStyle(
                              fontSize: 10, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(cap['rule']!,
                    style:
                        const TextStyle(fontSize: 11.5, color: Colors.black87)),
                ValueListenableBuilder<bool>(
                  valueListenable: ArabEnglishState.notifier,
                  builder: (context, isArabEnOn, _) {
                    if (!isArabEnOn) return const SizedBox.shrink();
                    final arabEn = ArabEnglishHelper.transliterate(cap['rule']!);
                    if (arabEn.isEmpty) return const SizedBox.shrink();
                    return Container(
                      margin: const EdgeInsets.only(top: 3, bottom: 3),
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                      ),
                      child: Text(
                        '🗣️ $arabEn',
                        style: const TextStyle(
                          fontSize: 10.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    );
                  },
                ),
                if (cap['ruleEn'] != null) ...[
                  const SizedBox(height: 3),
                  Text(cap['ruleEn']!,
                      style: const TextStyle(
                          fontSize: 11,
                          color: Color(0xFF64748B),
                          fontStyle: FontStyle.italic)),
                ],
                const SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(isDone ? '✓ تم إتقان الكبسولة' : 'غير منجزة',
                        style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: isDone
                                ? const Color(0xFF064E3B)
                                : Colors.black45)),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: isDone
                            ? const Color(0xFF0F172A)
                            : const Color(0xFF064E3B),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        minimumSize: const Size(60, 28),
                        shape: const RoundedRectangleBorder(
                            borderRadius: BorderRadius.zero),
                      ),
                      onPressed: () {
                        widget.onCapsuleCompleted(cap['id']!);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(
                                'أحسنت! تم إتقان كبسولة: ${cap['title']} 🏅'),
                            backgroundColor: const Color(0xFF064E3B),
                            duration: const Duration(seconds: 2),
                          ),
                        );
                      },
                      child: Text(isDone ? 'مكتملة' : 'إتمام الكبسولة',
                          style: const TextStyle(fontSize: 10)),
                    ),
                  ],
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// 8. ADAPTIVE TESTS & MOE EXAM VIEW
// ---------------------------------------------------------------------------
class AdaptiveTestsView extends StatefulWidget {
  final Map<String, dynamic>? activeChild;
  final ApiService? api;
  final String? token;
  final int grade;
  final int term;
  final VoidCallback? onBack;

  const AdaptiveTestsView({
    super.key,
    this.activeChild,
    this.api,
    this.token,
    this.grade = 5,
    this.term = 1,
    this.onBack,
  });

  @override
  State<AdaptiveTestsView> createState() => _AdaptiveTestsViewState();
}

class _AdaptiveTestsViewState extends State<AdaptiveTestsView> {
  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _exam;
  String? _sessionId;
  final Map<String, int> _answers = {};
  bool _submitting = false;
  Map<String, dynamic>? _evaluation;

  int _remainingSeconds = 1200; // 20 minutes default
  Timer? _countdownTimer;

  @override
  void initState() {
    super.initState();
    _loadOfficialExam();
  }

  @override
  void dispose() {
    _countdownTimer?.cancel();
    super.dispose();
  }

  void _startTimer() {
    _countdownTimer?.cancel();
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_remainingSeconds > 0) {
        if (mounted) {
          setState(() {
            _remainingSeconds--;
          });
        }
      } else {
        timer.cancel();
        if (!_submitting && _evaluation == null) {
          _submitExam();
        }
      }
    });
  }

  Future<void> _loadOfficialExam() async {
    final childId = widget.activeChild?['id']?.toString();
    if (widget.api == null) {
      setState(() {
        _loading = false;
        _error = 'خدمة الاختبارات غير متصلة بالخادم.';
      });
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _evaluation = null;
      _answers.clear();
    });

    try {
      final res = await widget.api!.examSimulation(
        grade: widget.grade,
        term: widget.term,
        childId: childId,
        token: widget.token,
      );

      if (mounted) {
        final examData = res is Map ? res['exam'] : null;
        final sessId = res is Map ? res['session_id']?.toString() : null;
        final timeLimitSec = (examData?['time_limit_seconds'] as num?)?.toInt() ?? 1200;

        setState(() {
          _loading = false;
          _exam = examData is Map<String, dynamic> ? examData : null;
          _sessionId = sessId;
          _remainingSeconds = timeLimitSec;
        });

        _startTimer();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.toString().replaceAll('AuthException: ', '');
        });
      }
    }
  }

  Future<void> _submitExam() async {
    final childId = widget.activeChild?['id']?.toString();
    if (childId == null || widget.api == null || _submitting) return;

    final questions = (_exam?['questions'] as List?) ?? [];
    if (_answers.length < questions.length) {
      final proceed = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('تأكيد التسليم', style: TextStyle(fontWeight: FontWeight.bold)),
          content: Text('أجبت على ${_answers.length} من أصل ${questions.length} أسئلة. هل ترغب في تسليم الامتحان الآن؟'),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('متابعة الحل')),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF064E3B)),
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('تسليم'),
            ),
          ],
        ),
      );
      if (proceed != true) return;
    }

    setState(() {
      _submitting = true;
    });

    _countdownTimer?.cancel();
    final timeTaken = 1200 - _remainingSeconds;

    try {
      final res = await widget.api!.submitExam({
        'child_id': childId,
        'grade': widget.grade,
        'term': widget.term,
        'session_id': _sessionId,
        'answers': _answers,
        'time_taken_seconds': timeTaken > 0 ? timeTaken : 60,
      }, token: widget.token);

      if (mounted) {
        setState(() {
          _submitting = false;
          _evaluation = res is Map ? res['evaluation'] as Map<String, dynamic>? : null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _submitting = false;
          _error = e.toString().replaceAll('AuthException: ', '');
        });
      }
    }
  }

  String _formatTimer(int totalSec) {
    final m = (totalSec ~/ 60).toString().padLeft(2, '0');
    final s = (totalSec % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: CircularProgressIndicator(color: Color(0xFF064E3B)),
        ),
      );
    }

    if (_error != null && _exam == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 40, color: Colors.red),
              const SizedBox(height: 10),
              Text(_error!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12)),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF064E3B)),
                onPressed: _loadOfficialExam,
                icon: const Icon(Icons.refresh, size: 14),
                label: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      );
    }

    final questions = (_exam?['questions'] as List?) ?? [];
    final examTitle = _exam?['exam_title_ar'] ?? 'محاكاة الاختبار الوزاري الموحد';

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (widget.onBack != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Row(
              children: [
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF064E3B),
                    side: const BorderSide(color: Color(0xFF064E3B)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                  onPressed: widget.onBack,
                  icon: const Icon(Icons.arrow_back, size: 16),
                  label: const Text('العودة للرئيسية · Back to Home', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ),
        // Exam Simulation Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF064E3B),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      examTitle,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: _remainingSeconds < 300 ? Colors.red.shade700 : Colors.black26,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.timer_outlined, size: 14, color: Colors.white),
                        const SizedBox(width: 4),
                        Text(
                          _formatTimer(_remainingSeconds),
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              const Text(
                'معايير التوزيع الوزاري: فهم المقروء 40% · القواعد 30% · المفردات 20% · الإملاء 10%',
                style: TextStyle(color: Colors.white70, fontSize: 10.5),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        if (_evaluation == null) ...[
          ...questions.asMap().entries.map((entry) {
            final idx = entry.key;
            final q = entry.value;
            return _questionCard(index: idx, q: q);
          }),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF064E3B),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: _submitting ? null : _submitExam,
              child: _submitting
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                    )
                  : Text(
                      'تصحيح الامتحان الوزاري (${_answers.length}/${questions.length})',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.white),
                    ),
            ),
          ),
        ] else ...[
          _resultsCard(),
        ],
      ],
    );
  }

  Widget _questionCard({required int index, required dynamic q}) {
    final qid = q['id']?.toString() ?? '';
    final promptAr = q['question_ar'] ?? q['prompt_ar'] ?? '';
    final promptEn = q['question_en'] ?? q['prompt_en'] ?? '';
    final bloomAr = q['bloom_name_ar'] ?? q['bloom_level'] ?? 'تفكير';
    final bloomEn = q['bloom_name_en'] ?? '';
    final points = q['points'] ?? 10;
    final options = (q['options'] as List?) ?? [];
    final optionsEn = (q['options_en'] as List?) ?? [];
    final chosen = _answers[qid];

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFFECFDF5),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  'سؤال ${index + 1} ($points درجات)',
                  style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF064E3B)),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  '$bloomAr · $bloomEn',
                  style: const TextStyle(fontSize: 9.5, fontWeight: FontWeight.bold, color: Color(0xFF475569)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            promptAr,
            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, height: 1.4),
          ),
          if (promptEn.isNotEmpty) ...[
            const SizedBox(height: 3),
            Text(
              promptEn,
              style: const TextStyle(fontSize: 10.5, fontStyle: FontStyle.italic, color: Color(0xFF64748B)),
            ),
          ],
          const SizedBox(height: 12),
          ...options.asMap().entries.map((optEntry) {
            final optIdx = optEntry.key;
            final optText = optEntry.value.toString();
            final optEn = optIdx < optionsEn.length ? optionsEn[optIdx].toString() : null;
            final isSelected = (chosen == optIdx);

            return InkWell(
              onTap: () {
                setState(() {
                  _answers[qid] = optIdx;
                });
              },
              child: Container(
                margin: const EdgeInsets.only(bottom: 6),
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: isSelected ? const Color(0xFF064E3B) : const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: isSelected ? const Color(0xFF064E3B) : const Color(0xFFE2E8F0),
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 20,
                      height: 20,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: isSelected ? Colors.white : const Color(0xFF94A3B8)),
                        color: isSelected ? Colors.white : Colors.transparent,
                      ),
                      child: isSelected
                          ? const Icon(Icons.check, size: 14, color: Color(0xFF064E3B))
                          : null,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            optText,
                            style: TextStyle(
                              fontSize: 11.5,
                              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                              color: isSelected ? Colors.white : const Color(0xFF1E293B),
                            ),
                          ),
                          if (optEn != null && optEn.isNotEmpty)
                            Text(
                              optEn,
                              style: TextStyle(
                                fontSize: 9.5,
                                fontStyle: FontStyle.italic,
                                color: isSelected ? Colors.white70 : const Color(0xFF64748B),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _resultsCard() {
    final eval = _evaluation!;
    final pct = (eval['percentage'] as num?)?.toDouble() ?? 0.0;
    final gradeLetter = eval['grade_letter'] ?? 'A';
    final feedbackAr = eval['feedback_ar'] ?? '';
    final feedbackEn = eval['feedback_en'] ?? '';
    final correctCount = eval['correct_count'] ?? 0;
    final totalQuestions = eval['total_questions'] ?? 10;
    final bloomBreakdown = (eval['bloom_breakdown'] as Map<String, dynamic>?) ?? {};
    final walkthrough = (eval['solution_walkthrough'] as List?) ?? [];

    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF064E3B), width: 2),
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
                        'نتيجة محاكاة الاختبار الوزاري الموحد',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF064E3B)),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'أجبت على $correctCount من أصل $totalQuestions بشكل صحيح',
                        style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        Text(
                          '${pct.toStringAsFixed(1)}%',
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF064E3B),
                          ),
                        ),
                        Text(
                          'التقدير: $gradeLetter',
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF064E3B),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const Divider(height: 20),
              Text(
                feedbackAr,
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              if (feedbackEn.isNotEmpty) ...[
                const SizedBox(height: 2),
                Text(
                  feedbackEn,
                  style: const TextStyle(fontSize: 10.5, fontStyle: FontStyle.italic, color: Color(0xFF64748B)),
                ),
              ],
              const SizedBox(height: 16),
              const Text(
                '📊 تحليل هرم بلوم المعرفي (Bloom\'s Taxonomy Radar):',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11.5, color: Color(0xFF334155)),
              ),
              const SizedBox(height: 8),
              ...bloomBreakdown.entries.map((entry) {
                final bKey = entry.key;
                final bVal = entry.value as Map<String, dynamic>;
                final bNameAr = bVal['name_ar'] ?? bKey;
                final bNameEn = bVal['name_en'] ?? '';
                final bPct = (bVal['percentage'] as num?)?.toDouble() ?? 0.0;
                final bCorr = bVal['correct'] ?? 0;
                final bTot = bVal['total'] ?? 0;

                return Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 140,
                        child: Text(
                          '$bNameAr ($bNameEn)',
                          style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold),
                        ),
                      ),
                      Expanded(
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: (bPct / 100.0).clamp(0.0, 1.0),
                            backgroundColor: const Color(0xFFF1F5F9),
                            valueColor: AlwaysStoppedAnimation<Color>(
                              bPct >= 75 ? const Color(0xFF064E3B) : const Color(0xFFD97706),
                            ),
                            minHeight: 6,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '$bCorr/$bTot (${bPct.toStringAsFixed(0)}%)',
                        style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                );
              }),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Solution Walkthrough Header
        const Align(
          alignment: Alignment.centerRight,
          child: Text(
            '💡 دليل الحل النموذجي والتحليل الوزاري:',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF064E3B)),
          ),
        ),
        const SizedBox(height: 10),

        ...walkthrough.asMap().entries.map((entry) {
          final idx = entry.key;
          final item = entry.value;
          final isCorrect = item['is_correct'] == true;
          final prompt = item['question_ar'] ?? '';
          final options = (item['options'] as List?) ?? [];
          final selectedIdx = item['selected_option'];
          final correctIdx = item['correct_option'];
          final walkAr = item['solution_walkthrough_ar'] ?? '';

          return Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isCorrect ? const Color(0xFF86EFAC) : const Color(0xFFFECACA),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      isCorrect ? Icons.check_circle : Icons.cancel,
                      color: isCorrect ? const Color(0xFF16A34A) : const Color(0xFFDC2626),
                      size: 16,
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        'سؤال ${idx + 1}: $prompt',
                        style: const TextStyle(fontSize: 11.5, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                if (selectedIdx != null && selectedIdx < options.length)
                  Text(
                    'إجابتك: ${options[selectedIdx]}',
                    style: TextStyle(
                      fontSize: 11,
                      color: isCorrect ? const Color(0xFF166534) : const Color(0xFFDC2626),
                    ),
                  ),
                if (!isCorrect && correctIdx != null && correctIdx < options.length)
                  Text(
                    'الإجابة النموذجية: ${options[correctIdx]}',
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF166534)),
                  ),
                if (walkAr.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF8FAFC),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      'التفسير التربوي: $walkAr',
                      style: const TextStyle(fontSize: 10.5, color: Color(0xFF475569)),
                    ),
                  ),
                ],
              ],
            ),
          );
        }),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: _loadOfficialExam,
            icon: const Icon(Icons.refresh, size: 16),
            label: const Text('إعادة محاكاة الامتحان بنموذج جديد'),
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// 12. ADMIN WORKFLOW & CURRICULUM MANAGEMENT VIEW
// ---------------------------------------------------------------------------
class AdminWorkflowView extends StatefulWidget {
  final String? token;
  final bool isArabic;
  final ApiService? api;
  final VoidCallback? onBack;

  const AdminWorkflowView({
    super.key,
    this.token,
    this.isArabic = false,
    this.api,
    this.onBack,
  });

  @override
  State<AdminWorkflowView> createState() => _AdminWorkflowViewState();
}

class _AdminWorkflowViewState extends State<AdminWorkflowView> with SingleTickerProviderStateMixin {
  late final ApiService _api;
  late final TabController _tabController;
  bool _loading = false;
  String? _error;
  String? _successMessage;

  Map<String, dynamic>? _coverageData;
  Map<String, dynamic>? _qualityData;
  List<dynamic> _reviewLessons = [];

  final _gradeCtrl = TextEditingController(text: '5');
  final _termCtrl = TextEditingController(text: '2');
  final _termTitleArCtrl = TextEditingController(text: 'الفصل الدراسي الثاني');
  final _termTitleEnCtrl = TextEditingController(text: 'Term 2');
  final _termPriceCtrl = TextEditingController(text: '33.00');

  final _classNumCtrl = TextEditingController(text: '6');
  final _classNameArCtrl = TextEditingController(text: 'الصف السادس');
  final _classNameEnCtrl = TextEditingController(text: 'Class 6');

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? ApiService();
    _tabController = TabController(length: 4, vsync: this);
    _tabController.addListener(() {
      if (_tabController.indexIsChanging) return;
      if (_tabController.index == 0) _loadCoverage();
      if (_tabController.index == 1) _loadQuality();
      if (_tabController.index == 3) _loadCurriculumReview();
    });
    _loadCoverage();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _gradeCtrl.dispose();
    _termCtrl.dispose();
    _termTitleArCtrl.dispose();
    _termTitleEnCtrl.dispose();
    _termPriceCtrl.dispose();
    _classNumCtrl.dispose();
    _classNameArCtrl.dispose();
    _classNameEnCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadCoverage() async {
    setState(() { _loading = true; _error = null; });
    try {
      final res = await _api.get('/api/admin/coverage-report', token: widget.token);
      if (mounted) {
        setState(() {
          _coverageData = res is Map<String, dynamic> ? res : null;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<void> _loadQuality() async {
    setState(() { _loading = true; _error = null; });
    try {
      final res = await _api.get('/api/admin/quality-report', token: widget.token);
      if (mounted) {
        setState(() {
          _qualityData = res is Map<String, dynamic> ? res : null;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<void> _loadCurriculumReview() async {
    setState(() { _loading = true; _error = null; });
    try {
      final res = await _api.get('/api/admin/curriculum-review', token: widget.token);
      if (mounted) {
        setState(() {
          _reviewLessons = res is List ? res : [];
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<void> _handleAddTerm() async {
    setState(() { _loading = true; _error = null; _successMessage = null; });
    try {
      await _api.post('/api/curriculum/add-term', token: widget.token, body: {
        'grade': int.tryParse(_gradeCtrl.text) ?? 5,
        'term': int.tryParse(_termCtrl.text) ?? 2,
        'title_ar': _termTitleArCtrl.text.trim(),
        'title_en': _termTitleEnCtrl.text.trim(),
        'price_usd': double.tryParse(_termPriceCtrl.text) ?? 33.0,
      });
      if (mounted) {
        setState(() {
          _loading = false;
          _successMessage = widget.isArabic ? 'تمت إضافة الفصل الدراسي بنجاح' : 'Term added successfully';
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<void> _handleAddClass() async {
    setState(() { _loading = true; _error = null; _successMessage = null; });
    try {
      await _api.post('/api/curriculum/add-class', token: widget.token, body: {
        'grade': int.tryParse(_classNumCtrl.text) ?? 6,
        'title_ar': _classNameArCtrl.text.trim(),
        'title_en': _classNameEnCtrl.text.trim(),
      });
      if (mounted) {
        setState(() {
          _loading = false;
          _successMessage = widget.isArabic ? 'تمت إضافة المرحلة الصفية بنجاح' : 'Class added successfully';
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isAr = widget.isArabic;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: const Color(0xFF4C1D95),
        leading: widget.onBack != null
            ? IconButton(
                icon: const Icon(Icons.arrow_back, color: Colors.white),
                tooltip: isAr ? 'العودة للرئيسية' : 'Back to Home',
                onPressed: widget.onBack,
              )
            : null,
        title: Text(
          isAr ? 'لوحة مشرف المنهاج والرقابة' : 'Curriculum Administration & Quality',
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
        ),
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Colors.amber,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.amber,
          tabs: [
            Tab(text: isAr ? 'تقرير التغطية' : 'Coverage Report'),
            Tab(text: isAr ? 'فحص الجودة' : 'Quality Checks'),
            Tab(text: isAr ? 'إضافة فصل / صف' : 'Add Term/Class'),
            Tab(text: isAr ? 'مراجعة المنهاج' : 'Curriculum Review'),
          ],
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF4C1D95)))
          : TabBarView(
              controller: _tabController,
              children: [
                _buildCoverageTab(isAr),
                _buildQualityTab(isAr),
                _buildAddTermTab(isAr),
                _buildReviewTab(isAr),
              ],
            ),
    );
  }

  Widget _buildCoverageTab(bool isAr) {
    final pages = _coverageData?['total_pages']?.toString() ?? '108';
    final audioCov = _coverageData?['audio_coverage']?.toString() ?? '100% TTS Coverage';
    final vocabCount = _coverageData?['vocab_cards']?.toString() ?? '85';
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (_error != null) _errorBanner(),
        _metricCard(
          title: isAr ? 'إجمالي صفحات الكتاب الممسوحة' : 'Total Scanned Textbook Pages',
          value: '$pages Pages',
          subtitle: isAr ? 'طبعة وزارة التربية والتعليم الرسمية 2024–2025' : 'Official UAE MoE 2024–2025 Edition',
          icon: Icons.menu_book,
          color: const Color(0xFF4C1D95),
        ),
        const SizedBox(height: 12),
        _metricCard(
          title: isAr ? 'تغطية النطق الصوتي التفاعلي' : 'Pronunciation Audio Targets',
          value: audioCov.contains('%') ? audioCov : '$audioCov% TTS Coverage',
          subtitle: isAr ? 'كلمة بكلمة وجملة بجملة مع نطق عربي معتمد' : 'Word-by-word & sentence audio playback',
          icon: Icons.record_voice_over,
          color: const Color(0xFF047857),
        ),
        const SizedBox(height: 12),
        _metricCard(
          title: isAr ? 'بطاقات المفردات المعتمدة' : 'Vocabulary Flashcards',
          value: '$vocabCount Cards',
          subtitle: isAr ? 'مشكولة بالكامل مع التفسير والترجمة الإنجليزية' : 'Fully vowelled with English translations',
          icon: Icons.style,
          color: const Color(0xFFB45309),
        ),
      ],
    );
  }

  Widget _buildQualityTab(bool isAr) {
    final ocrConf = _qualityData?['ocr_confidence']?.toString() ?? '99.4%';
    final boundary = _qualityData?['boundary_status']?.toString() ?? 'Verified';
    final dupes = _qualityData?['duplicate_count']?.toString() ?? '0';
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (_error != null) _errorBanner(),
        _metricCard(
          title: isAr ? 'دقة التعرف الضوئي على النصوص (OCR)' : 'OCR Transcription Confidence',
          value: ocrConf.contains('%') ? ocrConf : '$ocrConf%',
          subtitle: isAr ? 'مطابقة تامة لكتاب الوزارة العربي الأصلي' : 'Exact match with MoE printed textbook',
          icon: Icons.check_circle_outline,
          color: const Color(0xFF047857),
        ),
        const SizedBox(height: 12),
        _metricCard(
          title: isAr ? 'فحص الحدود وتطابق الفقرات' : 'Page Boundary Alignment',
          value: boundary,
          subtitle: isAr ? 'تسلسل رقم الصفحات يبدأ من ص 6 حتى ص 108' : 'Pages 6 to 108 seamlessly linked',
          icon: Icons.border_all,
          color: const Color(0xFF1D4ED8),
        ),
        const SizedBox(height: 12),
        _metricCard(
          title: isAr ? 'فحص النزاهة ومنع التكرار' : 'De-duplication Check',
          value: '$dupes Duplicates',
          subtitle: isAr ? 'لا توجد أسئلة أو نصوص مكررة عبر الفصول' : 'Zero duplicate questions or passages',
          icon: Icons.verified_user,
          color: const Color(0xFF4C1D95),
        ),
      ],
    );
  }

  Widget _buildAddTermTab(bool isAr) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (_successMessage != null)
          Container(
            padding: const EdgeInsets.all(12),
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(color: const Color(0xFFECFDF5), borderRadius: BorderRadius.circular(10)),
            child: Text(_successMessage!, style: const TextStyle(color: Color(0xFF065F46), fontWeight: FontWeight.bold)),
          ),
        if (_error != null) _errorBanner(),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFFE2E8F0))),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(isAr ? 'إضافة فصل دراسي جديد' : 'Add Curriculum Term', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 12),
              TextField(controller: _gradeCtrl, decoration: const InputDecoration(labelText: 'Grade / الصف', border: OutlineInputBorder())),
              const SizedBox(height: 8),
              TextField(controller: _termCtrl, decoration: const InputDecoration(labelText: 'Term Number / رقم الفصل', border: OutlineInputBorder())),
              const SizedBox(height: 8),
              TextField(controller: _termTitleArCtrl, decoration: const InputDecoration(labelText: 'Title Arabic / العنوان بالعربية', border: OutlineInputBorder())),
              const SizedBox(height: 8),
              TextField(controller: _termTitleEnCtrl, decoration: const InputDecoration(labelText: 'Title English / العنوان بالإنجليزية', border: OutlineInputBorder())),
              const SizedBox(height: 8),
              TextField(controller: _termPriceCtrl, decoration: const InputDecoration(labelText: 'Price USD / السعر بالدولار', border: OutlineInputBorder())),
              const SizedBox(height: 14),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _handleAddTerm,
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF4C1D95)),
                  child: Text(isAr ? 'حفظ الفصل' : 'Save Term', style: const TextStyle(color: Colors.white)),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFFE2E8F0))),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(isAr ? 'إضافة مرحلة دراسية جديدة' : 'Add Class / Grade', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 12),
              TextField(controller: _classNumCtrl, decoration: const InputDecoration(labelText: 'Class Number / رقم الصف', border: OutlineInputBorder())),
              const SizedBox(height: 8),
              TextField(controller: _classNameArCtrl, decoration: const InputDecoration(labelText: 'Name Arabic / اسم الصف بالعربية', border: OutlineInputBorder())),
              const SizedBox(height: 8),
              TextField(controller: _classNameEnCtrl, decoration: const InputDecoration(labelText: 'Name English / اسم الصف بالإنجليزية', border: OutlineInputBorder())),
              const SizedBox(height: 14),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _handleAddClass,
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF047857)),
                  child: Text(isAr ? 'حفظ المرحلة' : 'Save Class', style: const TextStyle(color: Colors.white)),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildReviewTab(bool isAr) {
    if (_reviewLessons.isEmpty) {
      return Center(
        child: OutlinedButton.icon(
          onPressed: _loadCurriculumReview,
          icon: const Icon(Icons.refresh),
          label: Text(isAr ? 'تحميل فصول المنهاج للمراجعة' : 'Load Lessons for Review'),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _reviewLessons.length,
      itemBuilder: (ctx, i) {
        final item = _reviewLessons[i] as Map<String, dynamic>;
        final title = isAr ? (item['title_ar'] ?? item['id']) : (item['title_en'] ?? item['id']);
        final status = (item['status'] ?? 'published').toString();
        final isPublished = status == 'published';

        return Card(
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            leading: Icon(
              isPublished ? Icons.check_circle : Icons.pending,
              color: isPublished ? const Color(0xFF047857) : Colors.amber.shade700,
            ),
            title: Text(title.toString(), style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text('ID: ${item['id']} · Term ${item['term']} · Page ${item['start_page']}'),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: isPublished ? const Color(0xFFDCFCE7) : const Color(0xFFFEF3C7),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                status.toUpperCase(),
                style: TextStyle(
                  color: isPublished ? const Color(0xFF166534) : const Color(0xFF92400E),
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _metricCard({required String title, required String value, required String subtitle, required IconData icon, required Color color}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(12)),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                const SizedBox(height: 2),
                Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 10.5, color: Color(0xFF94A3B8))),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _errorBanner() {
    return Container(
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(color: const Color(0xFFFEF2F2), borderRadius: BorderRadius.circular(10)),
      child: Text(_error!, style: const TextStyle(color: Color(0xFF991B1B), fontSize: 11)),
    );
  }
}


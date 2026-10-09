import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../auth_service.dart';

class AuthDialog extends StatefulWidget {
  final Function(Map<String, dynamic>) onSuccess;
  final bool isAddChildOnly;
  final String? token;
  final bool isArabic;
  final ValueChanged<bool>? onLanguageChanged;
  final bool isFullScreen;
  const AuthDialog({
    super.key,
    required this.onSuccess,
    this.isAddChildOnly = false,
    this.token,
    this.isArabic = false,
    this.onLanguageChanged,
    this.isFullScreen = false,
  });

  @override
  State<AuthDialog> createState() => _AuthDialogState();
}

class _AuthDialogState extends State<AuthDialog> {
  final AuthService _auth = AuthService();
  late bool _isSignup;
  late bool _dialogIsArabic;
  bool _isForgotPassword = false;
  String _loginRole = 'parent'; // 'parent', 'student_pin', 'tutor'
  String _parentLoginMethod = 'password'; // 'password', 'otp'
  bool _obscurePassword = true;
  bool _obscurePin = true;
  bool _isSubmitting = false;
  bool _otpRequested = false;
  String? _authError;
  String? _receivedDebugOtp;

  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _studentPinCtrl = TextEditingController();
  final _otpCtrl = TextEditingController();
  final _childNameCtrl = TextEditingController();
  final _schoolCtrl = TextEditingController();
  int _grade = 5;
  String _gender = 'Boy';
  final int _age = 10;
  String _selectedAvatar = 'avatar_falcon';
  final String _curriculumStream = 'MoE / CBSE Arabic (Non-Arabs)';
  final _accessPinCtrl = TextEditingController();

  final List<Map<String, String>> _uaeAvatars = [
    {'id': 'avatar_falcon', 'nameEn': 'Falcon', 'nameAr': 'صقر', 'icon': '🦅'},
    {'id': 'avatar_gazelle', 'nameEn': 'Gazelle', 'nameAr': 'غزال', 'icon': '🦌'},
    {'id': 'avatar_oryx', 'nameEn': 'Oryx', 'nameAr': 'مها', 'icon': '🦬'},
    {'id': 'avatar_camel', 'nameEn': 'Camel', 'nameAr': 'جمل', 'icon': '🐪'},
    {'id': 'avatar_palm', 'nameEn': 'Palm', 'nameAr': 'نخلة', 'icon': '🌴'},
  ];

  @override
  void initState() {
    super.initState();
    _isSignup = widget.isAddChildOnly;
    _dialogIsArabic = widget.isArabic;
    _auth.getServerUrl().then((_) {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passCtrl.dispose();
    _studentPinCtrl.dispose();
    _otpCtrl.dispose();
    _childNameCtrl.dispose();
    _schoolCtrl.dispose();
    _accessPinCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_isSubmitting) return;
    setState(() {
      _isSubmitting = true;
      _authError = null;
    });
    try {
      if (widget.isAddChildOnly) {
        if (widget.token == null || widget.token!.isEmpty) {
          throw AuthException(_dialogIsArabic
              ? 'يرجى تسجيل الدخول أولاً لإضافة متعلم.'
              : 'Please sign in first to add a learner.');
        }
        if (_childNameCtrl.text.trim().isEmpty) {
          throw AuthException(_dialogIsArabic
              ? 'يرجى إدخال اسم المتعلم.'
              : 'Please enter child name.');
        }
        final childData = await _auth.addChild(widget.token!, {
          'name': _childNameCtrl.text.trim(),
          'gender': _gender,
          'age': _age,
          'school_name': _schoolCtrl.text.trim().isEmpty
              ? 'Sunrise International School, Abu Dhabi'
              : _schoolCtrl.text.trim(),
          'default_grade': _grade,
          'avatar_id': _selectedAvatar,
          'curriculum_stream': _curriculumStream,
          'access_pin': _accessPinCtrl.text.trim().isEmpty
              ? '1234'
              : _accessPinCtrl.text.trim(),
        });
        widget.onSuccess({'child': childData, 'active_child': childData});
        if (mounted && !widget.isFullScreen) Navigator.of(context).pop();
        return;
      }

      if (_isForgotPassword) {
        if (!_otpRequested) {
          if (_emailCtrl.text.trim().isEmpty) {
            throw AuthException(_dialogIsArabic
                ? 'يرجى إدخال البريد الإلكتروني.'
                : 'Please enter your email.');
          }
          await _auth.requestForgotPasswordOtp(_emailCtrl.text.trim());
          setState(() => _otpRequested = true);
          return;
        }
        if (_otpCtrl.text.trim().isEmpty || _passCtrl.text.isEmpty) {
          throw AuthException(_dialogIsArabic
              ? 'يرجى إدخال رمز التحقق وكلمة المرور الجديدة.'
              : 'Please enter recovery code and new password.');
        }
        await _auth.resetPassword(
          _emailCtrl.text.trim(),
          _otpCtrl.text.trim(),
          _passCtrl.text,
        );
        final data = await _auth.login(_emailCtrl.text.trim(), _passCtrl.text);
        widget.onSuccess(data);
        if (mounted && !widget.isFullScreen) Navigator.of(context).pop();
        return;
      }

      if (_loginRole == 'student_pin') {
        final data = await _auth.learnerLogin(
            _emailCtrl.text.trim(), _studentPinCtrl.text.trim());
        widget.onSuccess(data);
        if (mounted && !widget.isFullScreen) Navigator.of(context).pop();
        return;
      }

      if (_isSignup) {
        if (!_otpRequested) {
          final res = await _auth.requestSignupOtp(_emailCtrl.text.trim());
          final debugOtp = res['debug_otp']?.toString();
          if (debugOtp != null && debugOtp.isNotEmpty) {
            _otpCtrl.text = debugOtp;
          }
          setState(() {
            _otpRequested = true;
            _receivedDebugOtp = debugOtp;
            _authError = null;
          });
          return;
        }
        final data = await _auth.completeSignup({
          'email': _emailCtrl.text.trim(),
          'code': _otpCtrl.text.trim(),
          'password': _passCtrl.text,
          'child_name': _childNameCtrl.text.trim(),
          'child_gender': _gender,
          'child_age': _age,
          'child_school': _schoolCtrl.text.trim(),
          'child_grade': _grade,
          'avatar_id': _selectedAvatar,
          'curriculum_stream': _curriculumStream,
          'access_pin': _accessPinCtrl.text.trim(),
        });
        widget.onSuccess(data);
        if (mounted && !widget.isFullScreen) Navigator.of(context).pop();
        return;
      }

      Map<String, dynamic> data;
      if (_parentLoginMethod == 'otp' && _loginRole == 'parent') {
        if (!_otpRequested) {
          final res = await _auth.requestLoginOtp(_emailCtrl.text.trim());
          final debugOtp = res['debug_otp']?.toString();
          if (debugOtp != null && debugOtp.isNotEmpty) {
            _otpCtrl.text = debugOtp;
          }
          setState(() {
            _otpRequested = true;
            _receivedDebugOtp = debugOtp;
            _authError = null;
          });
          return;
        }
        data = await _auth.verifyLoginOtp(
            _emailCtrl.text.trim(), _otpCtrl.text.trim());
      } else {
        final inputEmail = _emailCtrl.text.trim();
        final inputPass = _passCtrl.text;
        if (inputEmail.isEmpty || inputPass.isEmpty) {
          throw AuthException(_dialogIsArabic
              ? 'يرجى إدخال البريد الإلكتروني وكلمة المرور.'
              : 'Please enter email and password.');
        }
        data = await _auth.login(inputEmail, inputPass);
      }
      widget.onSuccess(data);
      if (mounted && !widget.isFullScreen) Navigator.of(context).pop();
    } on AuthException catch (error) {
      if (mounted) setState(() => _authError = error.message);
    } catch (e) {
      if (mounted) {
        final errText = e.toString().replaceAll('Exception: ', '').replaceAll('AuthException: ', '');
        setState(() => _authError = _dialogIsArabic
            ? 'تعذر الاتصال بـ جسر ($apiBase): $errText'
            : 'Unable to connect to JISR ($apiBase): $errText');
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final innerContent = Padding(
      padding: EdgeInsets.all(widget.isFullScreen ? 24 : 20),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
              // Top Bar: Prominent Language Switcher & Close Button
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Flexible(
                    child: Container(
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F0FB),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                            color: const Color(0xFF6C5CE7).withValues(alpha: 0.25)),
                      ),
                      child: FittedBox(
                        fit: BoxFit.scaleDown,
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            InkWell(
                              borderRadius: const BorderRadius.horizontal(
                                  left: Radius.circular(20)),
                              onTap: () {
                                setState(() => _dialogIsArabic = false);
                                widget.onLanguageChanged?.call(false);
                              },
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: !_dialogIsArabic
                                      ? const Color(0xFF6C5CE7)
                                      : Colors.transparent,
                                  borderRadius: const BorderRadius.horizontal(
                                      left: Radius.circular(20)),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(Icons.language,
                                        size: 11,
                                        color: !_dialogIsArabic
                                            ? Colors.white
                                            : const Color(0xFF6C5CE7)),
                                    const SizedBox(width: 3),
                                    Text(
                                      'English',
                                      style: TextStyle(
                                        fontSize: 10.5,
                                        fontWeight: FontWeight.bold,
                                        color: !_dialogIsArabic
                                            ? Colors.white
                                            : const Color(0xFF6C5CE7),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            InkWell(
                              borderRadius: const BorderRadius.horizontal(
                                  right: Radius.circular(20)),
                              onTap: () {
                                setState(() => _dialogIsArabic = true);
                                widget.onLanguageChanged?.call(true);
                              },
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: _dialogIsArabic
                                      ? const Color(0xFF6C5CE7)
                                      : Colors.transparent,
                                  borderRadius: const BorderRadius.horizontal(
                                      right: Radius.circular(20)),
                                ),
                                child: Text(
                                  'العربية',
                                  style: TextStyle(
                                    fontSize: 10.5,
                                    fontWeight: FontWeight.bold,
                                    color: _dialogIsArabic
                                      ? Colors.white
                                      : const Color(0xFF6C5CE7),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.wifi_tethering, size: 18, color: Color(0xFF6C5CE7)),
                        tooltip: _dialogIsArabic ? 'إعدادات الخادم' : 'Server IP Settings',
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                        onPressed: _showServerSettingsDialog,
                      ),
                      const SizedBox(width: 6),
                      if (!widget.isFullScreen)
                        IconButton(
                          icon: const Icon(Icons.close, size: 20, color: Colors.black45),
                          onPressed: () => Navigator.of(context).pop(),
                          padding: EdgeInsets.zero,
                          constraints: const BoxConstraints(),
                        )
                      else
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF1F5F9),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.school, size: 12, color: Color(0xFF6C5CE7)),
                              const SizedBox(width: 4),
                              Text(
                                _dialogIsArabic ? 'بوابة المنهاج' : 'Curriculum Portal',
                                style: const TextStyle(
                                  fontSize: 10,
                                  color: Color(0xFF475569),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 10),

              // Robot Mascot & Branding Header
              Center(
                child: Column(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(18),
                      child: Image.asset(
                        'assets/icon.png',
                        width: 68,
                        height: 68,
                        fit: BoxFit.cover,
                        errorBuilder: (_, error, stack) => Container(
                          width: 68,
                          height: 68,
                          decoration: BoxDecoration(
                            color: const Color(0xFF58337E),
                            borderRadius: BorderRadius.circular(18),
                          ),
                          alignment: Alignment.center,
                          child: const Icon(
                            Icons.smart_toy_rounded,
                            size: 38,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: const [
                        Text(
                          'JISR ',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF58337E),
                          ),
                        ),
                        Text(
                          'جسر',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF6C5CE7),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _dialogIsArabic
                          ? 'الذكاء الاصطناعي لمناهج اللغة العربية'
                          : 'AI for Arabic Curriculum Learning',
                      style:
                          const TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              if (_isForgotPassword) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF3F0FF),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.arrow_back, color: Color(0xFF6C5CE7)),
                        onPressed: () => setState(() {
                          _isForgotPassword = false;
                          _otpRequested = false;
                          _authError = null;
                        }),
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _dialogIsArabic ? 'استعادة كلمة المرور' : 'Reset Password',
                              style: const TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1E1B4B),
                              ),
                            ),
                            Text(
                              _dialogIsArabic
                                  ? (_otpRequested
                                      ? 'أدخل الرمز وكلمة المرور الجديدة'
                                      : 'أدخل بريدك الإلكتروني لإرسال الرمز')
                                  : (_otpRequested
                                      ? 'Enter OTP & new password'
                                      : 'Enter email to receive OTP'),
                              style: const TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _emailCtrl,
                  enabled: !_otpRequested,
                  decoration: InputDecoration(
                    labelText: _dialogIsArabic ? 'البريد الإلكتروني' : 'Email Address',
                    prefixIcon: const Icon(Icons.email_outlined),
                  ),
                ),
                if (_otpRequested) ...[
                  if (_receivedDebugOtp != null) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFFECFDF5),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: const Color(0xFFA7F3D0)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.mark_email_read_rounded, color: Color(0xFF059669), size: 16),
                          const SizedBox(width: 6),
                          Expanded(
                            child: Text(
                              _dialogIsArabic
                                  ? 'رمز التحقق: $_receivedDebugOtp (تم ملؤه تلقائيًا)'
                                  : 'Verification Code: $_receivedDebugOtp (Auto-filled)',
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF065F46)),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 10),
                  TextField(
                    controller: _otpCtrl,
                    maxLength: 6,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                      letterSpacing: 4,
                    ),
                    decoration: InputDecoration(
                      labelText: _dialogIsArabic ? 'رمز التحقق (6 أرقام)' : '6-Digit OTP Code',
                      hintText: '123456',
                      counterText: '',
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _passCtrl,
                    obscureText: _obscurePassword,
                    decoration: InputDecoration(
                      labelText: _dialogIsArabic ? 'كلمة المرور الجديدة' : 'New Password',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(_obscurePassword ? Icons.visibility : Icons.visibility_off),
                        onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                      ),
                    ),
                  ),
                ],
              ] else ...[
                // Segmented Toggle: [تسجيل الدخول] [إنشاء حساب]
                if (!widget.isAddChildOnly)
                Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF3F0FF),
                    borderRadius: BorderRadius.circular(25),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: InkWell(
                          borderRadius: BorderRadius.circular(22),
                          onTap: () => setState(() => _isSignup = false),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            decoration: BoxDecoration(
                              color: !_isSignup
                                  ? const Color(0xFF6C5CE7)
                                  : Colors.transparent,
                              borderRadius: BorderRadius.circular(22),
                              boxShadow: !_isSignup
                                  ? [
                                      BoxShadow(
                                        color: const Color(0xFF6C5CE7)
                                            .withValues(alpha: 0.3),
                                        blurRadius: 6,
                                        offset: const Offset(0, 2),
                                      ),
                                    ]
                                  : null,
                            ),
                            alignment: Alignment.center,
                            child: Text(
                              _dialogIsArabic ? 'تسجيل الدخول' : 'Sign In',
                              style: TextStyle(
                                color: !_isSignup
                                    ? Colors.white
                                    : const Color(0xFF6C5CE7),
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ),
                      ),
                      Expanded(
                        child: InkWell(
                          borderRadius: BorderRadius.circular(22),
                          onTap: () => setState(() => _isSignup = true),
                          child: Container(
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            decoration: BoxDecoration(
                              color: _isSignup
                                  ? const Color(0xFF6C5CE7)
                                  : Colors.transparent,
                              borderRadius: BorderRadius.circular(22),
                              boxShadow: _isSignup
                                  ? [
                                      BoxShadow(
                                        color: const Color(0xFF6C5CE7)
                                            .withValues(alpha: 0.3),
                                        blurRadius: 6,
                                        offset: const Offset(0, 2),
                                      ),
                                    ]
                                  : null,
                            ),
                            alignment: Alignment.center,
                            child: Text(
                              _dialogIsArabic ? 'إنشاء حساب' : 'Create Account',
                              style: TextStyle(
                                color: _isSignup
                                    ? Colors.white
                                    : const Color(0xFF6C5CE7),
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 14),

              // Role Tabs in Login mode
              if (!_isSignup && !widget.isAddChildOnly) ...[
                Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8F9FE),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  padding: const EdgeInsets.all(3),
                  child: Row(
                    children: [
                      _buildRoleTab(
                          'parent', _dialogIsArabic ? 'ولي الأمر' : 'Parent'),
                      _buildRoleTab('student_pin',
                          _dialogIsArabic ? 'طالب' : 'Student'),
                      _buildRoleTab(
                          'tutor', _dialogIsArabic ? 'المعلم' : 'Tutor'),
                      _buildRoleTab(
                          'admin', _dialogIsArabic ? 'المسؤول' : 'Admin'),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
              ],

              // STUDENT PIN LOGIN FORM
              if (!_isSignup && _loginRole == 'student_pin') ...[
                Container(
                  padding: const EdgeInsets.all(10),
                  color: const Color(0xFFECFDF5),
                  child: Text(
                    _dialogIsArabic
                        ? 'دخول مباشر للمتعلم: أدخل البريد الإلكتروني لولي الأمر والرمز المكون من 4 أرقام.'
                        : 'Learner Direct Access: Enter your parent\'s email and your 4-digit PIN.',
                    style: const TextStyle(
                        fontSize: 11,
                        color: Color(0xFF064E3B),
                        fontWeight: FontWeight.w600),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _emailCtrl,
                  decoration: InputDecoration(
                    labelText: _dialogIsArabic
                        ? 'البريد الإلكتروني لولي الأمر'
                        : 'Parent Email ID',
                    hintText: 'parent@jisr.ae',
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _studentPinCtrl,
                  obscureText: _obscurePin,
                  maxLength: 4,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                      letterSpacing: 6),
                  decoration: InputDecoration(
                    labelText: _dialogIsArabic
                        ? 'رمز دخول الطالب (4 أرقام)'
                        : '4-Digit Student Access PIN',
                    hintText: '1234',
                    counterText: '',
                    suffixIcon: IconButton(
                      icon: Icon(
                          _obscurePin ? Icons.visibility : Icons.visibility_off),
                      onPressed: () =>
                          setState(() => _obscurePin = !_obscurePin),
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  _dialogIsArabic
                      ? 'استخدم رمز الدخول المحدد في حساب ولي الأمر.'
                      : 'Use the learner PIN provided by the parent account.',
                  style: const TextStyle(fontSize: 10, color: Colors.black54),
                ),
              ],

              // PARENT, TUTOR OR ADMIN LOGIN FORM
              if (!_isSignup &&
                  (_loginRole == 'parent' || _loginRole == 'tutor' || _loginRole == 'admin')) ...[
                if (_loginRole == 'parent') ...[
                  Row(
                    children: [
                      ChoiceChip(
                        label: Text(
                            _dialogIsArabic ? 'كلمة المرور' : 'Password',
                            style: const TextStyle(fontSize: 11)),
                        selected: _parentLoginMethod == 'password',
                        shape: const RoundedRectangleBorder(
                            borderRadius: BorderRadius.zero),
                        onSelected: (_) =>
                            setState(() => _parentLoginMethod = 'password'),
                      ),
                      const SizedBox(width: 6),
                      ChoiceChip(
                        label: Text(
                            _dialogIsArabic
                                ? 'رمز التحقق (OTP)'
                                : '6-Digit OTP Code',
                            style: const TextStyle(fontSize: 11)),
                        selected: _parentLoginMethod == 'otp',
                        shape: const RoundedRectangleBorder(
                            borderRadius: BorderRadius.zero),
                        onSelected: (_) =>
                            setState(() => _parentLoginMethod = 'otp'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                ],
                TextField(
                  controller: _emailCtrl,
                  keyboardType: TextInputType.emailAddress,
                  decoration: InputDecoration(
                    labelText: _loginRole == 'parent'
                        ? (_dialogIsArabic
                            ? 'البريد الإلكتروني لولي الأمر'
                            : 'Parent Email ID')
                        : (_loginRole == 'tutor'
                            ? (_dialogIsArabic
                                ? 'البريد الإلكتروني للمعلم'
                                : 'Tutor Email ID')
                            : (_dialogIsArabic
                                ? 'البريد الإلكتروني للمسؤول'
                                : 'Admin Email Address')),
                    hintText: null,
                    prefixIcon: _loginRole == 'admin'
                        ? const Icon(Icons.shield_outlined, size: 20)
                        : null,
                  ),
                ),
                const SizedBox(height: 10),
                if (_loginRole == 'admin' || _loginRole == 'tutor' || _parentLoginMethod == 'password') ...[
                  TextField(
                    controller: _passCtrl,
                    obscureText: _obscurePassword,
                    decoration: InputDecoration(
                      labelText: _loginRole == 'admin'
                          ? (_dialogIsArabic ? 'كلمة مرور المسؤول' : 'Admin Password')
                          : (_dialogIsArabic ? 'كلمة المرور' : 'Password'),
                      prefixIcon: _loginRole == 'admin'
                          ? const Icon(Icons.lock_outline, size: 20)
                          : null,
                      suffixIcon: IconButton(
                        icon: Icon(_obscurePassword
                            ? Icons.visibility
                            : Icons.visibility_off),
                        onPressed: () => setState(
                            () => _obscurePassword = !_obscurePassword),
                      ),
                    ),
                  ),
                  if (_loginRole == 'parent')
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () => setState(() {
                          _isForgotPassword = true;
                          _otpRequested = false;
                          _authError = null;
                        }),
                        child: Text(
                          _dialogIsArabic ? 'نسيت كلمة المرور؟' : 'Forgot Password?',
                          style: const TextStyle(
                            fontSize: 11,
                            color: Color(0xFF6C5CE7),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                ]
                else ...[
                  if (_receivedDebugOtp != null) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFFECFDF5),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: const Color(0xFFA7F3D0)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.mark_email_read_rounded, color: Color(0xFF059669), size: 16),
                          const SizedBox(width: 6),
                          Expanded(
                            child: Text(
                              _dialogIsArabic
                                  ? 'رمز تسجيل الدخول: $_receivedDebugOtp (تم ملؤه تلقائيًا)'
                                  : 'Login Code: $_receivedDebugOtp (Auto-filled)',
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF065F46)),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 10),
                  TextField(
                    controller: _otpCtrl,
                    maxLength: 6,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                        fontFamily: 'monospace',
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                        letterSpacing: 4),
                    decoration: InputDecoration(
                      labelText: _dialogIsArabic
                          ? 'رمز تسجيل الدخول (6 أرقام)'
                          : '6-Digit Login Code',
                      hintText: '123456',
                      counterText: '',
                    ),
                  ),
                ],
              ],

              // SIGNUP OR ADD CHILD PROFILE FORM
              if (_isSignup || widget.isAddChildOnly) ...[
                if (!widget.isAddChildOnly) ...[
                  TextField(
                    controller: _emailCtrl,
                    decoration: InputDecoration(
                      labelText: _dialogIsArabic
                          ? 'البريد الإلكتروني لولي الأمر'
                          : 'Parent Email ID',
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _passCtrl,
                    obscureText: _obscurePassword,
                    decoration: InputDecoration(
                      labelText: _dialogIsArabic
                          ? 'كلمة مرور ولي الأمر'
                          : 'Parent Password',
                      suffixIcon: IconButton(
                        icon: Icon(
                          _obscurePassword ? Icons.visibility : Icons.visibility_off,
                          size: 20,
                        ),
                        onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                ],
                Text(
                  _dialogIsArabic
                      ? 'اختر رمز الهوية التراثية:'
                      : 'Choose UAE Heritage Avatar:',
                  style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF064E3B)),
                ),
                const SizedBox(height: 6),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: _uaeAvatars.map((av) {
                    final isSel = _selectedAvatar == av['id'];
                    final avName = _dialogIsArabic
                        ? (av['nameAr'] ?? av['nameEn']!)
                        : (av['nameEn'] ?? av['nameAr']!);
                    return InkWell(
                      onTap: () => setState(() => _selectedAvatar = av['id']!),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: isSel ? const Color(0xFFECFDF5) : Colors.white,
                          border: Border.all(
                            color: isSel
                                ? const Color(0xFF064E3B)
                                : const Color(0xFFCBD5E1),
                            width: isSel ? 2 : 1,
                          ),
                        ),
                        child: Column(
                          children: [
                            Text(av['icon']!,
                                style: const TextStyle(fontSize: 20)),
                            const SizedBox(height: 2),
                            Text(avName,
                                style: TextStyle(
                                    fontSize: 9,
                                    fontWeight: isSel
                                        ? FontWeight.bold
                                        : FontWeight.normal)),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _childNameCtrl,
                  decoration: InputDecoration(
                    labelText: _dialogIsArabic
                        ? 'اسم الطالب الكامل'
                        : "Child's Full Name",
                    hintText: _dialogIsArabic
                        ? 'مثال: زايد النعيمي'
                        : 'e.g. Zayed Al-Nuaimi',
                  ),
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        initialValue: _gender,
                        decoration: InputDecoration(
                          labelText: _dialogIsArabic ? 'الجنس' : 'Gender',
                        ),
                        items: [
                          DropdownMenuItem(
                              value: 'Boy',
                              child: Text(
                                  _dialogIsArabic ? 'ولد' : 'Boy (ولد)')),
                          DropdownMenuItem(
                              value: 'Girl',
                              child: Text(
                                  _dialogIsArabic ? 'بنت' : 'Girl (بنت)')),
                        ],
                        onChanged: (v) => setState(() => _gender = v ?? 'Boy'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: DropdownButtonFormField<int>(
                        initialValue: _grade,
                        decoration: InputDecoration(
                          labelText:
                              _dialogIsArabic ? 'الصف الدراسي' : 'Grade (الصف الدراسي)',
                        ),
                        items: List.generate(12, (i) => i + 1).map((g) {
                          return DropdownMenuItem(
                              value: g,
                              child: Text(
                                  _dialogIsArabic ? 'الصف $g' : 'Grade $g'));
                        }).toList(),
                        onChanged: (v) => setState(() => _grade = v ?? 5),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _schoolCtrl,
                  decoration: InputDecoration(
                    labelText: _dialogIsArabic
                        ? 'اسم المدرسة (الإمارات)'
                        : 'School Name (UAE)',
                    hintText: _dialogIsArabic
                        ? 'مثال: مدرسة الشروق الخاصة، أبوظبي'
                        : 'e.g. Sunrise School, Abu Dhabi',
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: _accessPinCtrl,
                  maxLength: 4,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      letterSpacing: 4),
                  decoration: InputDecoration(
                    labelText: _dialogIsArabic
                        ? 'رمز الطالب السريع (4 أرقام)'
                        : 'Child 4-Digit PIN',
                    hintText: '1234',
                    counterText: '',
                  ),
                ),
              ],
            ],

              const SizedBox(height: 16),
              if (_authError != null) ...[
                Text(_authError!,
                    style: const TextStyle(
                        color: Colors.red, fontWeight: FontWeight.bold)),
                const SizedBox(height: 10),
              ],
              if (_otpRequested) ...[
                Text(
                  _dialogIsArabic
                      ? 'تم إرسال رمز التحقق. أدخله في الحقل أعلاه للمتابعة.'
                      : 'A verification code was sent. Enter it above to continue.',
                ),
                const SizedBox(height: 10),
              ],
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6C5CE7),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16)),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    elevation: 2,
                  ),
                  child: Text(
                    _isSubmitting
                        ? (_dialogIsArabic ? 'يرجى الانتظار…' : 'Please wait…')
                        : _isForgotPassword
                            ? (_otpRequested
                                ? (_dialogIsArabic
                                    ? 'تأكيد كلمة المرور الجديدة'
                                    : 'Confirm New Password')
                                : (_dialogIsArabic
                                    ? 'إرسال رمز التحقق'
                                    : 'Send Reset Code'))
                            : widget.isAddChildOnly
                                ? (_dialogIsArabic
                                    ? 'حفظ ملف الطالب'
                                    : 'Save Profile')
                                : _isSignup
                                    ? (_otpRequested
                                        ? (_dialogIsArabic
                                            ? 'إنشاء حساب جديد'
                                            : 'Create Account')
                                        : (_dialogIsArabic
                                            ? 'إرسال رمز التحقق'
                                            : 'Send verification code'))
                                    : _loginRole == 'student_pin'
                                        ? (_dialogIsArabic
                                            ? 'دخول الفصل بالرمز'
                                            : 'Enter Classroom')
                                        : _loginRole == 'admin'
                                            ? (_dialogIsArabic
                                                ? 'دخول المسؤول'
                                                : 'Admin Sign In')
                                            : (_parentLoginMethod == 'otp' &&
                                                    !_otpRequested
                                                ? (_dialogIsArabic
                                                    ? 'إرسال رمز تسجيل الدخول'
                                                    : 'Send sign-in code')
                                                : (_dialogIsArabic
                                                    ? 'تسجيل الدخول'
                                                    : 'Sign In')),
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ),
              ),

              if (_isForgotPassword) ...[
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => setState(() {
                    _isForgotPassword = false;
                    _otpRequested = false;
                    _authError = null;
                  }),
                  child: Text(
                    _dialogIsArabic ? 'العودة لتسجيل الدخول' : 'Back to Sign In',
                    style: const TextStyle(
                      color: Color(0xFF6C5CE7),
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],

              // Google Sign-In Circular Button
              if (!widget.isAddChildOnly && !_isForgotPassword) ...[
                const SizedBox(height: 14),
                Center(
                  child: InkWell(
                    borderRadius: BorderRadius.circular(25),
                    onTap: () => setState(() => _authError = _dialogIsArabic
                        ? 'تسجيل الدخول عبر Google غير متاح حالياً.'
                        : 'Google sign-in is not configured.'),
                    child: Container(
                      width: 46,
                      height: 46,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.05),
                            blurRadius: 4,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      alignment: Alignment.center,
                      child: const Text(
                        'G',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFF4285F4),
                        ),
                      ),
                    ),
                  ),
                ),
              ],

              // Inspirational Quote Banner
              Container(
                margin: const EdgeInsets.only(top: 16),
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF3C7),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFFFDE68A)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.lightbulb_outline,
                        size: 18, color: Color(0xFFD97706)),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _dialogIsArabic
                            ? 'النجاح يبدأ بخطوة، خلك مع جسر!'
                            : 'Success starts with a step, stay with JISR!',
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF92400E),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );

    if (widget.isFullScreen) {
      return Scaffold(
        backgroundColor: const Color(0xFFF8FAFC),
        body: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
              child: Container(
                constraints: const BoxConstraints(maxWidth: 480),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(28),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.08),
                      blurRadius: 24,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: innerContent,
              ),
            ),
          ),
        ),
      );
    }

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
      child: innerContent,
    );
  }

  Widget _buildRoleTab(String role, String label) {
    final isSelected = _loginRole == role;
    return Expanded(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () {
          setState(() {
            _loginRole = role;
            _authError = null;
            _emailCtrl.clear();
            _passCtrl.clear();
          });
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 7),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF6C5CE7) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: const Color(0xFF6C5CE7).withValues(alpha: 0.25),
                      blurRadius: 4,
                      offset: const Offset(0, 1),
                    ),
                  ]
                : null,
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              color: isSelected ? Colors.white : const Color(0xFF64748B),
              fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
              fontSize: 10,
            ),
          ),
        ),
      ),
    );
  }

  void _showServerSettingsDialog() {
    final srvCtrl = TextEditingController(text: apiBase);
    String? pingResult;
    bool isPinging = false;
    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlgState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
          title: Row(
            children: [
              const Icon(Icons.wifi_tethering, color: Color(0xFF6C5CE7), size: 22),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _dialogIsArabic ? 'إعدادات عنوان الخادم' : 'Server Connection Settings',
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          content: SizedBox(
            width: 360,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _dialogIsArabic
                      ? 'عنوان خادم JISR API (تأكد من اتصال الهاتف والكمبيوتر بنفس شبكة الواي فاي):'
                      : 'Backend server URL used to connect to JISR API:',
                  style: const TextStyle(fontSize: 11, color: Colors.black87),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: srvCtrl,
                  style: const TextStyle(fontSize: 12, fontFamily: 'monospace', fontWeight: FontWeight.bold),
                  decoration: InputDecoration(
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    isDense: true,
                    hintText: 'http://192.168.1.17:8000',
                  ),
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: [
                    ActionChip(
                      avatar: const Icon(Icons.bolt, size: 12, color: Color(0xFF6C5CE7)),
                      label: const Text('Tunnel (Live)', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                      backgroundColor: const Color(0xFFEEF2FF),
                      onPressed: () => setDlgState(() => srvCtrl.text = 'https://walker-courier-reservations-william.trycloudflare.com'),
                    ),
                    ActionChip(
                      avatar: const Icon(Icons.cloud_done, size: 12, color: Color(0xFF10B981)),
                      label: const Text('Production', style: TextStyle(fontSize: 10)),
                      backgroundColor: const Color(0xFFECFDF5),
                      onPressed: () => setDlgState(() => srvCtrl.text = 'https://api.jisr.ae'),
                    ),
                    ActionChip(
                      label: const Text('Wi-Fi (192.168.1.17)', style: TextStyle(fontSize: 10)),
                      onPressed: () => setDlgState(() => srvCtrl.text = 'http://192.168.1.17:8000'),
                    ),
                    ActionChip(
                      label: const Text('Emulator (10.0.2.2)', style: TextStyle(fontSize: 10)),
                      onPressed: () => setDlgState(() => srvCtrl.text = 'http://10.0.2.2:8000'),
                    ),
                  ],
                ),
                if (pingResult != null) ...[
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: pingResult!.startsWith('✓') ? const Color(0xFFECFDF5) : const Color(0xFFFEF2F2),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: pingResult!.startsWith('✓') ? const Color(0xFF10B981) : Colors.red.shade300,
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          pingResult!.startsWith('✓') ? Icons.check_circle : Icons.error,
                          size: 16,
                          color: pingResult!.startsWith('✓') ? const Color(0xFF047857) : Colors.red.shade700,
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            pingResult!,
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: pingResult!.startsWith('✓') ? const Color(0xFF047857) : Colors.red.shade700,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: isPinging
                  ? null
                  : () async {
                      setDlgState(() {
                        isPinging = true;
                        pingResult = null;
                      });
                      try {
                        final raw = srvCtrl.text.trim();
                        final uri = Uri.parse('$raw/api/health');
                        final res = await http.get(uri).timeout(const Duration(seconds: 4));
                        if (res.statusCode == 200) {
                          setDlgState(() => pingResult = '✓ ${_dialogIsArabic ? "متصل بنجاح! الخادم يعمل." : "Connected! Server online (200 OK)."}');
                        } else {
                          setDlgState(() => pingResult = '✗ Status ${res.statusCode}');
                        }
                      } catch (e) {
                        setDlgState(() => pingResult = '✗ ${_dialogIsArabic ? "فشل الاتصال: تأكد من تشغيل الخادم والاتصال بالواي فاي" : "Connection failed: Ensure server is running & phone on same Wi-Fi"}');
                      } finally {
                        setDlgState(() => isPinging = false);
                      }
                    },
              child: isPinging
                  ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                  : Text(_dialogIsArabic ? 'فحص الاتصال (Ping)' : 'Test Ping'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF6C5CE7)),
              onPressed: () async {
                final newUrl = srvCtrl.text.trim();
                await _auth.setCustomServer(newUrl);
                if (mounted) setState(() {});
                if (ctx.mounted) {
                  Navigator.of(ctx).pop();
                }
              },
              child: Text(_dialogIsArabic ? 'حفظ وتطبيق' : 'Save & Apply'),
            ),
          ],
        ),
      ),
    );
  }
}

import 'dart:convert';
import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../api_service.dart';

/// Ask Fahim homework helper (POST /api/ai/homework/scan and /check): a worksheet photo, PDF or
/// Word file is explained question by question with a hint; the student's own answer is checked.
/// Fahim never gives the answers: they stay on the server.

const String docxMime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';

/// Upload type for a picked file name.
String homeworkMimeFor(String name) {
  final lower = name.toLowerCase();
  if (lower.endsWith('.pdf')) return 'application/pdf';
  if (lower.endsWith('.docx')) return docxMime;
  if (lower.endsWith('.png')) return 'image/png';
  if (lower.endsWith('.webp')) return 'image/webp';
  return 'image/jpeg';
}

class HomeworkQuestion {
  final String number;
  final String questionAr;
  final String questionEn;
  final String asksEn;
  final String hintEn;
  final String hintAr;

  const HomeworkQuestion({
    required this.number,
    required this.questionAr,
    required this.questionEn,
    required this.asksEn,
    required this.hintEn,
    required this.hintAr,
  });

  factory HomeworkQuestion.fromJson(Map json) => HomeworkQuestion(
        number: json['number']?.toString() ?? '',
        questionAr: json['question_ar']?.toString() ?? '',
        questionEn: json['question_en']?.toString() ?? '',
        asksEn: json['asks_en']?.toString() ?? '',
        hintEn: json['hint_en']?.toString() ?? '',
        hintAr: json['hint_ar']?.toString() ?? '',
      );
}

class HomeworkScan {
  final String scanId;
  final bool isHomework;
  final String titleEn;
  final List<HomeworkQuestion> questions;

  const HomeworkScan(this.scanId, this.isHomework, this.titleEn, this.questions);

  factory HomeworkScan.fromJson(Map json) => HomeworkScan(
        json['scan_id']?.toString() ?? '',
        json['is_homework'] == true,
        json['title_en']?.toString() ?? '',
        [
          for (final q in (json['questions'] as List? ?? const []).whereType<Map>()) HomeworkQuestion.fromJson(q),
        ],
      );
}

class HomeworkHelperView extends StatefulWidget {
  final String? token;
  final String? childId;
  final void Function(String text)? onVocalize;
  final HomeworkScan? initialScan;

  const HomeworkHelperView({super.key, this.token, this.childId, this.onVocalize, this.initialScan});

  @override
  State<HomeworkHelperView> createState() => _HomeworkHelperViewState();
}

class _HomeworkHelperViewState extends State<HomeworkHelperView> {
  final ApiService _api = ApiService();
  final ImagePicker _picker = ImagePicker();
  HomeworkScan? _scan;
  bool _busy = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _scan = widget.initialScan;
  }

  Future<void> _upload(Uint8List bytes, String name) async {
    setState(() {
      _busy = true;
      _error = null;
      _scan = null;
    });
    try {
      final data = await _api.post('/api/ai/homework/scan',
          token: widget.token,
          timeout: const Duration(seconds: 120),
          body: {
            'file_base64': base64Encode(bytes),
            'mime_type': homeworkMimeFor(name),
            'file_name': name,
            'child_id': ?widget.childId,
          });
      if (mounted) setState(() => _scan = HomeworkScan.fromJson(data is Map ? data : const {}));
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _pickPhoto(ImageSource source) async {
    final photo = await _picker.pickImage(source: source, imageQuality: 85, maxWidth: 2000);
    if (photo == null) return;
    await _upload(await photo.readAsBytes(), photo.name.isNotEmpty ? photo.name : 'worksheet.jpg');
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: const ['pdf', 'docx', 'jpg', 'jpeg', 'png', 'webp'],
      withData: true,
    );
    final picked = result?.files.firstOrNull;
    if (picked == null) return;
    var bytes = picked.bytes;
    if (bytes == null && picked.path != null && !kIsWeb) bytes = await File(picked.path!).readAsBytes();
    if (bytes != null && bytes.isNotEmpty) await _upload(bytes, picked.name);
  }

  @override
  Widget build(BuildContext context) {
    final scan = _scan;
    return ListView(
      padding: const EdgeInsets.only(bottom: 16),
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFFF5F3FF),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0xFFDDD6FE)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Homework helper · مُسَاعِدُ الوَاجِبِ',
                  style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF4C1D95))),
              const SizedBox(height: 4),
              const Text(
                'Snap your worksheet or upload it. Fahim explains each question in English and gives a hint, '
                'then checks your own answer before you hand it in. Fahim never gives the answers.',
                style: TextStyle(fontSize: 12, color: Color(0xFF4C1D95)),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  FilledButton.icon(
                    onPressed: _busy ? null : () => _pickPhoto(ImageSource.camera),
                    icon: const Icon(Icons.photo_camera_rounded, size: 18),
                    label: const Text('Take a photo'),
                  ),
                  OutlinedButton.icon(
                    onPressed: _busy ? null : () => _pickPhoto(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library_outlined, size: 18),
                    label: const Text('Gallery'),
                  ),
                  OutlinedButton.icon(
                    onPressed: _busy ? null : _pickFile,
                    icon: const Icon(Icons.upload_file_rounded, size: 18),
                    label: const Text('PDF or Word'),
                  ),
                ],
              ),
            ],
          ),
        ),
        if (_busy)
          const Padding(
            padding: EdgeInsets.all(16),
            child: Row(children: [
              SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
              SizedBox(width: 10),
              Text('Fahim is reading your worksheet…'),
            ]),
          ),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.all(12),
            child: Text(_error!, style: TextStyle(color: Colors.red.shade800)),
          ),
        if (scan != null && !scan.isHomework)
          const Padding(
            padding: EdgeInsets.all(12),
            child: Text("Fahim couldn't find homework questions in this file. Try a clearer photo of the "
                'printed worksheet, taken straight on in good light.'),
          ),
        if (scan != null && scan.isHomework) ...[
          Padding(
            padding: const EdgeInsets.fromLTRB(4, 12, 4, 4),
            child: Text(
              '${scan.titleEn.isNotEmpty ? '${scan.titleEn} · ' : ''}${scan.questions.length} questions',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          for (final q in scan.questions)
            HomeworkQuestionCard(
              question: q,
              scanId: scan.scanId,
              token: widget.token,
              childId: widget.childId,
              onVocalize: widget.onVocalize,
            ),
        ],
      ],
    );
  }
}

class HomeworkQuestionCard extends StatefulWidget {
  final HomeworkQuestion question;
  final String scanId;
  final String? token;
  final String? childId;
  final void Function(String text)? onVocalize;

  const HomeworkQuestionCard({
    super.key,
    required this.question,
    required this.scanId,
    this.token,
    this.childId,
    this.onVocalize,
  });

  @override
  State<HomeworkQuestionCard> createState() => _HomeworkQuestionCardState();
}

class _HomeworkQuestionCardState extends State<HomeworkQuestionCard> {
  final ApiService _api = ApiService();
  final _answer = TextEditingController();
  bool _showHint = false;
  bool _checking = false;
  Map? _result;
  String? _error;

  static const _verdicts = {
    'correct': ('Correct! Ready to hand in', Color(0xFFECFDF5), Color(0xFF065F46)),
    'almost': ('Almost there: one small slip', Color(0xFFFFFBEB), Color(0xFF92400E)),
    'not_yet': ('Not yet: have another try', Color(0xFFF0F9FF), Color(0xFF075985)),
    'unreadable': ("Fahim couldn't read that clearly", Color(0xFFF8FAFC), Color(0xFF334155)),
  };

  @override
  void dispose() {
    _answer.dispose();
    super.dispose();
  }

  Future<void> _check({XFile? photo}) async {
    setState(() {
      _checking = true;
      _error = null;
      _result = null;
    });
    try {
      final body = <String, dynamic>{
        'scan_id': widget.scanId,
        'question_number': widget.question.number,
        'child_id': ?widget.childId,
      };
      if (photo != null) {
        body['answer_image_base64'] = base64Encode(await photo.readAsBytes());
        body['answer_image_type'] = homeworkMimeFor(photo.name);
      } else {
        body['answer_text'] = _answer.text.trim();
      }
      final data = await _api.post('/api/ai/homework/check',
          token: widget.token, body: body, timeout: const Duration(seconds: 60));
      if (mounted) setState(() => _result = data is Map ? data : null);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _checking = false);
    }
  }

  Future<void> _checkPhoto() async {
    final photo = await ImagePicker().pickImage(source: ImageSource.camera, imageQuality: 85, maxWidth: 1600);
    if (photo != null) await _check(photo: photo);
  }

  @override
  Widget build(BuildContext context) {
    final q = widget.question;
    final verdict = _verdicts[_result?['verdict']];
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: const BorderSide(color: Color(0xFFE2E8F0))),
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(color: const Color(0xFF6D28D9), borderRadius: BorderRadius.circular(8)),
                  child: Text('Q${q.number}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(q.questionAr,
                      textDirection: TextDirection.rtl,
                      style: const TextStyle(fontSize: 18, height: 1.8, fontWeight: FontWeight.w600)),
                ),
                if (widget.onVocalize != null)
                  IconButton(
                    tooltip: 'Listen',
                    icon: const Icon(Icons.volume_up_rounded),
                    onPressed: () => widget.onVocalize!(q.questionAr),
                  ),
              ],
            ),
            Text.rich(TextSpan(children: [
              const TextSpan(text: 'In English: ', style: TextStyle(fontWeight: FontWeight.bold)),
              TextSpan(text: q.questionEn),
            ])),
            const SizedBox(height: 2),
            Text.rich(TextSpan(children: [
              const TextSpan(text: 'What to do: ', style: TextStyle(fontWeight: FontWeight.bold)),
              TextSpan(text: q.asksEn),
            ])),
            const SizedBox(height: 6),
            if (_showHint)
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFFBEB),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFFCD34D)),
                ),
                child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                  const Text('💡 Hint', style: TextStyle(fontWeight: FontWeight.bold)),
                  Text(q.hintEn),
                  Text(q.hintAr, textDirection: TextDirection.rtl),
                ]),
              )
            else
              Align(
                alignment: Alignment.centerLeft,
                child: TextButton.icon(
                  onPressed: () => setState(() => _showHint = true),
                  icon: const Icon(Icons.lightbulb_outline_rounded, size: 18),
                  label: const Text('Stuck? Show a hint'),
                ),
              ),
            const SizedBox(height: 6),
            TextField(
              controller: _answer,
              textDirection: TextDirection.rtl,
              minLines: 1,
              maxLines: 3,
              onChanged: (_) => setState(() {}),
              decoration: const InputDecoration(
                labelText: 'Check my answer before I hand it in',
                hintText: 'اُكْتُبْ جَوَابَكَ هُنَا',
                border: OutlineInputBorder(),
                isDense: true,
              ),
            ),
            const SizedBox(height: 6),
            Wrap(spacing: 8, runSpacing: 6, children: [
              FilledButton(
                onPressed: _checking || _answer.text.trim().isEmpty ? null : () => _check(),
                child: _checking
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('Check'),
              ),
              OutlinedButton.icon(
                onPressed: _checking ? null : _checkPhoto,
                icon: const Icon(Icons.photo_camera_outlined, size: 18),
                label: const Text('Photo of my handwriting'),
              ),
            ]),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Text(_error!, style: TextStyle(color: Colors.red.shade800)),
              ),
            if (verdict != null)
              Container(
                margin: const EdgeInsets.only(top: 8),
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(color: verdict.$2, borderRadius: BorderRadius.circular(10)),
                child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                  Text(verdict.$1, style: TextStyle(fontWeight: FontWeight.bold, color: verdict.$3)),
                  if ((_result?['student_answer_read'] ?? '').toString().isNotEmpty)
                    Text('Fahim read: ${_result!['student_answer_read']}', style: TextStyle(fontSize: 12, color: verdict.$3)),
                  Text(_result?['feedback_en']?.toString() ?? '', style: TextStyle(color: verdict.$3)),
                  Text(_result?['feedback_ar']?.toString() ?? '',
                      textDirection: TextDirection.rtl, style: TextStyle(color: verdict.$3)),
                ]),
              ),
          ],
        ),
      ),
    );
  }
}

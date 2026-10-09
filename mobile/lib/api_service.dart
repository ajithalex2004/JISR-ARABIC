import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import 'auth_service.dart';

class _CacheEntry {
  final dynamic data;
  final DateTime timestamp;
  _CacheEntry(this.data) : timestamp = DateTime.now();

  bool get isExpired => DateTime.now().difference(timestamp) > const Duration(minutes: 5);
}

/// Shared mobile client for the same API contract consumed by the web app.
/// Screens should pass the current access token and use these methods instead
/// of assembling endpoint URLs independently.
class ApiService {
  final String? _baseUrl;
  final http.Client client;
  static final Map<String, _CacheEntry> _cache = {};

  ApiService({String? baseUrl, http.Client? client})
      : _baseUrl = baseUrl,
        client = client ?? http.Client();

  String get baseUrl => _baseUrl ?? apiBase;

  static void clearCache() => _cache.clear();

  Future<dynamic> get(String path, {String? token, Map<String, String>? query, Duration? timeout, bool useCache = false}) async {
    final cacheKey = '$path?${query?.entries.map((e) => '${e.key}=${e.value}').join('&') ?? ''}';
    if (useCache && _cache.containsKey(cacheKey)) {
      final entry = _cache[cacheKey]!;
      if (!entry.isExpired) {
        return entry.data;
      }
    }
    final res = await _request('GET', path, token: token, query: query, timeout: timeout);
    if (useCache && res != null) {
      _cache[cacheKey] = _CacheEntry(res);
    }
    return res;
  }

  Future<dynamic> post(String path, {String? token, Map<String, dynamic>? body, Duration? timeout}) =>
      _request('POST', path, token: token, body: body, timeout: timeout);

  Future<dynamic> put(String path, {String? token, Map<String, dynamic>? body, Duration? timeout}) =>
      _request('PUT', path, token: token, body: body, timeout: timeout);

  Future<dynamic> delete(String path, {String? token, Duration? timeout}) =>
      _request('DELETE', path, token: token, timeout: timeout);

  Future<dynamic> _request(String method, String path, {String? token,
      Map<String, String>? query, Map<String, dynamic>? body, Duration? timeout}) async {
    try {
      return await _executeMethod(baseUrl, method, path, token: token, query: query, body: body, timeout: timeout);
    } catch (e) {
      if (e is AuthException) {
        rethrow;
      }
      if (e is TimeoutException) {
        throw const AuthException(
          'استغرقت المعالجة وقتاً أطول من المتوقع أثناء الاتصال. يرجى التحقق من سرعة الشبكة وإعادة المحاولة.\nRequest timed out. Please check your network and retry.',
        );
      }
      if (!kReleaseMode) {
        final alternateHost = baseUrl.contains('10.0.2.2')
            ? AuthService.fallbackLanHost
            : AuthService.emulatorHost;
        if (baseUrl != alternateHost) {
          try {
            final res = await _executeMethod(alternateHost, method, path, token: token, query: query, body: body, timeout: timeout);
            apiBase = alternateHost;
            return res;
          } catch (_) {}
        }
      }
      rethrow;
    }
  }

  Future<dynamic> _executeMethod(String host, String method, String path, {String? token,
      Map<String, String>? query, Map<String, dynamic>? body, Duration? timeout}) async {
    if (kReleaseMode && !host.startsWith('https://')) {
      throw const AuthException('Cleartext HTTP connections are prohibited in production release builds.');
    }
    final effectiveTimeout = timeout ?? const Duration(seconds: 30);
    final uri = Uri.parse('$host$path').replace(queryParameters: query);
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (token != null && token.isNotEmpty) headers['Authorization'] = 'Bearer $token';
    late http.Response response;
    switch (method) {
      case 'GET': response = await client.get(uri, headers: headers).timeout(effectiveTimeout); break;
      case 'POST': response = await client.post(uri, headers: headers, body: jsonEncode(body ?? {})).timeout(effectiveTimeout); break;
      case 'PUT': response = await client.put(uri, headers: headers, body: jsonEncode(body ?? {})).timeout(effectiveTimeout); break;
      case 'DELETE': response = await client.delete(uri, headers: headers).timeout(effectiveTimeout); break;
      default: throw const AuthException('Unsupported API method');
    }
    dynamic decoded;
    try { decoded = response.body.isEmpty ? <String, dynamic>{} : jsonDecode(utf8.decode(response.bodyBytes)); }
    catch (_) { decoded = {'detail': response.body}; }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      final detail = decoded is Map ? decoded['detail'] : null;
      throw AuthException(detail?.toString() ?? 'Request failed (${response.statusCode})');
    }
    return decoded;
  }

  Future<dynamic> grades({String? token}) => get('/api/curriculum/grades', token: token, useCache: true);
  Future<dynamic> terms(int grade, {String? childId, String? token}) => get('/api/curriculum/terms', token: token, query: {'grade': '$grade', 'child_id': ?childId}, useCache: true);
  Future<dynamic> lessons({int? grade, int? term, String? childId, String? token}) => get('/api/curriculum/lessons', token: token, query: {
    if (grade != null) 'grade': '$grade', if (term != null) 'term': '$term', 'child_id': ?childId,
  }, useCache: true);
  Future<dynamic> lesson(String id, {String? childId, String? token}) => get('/api/curriculum/lesson/$id', token: token, query: {'child_id': ?childId}, useCache: true);
  Future<dynamic> submitAttempt(Map<String, dynamic> body, {String? token}) => post('/api/attempts/submit', token: token, body: body);
  Future<dynamic> capsules({String? childId, String? token}) => get('/api/modules/capsules', token: token, query: {'child_id': ?childId}, useCache: true);
  Future<dynamic> completeCapsule(String id, Map<String, dynamic> body, {String? token}) => post('/api/modules/capsules/$id/complete', token: token, body: body);
  Future<dynamic> adaptiveAssessment(String lessonId, {String? childId, String? token}) => get('/api/modules/assessments/adaptive/$lessonId', token: token, query: {'child_id': ?childId});
  Future<dynamic> examSimulation({int grade = 5, int term = 1, String? childId, String? token}) => get('/api/modules/assessments/exam-simulation/$grade/$term', token: token, query: {'child_id': ?childId});
  Future<dynamic> submitExam(Map<String, dynamic> body, {String? token}) => post('/api/modules/assessments/submit-exam', token: token, body: body);
  Future<dynamic> heatmap(String childId, {String? token}) => get('/api/mastery/heatmap/$childId', token: token);
  Future<dynamic> gapReviewSession(String childId, {String? token}) => get('/api/mastery/review-session/$childId', token: token);
  Future<dynamic> recordDrill(Map<String, dynamic> body, {String? token}) => post('/api/mastery/record-drill', token: token, body: body);
  Future<dynamic> parentDashboard(String childId, {String? token}) => get('/api/parent/dashboard/$childId', token: token);
  Future<dynamic> gamificationProfile(String childId, {String? token}) => get('/api/gamification/profile/$childId', token: token);
  Future<dynamic> leaderboard({String? token, int? grade, String? stream}) => get('/api/gamification/leaderboard', token: token, query: {if (grade != null) 'grade': '$grade', 'stream': ?stream});
  Future<dynamic> askFahim(Map<String, dynamic> body, {String? token}) => post('/api/ai/ask-fahim', token: token, body: body, timeout: const Duration(seconds: 90));
  Future<dynamic> solveQuestionPaper(Map<String, dynamic> body, {String? token}) => post('/api/ai/solve-question-paper', token: token, body: body, timeout: const Duration(seconds: 120));
  Future<dynamic> evaluateSpeech(Map<String, dynamic> body, {String? token}) => post('/api/audio/evaluate-speech', token: token, body: body, timeout: const Duration(seconds: 45));
  Future<dynamic> submitTutorWork(Map<String, dynamic> body, {String? token}) => post('/api/tutor/submit', token: token, body: body);
  Future<dynamic> tutorQueue({String status = 'pending', String? token}) => get('/api/tutor/queue', token: token, query: {'status_filter': status});
  Future<dynamic> childSubmissions(String childId, {String? token}) => get('/api/tutor/submissions/$childId', token: token);
  Future<dynamic> listReceipts(String childId, {String? token}) => get('/api/payments/receipts', query: {'child_id': childId}, token: token);
  Future<dynamic> getInvoice(String receiptNumber, {String? token}) => get('/api/payments/invoice/$receiptNumber', token: token);
  Future<dynamic> submitFeedback(Map<String, dynamic> body, {String? token}) => post('/api/feedback', token: token, body: body, timeout: const Duration(seconds: 30));
  Future<dynamic> listFeedback({String? token}) => get('/api/feedback', token: token);
}

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

String get apiBase => AuthService.activeApiBase;
set apiBase(String val) => AuthService.activeApiBase = val;

class AuthException implements Exception {
  final String message;
  const AuthException(this.message);
  @override
  String toString() => message;
}

class AuthService {
  static const _tokenKey = 'fahim_access_token';
  static const _serverKey = 'fahim_custom_server_url';

  static const String productionApiBase = 'https://api.jisr.ae';
  static const String fallbackLanHost = 'http://192.168.1.17:8000';
  static const String emulatorHost = 'http://10.0.2.2:8000';

  static String resolveInitialApiBase() {
    const configured = String.fromEnvironment('FAHIM_API_BASE');
    if (kReleaseMode) {
      if (configured.isNotEmpty && configured.startsWith('https://')) {
        return configured;
      }
      return productionApiBase;
    }
    if (configured.isNotEmpty) return configured;
    return emulatorHost;
  }

  static String activeApiBase = resolveInitialApiBase();

  final FlutterSecureStorage storage;
  final http.Client client;

  AuthService({FlutterSecureStorage? storage, http.Client? client})
      : storage = storage ?? const FlutterSecureStorage(),
        client = client ?? http.Client();

  Future<void> setCustomServer(String url) async {
    if (kReleaseMode) {
      throw const AuthException('Custom server configuration is disabled in production release builds.');
    }
    final clean = url.trim().replaceAll(RegExp(r'/+$'), '');
    activeApiBase = clean;
    await storage.write(key: _serverKey, value: clean);
  }

  Future<String> getServerUrl() async {
    if (kReleaseMode) {
      activeApiBase = resolveInitialApiBase();
      return activeApiBase;
    }
    final savedServer = await storage.read(key: _serverKey);
    if (savedServer != null && savedServer.trim().isNotEmpty) {
      if (savedServer.contains('10.0.2.2')) {
        await storage.delete(key: _serverKey);
        activeApiBase = fallbackLanHost;
      } else {
        activeApiBase = savedServer.trim();
      }
    }
    return activeApiBase;
  }

  Future<Map<String, dynamic>> login(String email, String password) =>
      _authenticate('/api/auth/login', {'email': email.trim().toLowerCase(), 'password': password});

  Future<Map<String, dynamic>> requestLoginOtp(String email) =>
      _request('/api/auth/login-otp', body: {'email': email.trim().toLowerCase()});

  Future<Map<String, dynamic>> requestSignupOtp(String email) =>
      _request('/api/auth/signup', body: {'email': email.trim().toLowerCase()});

  Future<Map<String, dynamic>> forgotPassword(String email) =>
      _request('/api/auth/forgot-password', body: {'email': email.trim().toLowerCase()});

  Future<Map<String, dynamic>> completeSignup(Map<String, dynamic> enrollment) =>
      _authenticate('/api/auth/create-password-enroll', enrollment);

  Future<Map<String, dynamic>> verifyLoginOtp(String email, String code) =>
      _authenticate('/api/auth/verify-login-otp', {'email': email.trim().toLowerCase(), 'code': code.trim()});

  Future<Map<String, dynamic>> learnerLogin(String parentEmail, String pin) =>
      _authenticate('/api/auth/student-pin-login', {'parent_email': parentEmail.trim().toLowerCase(), 'pin': pin.trim()});

  Future<Map<String, dynamic>> switchChild(String token, String childId) async {
    final data = await _authenticateWithToken('/api/auth/switch-child/$childId', token);
    await storage.write(key: 'active_child_id', value: childId);
    return data;
  }

  Future<Map<String, dynamic>?> restore() async {
    await getServerUrl();
    final token = await storage.read(key: _tokenKey);
    if (token == null) return null;
    try {
      final user = await _request('/api/auth/me', token: token, method: 'GET');
      final children = List<Map<String, dynamic>>.from(
        (user['children'] as List? ?? []).map((e) => Map<String, dynamic>.from(e)),
      );
      final savedChildId = await storage.read(key: 'active_child_id');
      Map<String, dynamic>? activeChild;
      if (savedChildId != null && children.isNotEmpty) {
        activeChild = children.firstWhere(
          (c) => c['id']?.toString() == savedChildId,
          orElse: () => children.first,
        );
      } else if (children.isNotEmpty) {
        activeChild = children.first;
      }
      return {'access_token': token, 'user': user, 'active_child': activeChild};
    } on AuthException {
      await storage.delete(key: _tokenKey);
      await storage.delete(key: 'active_child_id');
      return null;
    }
  }

  Future<void> logout(String? token) async {
    try {
      if (token != null) await _request('/api/auth/logout', token: token);
    } finally {
      await storage.delete(key: _tokenKey);
      await storage.delete(key: 'active_child_id');
    }
  }

  Future<void> requestForgotPasswordOtp(String email) async {
    await _request('/api/auth/forgot-password', body: {'email': email.trim().toLowerCase()});
  }

  Future<Map<String, dynamic>> resetPassword(String email, String code, String newPassword) async {
    return await _request('/api/auth/reset-password', body: {
      'email': email.trim().toLowerCase(),
      'code': code.trim(),
      'new_password': newPassword,
    });
  }

  Future<Map<String, dynamic>> addChild(String token, Map<String, dynamic> data) async {
    return await _request('/api/auth/children', body: data, token: token);
  }

  Future<void> deleteAccount(String token) async {
    try {
      await _request('/api/auth/account', token: token, method: 'DELETE');
    } finally {
      await storage.delete(key: _tokenKey);
      await storage.delete(key: 'active_child_id');
    }
  }

  Future<Map<String, dynamic>> _authenticate(String path, Map<String, dynamic> body) async {
    final data = await _request(path, body: body);
    final token = data['access_token'] as String?;
    if (token == null || token.isEmpty) throw const AuthException('The server did not issue a session.');
    await storage.write(key: _tokenKey, value: token);
    return data;
  }

  Future<Map<String, dynamic>> _authenticateWithToken(String path, String token) async {
    final data = await _request(path, token: token);
    final nextToken = data['access_token'] as String?;
    if (nextToken == null) throw const AuthException('The server did not issue a session.');
    await storage.write(key: _tokenKey, value: nextToken);
    return data;
  }

  Future<Map<String, dynamic>> _request(String path, {Map<String, dynamic>? body, String? token, String method = 'POST'}) async {
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (token != null) headers['Authorization'] = 'Bearer $token';

    try {
      return await _executeHttp(activeApiBase, path, headers, body, method);
    } catch (e) {
      if (e is AuthException) {
        rethrow;
      }
      if (!kReleaseMode) {
        final alternateHost = activeApiBase.contains('10.0.2.2') ? fallbackLanHost : emulatorHost;
        if (activeApiBase != alternateHost) {
          try {
            final res = await _executeHttp(alternateHost, path, headers, body, method);
            activeApiBase = alternateHost;
            await storage.write(key: _serverKey, value: alternateHost);
            return res;
          } catch (_) {}
        }
      }
      rethrow;
    }
  }

  Future<Map<String, dynamic>> _executeHttp(String host, String path, Map<String, String> headers, Map<String, dynamic>? body, String method) async {
    if (kReleaseMode && !host.startsWith('https://')) {
      throw const AuthException('Cleartext HTTP connections are prohibited in production release builds.');
    }
    final uri = Uri.parse('$host$path');
    final response = switch (method) {
      'GET' => await client.get(uri, headers: headers).timeout(const Duration(seconds: 15)),
      'DELETE' => await client.delete(uri, headers: headers).timeout(const Duration(seconds: 15)),
      _ => await client.post(uri, headers: headers, body: body == null ? null : jsonEncode(body)).timeout(const Duration(seconds: 15)),
    };
    final decoded = response.bodyBytes.isEmpty ? <String, dynamic>{} : jsonDecode(utf8.decode(response.bodyBytes));
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw AuthException(decoded is Map ? (decoded['detail']?.toString() ?? 'Authentication failed.') : 'Authentication failed.');
    }
    return Map<String, dynamic>.from(decoded as Map);
  }
}

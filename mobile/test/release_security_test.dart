import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/auth_service.dart';
import 'package:mobile/api_service.dart';

void main() {
  group('Release Endpoint & Security Pinning', () {
    test('Production API base points to enterprise domain', () {
      expect(AuthService.productionApiBase, 'https://api.jisr.ae');
      expect(AuthService.productionApiBase.startsWith('https://'), isTrue);
    });

    test('Initial API base resolves correctly', () {
      final base = AuthService.resolveInitialApiBase();
      expect(base, isNotEmpty);
      // When kReleaseMode is false in test runner, fallback or default is handled cleanly
      expect(base.startsWith('http://') || base.startsWith('https://'), isTrue);
    });

    test('ApiService baseUrl defaults to activeApiBase', () {
      final api = ApiService();
      expect(api.baseUrl, AuthService.activeApiBase);
    });
  });
}

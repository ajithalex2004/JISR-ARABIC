import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/store_purchase.dart';

void main() {
  test('Buy in a store build opens the website payment screen for that class and term', () {
    final uri = webPurchaseUri(4, 2);
    expect(uri.scheme, 'https');
    expect(uri.host, 'app.jisrarabic.com');
    expect(uri.path, '/');
    expect(uri.queryParameters, {'buy': '1', 'grade': '4', 'term': '2'});
    expect(webPurchaseUri(1, 1, base: 'https://example.test/').toString(),
        'https://example.test/?buy=1&grade=1&term=1');
  });

  test('the privacy policy link points at the public page', () {
    expect(privacyPolicyUri().toString(), 'https://app.jisrarabic.com/privacy');
  });

  test('test and direct-install builds keep the in-app checkout', () {
    // The release workflow sets STORE_BUILD=true only for the .aab and iOS builds.
    expect(kStoreBuild, isFalse);
    expect(kStorePurchase, 'web');
  });
}

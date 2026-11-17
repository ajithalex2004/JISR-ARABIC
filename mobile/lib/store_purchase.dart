import 'package:url_launcher/url_launcher.dart';

/// Store builds (Google Play, App Store) take no payments inside the app: both stores require their
/// own billing for digital content bought in an app. The release workflow builds them with
///   --dart-define=STORE_BUILD=true
/// and the direct-install APK keeps the in-app checkout.
///
/// What "Buy" does in a store build (--dart-define=STORE_PURCHASE=...):
///   web  (default) opens the website's payment page for that class and term, in the browser;
///   none           no buying at all, only a note that passes are managed in the family account
///                  (use this if a store reviewer objects to the link).
const bool kStoreBuild = bool.fromEnvironment('STORE_BUILD');
const String kStorePurchase = String.fromEnvironment('STORE_PURCHASE', defaultValue: 'web');
const String kWebAppBase = String.fromEnvironment('JISR_WEB_BASE', defaultValue: 'https://app.jisrarabic.com');

/// The website opens its own payment screen for this class and term (after sign-in when needed).
Uri webPurchaseUri(int grade, int term, {String base = kWebAppBase}) =>
    Uri.parse(base).replace(path: '/', queryParameters: {'buy': '1', 'grade': '$grade', 'term': '$term'});

Future<bool> openWebPurchase(int grade, int term) async {
  try {
    return await launchUrl(webPurchaseUri(grade, term), mode: LaunchMode.externalApplication);
  } catch (_) {
    return false;
  }
}

/// The public privacy policy (both stores require a link to it inside the app).
Uri privacyPolicyUri({String base = kWebAppBase}) => Uri.parse(base).replace(path: '/privacy');

Future<bool> openPrivacyPolicy() async {
  try {
    return await launchUrl(privacyPolicyUri(), mode: LaunchMode.externalApplication);
  } catch (_) {
    return false;
  }
}

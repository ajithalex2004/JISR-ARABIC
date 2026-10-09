import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/arab_english_service.dart';

void main() {
  test('ArabEnglish transliteration test', () {
    expect(ArabEnglishHelper.transliterate('سَجَّلَ اللَّاعِبُ الهَدَفَ'), 'Sajjala al-laa\'ibu al-hadaf');
    expect(ArabEnglishHelper.transliterate('كُرَةُ القَدَمِ لُعْبَةٌ جَمَاعِيَّةٌ'), 'Kuratu al-qadami lu\'batun jamaa\'iyyah');
    expect(ArabEnglishHelper.transliterate('يَرْكُضُ الفَارِسُ فِي المَيْدَانِ'), 'Yarkudu al-faarisu fee al-maydaan');
    expect(ArabEnglishHelper.transliterate('الرُّوحُ الرِّيَاضِيَّةُ وَاللَّعِبُ النَّظِيفُ'), 'Al-roohu al-riyaadiyyatu wal-la\'ibu al-natheef');
  });
}

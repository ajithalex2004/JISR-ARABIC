import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/arab_english_spelling.dart';

void main() {
  test('vowelled lesson words are spelled the way they are read', () {
    const cases = {
      'أَنْوَاعٌ': "anwaa'un", // was aanooaa'un
      'كُرَةُ': 'kuratu', // was kuraahu
      'مُخْتَلِفَةٌ': 'mukhtalifatun',
      'دَائِمًا': "daa'iman", // was daa'imanaa
      'نَحْوَ': 'nahwa', // was nahooa
      'مُسْتَدِيرٌ': 'mustadeerun', // was mustadieerun
      'جَمَاعِيَّةٌ': "jamaa'iyyatun",
      'وَالْمَسَاحَةُ': 'wal-masaahatu', // was wal-lmasaahaahu
      'الرِّيَادَةُ': 'al-riyaadatu', // was al-rrieeaadaahu
      'لِلْكُرَةِ': 'lil-kurati',
      'إِلَى': 'ila',
      'سَجَّلَ': 'sajjala',
      'الرُّوحُ': 'al-roohu',
      'هُدًى': 'hudan',
      'أيضاً': 'aydan',
      'اخْتِبَارُ': 'ikhtibaaru',
    };
    cases.forEach((word, spelled) => expect(spellArabicWord(word), spelled, reason: word));
  });
}

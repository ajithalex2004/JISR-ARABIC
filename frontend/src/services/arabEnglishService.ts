/**
 * Arab-English (عربيزي) Phonetic Pronunciation Engine
 * Fully aligns the Web App with the Mobile App's ArabEnglishHelper engine.
 * Transliterates Arabic curriculum text, vocabulary, grammar rules, and exam questions
 * into natural, accurate Latin phonetics (Arab-English / Arabizi).
 */

import { useState, useEffect } from 'react';

type Listener = (enabled: boolean) => void;

class ArabEnglishStateManager {
  private _enabled: boolean;
  private _listeners: Set<Listener> = new Set();

  constructor() {
    if (typeof window !== 'undefined' && window.localStorage) {
      const stored = window.localStorage.getItem('fahim_arab_english_enabled');
      this._enabled = stored !== null ? stored === 'true' : true; // Default ON
    } else {
      this._enabled = true;
    }
  }

  get isEnabled(): boolean {
    return this._enabled;
  }

  set(val: boolean): void {
    this._enabled = val;
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.setItem('fahim_arab_english_enabled', String(val));
    }
    this._notify();
  }

  toggle(): void {
    this.set(!this._enabled);
  }

  subscribe(listener: Listener): () => void {
    this._listeners.add(listener);
    return () => {
      this._listeners.delete(listener);
    };
  }

  private _notify(): void {
    this._listeners.forEach((fn) => fn(this._enabled));
  }
}

export const ArabEnglishState = new ArabEnglishStateManager();

export class ArabEnglishHelper {
  // 1. Curated high-frequency dictionary for Grade 5 curriculum, grammar, and exam phrases
  private static readonly curatedMap: Record<string, string> = {
    // Lesson 1 & Ball Games vocabulary
    'سجل اللاعب الهدف': "Sajjala al-laa'ibu al-hadaf",
    'سَجَّلَ اللَّاعِبُ الهَدَفَ': "Sajjala al-laa'ibu al-hadaf",
    'كرة القدم': 'Kuratu al-qadam',
    'كُرَةُ القَدَمِ': 'Kuratu al-qadam',
    'كرة القدم لعبة جماعية': "Kuratu al-qadami lu'batun jamaa'iyyah",
    'كُرَةُ القَدَمِ لُعْبَةٌ جَمَاعِيَّةٌ': "Kuratu al-qadami lu'batun jamaa'iyyah",
    'يركض الفارس في الميدان': 'Yarkudu al-faarisu fee al-maydaan',
    'يَرْكُضُ الفَارِسُ فِي المَيْدَانِ': 'Yarkudu al-faarisu fee al-maydaan',
    'الساحرة المستديرة': 'Al-saahiratu al-mustadeerah',
    'السَّاحِرَةُ المُسْتَدِيرَةُ': 'Al-saahiratu al-mustadeerah',
    'الروح الرياضية': 'Al-roohu al-riyaadiyyah',
    'الرُّوحُ الرِّيَاضِيَّةُ': 'Al-roohu al-riyaadiyyah',
    'الروح الرياضية واللعب النظيف': "Al-roohu al-riyaadiyyatu wal-la'ibu al-natheef",
    'الرُّوحُ الرِّيَاضِيَّةُ وَاللَّعِبُ النَّظِيفُ': "Al-roohu al-riyaadiyyatu wal-la'ibu al-natheef",
    'ألعاب الكرة': "Al'aabu al-kurah",
    'أَلْعَابُ الكُرَةِ': "Al'aabu al-kurah",
    'ركوب الخيل': 'Rukoobu al-khayl',
    'رُكُوبُ الخَيْلِ': 'Rukoobu al-khayl',
    'الجري': 'Al-jary',
    'الفنون': 'Al-funoon',
    'القراءة': "Al-qiraa'ah",
    'في مدرستي': 'Fee madrasatee',
    'في بيتي': 'Fee baytee',
    'طعامي': "Ta'aamee",
    'ملابسي': 'Malaabisee',
    'وقت المرح': 'Waqtu al-marah',
    'مستدير': 'Mustadeer',
    'مُسْتَدِيرٌ': 'Mustadeer',
    'بيضوي': 'Baydawee',
    'بَيْضَوِيٌّ': 'Baydawee',
    'جماعي': "Jamaa'ee",
    'جَمَاعِيٌّ': "Jamaa'ee",
    'فردي': 'Fardee',
    'فَرْدِيٌّ': 'Fardee',
    'المباراة': 'Al-mubaaraah',
    'المُبَارَاةُ': 'Al-mubaaraah',
    'الفريق': 'Al-fareeq',
    'الفَرِيقُ': 'Al-fareeq',
    'الملعب': "Al-mal'ab",
    'المَلْعَبُ': "Al-mal'ab",
    'الحكام': 'Al-hukkaam',
    'الحُكَّامُ': 'Al-hukkaam',
    'حكم الساحة': 'Hakamu al-saahah',
    'حارس المرمى': 'Haarisu al-marma',
    'حَارِسُ المَرْمَى': 'Haarisu al-marma',
    'عشب أخضر': "'Ushbun akhdar",
    'عُشْبٌ أَخْضَرُ': "'Ushbun akhdar",
    'عدد اللاعبين': "'Adadu al-laa'ibeen",
    'عَدَدُ اللَّاعِبِينَ': "'Adadu al-laa'ibeen",
    '11 لاعبا': "11 laa'iban",
    '١١ لاعباً': "11 laa'iban",
    'شوط المباراة': 'Shawtu al-mubaaraah',
    '45 دقيقة': '45 daqeeqah',
    'أبعاد الملعب': "Ab'aadu al-mal'ab",
    'طول الملعب': "Toolu al-mal'ab",
    'عرض الملعب': "'Ardu al-mal'ab",

    // Grammar & Capsules
    'التاء المربوطة والهاء': "Al-taa'u al-marbootatu wal-haa'",
    'التاء المربوطة': "Al-taa'u al-marbootah",
    'التاء المفتوحة': "Al-taa'u al-maftoohah",
    'مطابقة الفعل للفاعل': "Mutaabaqatu al-fi'li lil-faa'il",
    'جمع المذكر السالم': 'Jam\'u al-mudhakkari al-saalim',
    'جمع المؤنث السالم': "Jam'u al-mu'annathi al-saalim",
    'همزة الوصل والقطع': "Hamzatu al-wasli wal-qat'",
    'همزة الوصل': 'Hamzatu al-wasl',
    'همزة القطع': "Hamzatu al-qat'",
    'الجملة الاسمية والفعلية': "Al-jumlatu al-ismiyyatu wal-fi'liyyah",
    'الجملة الاسمية': 'Al-jumlatu al-ismiyyah',
    'الجملة الفعلية': "Al-jumlatu al-fi'liyyah",
    'المبتدأ والخبر': 'Al-mubtada\'u wal-khabar',
    'المبتدأ': "Al-mubtada'",
    'الخبر': 'Al-khabar',
    'الفعل والفاعل': "Al-fi'lu wal-faa'il",
    'الفعل': "Al-fi'l",
    'الفاعل': "Al-faa'il",
    'المفعول به': "Al-maf'oolu bihi",
    'حروف الجر': 'Huroofu al-jarr',
    'الاسم المجرور': 'Al-ismu al-majroor',
    'النحو والإعراب': "Al-nahwu wal-i'raab",
    'المفردات والتضاد': 'Al-mufradaatu wal-tadaadd',
    'فهم المقروء': "Fahmu al-maqroo'",
    'الجذور والاشتقاق': 'Al-judhooru wal-ishtiqaaq',

    // Questions & Exam terms
    'حل السؤال الأول': "Hallu al-su'aali al-awwal",
    'حل السؤال الثاني': "Hallu al-su'aali al-thaanee",
    'حل السؤال الثالث': "Hallu al-su'aali al-thaalith",
    'حل السؤال الرابع': "Hallu al-su'aali al-raabi'",
    'حل السؤال الخامس': "Hallu al-su'aali al-khaamis",
    'السؤال الأول': "Al-su'aalu al-awwal",
    'السؤال الثاني': "Al-su'aalu al-thaanee",
    'السؤال الثالث': "Al-su'aalu al-thaalith",
    'السؤال الرابع': "Al-su'aalu al-raabi'",
    'السؤال الخامس': "Al-su'aalu al-khaamis",
    'الخطوة الأولى': 'Al-khutwatu al-oola',
    'الخطوة الثانية': 'Al-khutwatu al-thaaniyah',
    'الخطوة الثالثة': 'Al-khutwatu al-thaalithah',
    'الإجابة النموذجية': 'Al-ijaabatu al-namoodhajiyyah',
    'الإجابة الصحيحة': 'Al-ijaabatu al-saheehah',
    'الشرح والتوضيح': 'Al-sharhu wal-tawdeeh',
    'القاعدة المستفادة': "Al-qaa'idatu al-mustafaadah",
    'أحسنت يا بطل': 'Ahsanta ya batal',
    'ممتاز': 'Mumtaaz',
    'رائع': "Raa'i'",
    'إجابة صحيحة': 'Ijaabatun saheehah',
    'صح أو خطأ': "Sah aw khata'",
    'اختر الإجابة الصحيحة': 'Ikhtar al-ijaabata al-saheehah',
  };

  // 2. Common word-level phonetics
  private static readonly wordMap: Record<string, string> = {
    'في': 'fee',
    'فِي': 'fee',
    'من': 'min',
    'مِن': 'min',
    'إلى': 'ila',
    'إِلَى': 'ila',
    'على': "'ala",
    'عَلَى': "'ala",
    'عن': "'an",
    'عَنْ': "'an",
    'مع': "ma'a",
    'مَعَ': "ma'a",
    'هو': 'huwa',
    'هُوَ': 'huwa',
    'هي': 'hiya',
    'هِيَ': 'hiya',
    'هم': 'hum',
    'هُمْ': 'hum',
    'أنا': 'ana',
    'أَنَا': 'ana',
    'نحن': 'nahnu',
    'نَحْنُ': 'nahnu',
    'أنت': 'anta',
    'أَنْتَ': 'anta',
    'أنتِ': 'anti',
    'أَنْتِ': 'anti',
    'هذا': 'haadha',
    'هَذَا': 'haadha',
    'هذه': 'haadhihi',
    'هَذِهِ': 'haadhihi',
    'ذلك': 'dhaalika',
    'ذَلِكَ': 'dhaalika',
    'تلك': 'tilka',
    'تِلْكَ': 'tilka',
    'كل': 'kull',
    'كُلُّ': 'kullu',
    'ما': 'maa',
    'مَا': 'maa',
    'ماذا': 'maadha',
    'مَاذَا': 'maadha',
    'لماذا': 'limaadha',
    'لِمَاذَا': 'limaadha',
    'كيف': 'kayfa',
    'كَيْفَ': 'kayfa',
    'أين': 'ayna',
    'أَيْنَ': 'ayna',
    'متى': 'mata',
    'مَتَى': 'mata',
    'كم': 'kam',
    'كَمْ': 'kam',
    'مَنْ': 'man',
    'هل': 'hal',
    'هَلْ': 'hal',
    'نعم': "na'am",
    'نَعَمْ': "na'am",
    'لا': 'laa',
    'لَا': 'laa',
    'كان': 'kaana',
    'كَانَ': 'kaana',
    'يكون': 'yakoon',
    'يَكُونُ': 'yakoonu',
    'ليس': 'laysa',
    'لَيْسَ': 'laysa',
    'إن': 'inna',
    'إِنَّ': 'inna',
    'أن': 'anna',
    'أَنَّ': 'anna',
    'لأن': "li'anna",
    'لِأَنَّ': "li'anna",
    'ثم': 'thumma',
    'ثُمَّ': 'thumma',
    'أو': 'aw',
    'أَوْ': 'aw',
    'و': 'wa',
    'وَ': 'wa',
    'ف': 'fa',
    'فَ': 'fa',
    'ب': 'bi',
    'بِ': 'bi',
    'ل': 'li',
    'لِ': 'li',
    'س': 'sa',
    'سَ': 'sa',
    'الكرة': 'al-kurah',
    'الكُرَةُ': 'al-kuratu',
    'القدم': 'al-qadam',
    'القَدَمِ': 'al-qadami',
    'اللاعب': "al-laa'ib",
    'اللَّاعِبُ': "al-laa'ibu",
    'الهدف': 'al-hadaf',
    'الهَدَفَ': 'al-hadafa',
    'الملعب': "al-mal'ab",
    'المَلْعَبُ': "al-mal'abu",
    'الفريق': 'al-fareeq',
    'الفَرِيقُ': 'al-fareequ',
    'المباراة': 'al-mubaaraah',
    'المُبَارَاةُ': 'al-mubaaraatu',
    'الحكام': 'al-hukkaam',
    'الحُكَّامُ': 'al-hukkaamu',
    'لعبة': "lu'bah",
    'لُعْبَةٌ': "lu'batun",
    'جماعية': "jamaa'iyyah",
    'جَمَاعِيَّةٌ': "jamaa'iyyatun",
    'فردية': 'fardiyyah',
    'فَرْدِيَّةٌ': 'fardiyyatun',
    'مستدير': 'mustadeer',
    'مُسْتَدِيرٌ': 'mustadeerun',
    'بيضوي': 'baydawee',
    'بَيْضَوِيٌّ': 'baydaweeyun',
    'العالم': "al-'aalam",
    'العَالَمِ': "al-'aalami",
    'الرسمية': 'al-rasmiyyah',
    'الرَّسْمِيَّةُ': 'al-rasmiyyatu',
    'الماء': "al-maa'",
    'المَاءُ': "al-maa'u",
    'الشمس': 'ash-shams',
    'الشَّمْسُ': 'ash-shamsu',
    'القمر': 'al-qamar',
    'القَمَرُ': 'al-qamaru',
    'مدرسة': 'madrasah',
    'مَدْرَسَةٌ': 'madrasatun',
    'مدرستي': 'madrasatee',
    'مَدْرَسَتِي': 'madrasatee',
    'طالب': 'taalib',
    'طَالِبٌ': 'taalibun',
    'معلم': "mu'allim",
    'مُعَلِّمٌ': "mu'allimun",
    'فاهم': 'Fahim',
    'فَاهِمٌ': 'Faahimun',
  };

  /**
   * Main entrypoint: transliterate Arabic text to ArabEnglish phonetics.
   */
  static transliterate(text: string): string {
    if (!text || !text.trim()) return '';

    // If text has no Arabic characters, return empty
    if (!/[\u0600-\u06FF]/.test(text)) {
      return '';
    }

    const trimmed = text.trim();

    // Check exact curated match first
    if (this.curatedMap[trimmed]) {
      return this.curatedMap[trimmed];
    }

    const normalized = trimmed.replace(/[\u064B-\u065F\u0670\u0640]/g, '');
    if (this.curatedMap[normalized]) {
      return this.curatedMap[normalized];
    }

    // Process line-by-line
    const lines = trimmed.split('\n');
    const resultLines: string[] = [];

    for (const line of lines) {
      const lineTrim = line.trim();
      if (!lineTrim) {
        resultLines.push('');
        continue;
      }

      let cleanLine = lineTrim;
      let prefix = '';
      const bulletMatch = cleanLine.match(/^(\d+[\.\-\)]|\*|\-|•|\([0-9]+\))\s*/);
      if (bulletMatch) {
        prefix = bulletMatch[0];
        cleanLine = cleanLine.substring(prefix.length).trim();
      }

      if (this.curatedMap[cleanLine]) {
        resultLines.push(`${prefix}${this.curatedMap[cleanLine]}`);
        continue;
      }

      const normLine = cleanLine.replace(/[\u064B-\u065F\u0670\u0640]/g, '');
      if (this.curatedMap[normLine]) {
        resultLines.push(`${prefix}${this.curatedMap[normLine]}`);
        continue;
      }

      // Tokenize line into words and delimiters
      const tokens = this.tokenizeLine(cleanLine);
      const outTokens: string[] = [];

      for (let i = 0; i < tokens.length; i++) {
        const tok = tokens[i];
        if (!tok.trim() || /^[؟!\.,،؛:\x27"()\[\]\-—/\\«»<>0-9\s]+$/.test(tok)) {
          outTokens.push(this.convertPunctuation(tok));
          continue;
        }

        const transWord = this.transliterateWord(tok, i === 0);
        outTokens.push(transWord);
      }

      const formattedLine = outTokens.join('');
      resultLines.push(`${prefix}${this.capitalizeFirst(formattedLine)}`);
    }

    return resultLines.join('\n').trim();
  }

  private static tokenizeLine(line: string): string[] {
    const reg = /([\u0600-\u06FF\u064B-\u065F\u0670\u0640]+|[^\u0600-\u06FF\u064B-\u065F\u0670\u0640]+)/g;
    const tokens: string[] = [];
    let match: RegExpExecArray | null;
    while ((match = reg.exec(line)) !== null) {
      tokens.push(match[0]);
    }
    return tokens;
  }

  private static convertPunctuation(p: string): string {
    return p
      .replace(/،/g, ',')
      .replace(/؛/g, ';')
      .replace(/؟/g, '?')
      .replace(/«/g, '"')
      .replace(/»/g, '"')
      .replace(/١/g, '1')
      .replace(/٢/g, '2')
      .replace(/٣/g, '3')
      .replace(/٤/g, '4')
      .replace(/٥/g, '5')
      .replace(/٦/g, '6')
      .replace(/٧/g, '7')
      .replace(/٨/g, '8')
      .replace(/٩/g, '9')
      .replace(/٠/g, '0');
  }

  public static transliterateWord(rawWord: string, isFirstWord = false): string {
    if (!rawWord) return '';

    if (this.wordMap[rawWord]) {
      const w = this.wordMap[rawWord];
      return isFirstWord ? this.capitalizeFirst(w) : w;
    }

    const normWord = rawWord.replace(/[\u064B-\u065F\u0670\u0640]/g, '');
    if (this.wordMap[normWord]) {
      const w = this.wordMap[normWord];
      return isFirstWord ? this.capitalizeFirst(w) : w;
    }

    // Prefix stripping e.g. al- (ال)
    let wordToProcess = rawWord;
    let prefixTrans = '';

    if (normWord.startsWith('ال') && normWord.length > 2) {
      wordToProcess = wordToProcess.replace(/^(الْ|ال|ٱلْ|ٱل)/, '');
      prefixTrans = 'al-';
    } else if ((normWord.startsWith('وال') || normWord.startsWith('فال') || normWord.startsWith('بال')) && normWord.length > 3) {
      const lead = normWord[0] === 'و' ? 'w' : normWord[0] === 'ف' ? 'f' : 'b';
      wordToProcess = wordToProcess.substring(3);
      prefixTrans = `${lead}al-`;
    }

    const chars = Array.from(wordToProcess);
    let out = '';

    for (let i = 0; i < chars.length; i++) {
      const ch = chars[i];

      // Tashkeel / Short vowels
      if (ch === '\u064E') { out += 'a'; continue; } // Fatha
      if (ch === '\u064F') { out += 'u'; continue; } // Damma
      if (ch === '\u0650') { out += 'i'; continue; } // Kasra
      if (ch === '\u0652') { continue; }            // Sukun
      if (ch === '\u0651') {                         // Shadda
        if (out.length > 0) {
          const lastChar = out[out.length - 1];
          if (/[a-zA-Z]/.test(lastChar) && !'aeiou'.includes(lastChar.toLowerCase())) {
            out += lastChar;
          }
        }
        continue;
      }
      if (ch === '\u064B') { out += 'an'; continue; } // Tanween Fath
      if (ch === '\u064C') { out += 'un'; continue; } // Tanween Damm
      if (ch === '\u064D') { out += 'in'; continue; } // Tanween Kasr
      if (ch === '\u0670') { out += 'aa'; continue; } // Dagger alif

      // Consonants and letters
      switch (ch) {
        case 'ء':
        case 'ئ':
        case 'ؤ':
          out += "'";
          break;
        case 'أ':
        case 'إ':
        case 'ٱ':
          out += i === 0 ? (ch === 'إ' ? 'i' : 'a') : "'";
          break;
        case 'آ':
        case 'ا':
          out += 'aa';
          break;
        case 'ب': out += 'b'; break;
        case 'ت': out += 't'; break;
        case 'ث': out += 'th'; break;
        case 'ج': out += 'j'; break;
        case 'ح': out += 'h'; break;
        case 'خ': out += 'kh'; break;
        case 'د': out += 'd'; break;
        case 'ذ': out += 'dh'; break;
        case 'ر': out += 'r'; break;
        case 'ز': out += 'z'; break;
        case 'س': out += 's'; break;
        case 'ش': out += 'sh'; break;
        case 'ص': out += 's'; break;
        case 'ض': out += 'd'; break;
        case 'ط': out += 't'; break;
        case 'ظ': out += 'dh'; break;
        case 'ع': out += "'"; break;
        case 'غ': out += 'gh'; break;
        case 'ف': out += 'f'; break;
        case 'ق': out += 'q'; break;
        case 'ك': out += 'k'; break;
        case 'ل': out += 'l'; break;
        case 'م': out += 'm'; break;
        case 'ن': out += 'n'; break;
        case 'ه': out += 'h'; break;
        case 'و':
          if (i === 0 || (i > 0 && chars[i - 1] === '\u064E')) {
            out += 'w';
          } else {
            out += 'oo';
          }
          break;
        case 'ي':
          if (i === 0 || (i > 0 && chars[i - 1] === '\u064E')) {
            out += 'y';
          } else {
            out += 'ee';
          }
          break;
        case 'ى': out += 'aa'; break;
        case 'ة': out += 'ah'; break;
        default: break;
      }
    }

    out = out.replace(/a{3,}/g, 'aa');
    out = out.replace(/e{3,}/g, 'ee');
    out = out.replace(/o{3,}/g, 'oo');

    let finalWord = `${prefixTrans}${out}`;
    if (!finalWord) return rawWord;

    if (isFirstWord) {
      finalWord = this.capitalizeFirst(finalWord);
    }
    return finalWord;
  }

  private static capitalizeFirst(s: string): string {
    if (!s) return '';
    for (let i = 0; i < s.length; i++) {
      if (/[a-zA-Z]/.test(s[i])) {
        return s.substring(0, i) + s[i].toUpperCase() + s.substring(i + 1);
      }
    }
    return s;
  }
}

/**
 * React hook for consuming and updating Arab-English Pronunciation state.
 * Returns [isEnabled, toggleOrSet]
 */
export function useArabEnglish(): [boolean, (val?: boolean) => void] {
  const [enabled, setEnabled] = useState<boolean>(() => ArabEnglishState.isEnabled);

  useEffect(() => {
    return ArabEnglishState.subscribe((val) => setEnabled(val));
  }, []);

  const toggle = (val?: boolean) => {
    if (typeof val === 'boolean') {
      ArabEnglishState.set(val);
    } else {
      ArabEnglishState.toggle();
    }
  };

  return [enabled, toggle];
}

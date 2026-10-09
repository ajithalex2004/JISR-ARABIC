import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')
import scratch.gr6_dict_code as gr6

with open('frontend/src/services/arabicDictionary.ts', encoding='utf-8') as f:
    existing_dict_content = f.read()

# Core Grade 6 Chapter 1 vocabulary with high quality translations and grammar tags
GR6_VOCABULARY = {
    # Page 9 Dictionary Cards
    "رغبة": {"translation": "desire / wish / craving", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "الرغبة": {"translation": "the desire / wish", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "رغبات": {"translation": "desires / wishes", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "رغباتي": {"translation": "my desires / wishes", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "رغباتك": {"translation": "your desires", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "احتياج": {"translation": "need / requirement / necessity", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "الاحتياج": {"translation": "the need / necessity", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "احتياجات": {"translation": "needs / necessities", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "احتياجاتي": {"translation": "my needs / necessities", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "احتياجاتك": {"translation": "your needs", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "حاجة": {"translation": "need / necessity / want", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "حاجات": {"translation": "needs / wants", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "حاجاتي": {"translation": "my needs", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "حاجتي": {"translation": "my need", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "إنسان": {"translation": "human / person / human being", "partOfSpeech": "noun", "root": "أ-ن-س"},
    "الإنسان": {"translation": "the human / mankind / person", "partOfSpeech": "noun", "root": "أ-ن-س"},
    "ضروري": {"translation": "essential / necessary / vital", "partOfSpeech": "adjective", "root": "ض-ر-ر"},
    "ضرورية": {"translation": "essential / necessary (fem.)", "partOfSpeech": "adjective", "root": "ض-ر-ر"},
    "ضروريات": {"translation": "essentials / necessities", "partOfSpeech": "noun", "root": "ض-ر-ر"},
    "البقاء": {"translation": "survival / staying / remaining", "partOfSpeech": "noun", "root": "ب-ق-ي"},
    "بقاء": {"translation": "survival / staying", "partOfSpeech": "noun", "root": "ب-ق-ي"},
    "تمتلك": {"translation": "owns / possesses / holds", "partOfSpeech": "verb", "root": "م-ل-ك"},
    "يمتلك": {"translation": "owns / possesses (masc.)", "partOfSpeech": "verb", "root": "م-ل-ك"},
    "امتلاك": {"translation": "ownership / possession", "partOfSpeech": "noun", "root": "م-ل-ك"},
    "يؤثر": {"translation": "influences / affects", "partOfSpeech": "verb", "root": "أ-ث-ر"},
    "تؤثر": {"translation": "influences / affects (fem.)", "partOfSpeech": "verb", "root": "أ-ث-ر"},
    "تأثير": {"translation": "effect / influence / impact", "partOfSpeech": "noun", "root": "أ-ث-ر"},
    "الكائن": {"translation": "the being / organism / creature", "partOfSpeech": "noun", "root": "ك-و-ن"},
    "كائن": {"translation": "being / creature", "partOfSpeech": "noun", "root": "ك-و-ن"},
    "المفكر": {"translation": "the thinking / intellectual", "partOfSpeech": "adjective", "root": "ف-ك-ر"},
    "مفكر": {"translation": "thinking / thinker", "partOfSpeech": "noun", "root": "ف-ك-ر"},
    "الميل": {"translation": "inclination / inclination / tendency", "partOfSpeech": "noun", "root": "م-ي-ل"},
    "ميل": {"translation": "inclination / tendency", "partOfSpeech": "noun", "root": "م-ي-ل"},
    "يميل": {"translation": "tends / inclines", "partOfSpeech": "verb", "root": "م-ي-ل"},
    "الشهوة": {"translation": "appetite / craving / desire", "partOfSpeech": "noun", "root": "ش-ه-و"},
    "شهوة": {"translation": "appetite / desire", "partOfSpeech": "noun", "root": "ش-ه-و"},
    "المستهلك": {"translation": "the consumer", "partOfSpeech": "noun", "root": "ه-ل-ك"},
    "مستهلك": {"translation": "consumer", "partOfSpeech": "noun", "root": "ه-ل-ك"},
    "المكوث": {"translation": "staying / remaining / dwelling", "partOfSpeech": "noun", "root": "م-ك-ث"},
    "مكوث": {"translation": "staying / dwelling", "partOfSpeech": "noun", "root": "م-ك-ث"},
    "الاستمرار": {"translation": "continuation / persistence", "partOfSpeech": "noun", "root": "م-ر-ر"},
    "استمرار": {"translation": "continuation", "partOfSpeech": "noun", "root": "م-ر-ر"},
    "افتقار": {"translation": "lack / poverty / shortage", "partOfSpeech": "noun", "root": "ف-ق-ر"},
    "المجاعات": {"translation": "famines / starvation crises", "partOfSpeech": "noun", "root": "ج-و-ع"},
    "مجاعة": {"translation": "famine / starvation", "partOfSpeech": "noun", "root": "ج-و-ع"},
    "الموارد": {"translation": "the resources / assets", "partOfSpeech": "noun", "root": "و-ر-د"},
    "موارد": {"translation": "resources / revenues", "partOfSpeech": "noun", "root": "و-ر-د"},
    "تحوز": {"translation": "holds / possesses / acquires", "partOfSpeech": "verb", "root": "ح-و-ز"},
    "يقنع": {"translation": "persuades / convinces", "partOfSpeech": "verb", "root": "ق-ن-ع"},
    "يؤكل": {"translation": "is eaten / edible", "partOfSpeech": "verb", "root": "أ-ك-ل"},
    "الإعلان": {"translation": "the advertisement / announcement", "partOfSpeech": "noun", "root": "ع-ل-ن"},
    "إعلان": {"translation": "advertisement / ad", "partOfSpeech": "noun", "root": "ع-ل-ن"},
    "الاعتدال": {"translation": "moderation / balance", "partOfSpeech": "noun", "root": "ع-د-ل"},
    "اعتدال": {"translation": "moderation", "partOfSpeech": "noun", "root": "ع-د-ل"},
    "الإزعاج": {"translation": "the annoyance / disturbance / noise", "partOfSpeech": "noun", "root": "ز-ع-ج"},
    "إزعاج": {"translation": "annoyance / disturbance", "partOfSpeech": "noun", "root": "ز-ع-ج"},
    "الكتب": {"translation": "the books", "partOfSpeech": "noun", "root": "ك-ت-ب"},
    "منى": {"translation": "Mona (female proper name)", "partOfSpeech": "noun"},
    "بشدة": {"translation": "intensely / strongly / severely", "partOfSpeech": "adverb"},
    "شدة": {"translation": "intensity / strength / hardship", "partOfSpeech": "noun", "root": "ش-د-د"},
    "نحتاجه": {"translation": "we need it", "partOfSpeech": "verb", "root": "ح-و-ج"},
    "نحتاج": {"translation": "we need", "partOfSpeech": "verb", "root": "ح-و-ج"},
    "يحتاج": {"translation": "needs / requires", "partOfSpeech": "verb", "root": "ح-و-ج"},
    "أحتاج": {"translation": "I need", "partOfSpeech": "verb", "root": "ح-و-ج"},
    
    # Unit 2 & Chapter 1 additional pages
    "بيع": {"translation": "sale / selling", "partOfSpeech": "noun", "root": "ب-ي-ع"},
    "شراء": {"translation": "buying / purchasing", "partOfSpeech": "noun", "root": "ش-ر-ي"},
    "التسوق": {"translation": "shopping", "partOfSpeech": "noun", "root": "س-و-ق"},
    "قائمة": {"translation": "list / menu", "partOfSpeech": "noun", "root": "ق-و-م"},
    "نقدا": {"translation": "in cash", "partOfSpeech": "adverb", "root": "ن-ق-د"},
    "بالبطاقة": {"translation": "by card / with card", "partOfSpeech": "noun", "root": "ب-ط-ق"},
    "بطاقة": {"translation": "card / badge", "partOfSpeech": "noun"},
    "أسواق": {"translation": "markets / souks", "partOfSpeech": "noun", "root": "س-و-ق"},
    "القرية": {"translation": "the village", "partOfSpeech": "noun", "root": "ق-ر-ي"},
    "العالمية": {"translation": "global / worldwide (fem.)", "partOfSpeech": "adjective", "root": "ع-ل-م"},
    "متجر": {"translation": "store / shop", "partOfSpeech": "noun", "root": "ت-ج-ر"},
    "أولويات": {"translation": "priorities", "partOfSpeech": "noun", "root": "أ-و-ل"},
    "أولوياتي": {"translation": "my priorities", "partOfSpeech": "noun", "root": "أ-و-ل"},
    "أولوياتك": {"translation": "your priorities", "partOfSpeech": "noun", "root": "أ-و-ل"},
    "ترتيب": {"translation": "arranging / ordering / prioritizing", "partOfSpeech": "noun", "root": "ر-ت-ب"},
    "أرتب": {"translation": "I arrange / I order", "partOfSpeech": "verb", "root": "ر-ت-ب"},
    "أقسم": {"translation": "I divide / allocate", "partOfSpeech": "verb", "root": "ق-س-م"},
    "سأقسم": {"translation": "I will divide / distribute", "partOfSpeech": "verb", "root": "ق-س-م"},
    "مبلغ": {"translation": "amount / sum of money", "partOfSpeech": "noun", "root": "ب-ل-غ"},
    "المال": {"translation": "money / wealth", "partOfSpeech": "noun", "root": "م-و-ل"},
    "مال": {"translation": "money", "partOfSpeech": "noun", "root": "م-و-ل"},
    "فزت": {"translation": "I won", "partOfSpeech": "verb", "root": "ف-و-ز"},
    "أتخيل": {"translation": "I imagine", "partOfSpeech": "verb", "root": "خ-ي-ل"},
    "الماسح": {"translation": "the scanner", "partOfSpeech": "noun", "root": "م-س-ح"},
    "الضوئي": {"translation": "optical / light-based", "partOfSpeech": "adjective", "root": "ض-و-ء"},
    "الضائعة": {"translation": "the lost / missing (fem.)", "partOfSpeech": "adjective", "root": "ض-ي-ع"},
    "الجدول": {"translation": "the table / schedule", "partOfSpeech": "noun", "root": "ج-د-ل"},
    "جدول": {"translation": "table / chart", "partOfSpeech": "noun", "root": "ج-د-ل"},
    "العجلة": {"translation": "the wheel", "partOfSpeech": "noun", "root": "ع-ج-ل"},
    "عجلة": {"translation": "wheel", "partOfSpeech": "noun", "root": "ع-ج-ل"},
    "أدير": {"translation": "I spin / manage / turn", "partOfSpeech": "verb", "root": "د-و-ر"},
    "تخطيط": {"translation": "planning", "partOfSpeech": "noun", "root": "خ-ط-ط"},
    "التخطيط": {"translation": "the planning", "partOfSpeech": "noun", "root": "خ-ط-ط"},
    "الحقيقية": {"translation": "the real / true (fem.)", "partOfSpeech": "adjective", "root": "ح-ق-ق"},
    "حقيقية": {"translation": "real / genuine", "partOfSpeech": "adjective", "root": "ح-ق-ق"},
    "موضحا": {"translation": "clarifying / explaining", "partOfSpeech": "adverb", "root": "و-ض-ح"},
    "أشارك": {"translation": "I participate / share", "partOfSpeech": "verb", "root": "ش-ر-ك"},
    "تصنيف": {"translation": "classification / sorting", "partOfSpeech": "noun", "root": "ص-ن-ف"},
    "مجموعتين": {"translation": "two groups", "partOfSpeech": "noun", "root": "ج-م-ع"},
    "مختلفتين": {"translation": "two different (fem.)", "partOfSpeech": "adjective", "root": "خ-ل-ف"},
}

print(f"Total vocabulary terms prepared: {len(GR6_VOCABULARY)}")

# Check formatting for adding to ARABIC_DICTIONARY in arabicDictionary.ts
entries = []
for k, v in sorted(GR6_VOCABULARY.items()):
    tr = v['translation']
    pos = v.get('partOfSpeech', 'noun')
    root_part = f", root: '{v['root']}'" if 'root' in v else ""
    entries.append(f"  '{k}': {{ translation: '{tr}', partOfSpeech: '{pos}'{root_part} }},")

print(f"Generated {len(entries)} entry lines.")

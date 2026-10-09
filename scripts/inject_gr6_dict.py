import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load generated dict
with open('scratch/gr6_generated_dict.json', encoding='utf-8') as f:
    generated = json.load(f)

# 2. Curated additions for Page 9 and Chapter 1
curated = {
    "رغبة": {"translation": "desire / wish / appetite", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "الرغبة": {"translation": "the desire / wish", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "رغبات": {"translation": "desires / wishes", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "رغباتي": {"translation": "my desires / wishes", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "رغباتك": {"translation": "your desires", "partOfSpeech": "noun", "root": "ر-غ-ب"},
    "احتياج": {"translation": "need / requirement / demand", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "الاحتياج": {"translation": "the need / requirement", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "احتياجات": {"translation": "needs / requirements", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "احتياجاتي": {"translation": "my needs / requirements", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "احتياجاتك": {"translation": "your needs", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "حاجة": {"translation": "need / necessity / want", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "حاجات": {"translation": "needs / necessities", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "حاجاتي": {"translation": "my needs", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "حاجتي": {"translation": "my need", "partOfSpeech": "noun", "root": "ح-و-ج"},
    "إنسان": {"translation": "human / person / living being", "partOfSpeech": "noun", "root": "أ-ن-س"},
    "انسان": {"translation": "human / person / living being", "partOfSpeech": "noun", "root": "أ-ن-س"},
    "الإنسان": {"translation": "the human / human being", "partOfSpeech": "noun", "root": "أ-ن-س"},
    "الانسان": {"translation": "the human / human being", "partOfSpeech": "noun", "root": "أ-ن-س"},
    "طعام": {"translation": "food / meal", "partOfSpeech": "noun", "root": "ط-ع-م"},
    "الطعام": {"translation": "the food", "partOfSpeech": "noun", "root": "ط-ع-م"},
    "ضروري": {"translation": "essential / necessary / vital", "partOfSpeech": "adjective", "root": "ض-ر-ر"},
    "الضروري": {"translation": "the essential / necessary", "partOfSpeech": "adjective", "root": "ض-ر-ر"},
    "ضرورية": {"translation": "essential / necessary (fem.)", "partOfSpeech": "adjective", "root": "ض-ر-ر"},
    "ضروريات": {"translation": "essentials / necessities", "partOfSpeech": "noun", "root": "ض-ر-ر"},
    "البقاء": {"translation": "survival / staying / remaining", "partOfSpeech": "noun", "root": "ب-ق-ي"},
    "بقاء": {"translation": "survival / remaining", "partOfSpeech": "noun", "root": "ب-ق-ي"},
    "تمتلك": {"translation": "owns / possesses / holds", "partOfSpeech": "verb", "root": "م-ل-ك"},
    "يمتلك": {"translation": "owns / possesses (masc.)", "partOfSpeech": "verb", "root": "م-ل-ك"},
    "يؤثر": {"translation": "influences / affects / persuades", "partOfSpeech": "verb", "root": "أ-ث-ر"},
    "تؤثر": {"translation": "influences / affects (fem.)", "partOfSpeech": "verb", "root": "أ-ث-ر"},
    "الميل": {"translation": "inclination / appetite / leaning", "partOfSpeech": "noun", "root": "م-ي-ل"},
    "ميل": {"translation": "inclination / leaning", "partOfSpeech": "noun", "root": "م-ي-ل"},
    "الشهوة": {"translation": "desire / appetite / craving", "partOfSpeech": "noun", "root": "ش-ه-و"},
    "شهوة": {"translation": "desire / appetite", "partOfSpeech": "noun", "root": "ش-ه-و"},
    "الكائن": {"translation": "the living being / creature", "partOfSpeech": "noun", "root": "ك-و-ن"},
    "كائن": {"translation": "being / creature", "partOfSpeech": "noun", "root": "ك-و-ن"},
    "المفكر": {"translation": "the thinking / intellectual", "partOfSpeech": "adjective", "root": "ف-ك-ر"},
    "مفكر": {"translation": "thinking / thinker", "partOfSpeech": "noun", "root": "ف-ك-ر"},
    "المستهلك": {"translation": "the consumer", "partOfSpeech": "noun", "root": "ه-ل-ك"},
    "مستهلك": {"translation": "consumer", "partOfSpeech": "noun", "root": "ه-ل-ك"},
    "المكوث": {"translation": "staying / remaining / dwelling", "partOfSpeech": "noun", "root": "م-ك-ث"},
    "مكوث": {"translation": "staying / dwelling", "partOfSpeech": "noun", "root": "م-ك-ث"},
    "الاستمرار": {"translation": "continuation / persistence", "partOfSpeech": "noun", "root": "م-ر-ر"},
    "استمرار": {"translation": "continuation", "partOfSpeech": "noun", "root": "م-ر-ر"},
    "افتقار": {"translation": "lack / poverty / destitution", "partOfSpeech": "noun", "root": "ف-ق-ر"},
    "المجاعات": {"translation": "famines / starvation crises", "partOfSpeech": "noun", "root": "ج-و-ع"},
    "مجاعات": {"translation": "famines", "partOfSpeech": "noun", "root": "ج-و-ع"},
    "الموارد": {"translation": "the resources / assets", "partOfSpeech": "noun", "root": "و-ر-د"},
    "موارد": {"translation": "resources", "partOfSpeech": "noun", "root": "و-ر-د"},
    "تحوز": {"translation": "holds / possesses / acquires", "partOfSpeech": "verb", "root": "ح-و-ز"},
    "يقنع": {"translation": "persuades / convinces", "partOfSpeech": "verb", "root": "ق-ن-ع"},
    "يؤكل": {"translation": "is eaten / edible", "partOfSpeech": "verb", "root": "أ-ك-ل"},
    "الإعلان": {"translation": "the advertisement / announcement", "partOfSpeech": "noun", "root": "ع-ل-ن"},
    "إعلان": {"translation": "advertisement / ad", "partOfSpeech": "noun", "root": "ع-ل-ن"},
    "الاعتدال": {"translation": "moderation / balance", "partOfSpeech": "noun", "root": "ع-د-ل"},
    "اعتدال": {"translation": "moderation", "partOfSpeech": "noun", "root": "ع-د-ل"},
    "الإزعاج": {"translation": "the annoyance / disturbance", "partOfSpeech": "noun", "root": "ز-ع-ج"},
    "إزعاج": {"translation": "annoyance / noise", "partOfSpeech": "noun", "root": "ز-ع-ج"},
    "الكتب": {"translation": "the books", "partOfSpeech": "noun", "root": "ك-ت-ب"},
    "منى": {"translation": "Mona (female proper name)", "partOfSpeech": "noun"},
    "بشدة": {"translation": "intensely / severely / strongly", "partOfSpeech": "adverb"},
    "نحتاجه": {"translation": "we need it", "partOfSpeech": "verb", "root": "ح-و-ج"},
    "نحتاج": {"translation": "we need", "partOfSpeech": "verb", "root": "ح-و-ج"},
    "قاموسي": {"translation": "my glossary / my dictionary", "partOfSpeech": "noun", "root": "ق-م-س"},
    "القاموس": {"translation": "the glossary / dictionary", "partOfSpeech": "noun", "root": "ق-م-س"},
    "قاموس": {"translation": "glossary / dictionary", "partOfSpeech": "noun", "root": "ق-م-س"},
    "بيع": {"translation": "sale / selling", "partOfSpeech": "noun", "root": "ب-ي-ع"},
    "شراء": {"translation": "buying / purchase", "partOfSpeech": "noun", "root": "ش-ر-ي"},
    "التسوق": {"translation": "shopping", "partOfSpeech": "noun", "root": "س-و-ق"},
    "قائمة": {"translation": "list / roster", "partOfSpeech": "noun", "root": "ق-و-م"},
    "نقدا": {"translation": "in cash", "partOfSpeech": "adverb", "root": "ن-ق-د"},
    "بالبطاقة": {"translation": "by card / with credit card", "partOfSpeech": "noun"},
    "بطاقة": {"translation": "card / ticket", "partOfSpeech": "noun"},
    "أسواق": {"translation": "markets / souks", "partOfSpeech": "noun", "root": "س-و-ق"},
    "القرية": {"translation": "the village", "partOfSpeech": "noun", "root": "ق-ر-ي"},
    "العالمية": {"translation": "global / worldwide (fem.)", "partOfSpeech": "adjective", "root": "ع-ل-م"},
    "متجر": {"translation": "store / shop", "partOfSpeech": "noun", "root": "ت-ج-ر"},
    "أولويات": {"translation": "priorities", "partOfSpeech": "noun", "root": "أ-و-ل"},
    "أولوياتي": {"translation": "my priorities", "partOfSpeech": "noun", "root": "أ-و-ل"},
    "ترتيب": {"translation": "arranging / ordering / prioritizing", "partOfSpeech": "noun", "root": "ر-ت-ب"},
    "أقسم": {"translation": "I divide / allocate", "partOfSpeech": "verb", "root": "ق-س-م"},
    "مبلغ": {"translation": "sum / amount of money", "partOfSpeech": "noun", "root": "ب-ل-غ"},
    "المال": {"translation": "money / wealth", "partOfSpeech": "noun", "root": "م-و-ل"},
    "فزت": {"translation": "I won / triumphed", "partOfSpeech": "verb", "root": "ف-و-ز"},
    "أتخيل": {"translation": "I imagine", "partOfSpeech": "verb", "root": "خ-ي-ل"},
    "الماسح": {"translation": "the scanner", "partOfSpeech": "noun", "root": "م-س-ح"},
    "الضوئي": {"translation": "optical", "partOfSpeech": "adjective", "root": "ض-و-ء"},
    "الضائعة": {"translation": "the missing / lost", "partOfSpeech": "adjective", "root": "ض-ي-ع"},
    "العجلة": {"translation": "the wheel", "partOfSpeech": "noun", "root": "ع-ج-ل"},
    "عجلة": {"translation": "wheel", "partOfSpeech": "noun", "root": "ع-ج-ل"},
    "أدير": {"translation": "I spin / rotate / manage", "partOfSpeech": "verb", "root": "د-و-ر"},
    "تخطيط": {"translation": "planning", "partOfSpeech": "noun", "root": "خ-ط-ط"},
    "التخطيط": {"translation": "the planning", "partOfSpeech": "noun", "root": "خ-ط-ط"},
    "الحقيقية": {"translation": "the real / genuine (fem.)", "partOfSpeech": "adjective", "root": "ح-ق-ق"},
    "حقيقية": {"translation": "real / genuine", "partOfSpeech": "adjective", "root": "ح-ق-ق"},
    "موضحا": {"translation": "explaining / clarifying", "partOfSpeech": "adverb", "root": "و-ض-ح"},
    "أشارك": {"translation": "I participate / share", "partOfSpeech": "verb", "root": "ش-ر-ك"},
    "تصنيف": {"translation": "classifying / sorting", "partOfSpeech": "noun", "root": "ص-ن-ف"},
}

merged = dict(generated)
merged.update(curated)

print(f"Total merged Grade 6 entries: {len(merged)}")

with open('frontend/src/services/arabicDictionary.ts', encoding='utf-8') as f:
    orig = f.read()

target = "'يوما': { translation: 'a day (accusative)', partOfSpeech: 'verb' },"
assert target in orig, "target not found"

new_entries_lines = []
new_entries_lines.append("\n  // === UAE MoE Grade 6 Curriculum Entries (Needs, Desires, Commerce & Economics) ===")
for k in sorted(merged.keys()):
    v = merged[k]
    if not isinstance(v, dict): continue
    tr = v.get('translation', '').replace("'", "\\'")
    pos = v.get('partOfSpeech', 'noun')
    root_str = f", root: '{v['root']}'" if v.get('root') else ""
    cat_str = f", category: '{v['category']}'" if v.get('category') else ""
    new_entries_lines.append(f"  '{k}': {{ translation: '{tr}', partOfSpeech: '{pos}'{root_str}{cat_str} }},")

replacement = target + "\n" + "\n".join(new_entries_lines)
updated = orig.replace(target, replacement, 1)

with open('frontend/src/services/arabicDictionary.ts', 'w', encoding='utf-8') as f:
    f.write(updated)

print(f"Successfully injected {len(new_entries_lines) - 1} new Grade 6 dictionary terms into arabicDictionary.ts!")

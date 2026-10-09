import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

with open('backend/ocr_reader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define model answers
page_12_answers = {
    1: {
        "text_ar": "الحَاجَاتُ (الضَّرُورِيَّةُ لِلْحَيَاةِ): المَاءُ، الطَّعَامُ، الدَّوَاءُ، المَلَابِسُ، العَمَلُ، الدِّرَاسَةُ. الرَّغَبَاتُ (التَّرْفِيهِيَّةُ): السَّفَرُ، اللَّعِبُ، الرِّيَاضَةُ، الإِنْتَرْنِت، الفَوَاكِهُ، القِرَاءَةُ.",
        "arabzi": "Al-Hājāt: Al-mā', at-ta'ām, ad-dawā', al-malābis, al-'amal, ad-dirāsah. Ar-Raghabāt: As-safar, al-la'ib, ar-riyādah, al-internet, al-fawākih, al-qirā'ah.",
        "text_en": "Needs (essential for life): Water, Food, Medicine, Clothes, Work, Study. Desires / Wants (recreation): Travel, Playing, Sports, Internet, Fruits, Reading.",
        "explanation_en": "Needs (الحاجات) are vital for survival, health, and development. Desires (الرغبات) are extra comforts that improve life quality."
    },
    17: {
        "text_ar": "الأُسْلُوبُ الخَبَرِيُّ يَحْتَمِلُ الصِّدْقَ وَالكَذِبَ (يَنْقُلُ مَعْلُومَةً). الأُسْلُوبُ الإِنْشَائِيُّ لَا يَحْتَمِلُ الصِّدْقَ وَالكَذِبَ، وَمِنْهُ الطَّلَبِيُّ كَالاسْتِفْهَامِ وَالأَمْرِ وَالنَّهْيِ وَالنِّدَاءِ.",
        "arabzi": "Al-uslūb al-khabarī yahtamilu as-sidqa wal-kadhib. Al-uslūb al-inshā'ī lā yahtamilu as-sidqa wal-kadhib, wa minhu at-talabī kal-istifhām wal-amr wan-nahy wan-nidā'.",
        "text_en": "Declarative style conveys facts that can be true or false. Creative style does not judge truth/falsehood and includes requests such as questions, commands, prohibitions, and calls.",
        "explanation_en": "Khabari = Fact / Statement. Insha'i = Question / Command / Call / Prohibition."
    },
    18: {
        "text_ar": "أُسْلُوبٌ إِنْشَائِيٌّ (طَلَبِيٌّ: اسْتِفْهَامٌ).",
        "arabzi": "Uslūbun Inshā'iyyun (Talabiyyun: Istifhām)",
        "text_en": "Creative / Interrogative Style (Question).",
        "explanation_en": "Begins with the question particle 'Hal' (هَلْ) and ends with a question mark (؟), inquiring about essential survival needs."
    },
    19: {
        "text_ar": "أُسْلُوبٌ خَبَرِيٌّ (مُؤَكَّدٌ بِـ 'إِنَّ').",
        "arabzi": "Uslūbun Khabariyyun (Mu'akkadun bi-Inna)",
        "text_en": "Declarative / Informative Style (Affirmed Statement).",
        "explanation_en": "Conveys a factual statement confirmed by the emphasis particle 'Inna' (إِنَّ)."
    },
    20: {
        "text_ar": "أُسْلُوبٌ إِنْشَائِيٌّ (طَلَبِيٌّ: اسْتِفْهَامٌ).",
        "arabzi": "Uslūbun Inshā'iyyun (Talabiyyun: Istifhām)",
        "text_en": "Creative / Interrogative Style (Question).",
        "explanation_en": "Begins with the question noun 'Kayfa' (كَيْفَ) and ends with a question mark (؟), asking how one divides their monthly allowance."
    },
    21: {
        "text_ar": "أُسْلُوبٌ خَبَرِيٌّ.",
        "arabzi": "Uslūbun Khabariyyun",
        "text_en": "Declarative / Informative Style (Factual Statement).",
        "explanation_en": "States information about how consumption impacts the environment."
    },
    22: {
        "text_ar": "أُسْلُوبٌ إِنْشَائِيٌّ (طَلَبِيٌّ: نِدَاءٌ وَنَهْيٌ).",
        "arabzi": "Uslūbun Inshā'iyyun (Talabiyyun: Nidā'un wa Nahyun)",
        "text_en": "Creative Style (Vocative Call & Prohibition).",
        "explanation_en": "Combines a vocative call ('Yā Ādam' يَا آدَمُ) followed by a direct prohibition ('Lā tusrif' لَا تُسْرِفْ) against wasteful spending."
    },
    23: {
        "text_ar": "أُسْلُوبٌ خَبَرِيٌّ.",
        "arabzi": "Uslūbun Khabariyyun",
        "text_en": "Declarative / Informative Style (Aphorism & Wisdom).",
        "explanation_en": "Expresses a moral guideline and general wisdom that prioritizes basic needs over elective desires."
    }
}

page_11_answers = {
    1: {
        "text_ar": "احْتِيَاجَاتٌ أَسَاسِيَّةٌ ضَرُورِيَّةٌ لِلْبَقَاءِ (كَالطَّعَامِ وَالمَاءِ وَالمَسْكَنِ)، وَاحْتِيَاجَاتٌ ثَانَوِيَّةٌ.",
        "arabzi": "Ihtiyājāt asāsiyyah darūriyyah lil-baqā' (kat-ta'ām wal-mā' wal-maskan), wa ihtiyājāt thānawiyyah.",
        "text_en": "Essential primary needs for survival (such as food, water, and shelter), and secondary needs.",
        "explanation_en": "Categorizes human needs based on their necessity for life."
    },
    2: {
        "text_ar": "تَتَحَوَّلُ الرَّغْبَةُ إِلَى حَاجَةٍ عِنْدَمَا يُصْبِحُ الشَّيْءُ ضَرُورِيّاً لِإِتْمَامِ التَّعْلِيمِ أَوِ العَمَلِ، كَالحَاسُوبِ فِي الدِّرَاسَةِ.",
        "arabzi": "Tatahawwalu ar-raghbatu ilā hājatin 'indamā yusbihu ash-shay'u darūriyyan li-itmāmi at-ta'līmi awi al-'amali, kal-hāsūbi fid-dirāsati.",
        "text_en": "A desire becomes a need when an item becomes necessary to complete education or work, such as a computer for studying.",
        "explanation_en": "Shifts with context and technological requirements."
    },
    3: {
        "text_ar": "نَعَمْ؛ لِأَنَّ المَالَ وَسِيلَةٌ لِتَحْقِيقِ الرَّغَبَاتِ وَشِرَاءِ الاِحْتِيَاجَاتِ، وَيَجِبُ تَوْفِيرُ الضَّرُورِيَّاتِ أَوَّلًا.",
        "arabzi": "Na'am; li'anna al-māla wasīlatun li-tahqīqi ar-raghabāti wa shirā'i al-ihtiyājāti, wa yajibu tawfīru ad-darūriyyāti awwalan.",
        "text_en": "Yes; because money is the means to fulfill desires and purchase needs, and necessities must always be secured first.",
        "explanation_en": "Emphasizes prioritizing spending on essentials before luxuries."
    }
}

page_13_answers = {
    0: {
        "text_ar": "أُقَسِّمُ المَالَ حَسَبَ قَاعِدَةِ الأَوْلَوِيَّاتِ: ٥٠٪ لِلِاحْتِيَاجَاتِ الأَسَاسِيَّةِ، ٣٠٪ لِلرَّغَبَاتِ، وَ٢٠٪ لِلِادِّخَارِ لِلْمُسْتَقْبَلِ.",
        "arabzi": "Uqassimu al-māla hasaba qā'idati al-awlawiyyāt: 50% lil-ihtiyājāt al-asāsiyyah, 30% lir-raghabāt, wa 20% lil-iddikhār lil-mustaqbal.",
        "text_en": "I divide the money according to the priority budgeting rule: 50% for essential needs, 30% for desires, and 20% for future savings.",
        "explanation_en": "Teaches balanced financial planning and prioritizing necessities before luxuries."
    }
}

# We can import and modify GRADE_6_TEXTBOOK_PAGES_DATA in memory, then serialize or replace in file!
# Let's inspect how backend/ocr_reader.py defines GRADE_6_TEXTBOOK_PAGES_DATA
import backend.ocr_reader as ocr_mod

ocr_mod.GRADE_6_TEXTBOOK_PAGES_DATA[12]["model_answers"] = page_12_answers
ocr_mod.GRADE_6_TEXTBOOK_PAGES_DATA[11]["model_answers"] = page_11_answers
ocr_mod.GRADE_6_TEXTBOOK_PAGES_DATA[13]["model_answers"] = page_13_answers

# Now let's write updated GRADE_6_TEXTBOOK_PAGES_DATA into backend/ocr_reader.py
# First find where GRADE_6_TEXTBOOK_PAGES_DATA begins and ends
start_marker = "GRADE_6_TEXTBOOK_PAGES_DATA = {"
end_marker = "def get_textbook_coverage_report() -> Dict[str, Any]:"

start_pos = content.find(start_marker)
end_pos = content.find(end_marker)
assert start_pos != -1 and end_pos != -1

# Generate python code for GRADE_6_TEXTBOOK_PAGES_DATA
formatted_dict = "GRADE_6_TEXTBOOK_PAGES_DATA = " + json.dumps(ocr_mod.GRADE_6_TEXTBOOK_PAGES_DATA, ensure_ascii=False, indent=4) + "\n\n"

new_content = content[:start_pos] + formatted_dict + content[end_pos:]

# Update get_page_ocr_data return to include model_answers
if '"model_answers"' not in new_content:
    old_ret = '"paragraphs_en": data.get("paragraphs_en", []),'
    new_ret = '"paragraphs_en": data.get("paragraphs_en", []),\n            "model_answers": data.get("model_answers", {}),'
    new_content = new_content.replace(old_ret, new_ret)

with open('backend/ocr_reader.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully injected model_answers into backend/ocr_reader.py!")

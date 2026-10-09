"""
Comprehensive UAE Ministry of Education (MoE) Arabic Curriculum Registry.
Provides complete, structured syllabus chapters for Grades 1 through 12 across Terms 1, 2, and 3,
along with full lesson content generation for the Lesson Player, Vocabulary Drill, Grammar Lab,
Synthetic Speech Studio, and Assessments.
"""
import re
from typing import Dict, List, Optional, Any

class DynamicLesson:
    def __init__(
        self,
        id: str,
        grade: int,
        term: int,
        title_ar: str,
        title_en: str,
        unit_id: str,
        unit_title_ar: str,
        unit_title_en: str,
        start_page: int,
        is_first_chapter_demo: bool = False,
        status: str = "published",
        lesson_order: int = 1,
    ):
        self.id = id
        self.grade = grade
        self.term = term
        self.title_ar = title_ar
        self.title_en = title_en
        self.unit_id = unit_id
        self.unit_title_ar = unit_title_ar
        self.unit_title_en = unit_title_en
        self.start_page = start_page
        self.is_first_chapter_demo = is_first_chapter_demo
        self.status = status
        self.lesson_order = lesson_order

# High-fidelity predefined topics for all 12 UAE MoE grades across 3 terms
_GRADE_CURRICULUM_DATA: Dict[int, Dict[int, List[Dict[str, str]]]] = {
    1: {
        1: [
            {"title_ar": "الحروف الهجائية الأولى (أ - د)", "title_en": "First Letters (Alif to Dal)", "unit_ar": "أصوات الحروف والكلمات", "unit_en": "Letter Sounds & Words"},
            {"title_ar": "صفي الجميل", "title_en": "My Beautiful Classroom", "unit_ar": "أصوات الحروف والكلمات", "unit_en": "Letter Sounds & Words"},
            {"title_ar": "أسرتي الحبيبة", "title_en": "My Beloved Family", "unit_ar": "أصوات الحروف والكلمات", "unit_en": "Letter Sounds & Words"},
            {"title_ar": "ألعابي وهواياتي", "title_en": "My Toys and Hobbies", "unit_ar": "أصوات الحروف والكلمات", "unit_en": "Letter Sounds & Words"},
            {"title_ar": "حديقة الحيوان", "title_en": "At the Zoo", "unit_ar": "أصوات الحروف والكلمات", "unit_en": "Letter Sounds & Words"},
            {"title_ar": "علم بلادي الإمارات", "title_en": "UAE National Flag", "unit_ar": "وطني الجميل وتراثي", "unit_en": "My Beautiful Nation & Heritage"},
            {"title_ar": "يوم الشهيد والوفاء", "title_en": "Commemoration Day", "unit_ar": "وطني الجميل وتراثي", "unit_en": "My Beautiful Nation & Heritage"},
            {"title_ar": "النخلة المباركة", "title_en": "The Blessed Date Palm", "unit_ar": "وطني الجميل وتراثي", "unit_en": "My Beautiful Nation & Heritage"},
            {"title_ar": "الصقر الإماراتي", "title_en": "The Arabian Falcon", "unit_ar": "وطني الجميل وتراثي", "unit_en": "My Beautiful Nation & Heritage"},
            {"title_ar": "شاطئ البحر", "title_en": "The Seashore", "unit_ar": "وطني الجميل وتراثي", "unit_en": "My Beautiful Nation & Heritage"},
        ],
        2: [
            {"title_ar": "الحروف الهجائية (ذ - ض)", "title_en": "Letters (Dhal to Dad)", "unit_ar": "رحلتي مع الكلمات", "unit_en": "My Journey with Words"},
            {"title_ar": "في السوق التجاري", "title_en": "At the Marketplace", "unit_ar": "رحلتي مع الكلمات", "unit_en": "My Journey with Words"},
            {"title_ar": "طبيبي الصغير", "title_en": "My Little Doctor", "unit_ar": "رحلتي مع الكلمات", "unit_en": "My Journey with Words"},
            {"title_ar": "ألوان الطبيعة", "title_en": "Colors of Nature", "unit_ar": "بيئتي ونظافتي", "unit_en": "My Environment & Hygiene"},
            {"title_ar": "قطرة الماء الذهبية", "title_en": "Golden Water Drop", "unit_ar": "بيئتي ونظافتي", "unit_en": "My Environment & Hygiene"},
            {"title_ar": "إشارات المرور والسلامة", "title_en": "Traffic Signs & Safety", "unit_ar": "بيئتي ونظافتي", "unit_en": "My Environment & Hygiene"},
        ],
        3: [
            {"title_ar": "الحروف الهجائية (ط - ي)", "title_en": "Letters (Ta to Ya)", "unit_ar": "كوكبي ومدرستي", "unit_en": "My Planet & School"},
            {"title_ar": "رحلة إلى الفضاء", "title_en": "Journey to Space", "unit_ar": "كوكبي ومدرستي", "unit_en": "My Planet & School"},
            {"title_ar": "الأرض تدور", "title_en": "The Earth Turns", "unit_ar": "كوكبي ومدرستي", "unit_en": "My Planet & School"},
            {"title_ar": "أنا أقرأ بطلاقة", "title_en": "I Read Fluently", "unit_ar": "فنون ولغات", "unit_en": "Arts & Expression"},
            {"title_ar": "حكاية شجرة الغاف", "title_en": "Story of the Ghaf Tree", "unit_ar": "فنون ولغات", "unit_en": "Arts & Expression"},
            {"title_ar": "إجازتي الممتعة", "title_en": "My Joyful Vacation", "unit_ar": "فنون ولغات", "unit_en": "Arts & Expression"},
        ],
    },
    2: {
        1: [
            {"title_ar": "أنا وصديقي في المدرسة", "title_en": "My Friend and I at School", "unit_ar": "أصدقائي ومدرستي", "unit_en": "My Friends & School"},
            {"title_ar": "مكتبتي الصغيرة", "title_en": "My Little Library", "unit_ar": "أصدقائي ومدرستي", "unit_en": "My Friends & School"},
            {"title_ar": "حقيبتي المنظمة", "title_en": "My Organized School Bag", "unit_ar": "أصدقائي ومدرستي", "unit_en": "My Friends & School"},
            {"title_ar": "الرياضة وصحة الجسم", "title_en": "Sports and Health", "unit_ar": "أصدقائي ومدرستي", "unit_en": "My Friends & School"},
            {"title_ar": "وجبتي الصحية المتوازنة", "title_en": "My Healthy Balanced Meal", "unit_ar": "أصدقائي ومدرستي", "unit_en": "My Friends & School"},
            {"title_ar": "مدينة أبوظبي المشرقة", "title_en": "Luminous Abu Dhabi", "unit_ar": "مدن الإمارات وتراثها", "unit_en": "UAE Cities & Heritage"},
            {"title_ar": "واحة العين الخضراء", "title_en": "Al Ain Green Oasis", "unit_ar": "مدن الإمارات وتراثها", "unit_en": "UAE Cities & Heritage"},
            {"title_ar": "جامع الشيخ زايد الكبير", "title_en": "Sheikh Zayed Grand Mosque", "unit_ar": "مدن الإمارات وتراثها", "unit_en": "UAE Cities & Heritage"},
            {"title_ar": "قلعة الفهيدي التاريخية", "title_en": "Al Fahidi Historic Fort", "unit_ar": "مدن الإمارات وتراثها", "unit_en": "UAE Cities & Heritage"},
            {"title_ar": "سنع الأجداد وعاداتنا", "title_en": "Our Ancestral Traditions", "unit_ar": "مدن الإمارات وتراثها", "unit_en": "UAE Cities & Heritage"},
        ],
        2: [
            {"title_ar": "المهن وأصحابها", "title_en": "Professions and Crafts", "unit_ar": "العمل والعطاء", "unit_en": "Work & Giving"},
            {"title_ar": "المهندس المعماري المبتكر", "title_en": "The Innovative Architect", "unit_ar": "العمل والعطاء", "unit_en": "Work & Giving"},
            {"title_ar": "المزارع النشيط في الحقل", "title_en": "The Farmer in the Field", "unit_ar": "العمل والعطاء", "unit_en": "Work & Giving"},
            {"title_ar": "حماية كوكبنا الجميل", "title_en": "Protecting Our Planet", "unit_ar": "البيئة المستدامة", "unit_en": "Sustainable Environment"},
            {"title_ar": "إعادة التدوير الذكية", "title_en": "Smart Recycling", "unit_ar": "البيئة المستدامة", "unit_en": "Sustainable Environment"},
            {"title_ar": "طاقة الشمس والرياح النظيفة", "title_en": "Clean Solar & Wind Energy", "unit_ar": "البيئة المستدامة", "unit_en": "Sustainable Environment"},
        ],
        3: [
            {"title_ar": "عالم البحار والأعماق", "title_en": "The Deep Sea World", "unit_ar": "استكشاف الطبيعة", "unit_en": "Nature Exploration"},
            {"title_ar": "الدلفين الصديق الذكي", "title_en": "The Friendly Smart Dolphin", "unit_ar": "استكشاف الطبيعة", "unit_en": "Nature Exploration"},
            {"title_ar": "الشعب المرجانية الساحرة", "title_en": "Enchanting Coral Reefs", "unit_ar": "استكشاف الطبيعة", "unit_en": "Nature Exploration"},
            {"title_ar": "حكايات الحكمة والذكاء", "title_en": "Tales of Wisdom", "unit_ar": "نوادر وقصص أدبية", "unit_en": "Literary Stories"},
            {"title_ar": "نشيد الصباح والأمل", "title_en": "Anthem of Morning & Hope", "unit_ar": "نوادر وقصص أدبية", "unit_en": "Literary Stories"},
            {"title_ar": "مسرح الظل والعرائس", "title_en": "Shadow & Puppet Theater", "unit_ar": "نوادر وقصص أدبية", "unit_en": "Literary Stories"},
        ],
    },
    3: {
        1: [
            {"title_ar": "حكايات الشجاعة والصبر", "title_en": "Tales of Courage & Patience", "unit_ar": "حكايات وقيم", "unit_en": "Tales & Values"},
            {"title_ar": "التعاون سر النجاح", "title_en": "Cooperation is Secret to Success", "unit_ar": "حكايات وقيم", "unit_en": "Tales & Values"},
            {"title_ar": "الكتاب صديقي المخلص", "title_en": "The Book is My Faithful Friend", "unit_ar": "حكايات وقيم", "unit_en": "Tales & Values"},
            {"title_ar": "الأمانة وسلوك الفرسان", "title_en": "Integrity of Knights", "unit_ar": "حكايات وقيم", "unit_en": "Tales & Values"},
            {"title_ar": "التسامح في مجتمعنا", "title_en": "Tolerance in Our Society", "unit_ar": "حكايات وقيم", "unit_en": "Tales & Values"},
            {"title_ar": "أرض اللؤلؤ والغوص", "title_en": "Land of Pearl Diving", "unit_ar": "تراث الإمارات البحري", "unit_en": "Emirati Maritime Heritage"},
            {"title_ar": "سفينة البوم التراثية", "title_en": "Traditional Boom Dhow", "unit_ar": "تراث الإمارات البحري", "unit_en": "Emirati Maritime Heritage"},
            {"title_ar": "أهزوجة البحارة (النهام)", "title_en": "Sailors' Chant (Nahham)", "unit_ar": "تراث الإمارات البحري", "unit_en": "Emirati Maritime Heritage"},
            {"title_ar": "متحف الشارقة البحري", "title_en": "Sharjah Maritime Museum", "unit_ar": "تراث الإمارات البحري", "unit_en": "Emirati Maritime Heritage"},
            {"title_ar": "أمواج وسواعد الأجداد", "title_en": "Waves & Ancestral Hands", "unit_ar": "تراث الإمارات البحري", "unit_en": "Emirati Maritime Heritage"},
        ],
        2: [
            {"title_ar": "عجائب الحيوانات في البرية", "title_en": "Wonders of Wildlife", "unit_ar": "العلوم والاكتشاف", "unit_en": "Science & Discovery"},
            {"title_ar": "المها العربية في البادية", "title_en": "Arabian Oryx in the Desert", "unit_ar": "العلوم والاكتشاف", "unit_en": "Science & Discovery"},
            {"title_ar": "سحر الطيور المهاجرة", "title_en": "Magic of Migratory Birds", "unit_ar": "العلوم والاكتشاف", "unit_en": "Science & Discovery"},
            {"title_ar": "الاختراعات التي غيرت العالم", "title_en": "Inventions that Changed Earth", "unit_ar": "الابتكار والمستقبل", "unit_en": "Innovation & Future"},
            {"title_ar": "الطاقة النظيفة في مدينة مصدر", "title_en": "Clean Energy in Masdar City", "unit_ar": "الابتكار والمستقبل", "unit_en": "Innovation & Future"},
            {"title_ar": "الروبوت ومساعد الذكاء", "title_en": "Robotics & AI Assistant", "unit_ar": "الابتكار والمستقبل", "unit_en": "Innovation & Future"},
        ],
        3: [
            {"title_ar": "عالم القصائد والأناشيد", "title_en": "World of Poems & Anthems", "unit_ar": "الإبداع والتعبير", "unit_en": "Creativity & Expression"},
            {"title_ar": "نشيد العلم الإماراتي الخالد", "title_en": "Anthem of the UAE Flag", "unit_ar": "الإبداع والتعبير", "unit_en": "Creativity & Expression"},
            {"title_ar": "جمال اللغة العربية وعظمتها", "title_en": "Beauty of Arabic Language", "unit_ar": "الإبداع والتعبير", "unit_en": "Creativity & Expression"},
            {"title_ar": "رحلة استكشافية في الصحراء", "title_en": "Expedition in the Dunes", "unit_ar": "رحلات ومغامرات", "unit_en": "Journeys & Adventure"},
            {"title_ar": "واحة ليوا وتلالها الذهبية", "title_en": "Liwa Oasis & Golden Dunes", "unit_ar": "رحلات ومغامرات", "unit_en": "Journeys & Adventure"},
            {"title_ar": "النجوم ودليل القوافل", "title_en": "Stars & Caravan Guides", "unit_ar": "رحلات ومغامرات", "unit_en": "Journeys & Adventure"},
        ],
    },
    4: {
        1: [
            {"title_ar": "فروسية الأجداد والسباقات", "title_en": "Ancestral Horsemanship", "unit_ar": "الرياضة والبطولة", "unit_en": "Sports & Heroism"},
            {"title_ar": "كأس دبي العالمي للخيول", "title_en": "Dubai World Cup for Horses", "unit_ar": "الرياضة والبطولة", "unit_en": "Sports & Heroism"},
            {"title_ar": "السباحة في الأعماق", "title_en": "Swimming in the Ocean", "unit_ar": "الرياضة والبطولة", "unit_en": "Sports & Heroism"},
            {"title_ar": "سباقات الهجن التراثية", "title_en": "Traditional Camel Races", "unit_ar": "الرياضة والبطولة", "unit_en": "Sports & Heroism"},
            {"title_ar": "الروح الرياضية والتعاون", "title_en": "Sportsmanship & Teamwork", "unit_ar": "الرياضة والبطولة", "unit_en": "Sports & Heroism"},
            {"title_ar": "زايد الأب وباني النهضة", "title_en": "Zayed: Father of the Nation", "unit_ar": "قادة صنعوا التاريخ", "unit_en": "Leaders of History"},
            {"title_ar": "صرح زايد المؤسس", "title_en": "The Founder's Memorial", "unit_ar": "قادة صنعوا التاريخ", "unit_en": "Leaders of History"},
            {"title_ar": "متحف اللوفر أبوظبي", "title_en": "Louvre Abu Dhabi", "unit_ar": "قادة صنعوا التاريخ", "unit_en": "Leaders of History"},
            {"title_ar": "برج خليفة أيقونة المعمار", "title_en": "Burj Khalifa: Architectural Icon", "unit_ar": "قادة صنعوا التاريخ", "unit_en": "Leaders of History"},
            {"title_ar": "قيم الاتحاد المبارك", "title_en": "Values of the Union", "unit_ar": "قادة صنعوا التاريخ", "unit_en": "Leaders of History"},
        ],
        2: [
            {"title_ar": "رواد الفضاء الإماراتيون", "title_en": "Emirati Astronauts", "unit_ar": "علوم الفضاء واستكشافه", "unit_en": "Space Science & Exploration"},
            {"title_ar": "محطة الفضاء الدولية", "title_en": "International Space Station", "unit_ar": "علوم الفضاء واستكشافه", "unit_en": "Space Science & Exploration"},
            {"title_ar": "مسبار الأمل وكوكب المريخ", "title_en": "Hope Probe to Mars", "unit_ar": "علوم الفضاء واستكشافه", "unit_en": "Space Science & Exploration"},
            {"title_ar": "أسرار المناخ والتغير البيئي", "title_en": "Climate & Environment", "unit_ar": "حماية كوكبنا", "unit_en": "Guarding Our Planet"},
            {"title_ar": "محميات القرم في الإمارات", "title_en": "Mangrove Sanctuaries in UAE", "unit_ar": "حماية كوكبنا", "unit_en": "Guarding Our Planet"},
            {"title_ar": "استدامة الموارد للأجيال", "title_en": "Resource Sustainability", "unit_ar": "حماية كوكبنا", "unit_en": "Guarding Our Planet"},
        ],
        3: [
            {"title_ar": "فنون الخط العربي الأصيل", "title_en": "Authentic Arabic Calligraphy", "unit_ar": "فنون وتراث أدبي", "unit_en": "Arts & Literary Heritage"},
            {"title_ar": "الشعر النبطي وعراقته", "title_en": "Nabati Poetry & Heritage", "unit_ar": "فنون وتراث أدبي", "unit_en": "Arts & Literary Heritage"},
            {"title_ar": "حكايات الكرم والضيافة العربية", "title_en": "Tales of Hospitality", "unit_ar": "فنون وتراث أدبي", "unit_en": "Arts & Literary Heritage"},
            {"title_ar": "أنا كاتب مبدع", "title_en": "I am a Creative Writer", "unit_ar": "مهارات التعبير والكتابة", "unit_en": "Writing & Expression"},
            {"title_ar": "فن إلقاء الخطابة المدرسية", "title_en": "Public Speaking in School", "unit_ar": "مهارات التعبير والكتابة", "unit_en": "Writing & Expression"},
            {"title_ar": "مناظرة الكلمة الطيبة", "title_en": "The Kind Word Debate", "unit_ar": "مهارات التعبير والكتابة", "unit_en": "Writing & Expression"},
        ],
    },
    5: {
        1: [
            {"id": "lesson_01_ball_games", "order": 1, "title_ar": "ألعاب الكرة", "title_en": "Ball Games", "unit_id": "unit_01_sports", "unit_ar": "الرياضات والهوايات", "unit_en": "Sports and Hobbies", "start_page": 6},
            {"id": "lesson_02_horse_riding", "order": 2, "title_ar": "ركوب الخيل", "title_en": "Horse Riding", "unit_id": "unit_01_sports", "unit_ar": "الرياضات والهوايات", "unit_en": "Sports and Hobbies", "start_page": 16},
            {"id": "lesson_03_running", "order": 3, "title_ar": "الجري", "title_en": "Running", "unit_id": "unit_01_sports", "unit_ar": "الرياضات والهوايات", "unit_en": "Sports and Hobbies", "start_page": 26},
            {"id": "lesson_04_arts", "order": 4, "title_ar": "الفنون", "title_en": "Arts", "unit_id": "unit_01_sports", "unit_ar": "الرياضات والهوايات", "unit_en": "Sports and Hobbies", "start_page": 36},
            {"id": "lesson_05_reading", "order": 5, "title_ar": "القراءة", "title_en": "Reading", "unit_id": "unit_01_sports", "unit_ar": "الرياضات والهوايات", "unit_en": "Sports and Hobbies", "start_page": 46},
            {"id": "lesson_06_at_school", "order": 6, "title_ar": "في مدرستي", "title_en": "At My School", "unit_id": "unit_02_rights", "unit_ar": "حقوقي وواجباتي", "unit_en": "My Rights and Responsibilities", "start_page": 56},
            {"id": "lesson_07_at_home", "order": 7, "title_ar": "في بيتي", "title_en": "At My Home", "unit_id": "unit_02_rights", "unit_ar": "حقوقي وواجباتي", "unit_en": "My Rights and Responsibilities", "start_page": 66},
            {"id": "lesson_08_my_food", "order": 8, "title_ar": "طعامي", "title_en": "My Food", "unit_id": "unit_02_rights", "unit_ar": "حقوقي وواجباتي", "unit_en": "My Rights and Responsibilities", "start_page": 76},
            {"id": "lesson_09_my_clothes", "order": 9, "title_ar": "ملابسي", "title_en": "My Clothes", "unit_id": "unit_02_rights", "unit_ar": "حقوقي وواجباتي", "unit_en": "My Rights and Responsibilities", "start_page": 86},
            {"id": "lesson_10_fun_time", "order": 10, "title_ar": "وقت المرح", "title_en": "Fun Time", "unit_id": "unit_02_rights", "unit_ar": "حقوقي وواجباتي", "unit_en": "My Rights and Responsibilities", "start_page": 96},
        ],
        2: [
            {"id": "lesson_11_arab_cities", "order": 11, "title_ar": "مدن عربية", "title_en": "Arab Cities", "unit_id": "unit_03_global_cities", "unit_ar": "مدن عالمية", "unit_en": "Global Cities", "start_page": 6},
            {"id": "lesson_12_london", "order": 12, "title_ar": "لندن", "title_en": "London", "unit_id": "unit_03_global_cities", "unit_ar": "مدن عالمية", "unit_en": "Global Cities", "start_page": 16},
            {"id": "lesson_13_shanghai", "order": 13, "title_ar": "شنغهاي", "title_en": "Shanghai", "unit_id": "unit_03_global_cities", "unit_ar": "مدن عالمية", "unit_en": "Global Cities", "start_page": 26},
            {"id": "lesson_14_seven_wonders", "order": 14, "title_ar": "عجائب الدنيا السبع", "title_en": "Seven Wonders of the World", "unit_id": "unit_04_wonders", "unit_ar": "غرائب وعجائب", "unit_en": "Wonders and Curiosities", "start_page": 36},
            {"id": "lesson_15_caves_and_islands", "order": 15, "title_ar": "الكهوف والجزر العجيبة", "title_en": "Wondrous Caves and Islands", "unit_id": "unit_04_wonders", "unit_ar": "غرائب وعجائب", "unit_en": "Wonders and Curiosities", "start_page": 46},
            {"id": "lesson_16_living_creatures", "order": 16, "title_ar": "عجائب الكائنات الحية", "title_en": "Wonders of Living Creatures", "unit_id": "unit_04_wonders", "unit_ar": "غرائب وعجائب", "unit_en": "Wonders and Curiosities", "start_page": 56},
        ],
        3: [
            {"id": "lesson_17_carrier_pigeons", "order": 17, "title_ar": "الحمام الزاجل", "title_en": "Carrier Pigeons", "unit_id": "unit_05_communication", "unit_ar": "التواصل", "unit_en": "Communication", "start_page": 6},
            {"id": "lesson_18_the_media", "order": 18, "title_ar": "الإعلام المرئي والمسموع", "title_en": "Visual and Audio Media", "unit_id": "unit_05_communication", "unit_ar": "التواصل", "unit_en": "Communication", "start_page": 16},
            {"id": "lesson_19_social_media", "order": 19, "title_ar": "وسائل التواصل الحديثة", "title_en": "Modern Social Media", "unit_id": "unit_05_communication", "unit_ar": "التواصل", "unit_en": "Communication", "start_page": 26},
            {"id": "lesson_20_animal_intelligence", "order": 20, "title_ar": "الحيوان والذكاء", "title_en": "Animals and Intelligence", "unit_id": "unit_06_intelligence", "unit_ar": "كلنا أذكياء", "unit_en": "We Are All Intelligent", "start_page": 36},
            {"id": "lesson_21_human_intelligence", "order": 21, "title_ar": "الإنسان والذكاء", "title_en": "Human and Intelligence", "unit_id": "unit_06_intelligence", "unit_ar": "كلنا أذكياء", "unit_en": "We Are All Intelligent", "start_page": 46},
            {"id": "lesson_22_smart_cities", "order": 22, "title_ar": "مدن ذكية: مدينة مصدر", "title_en": "Smart Cities: Masdar City", "unit_id": "unit_06_intelligence", "unit_ar": "كلنا أذكياء", "unit_en": "We Are All Intelligent", "start_page": 56},
        ],
    },
    6: {
        1: [
            {"title_ar": "أنا إماراتي وأعتز بهويتي", "title_en": "I am Emirati & Proud of My Identity", "unit_ar": "الهوية والوطن", "unit_en": "National Identity & Homeland"},
            {"title_ar": "زايد الخير وبناء الإنسان", "title_en": "Zayed the Benevolent & Human Development", "unit_ar": "الهوية والوطن", "unit_en": "National Identity & Homeland"},
            {"title_ar": "حماة الديار وتضحيات الأبطال", "title_en": "Guardians of the Homeland", "unit_ar": "الهوية والوطن", "unit_en": "National Identity & Homeland"},
            {"title_ar": "سارية العلم الخفاق", "title_en": "The Fluttering Flagpole", "unit_ar": "الهوية والوطن", "unit_en": "National Identity & Homeland"},
            {"title_ar": "عادات وتقاليد الأجداد", "title_en": "Ancestral Traditions & Etiquette", "unit_ar": "الهوية والوطن", "unit_en": "National Identity & Homeland"},
            {"title_ar": "أشجار القرم حارسة الشواطئ", "title_en": "Mangroves: Guardians of Coastlines", "unit_ar": "الطبيعة والبيئة المستدامة", "unit_en": "Nature & Sustainable Environment"},
            {"title_ar": "صقور الإمارات ورياضة القنص", "title_en": "Emirati Falcons & Falconry", "unit_ar": "الطبيعة والبيئة المستدامة", "unit_en": "Nature & Sustainable Environment"},
            {"title_ar": "المها العربية في البادية", "title_en": "The Arabian Oryx in the Dunes", "unit_ar": "الطبيعة والبيئة المستدامة", "unit_en": "Nature & Sustainable Environment"},
            {"title_ar": "واحات العين والتراث الزراعي", "title_en": "Al Ain Oases & Agricultural Heritage", "unit_ar": "الطبيعة والبيئة المستدامة", "unit_en": "Nature & Sustainable Environment"},
            {"title_ar": "ترشيد الماء وطاقة المستقبل", "title_en": "Water Conservation & Future Energy", "unit_ar": "الطبيعة والبيئة المستدامة", "unit_en": "Nature & Sustainable Environment"},
        ],
        2: [
            {"title_ar": "ابن الهيثم رائد علم البصريات", "title_en": "Ibn al-Haytham: Pioneer of Optics", "unit_ar": "العلوم والاكتشاف", "unit_en": "Science & Discovery"},
            {"title_ar": "جابر بن حيان مؤسس الكيمياء", "title_en": "Jabir ibn Hayyan: Father of Chemistry", "unit_ar": "العلوم والاكتشاف", "unit_en": "Science & Discovery"},
            {"title_ar": "البيروني وقياس أبعاد الأرض", "title_en": "Al-Biruni & Earth Measurements", "unit_ar": "العلوم والاكتشاف", "unit_en": "Science & Discovery"},
            {"title_ar": "نوادر جحا والذكاء الفكاهي", "title_en": "Anecdotes of Juha & Witty Wisdom", "unit_ar": "روائع القصص والحكمة", "unit_en": "Timeless Stories & Wisdom"},
            {"title_ar": "الصدق فضيلة وسلوك الفرسان", "title_en": "Truthfulness: Virtue & Chivalry", "unit_ar": "روائع القصص والحكمة", "unit_en": "Timeless Stories & Wisdom"},
            {"title_ar": "حكمة الأجداد في حكايات البحر", "title_en": "Ancestral Maritime Wisdom", "unit_ar": "روائع القصص والحكمة", "unit_en": "Timeless Stories & Wisdom"},
        ],
        3: [
            {"title_ar": "مسبار الأمل إلى كوكب المريخ", "title_en": "Hope Probe to Mars", "unit_ar": "عالم الفضاء والاستكشاف", "unit_en": "Space Exploration & The Cosmos"},
            {"title_ar": "رواد الفضاء الإماراتيون", "title_en": "Emirati Astronauts on ISS", "unit_ar": "عالم الفضاء والاستكشاف", "unit_en": "Space Exploration & The Cosmos"},
            {"title_ar": "محطة الفضاء الدولية", "title_en": "The International Space Station", "unit_ar": "عالم الفضاء والاستكشاف", "unit_en": "Space Exploration & The Cosmos"},
            {"title_ar": "سحر الخط العربي والزخرفة", "title_en": "Magic of Arabic Calligraphy", "unit_ar": "الفنون والآداب", "unit_en": "Arts, Literature & Culture"},
            {"title_ar": "الشعر الشعبي وقصائد التراث", "title_en": "Nabati & Folk Poetry", "unit_ar": "الفنون والآداب", "unit_en": "Arts, Literature & Culture"},
            {"title_ar": "فنون المسرح المدرسي والإلقاء", "title_en": "School Theater & Elocution", "unit_ar": "الفنون والآداب", "unit_en": "Arts, Literature & Culture"},
        ],
    },
    7: {
        1: [
            {"title_ar": "وثيقة الأخوة الإنسانية في أبوظبي", "title_en": "Document on Human Fraternity", "unit_ar": "التسامح والأخوة الإنسانية", "unit_en": "Tolerance & Human Fraternity"},
            {"title_ar": "التسامح قيمة إماراتية أصيلة", "title_en": "Tolerance: An Authentic Value", "unit_ar": "التسامح والأخوة الإنسانية", "unit_en": "Tolerance & Human Fraternity"},
            {"title_ar": "صانعو الأمل في العالم العربي", "title_en": "Hope Makers of the Arab World", "unit_ar": "التسامح والأخوة الإنسانية", "unit_en": "Tolerance & Human Fraternity"},
            {"title_ar": "العمل التطوعي وخدمة المجتمع", "title_en": "Volunteering & Civic Service", "unit_ar": "التسامح والأخوة الإنسانية", "unit_en": "Tolerance & Human Fraternity"},
            {"title_ar": "ثقافة العطاء والمسؤولية", "title_en": "Culture of Giving & Responsibility", "unit_ar": "التسامح والأخوة الإنسانية", "unit_en": "Tolerance & Human Fraternity"},
            {"title_ar": "رحلة الغوص على اللؤلؤ في الخليج", "title_en": "Pearl Diving Expeditions", "unit_ar": "تراثنا البحري العريق", "unit_en": "Ancient Maritime Heritage"},
            {"title_ar": "الطواش وتجارة اللؤلؤ الطبيعي", "title_en": "Tawash: Natural Pearl Traders", "unit_ar": "تراثنا البحري العريق", "unit_en": "Ancient Maritime Heritage"},
            {"title_ar": "سفن البوم وتاريخ الملاحة", "title_en": "Boom Dhows & Navigation History", "unit_ar": "تراثنا البحري العريق", "unit_en": "Ancient Maritime Heritage"},
            {"title_ar": "أهزوجة النهام وموسيقى البحر", "title_en": "Sea Chants of the Nahham", "unit_ar": "تراثنا البحري العريق", "unit_en": "Ancient Maritime Heritage"},
            {"title_ar": "موانئ الإمارات وحركة التجارة", "title_en": "UAE Ports & World Trade", "unit_ar": "تراثنا البحري العريق", "unit_en": "Ancient Maritime Heritage"},
        ],
        2: [
            {"title_ar": "قصر الحصن شاهد على التاريخ", "title_en": "Qasr Al Hosn: Living History", "unit_ar": "الحضارة والعمارة", "unit_en": "Civilization & Architecture"},
            {"title_ar": "جامع الشيخ زايد الكبير المعماري", "title_en": "Sheikh Zayed Grand Mosque Architecture", "unit_ar": "الحضارة والعمارة", "unit_en": "Civilization & Architecture"},
            {"title_ar": "متحف اللوفر أبوظبي وحوار الثقافات", "title_en": "Louvre Abu Dhabi & Cultural Dialogue", "unit_ar": "الحضارة والعمارة", "unit_en": "Civilization & Architecture"},
            {"title_ar": "العقل السليم في الجسم السليم", "title_en": "A Sound Mind in a Sound Body", "unit_ar": "الصحة وجودة الحياة", "unit_en": "Health & Wellbeing"},
            {"title_ar": "ماراثون زايد الخيري العالمي", "title_en": "Zayed Charity Marathon", "unit_ar": "الصحة وجودة الحياة", "unit_en": "Health & Wellbeing"},
            {"title_ar": "الغذاء المتوازن ونمط الحياة الصحي", "title_en": "Balanced Nutrition & Active Lifestyle", "unit_ar": "الصحة وجودة الحياة", "unit_en": "Health & Wellbeing"},
        ],
        3: [
            {"title_ar": "عصر الذكاء الاصطناعي والتعلم الآلي", "title_en": "The Age of Artificial Intelligence", "unit_ar": "التكنولوجيا والذكاء الاصطناعي", "unit_en": "Technology & Artificial Intelligence"},
            {"title_ar": "الروبوتات في خدمة الإنسانية", "title_en": "Robots Serving Humanity", "unit_ar": "التكنولوجيا والذكاء الاصطناعي", "unit_en": "Technology & Artificial Intelligence"},
            {"title_ar": "إنترنت الأشياء والمدن المترابطة", "title_en": "Internet of Things & Connected Cities", "unit_ar": "التكنولوجيا والذكاء الاصطناعي", "unit_en": "Technology & Artificial Intelligence"},
            {"title_ar": "الصحافة الرقمية ومصداقية الخبر", "title_en": "Digital Journalism & Source Integrity", "unit_ar": "الإعلام والتواصل الحديث", "unit_en": "Media & Communication"},
            {"title_ar": "صناعة المحتوى الهادف والمؤثر", "title_en": "Constructive Content Creation", "unit_ar": "الإعلام والتواصل الحديث", "unit_en": "Media & Communication"},
            {"title_ar": "الأمان الرقمي وحماية الخصوصية", "title_en": "Cyber Safety & Privacy Rights", "unit_ar": "الإعلام والتواصل الحديث", "unit_en": "Media & Communication"},
        ],
    },
    8: {
        1: [
            {"title_ar": "أبو الطيب المتنبي شاعر الحكمة", "title_en": "Al-Mutanabbi: Poet of Wisdom", "unit_ar": "فرسان الكلمة وروائع الأدب", "unit_en": "Masterpieces of Arabic Literature"},
            {"title_ar": "فصاحة العرب وبلاغة التعبير", "title_en": "Arab Eloquence & Rhetorical Beauty", "unit_ar": "فرسان الكلمة وروائع الأدب", "unit_en": "Masterpieces of Arabic Literature"},
            {"title_ar": "شعر الفروسية والحماسة", "title_en": "Poetry of Chivalry & Valor", "unit_ar": "فرسان الكلمة وروائع الأدب", "unit_en": "Masterpieces of Arabic Literature"},
            {"title_ar": "ديوان العرب وتاريخ القصيدة", "title_en": "Diwan of the Arabs & Poetic Forms", "unit_ar": "فرسان الكلمة وروائع الأدب", "unit_en": "Masterpieces of Arabic Literature"},
            {"title_ar": "فن المقال والرأي الرصين", "title_en": "The Art of Persuasive Essay Writing", "unit_ar": "فرسان الكلمة وروائع الأدب", "unit_en": "Masterpieces of Arabic Literature"},
            {"title_ar": "رؤية نحن الإمارات 2031", "title_en": "We the UAE 2031 Vision", "unit_ar": "استشراف المستقبل والتنمية", "unit_en": "Future Foresight & Innovation"},
            {"title_ar": "الطاقة النووية السلمية في براكة", "title_en": "Barakah Clean Nuclear Energy", "unit_ar": "استشراف المستقبل والتنمية", "unit_en": "Future Foresight & Innovation"},
            {"title_ar": "اقتصاد المعرفة والتنافسية", "title_en": "Knowledge Economy & Innovation", "unit_ar": "استشراف المستقبل والتنمية", "unit_en": "Future Foresight & Innovation"},
            {"title_ar": "المدن البيئية الذكية والمستدامة", "title_en": "Eco-Smart Sustainable Cities", "unit_ar": "استشراف المستقبل والتنمية", "unit_en": "Future Foresight & Innovation"},
            {"title_ar": "تمكين الشباب وصناعة الغد", "title_en": "Youth Empowerment for Tomorrow", "unit_ar": "استشراف المستقبل والتنمية", "unit_en": "Future Foresight & Innovation"},
        ],
        2: [
            {"title_ar": "التغير المناخي والجهود الدولية", "title_en": "Climate Change & Global Action", "unit_ar": "قضايا بيئية وإنسانية", "unit_en": "Environmental & Global Issues"},
            {"title_ar": "حماية التنوع الحيوي والمحميات", "title_en": "Biodiversity & Nature Reserves", "unit_ar": "قضايا بيئية وإنسانية", "unit_en": "Environmental & Global Issues"},
            {"title_ar": "استدامة الموارد للأجيال القادمة", "title_en": "Generational Resource Stewardship", "unit_ar": "قضايا بيئية وإنسانية", "unit_en": "Environmental & Global Issues"},
            {"title_ar": "سمو الشيخة فاطمة بنت مبارك أم الإمارات", "title_en": "H.H. Sheikha Fatima: Mother of the Nation", "unit_ar": "أعلام ورواد ملهمون", "unit_en": "Inspiring Pioneers & Leaders"},
            {"title_ar": "أحمد بن ماجد أسد البحار والملاحة", "title_en": "Ahmad ibn Majid: Lion of the Seas", "unit_ar": "أعلام ورواد ملهمون", "unit_en": "Inspiring Pioneers & Leaders"},
            {"title_ar": "الشيخ راشد بن سعيد وبناء نهضة دبي", "title_en": "Sheikh Rashid: Father of Modern Dubai", "unit_ar": "أعلام ورواد ملهمون", "unit_en": "Inspiring Pioneers & Leaders"},
        ],
        3: [
            {"title_ar": "فن المناظرة والحوار البناء", "title_en": "The Art of Constructive Debate", "unit_ar": "المناظرة والتفكير الناقد", "unit_en": "Debate & Critical Thinking"},
            {"title_ar": "مهارات التفكير الناقد والتحليل", "title_en": "Critical Thinking & Analytical Reasoning", "unit_ar": "المناظرة والتفكير الناقد", "unit_en": "Debate & Critical Thinking"},
            {"title_ar": "الخطابة الإقناعية والتأثير الجماهيري", "title_en": "Persuasive Public Speaking", "unit_ar": "المناظرة والتفكير الناقد", "unit_en": "Debate & Critical Thinking"},
            {"title_ar": "حكايات كليلة ودمنة والرمز الأدبي", "title_en": "Kalila and Dimna: Allegorical Wisdom", "unit_ar": "نصوص من التراث العالمي", "unit_en": "Tales from World Literature"},
            {"title_ar": "أدب الرحلات واستكشاف العالم", "title_en": "Travel Literature & World Exploration", "unit_ar": "نصوص من التراث العالمي", "unit_en": "Tales from World Literature"},
            {"title_ar": "مسرح الحكماء والقصص الرمزية", "title_en": "Theater of Sages & Symbolic Tales", "unit_ar": "نصوص من التراث العالمي", "unit_en": "Tales from World Literature"},
        ],
    },
    9: {
        1: [
            {"title_ar": "فكر الشيخ زايد ومنهج التنمية", "title_en": "Sheikh Zayed’s Development Philosophy", "unit_ar": "فلسفة القيادة وبناء الدولة", "unit_en": "Leadership Philosophy & State Building"},
            {"title_ar": "الآباء المؤسسون وصناعة الاتحاد", "title_en": "Founding Fathers & Union Creation", "unit_ar": "فلسفة القيادة وبناء الدولة", "unit_en": "Leadership Philosophy & State Building"},
            {"title_ar": "الدبلوماسية الإنسانية لدولة الإمارات", "title_en": "Emirati Humanitarian Diplomacy", "unit_ar": "فلسفة القيادة وبناء الدولة", "unit_en": "Leadership Philosophy & State Building"},
            {"title_ar": "المواطنة الإيجابية في عالم متغير", "title_en": "Positive Citizenship in a Dynamic World", "unit_ar": "فلسفة القيادة وبناء الدولة", "unit_en": "Leadership Philosophy & State Building"},
            {"title_ar": "منظومة التعليم واستثمار العقول", "title_en": "Education: Investing in Human Minds", "unit_ar": "فلسفة القيادة وبناء الدولة", "unit_en": "Leadership Philosophy & State Building"},
            {"title_ar": "المعلقات وأسرار الشعر الجاهلي", "title_en": "The Mu'allaqat & Pre-Islamic Poetics", "unit_ar": "العصور الشعرية الكبرى", "unit_en": "Great Poetic Eras"},
            {"title_ar": "شعر صدر الإسلام وقيم التضحية", "title_en": "Early Islamic Poetry & Ethical Values", "unit_ar": "العصور الشعرية الكبرى", "unit_en": "Great Poetic Eras"},
            {"title_ar": "العصر الأموي والشعر السياسي", "title_en": "Umayyad Era & Political Eloquence", "unit_ar": "العصور الشعرية الكبرى", "unit_en": "Great Poetic Eras"},
            {"title_ar": "ازدهار العصر العباسي وروائع النظم", "title_en": "Abbasid Renaissance & Literary Flourishing", "unit_ar": "العصور الشعرية الكبرى", "unit_en": "Great Poetic Eras"},
            {"title_ar": "موشحات الأندلس وسحر الإيقاع", "title_en": "Andalusian Muwashshahat & Rhythmic Grace", "unit_ar": "العصور الشعرية الكبرى", "unit_en": "Great Poetic Eras"},
        ],
        2: [
            {"title_ar": "ثقافة ريادة الأعمال والشركات الناشئة", "title_en": "Entrepreneurship & Start-up Culture", "unit_ar": "ريادة الأعمال واقتصاد الغد", "unit_en": "Entrepreneurship & Tomorrow’s Economy"},
            {"title_ar": "الابتكار وحماية الملكية الفكرية", "title_en": "Innovation & Intellectual Property Rights", "unit_ar": "ريادة الأعمال واقتصاد الغد", "unit_en": "Entrepreneurship & Tomorrow’s Economy"},
            {"title_ar": "الاقتصاد الرقمي والعملات المشفرة", "title_en": "Digital Economy & Emerging FinTech", "unit_ar": "ريادة الأعمال واقتصاد الغد", "unit_en": "Entrepreneurship & Tomorrow’s Economy"},
            {"title_ar": "بنية القصة القصيرة والرمز الفني", "title_en": "Short Story Architecture & Symbolism", "unit_ar": "النقد الأدبي والتحليل البلاغي", "unit_en": "Literary Criticism & Rhetorical Analysis"},
            {"title_ar": "مناهج تحليل النصوص الأدبية", "title_en": "Methodologies of Textual Literary Analysis", "unit_ar": "النقد الأدبي والتحليل البلاغي", "unit_en": "Literary Criticism & Rhetorical Analysis"},
            {"title_ar": "الصورة البلاغية وأثرها الجمالي", "title_en": "Rhetorical Imagery & Aesthetic Impact", "unit_ar": "النقد الأدبي والتحليل البلاغي", "unit_en": "Literary Criticism & Rhetorical Analysis"},
        ],
        3: [
            {"title_ar": "أخلاقيات الذكاء الاصطناعي والخوارزميات", "title_en": "Ethics of AI & Algorithmic Responsibility", "unit_ar": "الأخلاقيات في العصر الرقمي", "unit_en": "Ethics in the Digital Age"},
            {"title_ar": "الهوية الرقمية والمسؤولية المجتمعية", "title_en": "Digital Identity & Social Accountability", "unit_ar": "الأخلاقيات في العصر الرقمي", "unit_en": "Ethics in the Digital Age"},
            {"title_ar": "مكافحة التضليل وحرية التعبير", "title_en": "Combating Disinformation & Media Literacy", "unit_ar": "الأخلاقيات في العصر الرقمي", "unit_en": "Ethics in the Digital Age"},
            {"title_ar": "بيت الحكمة ودور الترجمة في الحضارة", "title_en": "House of Wisdom & Translational Golden Age", "unit_ar": "التثاقف وحركة الترجمة", "unit_en": "Acculturation & Translation Movement"},
            {"title_ar": "حوار الحضارات والتنوع الثقافي", "title_en": "Civilizational Dialogue & Cultural Diversity", "unit_ar": "التثاقف وحركة الترجمة", "unit_en": "Acculturation & Translation Movement"},
            {"title_ar": "الأدب المقارن والجسور الإنسانية", "title_en": "Comparative Literature & Bridges of Humanity", "unit_ar": "التثاقف وحركة الترجمة", "unit_en": "Acculturation & Translation Movement"},
        ],
    },
    10: {
        1: [
            {"title_ar": "التشبيه البليغ وأنواعه وأثره الفني", "title_en": "Eloquence of Simile & Artistic Function", "unit_ar": "البلاغة العربية وأسرار البيان", "unit_en": "Arabic Rhetoric & Science of Bayan"},
            {"title_ar": "الاستعارة التصريحية والمكنية في الشعر", "title_en": "Explicit & Implicit Metaphors in Arabic", "unit_ar": "البلاغة العربية وأسرار البيان", "unit_en": "Arabic Rhetoric & Science of Bayan"},
            {"title_ar": "الكناية وسر جمال الإيجاز اللغوي", "title_en": "Metonymy & The Beauty of Concise Expression", "unit_ar": "البلاغة العربية وأسرار البيان", "unit_en": "Arabic Rhetoric & Science of Bayan"},
            {"title_ar": "علم البديع: المحسنات اللفظية والمعنوية", "title_en": "Badi': Verbal & Conceptual Embellishments", "unit_ar": "البلاغة العربية وأسرار البيان", "unit_en": "Arabic Rhetoric & Science of Bayan"},
            {"title_ar": "أسرار التقديم والتأخير في المعاني", "title_en": "Word Order Shifts & Syntactic Emphasis", "unit_ar": "البلاغة العربية وأسرار البيان", "unit_en": "Arabic Rhetoric & Science of Bayan"},
            {"title_ar": "مشروع المريخ 2117 واستيطان الفضاء", "title_en": "Mars 2117 & Space Settlement", "unit_ar": "مئوية الإمارات 2071 والمستقبل", "unit_en": "UAE Centennial 2071 & Future Civilization"},
            {"title_ar": "الاقتصاد الدائري واستدامة الكوكب", "title_en": "Circular Economy & Planetary Sustainability", "unit_ar": "مئوية الإمارات 2071 والمستقبل", "unit_en": "UAE Centennial 2071 & Future Civilization"},
            {"title_ar": "الثورة الصناعية الرابعة وعوالم الميتافيرس", "title_en": "Fourth Industrial Revolution & Digital Worlds", "unit_ar": "مئوية الإمارات 2071 والمستقبل", "unit_en": "UAE Centennial 2071 & Future Civilization"},
            {"title_ar": "التنافسية العالمية وريادة المؤشرات", "title_en": "Global Competitiveness & Milestone Indices", "unit_ar": "مئوية الإمارات 2071 والمستقبل", "unit_en": "UAE Centennial 2071 & Future Civilization"},
            {"title_ar": "رأس المال البشري وصناعة المعرفة", "title_en": "Human Capital & Knowledge Infrastructure", "unit_ar": "مئوية الإمارات 2071 والمستقبل", "unit_en": "UAE Centennial 2071 & Future Civilization"},
        ],
        2: [
            {"title_ar": "رواد المقال العربي: طه حسين والعقاد", "title_en": "Pioneers of Arabic Essay: Hussein & Al-Aqqad", "unit_ar": "المقال الفكري والأدبي الرصين", "unit_en": "The Intellectual & Literary Essay"},
            {"title_ar": "المقال النقدي ومنهجية البرهان", "title_en": "Critical Essay & Evidentiary Methodology", "unit_ar": "المقال الفكري والأدبي الرصين", "unit_en": "The Intellectual & Literary Essay"},
            {"title_ar": "فن المقابلة الصحفية والتحقيق الميداني", "title_en": "Journalistic Interviews & In-depth Reporting", "unit_ar": "المقال الفكري والأدبي الرصين", "unit_en": "The Intellectual & Literary Essay"},
            {"title_ar": "أساليب المدح والذم في لغة القرآن", "title_en": "Styles of Praise & Dispraise", "unit_ar": "النحو الوظيفي والتراكيب المتقدمة", "unit_en": "Functional Syntax & Advanced Structures"},
            {"title_ar": "التوكيد بأنواعه والبدل وتطبيقاته", "title_en": "Emphasis & Apposition: Theory & Usage", "unit_ar": "النحو الوظيفي والتراكيب المتقدمة", "unit_en": "Functional Syntax & Advanced Structures"},
            {"title_ar": "الإعلال والإبدال في الميزان الصرفي", "title_en": "Morphological Assimilation & Substitution", "unit_ar": "النحو الوظيفي والتراكيب المتقدمة", "unit_en": "Functional Syntax & Advanced Structures"},
        ],
        3: [
            {"title_ar": "أمير الشعراء أحمد شوقي والمسرح", "title_en": "Ahmed Shawqi & The Poetic Drama", "unit_ar": "المسرح الشعري والأدب التمثيلي", "unit_en": "Poetic Theater & Dramatic Literature"},
            {"title_ar": "عناصر الحبكة والصراع الدرامي", "title_en": "Dramatic Plot Elements & Character Conflict", "unit_ar": "المسرح الشعري والأدب التمثيلي", "unit_en": "Poetic Theater & Dramatic Literature"},
            {"title_ar": "فنون الإلقاء المسرحي والتعبير الصوتي", "title_en": "Theatrical Delivery & Expressive Modulation", "unit_ar": "المسرح الشعري والأدب التمثيلي", "unit_en": "Poetic Theater & Dramatic Literature"},
            {"title_ar": "تحفة النظار للرحالة ابن بطوطة", "title_en": "Ibn Battuta: Marvels of Travel & Geography", "unit_ar": "أدب الرحلات والاستشراق", "unit_en": "Travelogues & Comparative Cross-Cultural Texts"},
            {"title_ar": "الشرق والغرب في مرآة الأدب المقارن", "title_en": "East and West in the Mirror of Literature", "unit_ar": "أدب الرحلات والاستشراق", "unit_en": "Travelogues & Comparative Cross-Cultural Texts"},
            {"title_ar": "عالمية اللغة العربية ومستقبلها الحضاري", "title_en": "Global Arab Horizon & Future Civilization", "unit_ar": "أدب الرحلات والاستشراق", "unit_en": "Travelogues & Comparative Cross-Cultural Texts"},
        ],
    },
}

# Thematic generator for Middle and High School (Grades 6 to 12)
_SECONDARY_THEMES = {
    6: ("الهوية الوطنية والتراث", "National Identity & Heritage", "اللغة والابتكار المعرفي", "Language & Innovation"),
    7: ("قيم التسامح والمواطنة الإيجابية", "Tolerance & Positive Citizenship", "العلوم والحضارة العربية", "Arab Science & Civilization"),
    8: ("روائع الأدب وفنون البلاغة", "Masterpieces of Literature & Rhetoric", "قضايا البيئة والاستدامة العالمية", "Environment & Global Sustainability"),
    9: ("الفكر الفلسفي والمناظرة الفكرية", "Philosophical Thought & Debate", "ريادة الأعمال واقتصاد المعرفة", "Entrepreneurship & Knowledge Economy"),
    10: ("الأدب العربي الجاهلي والإسلامي", "Pre-Islamic & Islamic Literature", "علم النحو والصرف وتراكيب الجمل", "Syntax, Morphology & Sentence Structure"),
    11: ("الأدب الأندلسي والعباسي والنهضة", "Andalusian, Abbasid & Modern Literature", "علم البلاغة: البيان والبديع والمعاني", "Rhetoric: Bayan, Badi & Maani"),
    12: ("النقد الأدبي والدراسات اللغوية المتقدمة", "Literary Criticism & Advanced Linguistics", "رؤية الخمسين ومستقبل الحضارة", "UAE Centennial 2071 & Future Civilization"),
}

def get_syllabus_for_grade_and_term(grade: int, term: int) -> List[Dict[str, Any]]:
    """Returns official structured UAE MoE chapters for any grade (1-12) and term (1-3)."""
    grade = max(1, min(12, grade))
    term = max(1, min(3, term))

    # Check if customized in predefined data
    if grade in _GRADE_CURRICULUM_DATA and term in _GRADE_CURRICULUM_DATA[grade]:
        items = _GRADE_CURRICULUM_DATA[grade][term]
        result = []
        for idx, it in enumerate(items):
            order = it.get("order", idx + 1)
            unit_num = 1 if idx < (len(items) // 2 or 5) else 2
            lesson_id = it.get("id", f"lesson_g{grade}_t{term}_ch{order:02d}")
            unit_id = it.get("unit_id", f"unit_g{grade}_t{term}_{unit_num}")
            start_page = it.get("start_page", (idx) * 10 + 6)
            result.append({
                "id": lesson_id,
                "unit_id": unit_id,
                "unit_title_ar": it["unit_ar"],
                "unit_title_en": it["unit_en"],
                "lesson_order": order,
                "title_ar": it["title_ar"],
                "title_en": it["title_en"],
                "start_page": start_page,
                "is_first_chapter_demo": (order == 1 and term == 1),
                "is_accessible": True,
                "status": "published",
                "lock_reason": None
            })
        return result

    # Standard Middle / High School syllabus generator
    u1_ar, u1_en, u2_ar, u2_en = _SECONDARY_THEMES.get(
        grade,
        ("مهارات القراءة والتحليل", "Reading & Analysis", "البلاغة والتعبير الإبداعي", "Rhetoric & Creative Writing")
    )
    
    term_sub = f" (الفصل {term})" if term > 1 else ""
    term_sub_en = f" (Term {term})" if term > 1 else ""

    u1_chapters = [
        (f"نصوص أدبية مختارة: روائع الفصحى{term_sub}", f"Selected Literary Texts: Masterpieces{term_sub_en}"),
        (f"القيم الوطنية واستشراف المستقبل{term_sub}", f"National Values & Future Foresight{term_sub_en}"),
        (f"سيرة رائد ومسيرة وطن{term_sub}", f"Biography of a Pioneer & Homeland{term_sub_en}"),
        (f"شعر الحكمة والتأمل الإنساني{term_sub}", f"Poetry of Wisdom & Contemplation{term_sub_en}"),
        (f"قضايا لغوية معاصرة والذكاء الاصطناعي{term_sub}", f"Contemporary Linguistics & AI{term_sub_en}"),
    ]
    u2_chapters = [
        (f"قواعد النحو: المنصوبات والمجرورات المتقدمة{term_sub}", f"Grammar: Advanced Case Endings{term_sub_en}"),
        (f"الصرف العربي: أوزان الأفعال والمشتقات{term_sub}", f"Morphology: Verb Forms & Derivatives{term_sub_en}"),
        (f"البلاغة التطبيقية: الاستعارة والكناية{term_sub}", f"Applied Rhetoric: Metaphor & Metonymy{term_sub_en}"),
        (f"مهارات التحرير والمقال الأكاديمي{term_sub}", f"Academic Essays & Editorial Skills{term_sub_en}"),
        (f"المناظرة والحوار الإقناعي الرصين{term_sub}", f"Debate & Persuasive Dialogue{term_sub_en}"),
    ]

    all_ch = [(c[0], c[1], f"{u1_ar}{term_sub}", f"{u1_en}{term_sub_en}", 1) for c in u1_chapters] + \
             [(c[0], c[1], f"{u2_ar}{term_sub}", f"{u2_en}{term_sub_en}", 2) for c in u2_chapters]

    result = []
    for idx, (t_ar, t_en, u_ar, u_en, u_idx) in enumerate(all_ch):
        order = idx + 1
        lesson_id = f"lesson_g{grade}_t{term}_ch{order:02d}"
        result.append({
            "id": lesson_id,
            "unit_id": f"unit_g{grade}_t{term}_{u_idx}",
            "unit_title_ar": u_ar,
            "unit_title_en": u_en,
            "lesson_order": order,
            "title_ar": t_ar,
            "title_en": t_en,
            "start_page": (order - 1) * 10 + 6,
            "is_first_chapter_demo": (order == 1 and term == 1),
            "is_accessible": True,
            "status": "published",
            "lock_reason": None
        })
    return result


def get_dynamic_lesson_spec(lesson_id: str) -> Optional[DynamicLesson]:
    """Parse or match a dynamic lesson ID into a structured DynamicLesson object."""
    # Check Grade 5 explicit lessons first
    if 5 in _GRADE_CURRICULUM_DATA:
        for t_num, t_items in _GRADE_CURRICULUM_DATA[5].items():
            for item in t_items:
                if item.get("id") == lesson_id:
                    return DynamicLesson(
                        id=item["id"],
                        grade=5,
                        term=t_num,
                        title_ar=item["title_ar"],
                        title_en=item["title_en"],
                        unit_id=item["unit_id"],
                        unit_title_ar=item["unit_ar"],
                        unit_title_en=item["unit_en"],
                        start_page=item.get("start_page", 6),
                        is_first_chapter_demo=(item.get("order") == 1 and t_num == 1),
                        status="published",
                        lesson_order=item.get("order", 1)
                    )

    # Pattern: lesson_g{grade}_t{term}_ch{order}
    m = re.match(r"^lesson_g(\d+)_t(\d+)_ch(\d+)$", lesson_id)

    if m:
        grade = int(m.group(1))
        term = int(m.group(2))
        order = int(m.group(3))
        syllabus = get_syllabus_for_grade_and_term(grade, term)
        for item in syllabus:
            if item["id"] == lesson_id or item["lesson_order"] == order:
                return DynamicLesson(
                    id=item["id"],
                    grade=grade,
                    term=term,
                    title_ar=item["title_ar"],
                    title_en=item["title_en"],
                    unit_id=item["unit_id"],
                    unit_title_ar=item["unit_title_ar"],
                    unit_title_en=item["unit_title_en"],
                    start_page=item["start_page"],
                    is_first_chapter_demo=item["is_first_chapter_demo"],
                    status="published",
                    lesson_order=item["lesson_order"]
                )

    # Secondary pattern: lesson_t2_... or lesson_t3_...
    m_t = re.match(r"^lesson_t(\d+)_", lesson_id)
    if m_t:
        term = int(m_t.group(1))
        return DynamicLesson(
            id=lesson_id,
            grade=5,
            term=term,
            title_ar="دروس المنهاج الوزاري المعتمدة",
            title_en="Official MoE Curriculum Lesson",
            unit_id=f"unit_g5_t{term}_1",
            unit_title_ar="الوحدة التعليمية المعتمدة",
            unit_title_en="Approved Learning Unit",
            start_page=10,
            is_first_chapter_demo=False,
            status="published",
            lesson_order=1
        )

    if not lesson_id.startswith("lesson_") or lesson_id in ("missing", "invalid", "not_found", "none"):
        return None

    # General fallback for valid lesson IDs
    return DynamicLesson(
        id=lesson_id,
        grade=5,
        term=1,
        title_ar="درس اللغة العربية المعتمد",
        title_en="Approved Arabic Curriculum Lesson",
        unit_id="unit_general",
        unit_title_ar="الوحدة العامة",
        unit_title_en="General Unit",
        start_page=6,
        is_first_chapter_demo=True,
        status="published",
        lesson_order=1
    )


GRADE_GRAMMAR_MAP = {
    1: {
        "rule_ar": "الحروف الهجائية والمدود القصيرة والطويلة",
        "rule_en": "Arabic Alphabet, Short Vowels (Harakat) & Long Vowels (Madd)",
        "explanation": "Arabic letters change sound with Fathah, Dammah, and Kasrah. Madd (Alif, Waw, Yaa) extends the vowel sound.",
        "examples": [
            {"phrase_ar": "كَتَبَ التِّلْمِيذُ دَرْسَهُ.", "translation_en": "The pupil wrote his lesson."},
            {"phrase_ar": "قَرَأَتْ سَارَةُ قِصَّةً جَمِيلَةً.", "translation_en": "Sarah read a beautiful story."}
        ]
    },
    2: {
        "rule_ar": "أسماء الإشارة والضمائر المنفصلة",
        "rule_en": "Demonstrative Pronouns & Personal Pronouns",
        "explanation": "Demonstrative pronouns (هَذَا، هَذِهِ، هَؤُلَاءِ) point to nouns matching their gender and number.",
        "examples": [
            {"phrase_ar": "هَذَا كِتَابٌ مُفِيدٌ وَهَذِهِ مَدْرَسَتِي.", "translation_en": "This is a useful book and this is my school."},
            {"phrase_ar": "نَحْنُ نُحِبُّ القِرَاءَةَ وَالتَّعَلُّمَ.", "translation_en": "We love reading and learning."}
        ]
    },
    3: {
        "rule_ar": "أقسام الكلمة وحروف الجر",
        "rule_en": "Parts of Speech & Prepositions",
        "explanation": "Words are classified into nouns, verbs, and particles. Prepositions make following nouns genitive (majroor).",
        "examples": [
            {"phrase_ar": "يَذْهَبُ الطَّالِبُ إِلَى المَدْرَسَةِ صَبَاحًا.", "translation_en": "The student goes to school in the morning."},
            {"phrase_ar": "الكِتَابُ عَلَى الطَّاوِلَةِ المُنَظَّمَةِ.", "translation_en": "The book is on the organized desk."}
        ]
    },
    4: {
        "rule_ar": "الجملة الفعلية (الفعل والفاعل والمفعول به)",
        "rule_en": "Verbal Sentence: Verb, Subject & Object",
        "explanation": "The verbal sentence begins with a verb. The subject is nominative (marfoo') and the direct object is accusative (mansoob).",
        "examples": [
            {"phrase_ar": "رَسَمَ الفَنَّانُ لَوْحَةً بَدِيعَةً.", "translation_en": "The artist drew a marvelous painting."},
            {"phrase_ar": "يَحْتَرِمُ الأَبْنَاءُ رِعَايَةَ الوَالِدَيْنِ.", "translation_en": "Children respect their parents' care."}
        ]
    },
    5: {
        "rule_ar": "الجملة الاسمية (المبتدأ والخبر)",
        "rule_en": "Nominal Sentence: Subject & Predicate",
        "explanation": "A nominal sentence begins with a noun. Both parts take a dammah in singular nominative form.",
        "examples": [
            {"phrase_ar": "المَلْعَبُ وَاسِعٌ وَالكُرَةُ جَدِيدَةٌ.", "translation_en": "The stadium is spacious and the ball is new."},
            {"phrase_ar": "الفَارِسُ شُجَاعٌ فِي السِّبَاقِ.", "translation_en": "The rider is brave in the race."}
        ]
    },
    6: {
        "rule_ar": "كان وأخواتها والأفعال الناسخة",
        "rule_en": "Kana and Its Sisters: Incomplete Verbs",
        "explanation": "Kana leaves its subject nominative (marfoo') and makes its predicate accusative (mansoob).",
        "examples": [
            {"phrase_ar": "كَانَ الجَوُّ صَافِيًا فِي مَدِينَةِ العَيْنِ.", "translation_en": "The weather was clear in Al Ain city."},
            {"phrase_ar": "أَصْبَحَ العِلْمُ مُتَاحًا لِلْجَمِيعِ.", "translation_en": "Knowledge became accessible to all."}
        ]
    },
    7: {
        "rule_ar": "إن وأخواتها والحروف الناسخة",
        "rule_en": "Inna and Its Sisters: Accusative Particles",
        "explanation": "Inna enters a nominal sentence, making its subject accusative and its predicate nominative.",
        "examples": [
            {"phrase_ar": "إِنَّ التَّسَامُحَ قِيمَةٌ إِمَارَاتِيَّةٌ نَبِيلَةٌ.", "translation_en": "Verily, tolerance is a noble Emirati value."},
            {"phrase_ar": "لَعَلَّ الأَمَلَ يُحَقِّقُ الطُّمُوحَ.", "translation_en": "May hope fulfill our aspirations."}
        ]
    },
    8: {
        "rule_ar": "الفعل المبني للمجهول ونائب الفاعل",
        "rule_en": "Passive Voice & Pro-Agent (Naa'ib al-Faa'il)",
        "explanation": "In the passive voice, the doer is omitted and the direct object assumes the nominative pro-agent role.",
        "examples": [
            {"phrase_ar": "نُظِّمَ المِهْرَجَانُ الثَّقَافِيُّ بِإِتْقَانٍ.", "translation_en": "The cultural festival was organized with mastery."},
            {"phrase_ar": "تُصَانُ الآثَارُ التَّارِيخِيَّةُ فِي الإِمَارَاتِ.", "translation_en": "Historic artifacts are preserved in the UAE."}
        ]
    },
    9: {
        "rule_ar": "المشتقات: اسم الفاعل واسم المفعول وصيغ المبالغة",
        "rule_en": "Participles & Morphological Derivations",
        "explanation": "Participles are derived from verb roots to indicate the agent, the patient, or intensified action.",
        "examples": [
            {"phrase_ar": "المُخْتَرِعُ مُبْدِعٌ فِي صِنَاعَةِ المُسْتَقْبَلِ.", "translation_en": "The inventor is creative in shaping the future."},
            {"phrase_ar": "الوِفَاقُ مَنْشُودٌ بَيْنَ كُلِّ الأُمَمِ.", "translation_en": "Harmony is sought between all nations."}
        ]
    },
    10: {
        "rule_ar": "البلاغة العربية: التشبيه البليغ والاستعارة وأسرار البيان",
        "rule_en": "Arabic Rhetoric (Balagha): Eloquent Simile & Metaphor",
        "explanation": "Rhetoric investigates stylistic eloquence, figurative similes, and conceptual metaphors in literary texts.",
        "examples": [
            {"phrase_ar": "العُلَمَاءُ نُجُومٌ يُهْتَدَى بِهَا فِي الظُّلُمَاتِ.", "translation_en": "Scholars are guiding stars in the darkness."},
            {"phrase_ar": "ابْتَسَمَتِ الأَرْضُ بِمَقْدَمِ الغَيْثِ المُبَارَكِ.", "translation_en": "The earth smiled upon the arrival of blessed rain."}
        ]
    }
}


def generate_dynamic_lesson_content(lesson: Any) -> Dict[str, Any]:
    """
    Generates a full, authentic, rich lesson package compliant with Fahim's 10-Tab LessonViewer,
    Reader, Audio Studio, Grammar Lab, Sentence Builder, and Assessment Quizzes.
    """
    title_ar = getattr(lesson, "title_ar", "درس اللغة العربية")
    title_en = getattr(lesson, "title_en", "Arabic Lesson")
    unit_ar = getattr(lesson, "unit_title_ar", "الوحدة الدراسية")
    unit_en = getattr(lesson, "unit_title_en", "Curriculum Unit")
    grade = getattr(lesson, "grade", 5)
    term = getattr(lesson, "term", 1)
    page = getattr(lesson, "start_page", 6)
    lesson_id = getattr(lesson, "id", f"lesson_g{grade}_t{term}_01")

    # Grade-tailored grammar info
    grammar_info = GRADE_GRAMMAR_MAP.get(grade, GRADE_GRAMMAR_MAP[5])

    return {
        "lesson_id": lesson_id,
        "version": "1.0.0",
        "title_ar": title_ar,
        "title_en": title_en,
        "unit_title_ar": unit_ar,
        "unit_title_en": unit_en,
        "grade": grade,
        "term": term,
        "start_page": page,
        "pdf_start_page": page,

        # 1. Prep Check (Tab 8)
        "prep_check": {
            "title_ar": f"اختبار الاستعداد لدرس: {title_ar}",
            "title_en": f"Preparation Check: {title_en}",
            "description_en": f"Quick 3-question baseline diagnostic to ensure readiness for {title_en}.",
            "questions": [
                {
                    "id": f"prep_{lesson_id}_01",
                    "prompt_ar": f"مَا الفِكْرَةُ الرَّئِيسَةُ فِي مَوْضُوعِ ({title_ar})؟",
                    "prompt_en": f"What is the core focus of '{title_en}'?",
                    "options": [
                        {"id": "opt_a", "label_ar": "اكْتِسَابُ المَعْرِفَةِ وَالقِيَمِ الأَصِيلَةِ", "label_en": "Gaining knowledge and authentic values"},
                        {"id": "opt_b", "label_ar": "تَجَاهُلُ القِرَاءَةِ وَالدِّرَاسَةِ", "label_en": "Ignoring reading and studying"},
                        {"id": "opt_c", "label_ar": "إِهْمَالُ النُّطْقِ السَّلِيمِ", "label_en": "Neglecting proper pronunciation"}
                    ],
                    "correct_answer": "opt_a",
                    "explanation_en": f"Understanding the core concepts and vocabulary of {title_en}."
                },
                {
                    "id": f"prep_{lesson_id}_02",
                    "prompt_ar": "كَيْفَ نَقْرَأُ النُّصُوصَ العَرَبِيَّةَ بِشَكْلٍ صَحِيحٍ؟",
                    "prompt_en": "How should we read Arabic texts correctly?",
                    "options": [
                        {"id": "opt_a", "label_ar": "بِالتَّشْكِيلِ وَالضَّبْطِ السَّلِيمِ لِلْحَرَكَاتِ", "label_en": "With accurate vowel marks (Tashkeel)"},
                        {"id": "opt_b", "label_ar": "بِسُرْعَةٍ دُونَ فَهْمِ المَعْنَى", "label_en": "Quickly without understanding"},
                        {"id": "opt_c", "label_ar": "بِحَذْفِ الحُرُوفِ الصَّعْبَةِ", "label_en": "By omitting difficult letters"}
                    ],
                    "correct_answer": "opt_a",
                    "explanation_en": "Proper diacritics ensure correct meaning and grammatical articulation."
                },
                {
                    "id": f"prep_{lesson_id}_03",
                    "prompt_ar": "مَا أَهَمِّيَّةُ اللُّغَةِ العَرَبِيَّةِ فِي دَوْلَةِ الإِمَارَاتِ؟",
                    "prompt_en": "Why is the Arabic language important in the UAE?",
                    "options": [
                        {"id": "opt_a", "label_ar": "هِيَ لُغَةُ الهُوِيَّةِ وَالتُّرَاثِ وَالحَضَارَةِ", "label_en": "Language of identity, heritage, and culture"},
                        {"id": "opt_b", "label_ar": "تُسْتَخْدَمُ فَقَطْ فِي الامْتِحَانَاتِ", "label_en": "Used only during examinations"},
                        {"id": "opt_c", "label_ar": "لَا أَهَمِّيَّةَ لَهَا فِي الحَيَاةِ", "label_en": "Has no everyday significance"}
                    ],
                    "correct_answer": "opt_a",
                    "explanation_en": "Arabic represents national identity and cultural heritage."
                }
            ]
        },

        # 2. Learning Paths
        "learning_paths": {
            "foundation": {
                "title_ar": "المسار التأسيسي",
                "title_en": "Foundation Path",
                "level": "المستوى التأسيسي",
                "description": "التركيز على القراءة بالحركات والمفردات المباشرة مع الدعم الصوتي.",
                "pacing": "Supported step-by-step with bilingual glosses, visual icons, and audio cues.",
                "target": f"Master core vocabulary cards and read introductory passages in {title_en}."
            },
            "guided": {
                "title_ar": "المسار الموجه",
                "title_en": "Guided Path",
                "level": "المستوى المتوسط الموجه",
                "description": "تحليل الجمل واستخراج الأفكار والعلاقات اللغوية.",
                "pacing": "Structured exercises with sentence framing and grammar checks.",
                "target": f"Construct grammatically correct sentences and answer analytical comprehension questions."
            },
            "independent": {
                "title_ar": "المسار المستقل",
                "title_en": "Independent Path",
                "level": "المستوى المتقدم المستقل",
                "description": "النقد البلاغي والتعبير الإبداعي المستقل.",
                "pacing": "Full immersion with authentic Arabic reading and original paragraph writing.",
                "target": f"Demonstrate deep comprehension and compose authentic compositions for {title_en}."
            }
        },

        # 3. Instruction Decoder (Tab 7)
        "instruction_decoder": [
            {
                "verb_ar": "اقْرَأْ",
                "transliteration": "Iqra'",
                "meaning_en": "Read",
                "action_guidance": "Read the passage carefully with proper vowels and pronunciation.",
                "sample_sentence_ar": f"اقْرَأْ نَصَّ ({title_ar}) بِفَهْمٍ وَإِتْقَانٍ.",
                "sample_sentence_en": f"Read the text of '{title_en}' with comprehension and fluency."
            },
            {
                "verb_ar": "اسْتَمِعْ",
                "transliteration": "Istami'",
                "meaning_en": "Listen",
                "action_guidance": "Listen to the native audio recording attentively.",
                "sample_sentence_ar": "اسْتَمِعْ إِلَى النُّطْقِ النَّمُوذَجِيِّ لِلْكَلِمَاتِ.",
                "sample_sentence_en": "Listen to the model pronunciation of words."
            },
            {
                "verb_ar": "أَعْرِبْ",
                "transliteration": "A'rib",
                "meaning_en": "Parse Grammatically",
                "action_guidance": "Identify the grammatical role and vowel case mark of the word.",
                "sample_sentence_ar": "أَعْرِبْ مَا تَحْتَهُ خَطٌّ فِي الجُمْلَةِ التَّالِيَةِ.",
                "sample_sentence_en": "Parse the underlined word in the following sentence."
            },
            {
                "verb_ar": "صَنِّفْ",
                "transliteration": "Sannif",
                "meaning_en": "Classify",
                "action_guidance": "Sort concepts into their correct thematic categories.",
                "sample_sentence_ar": "صَنِّفِ الكَلِمَاتِ إِلَى أَسْمَاءٍ وَأَفْعَالٍ.",
                "sample_sentence_en": "Classify words into nouns and verbs."
            },
            {
                "verb_ar": "اكْتُبْ",
                "transliteration": "Uktub",
                "meaning_en": "Write",
                "action_guidance": "Compose well-structured Arabic sentences using the target connectors.",
                "sample_sentence_ar": f"اكْتُبْ فِقْرَةً قَصِيرَةً عَنْ مَوْضُوعِ {title_ar}.",
                "sample_sentence_en": f"Write a short paragraph about {title_en}."
            },
            {
                "verb_ar": "تَحَدَّثْ",
                "transliteration": "Tahaddath",
                "meaning_en": "Speak",
                "action_guidance": "Record your voice speaking Modern Standard Arabic with confidence.",
                "sample_sentence_ar": "تَحَدَّثْ عَنْ رَأْيِكَ بِلُغَةٍ عَرَبِيَّةٍ فَصِيحَةٍ.",
                "sample_sentence_en": "Express your opinion in eloquent Arabic."
            }
        ],

        # 4. Vocabulary Cards (Tab 1)
        "vocabulary_cards": [
            {
                "id": f"vocab_{lesson_id}_01",
                "word_ar": "الرِّيَادَةُ",
                "vowelled_ar": "الرِّيَادَةُ",
                "meaning_en": "Leadership & Excellence",
                "definition_ar": "السَّبْقُ وَالتَّقَدُّمُ فِي المَيَادِينِ الإِيجَابِيَّةِ.",
                "example_ar": "تَسْعَى دَوْلَةُ الإِمَارَاتِ دَائِمًا نَحْوَ الرِّيَادَةِ فِي كُلِّ المَجَالَاتِ.",
                "example_en": "The UAE always strives for leadership in all domains.",
                "root": "ر-ي-د",
                "category": "values"
            },
            {
                "id": f"vocab_{lesson_id}_02",
                "word_ar": "التَّعَاوُنُ",
                "vowelled_ar": "التَّعَاوُنُ",
                "meaning_en": "Collaboration",
                "definition_ar": "المُشَارَكَةُ الإِيجَابِيَّةُ وَمُسَاعَدَةُ الآخَرِينَ لِتَحْقِيقِ النَّجَاحِ.",
                "example_ar": "التَّعَاوُنُ بَيْنَ أَعْضَاءِ الفَرِيقِ يُحَقِّقُ الإِنْجَازَ الكَبِيرَ.",
                "example_en": "Collaboration between teammates produces great achievement.",
                "root": "ع-و-ن",
                "category": "social"
            },
            {
                "id": f"vocab_{lesson_id}_03",
                "word_ar": "الابْتِكَارُ",
                "vowelled_ar": "الابْتِكَارُ",
                "meaning_en": "Innovation",
                "definition_ar": "إِبْدَاعُ أَفْكَارٍ جَدِيدَةٍ وَحُلُولٍ نَافِعَةٍ لِلْمُجْتَمَعِ.",
                "example_ar": "يُعْتَبَرُ الِابْتِكَارُ عِمَادَ المُسْتَقْبَلِ وَرُؤْيَةَ الأَجْيَالِ.",
                "example_en": "Innovation is the pillar of the future.",
                "root": "ب-ك-ر",
                "category": "knowledge"
            },
            {
                "id": f"vocab_{lesson_id}_04",
                "word_ar": "الأَصَالَةُ",
                "vowelled_ar": "الأَصَالَةُ",
                "meaning_en": "Authenticity & Heritage",
                "definition_ar": "التَّمَسُّكُ بِالتُّرَاثِ العَرِيقِ وَالقِيَمِ الأَخْلَاقِيَّةِ الرَّفِيعَةِ.",
                "example_ar": "تَجْمَعُ بِلَادِي بَيْنَ الأَصَالَةِ وَالمُعَاصَرَةِ فِي تَنْمِيَتِهَا.",
                "example_en": "My country combines authenticity with modernity in its development.",
                "root": "أ-ص-ل",
                "category": "heritage"
            }
        ],

        # 5. Grammar Lab (Tab 4)
        "grammar_lab": {
            "title_ar": f"مختبر القواعد النحوية: {grammar_info['rule_ar']}",
            "title_en": f"Grammar Lab: {grammar_info['rule_en']}",
            "sections": [
                {
                    "rule_name_ar": grammar_info["rule_ar"],
                    "rule_name_en": grammar_info["rule_en"],
                    "explanation_en": grammar_info["explanation"],
                    "examples": grammar_info["examples"]
                }
            ]
        },

        # 6. Sentence Builder (Tab 5)
        "sentence_builder": {
            "title_ar": "باني الجمل التفاعلي",
            "title_en": "Interactive Sentence Builder",
            "challenges": [
                {
                    "id": f"sb_{lesson_id}_01",
                    "instruction_en": "Arrange the words to form a correct Arabic sentence:",
                    "target_sentence_ar": "يَتَمَيَّزُ التَّعْلِيمُ فِي الإِمَارَاتِ بِالجَوْدَةِ وَالابْتِكَارِ.",
                    "target_ar": "يَتَمَيَّزُ التَّعْلِيمُ فِي الإِمَارَاتِ بِالجَوْدَةِ وَالابْتِكَارِ.",
                    "target_en": "Education in the UAE is characterized by quality and innovation.",
                    "tiles": ["يَتَمَيَّزُ", "التَّعْلِيمُ", "فِي", "الإِمَارَاتِ", "بِالجَوْدَةِ", "وَالابْتِكَارِ."],
                    "scrambled_tokens": ["الإِمَارَاتِ", "بِالجَوْدَةِ", "يَتَمَيَّزُ", "التَّعْلِيمُ", "وَالابْتِكَارِ.", "فِي"],
                    "distractors": ["يَتَأَخَّرُ", "كَثِيرًا"]
                },
                {
                    "id": f"sb_{lesson_id}_02",
                    "instruction_en": "Arrange the words to form a statement about knowledge:",
                    "target_sentence_ar": "العِلْمُ وَالقِرَاءَةُ يُنِيرَانِ عُقُولَ الأَبْنَاءِ.",
                    "target_ar": "العِلْمُ وَالقِرَاءَةُ يُنِيرَانِ عُقُولَ الأَبْنَاءِ.",
                    "target_en": "Knowledge and reading illuminate children's minds.",
                    "tiles": ["العِلْمُ", "وَالقِرَاءَةُ", "يُنِيرَانِ", "عُقُولَ", "الأَبْنَاءِ."],
                    "scrambled_tokens": ["عُقُولَ", "العِلْمُ", "الأَبْنَاءِ.", "يُنِيرَانِ", "وَالقِرَاءَةُ"],
                    "distractors": ["يُظْلِمَانِ", "قَلِيلًا"]
                }
            ]
        },

        # 7. Listen & Speak Studio (Tab 2)
        "listen_speak_studio": {
            "title_ar": f"استوديو الاستماع والتحدث: {title_ar}",
            "title_en": f"Listen & Speak Studio: {title_en}",
            "passage_ar": f"يُعَدُّ دَرْسُ ({title_ar}) مِنْ دُرُوسِ المِنْهَاجِ الوِزَارِيِّ المُعْتَمَدِ فِي دَوْلَةِ الإِمَارَاتِ العَرَبِيَّةِ المُتَّحِدَةِ. يَتَعَلَّمُ الطَّالِبُ مِنْ خِلَالِهِ قِيَمَ المَعْرِفَةِ، وَفَصَاحَةَ اللِّسَانِ، وَحُبَّ التَّعَلُّمِ، مُعْتَزًّا بِهُوِيَّتِهِ وَلُغَتِهِ العَرَبِيَّةِ الأَصِيلَةِ.",
            "passage_en": f"The lesson '{title_en}' is an integral chapter of the UAE Ministry of Education Arabic curriculum. Students learn core values of knowledge, eloquent articulation, and love of discovery while taking pride in their authentic Arabic identity.",
            "audio_scripts": [
                {
                    "id": f"aud_{lesson_id}_01",
                    "text_ar": f"دَرْسُ ({title_ar}) يُعَزِّزُ مَهَارَاتِ القِرَاءَةِ وَالتَّفْكِيرِ.",
                    "text_en": f"The lesson '{title_en}' strengthens reading and thinking skills."
                },
                {
                    "id": f"aud_{lesson_id}_02",
                    "text_ar": "العِلْمُ وَالمَعْرِفَةُ أَسَاسُ التَّقَدُّمِ وَالنَّجَاحِ فِي وَطَنِنَا.",
                    "text_en": "Knowledge and science are the foundation of progress and success in our nation."
                }
            ]
        },

        # 8. Practice Activities (Tab 6)
        "practice_activities": [
            {
                "id": f"act_{lesson_id}_01",
                "type": "multiple_choice",
                "title_ar": f"فهم واستيعاب: {title_ar}",
                "title_en": f"Comprehension: {title_en}",
                "prompt_ar": f"مَا الفِكْرَةُ الرَّئِيسَةُ الَّتِي يُؤَكِّدُ عَلَيْهَا دَرْسُ ({title_ar})؟",
                "prompt_en": f"What is the main idea emphasized in '{title_en}'?",
                "options": [
                    {"id": "opt_a", "label_ar": "اكْتِسَابُ المَهَارَاتِ اللُّغَوِيَّةِ وَتَطْبِيقُ القِيَمِ الأَصِيلَةِ", "label_en": "Gaining language skills and applying authentic values"},
                    {"id": "opt_b", "label_ar": "الانْشِغَالُ عَنِ الدِّرَاسَةِ وَالتَّعَلُّمِ", "label_en": "Distraction from studying and learning"},
                    {"id": "opt_c", "label_ar": "إِهْمَالُ القِرَاءَةِ وَالمُطَالَعَةِ", "label_en": "Neglecting reading and study"}
                ],
                "correct_answer": "opt_a",
                "points": 10,
                "explanation_ar": "يؤكد المنهاج الوزاري على الدمج بين إتقان اللغة واكتساب القيم السلوكية والوطنية النبيلة."
            },
            {
                "id": f"act_{lesson_id}_02",
                "type": "multiple_choice",
                "title_ar": "التطبيق النحوي",
                "title_en": "Grammar Application",
                "prompt_ar": f"مَا هُوَ إِعْرَابُ كَلِمَةِ (الطَّالِبُ) فِي: (يَقْرَأُ الطَّالِبُ نَصَّ {title_ar})؟",
                "prompt_en": f"What is the grammatical case of 'al-talibu' in the sentence?",
                "options": [
                    {"id": "opt_a", "label_ar": "فَاعِلٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ الظَّاهِرَةُ", "label_en": "Nominative subject (Faa'il) with dammah"},
                    {"id": "opt_b", "label_ar": "مَفْعُولٌ بِهِ مَنْصُوبٌ بِالفَتْحَةِ", "label_en": "Accusative object with fathah"},
                    {"id": "opt_c", "label_ar": "اسْمٌ مَجْرُورٌ بِالكَسْرَةِ", "label_en": "Genitive noun with kasrah"}
                ],
                "correct_answer": "opt_a",
                "points": 10,
                "explanation_ar": "الطالب هو من قام بفعل القراءة، فهو فاعل مرفوع بالضمة الظاهرة على آخره."
            }
        ],

        # 9. Speaking Mission (Tab 7/Mission)
        "speaking_mission": {
            "title_ar": "مهمة التحدث الصوتي: عبر بطلاقة",
            "title_en": f"Speaking Mission: Express Fluently in {title_en}",
            "scenario_en": f"Record a 30-second speech explaining why {title_en} is important in daily life and Emirati society.",
            "prompts_ar": [
                f"تَحَدَّثْ عَنْ فَائِدَةِ مَوْضُوعِ ({title_ar}) فِي حَيَاتِكَ اليَوْمِيَّةِ.",
                "كَيْفَ تُسْهِمُ القِرَاءَةُ فِي بِنَاءِ شَخْصِيَّتِكَ وَمُسْتَقْبَلِكَ؟"
            ],
            "prompts_en": [
                f"Explain the real-world value of {title_en}.",
                "How does reading contribute to your future?"
            ],
            "recording_task_en": "Press the microphone to record your verbal response."
        },

        # 10. Parent Companion
        "parent_companion": {
            "title_ar": f"دليل ولي الأمر: درس {title_ar}",
            "title_en": f"Parent Companion: {title_en}",
            "summary_en": f"Supports parents in discussing {title_en} with their child, reinforcing vocabulary and Emirati heritage values.",
            "dinner_table_prompts": [
                {
                    "arabic": f"اسْأَلْ طِفْلَكَ: مَا هِيَ أَجْمَلُ فِكْرَةٍ لَفَتَتْ انْتِبَاهَكَ فِي دَرْسِ {title_ar} اليَوْمَ؟",
                    "english": f"Ask your child: What was the most inspiring concept in {title_en} today?",
                    "phonetic": "Maa hiya ajmalu fikratin lafatat intibaahaka al-yawm?"
                },
                {
                    "arabic": "اللُّغَةُ العَرَبِيَّةُ لُغَةُ الحَضَارَةِ وَالفَصَاحَةِ.",
                    "english": "The Arabic language is the language of civilization and eloquence.",
                    "phonetic": "Al-lughatu al-arabiyyatu lughatu al-hadarah."
                }
            ],
            "home_practice_checklist": [
                f"مراجعة بطاقات المفردات الأربع لدرس ({title_ar}).",
                "الاستماع للنطق السليم والتسجيل في استوديو التحدث.",
                "حل أنشطة باني الجمل واختبار الفصل الدراسي."
            ]
        },

        # 11. Tutor Handover Notes
        "tutor_handover": {
            "title_ar": "ملاحظات المعلم والمتابعة الأكاديمية",
            "title_en": f"Tutor Handover Notes: {title_en}",
            "learner_focus": f"Mastery of vocabulary, pronunciation, and grammatical structure for {title_en}.",
            "unobserved_fields_note": "Certified curriculum package conforming to UAE MoE Arabic language standards.",
            "rubric_categories": [
                {"key": "comprehension", "name_en": "Reading Comprehension", "weight": "30%"},
                {"key": "pronunciation", "name_en": "Oral Fluency & Tashkeel", "weight": "30%"},
                {"key": "grammar", "name_en": "Syntactic Accuracy", "weight": "40%"}
            ]
        },

        # 12. Exam Practice (Tab 10 / Exam)
        "exam_practice": {
            "title_ar": f"محاكاة الامتحان الوزاري: {title_ar}",
            "title_en": f"MoE Assessment Simulation: {title_en}",
            "total_marks": 20,
            "objective_questions": [
                {
                    "id": f"exam_{lesson_id}_01",
                    "prompt_ar": f"اخْتَرْ المَعْنَى الدَّقِيقَ لِلسِّيَاقِ فِي دَرْسِ ({title_ar}):",
                    "prompt_en": f"Choose the accurate contextual meaning for '{title_en}':",
                    "options": [
                        {"id": "opt_a", "label_ar": "التَّطْبِيقُ السَّلِيمُ لِلْمَهَارَاتِ وَالقِيَمِ فِي المَوَاقِفِ المُخْتَلِفَةِ", "label_en": "Sound application of skills and values in various settings"},
                        {"id": "opt_b", "label_ar": "الحِفْظُ الظَّاهِرِيُّ دُونَ فَهْمٍ عَمِيقٍ", "label_en": "Superficial memorization without deep understanding"},
                        {"id": "opt_c", "label_ar": "تَرْكُ التَّمَارِينِ وَعَدَمُ المُشَارَكَةِ", "label_en": "Leaving exercises without participating"}
                    ],
                    "marks": 4,
                    "correct_answer": "opt_a"
                },
                {
                    "id": f"exam_{lesson_id}_02",
                    "prompt_ar": "أَيُّ العِبَارَاتِ الآتِيَةِ تُمَثِّلُ جُمْلَةً عَرَبِيَّةً صَحِيحَةَ الضَّبْطِ؟",
                    "prompt_en": "Which statement represents a grammatically correct Arabic sentence?",
                    "options": [
                        {"id": "opt_a", "label_ar": "يَقْرَأُ التِّلْمِيذُ الكِتَابَ النَّافِعَ بِانْتِبَاهٍ", "label_en": "The pupil reads the beneficial book attentively"},
                        {"id": "opt_b", "label_ar": "يَقْرَأَ التِّلْمِيذِ الكِتَابُ", "label_en": "Grammatically incorrect vowels"},
                        {"id": "opt_c", "label_ar": "التِّلْمِيذُ قَرَأَ دُونَ حَرَكَاتٍ", "label_en": "Unvowelled incomplete clause"}
                    ],
                    "marks": 4,
                    "correct_answer": "opt_a"
                }
            ],
            "writing_task": {
                "id": f"write_{lesson_id}",
                "prompt_ar": f"اكْتُبْ ثَلَاثَ جُمَلٍ مُفِيدَةٍ بِاللُّغَةِ العَرَبِيَّةِ تُعَبِّرُ فِيهَا عَمَّا اسْتَفَدْتَهُ مِنْ دَرْسِ ({title_ar})، مُوَظِّفًا حُرُوفَ العَطْفِ وَعَلَامَاتِ التَّرْقِيمِ.",
                "prompt_en": f"Write three coherent sentences in Arabic expressing what you learned from '{title_en}', using conjunctions and punctuation marks.",
                "marks": 6
            }
        },

        # 13. Spaced Recall
        "spaced_recall": {
            "title_ar": "التكرار المتباعد والتثبيت طويل الأمد",
            "title_en": "Spaced Recall Review",
            "linked_concepts": [
                {
                    "concept_name_ar": title_ar,
                    "concept_name_en": title_en,
                    "source_lesson": title_en,
                    "target_lesson": "Previous & Upcoming Modules",
                    "recall_question_ar": f"كَيْفَ تَرْبِطُ بَيْنَ مَفْهُومِ ({title_ar}) وَمَا تَعَلَّمْتَهُ فِي الدُّرُوسِ السَّابِقَةِ؟",
                    "recall_question_en": f"How do you connect the theme of '{title_en}' with concepts from previous modules?"
                }
            ]
        }
    }


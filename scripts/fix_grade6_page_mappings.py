"""Fix Grade 6 page mappings and calibrate scanned_pages in the database."""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import ScannedPage


def fix_grade6_mapping():
    db = SessionLocal()
    try:
        # 1. Reset printed_page = pdf_page for all pages in moe_gr6_vol1_2023
        pages = db.query(ScannedPage).filter(
            ScannedPage.book_edition_id == "moe_gr6_vol1_2023"
        ).order_by(ScannedPage.pdf_page).all()

        fixed_count = 0
        for p in pages:
            if p.pdf_page != 7 and p.printed_page != p.pdf_page:
                p.printed_page = p.pdf_page
                fixed_count += 1

        print(f"Reset printed_page = pdf_page for {fixed_count} pages in moe_gr6_vol1_2023.")

        # 2. Update page 27 with exact authentic Arabic text
        p27 = db.query(ScannedPage).filter(
            ScannedPage.book_edition_id == "moe_gr6_vol1_2023",
            ScannedPage.pdf_page == 27
        ).first()

        text_27 = (
            "٣ أكتب نصًّا مترابطًا عن الوظائف وعلاقتها بسوق العمل، مستخدمًا المعلومات "
            "والأدلة والبراهين التي تدعم كتابتي.\n\n"
            "٤ أُعيد كتابتي مراعيًا شَبَكَةَ التَّقْيِيمِ التي يُقَدِّمُها لي المُعَلِّمُ."
        )

        if p27:
            p27.printed_page = 27
            p27.ocr_text_ar = text_27
            p27.review_status = "reviewed"
            p27.confidence = 0.99
            print("✓ Updated page 27 with authentic writing rubric text.")
        else:
            p27 = ScannedPage(
                book_edition_id="moe_gr6_vol1_2023",
                pdf_page=27,
                printed_page=27,
                ocr_text_ar=text_27,
                review_status="reviewed",
                confidence=0.99
            )
            db.add(p27)
            print("✓ Created page 27 record.")

        # 3. Update page 34 with exact authentic Arabic text
        p34 = db.query(ScannedPage).filter(
            ScannedPage.book_edition_id == "moe_gr6_vol1_2023",
            ScannedPage.pdf_page == 34
        ).first()

        text_34 = (
            "أَقْرَأُ: عُمْلَاتٌ مُخْتَلِفَةٌ\n\n"
            "البَتْكويْنُ\n\n"
            "البَتْكويْنُ عُمْلَةٌ جَدِيدَةٌ، ظَهَرَتْ عام 2009 م، وأهَمُّ ما يُمَيِّزُها أنَّها إلكترونيَّةٌ رَقَميَّةٌ، "
            "أَنْشَأَها رَجُلٌ مَجْهُولٌ، يَحْمِلُ اسْمًا غَيْرَ حَقيقيٍّ يُسَمَّى 'ساتوشي ناكاموتو'.\n\n"
            "والغَرِيبُ فِي الأمْرِ أَنَّ هَذِهِ العُمْلَةَ لَيْسَ لَها ووجوَدٌ ماديٌّ عَلى أرْضِ الواقِعِ، "
            "فَمِنَ المَعْرُوفِ أَنَّ الْأَمْوَالَ الَّتي تُصْدِرُها الدُّوَلُ يَكونُ لَها رَصِيدٌ مِنَ الذَّهَبِ، "
            "أمَّا البَتْكويْنُ فَهِيَ عُمْلَةٌ مُسْتَقِلَّةٌ ليسَ لَها رَصِيدٌ مِنَ الذَّهَبِ ولا تَتْبَعُ أيَّ دَوْلَةٍ مُحَدَّدَةٍ.\n\n"
            "يَتِمُّ الحُصُولُ عَلَى عُمْلَةِ البَتْكويْن مِن خِلالِ شَبَكَةِ الإِنْتْرَنِت مُقابِلَ المالِ أو خِدْماتٍ أُخْرَى.\n\n"
            "لاسْتِخْدامِ عُمْلَةِ البَتْكويْن فَوائِدُ عَدِيدَةٌ مِنْها:\n"
            "* لا تَحْتاجُ اسْتِخْدامَ أَيِّ مَعْلُوماتٍ شَخْصيَّةٍ فَهِيَ سِرِّيَّةٌ تمامًا.\n"
            "* وسيلَةٌ جَيِّدَةٌ للإِدْخارِ، لأنَّكَ لا تَحْتاجُ دَفْعَ ضَرائِبَ عَلَيْها.\n"
            "* التَّعاملُ بِالبْتْكويْن لا يَحْتاجُ إلَى وَسِيطٍ كالبَنْكِ مَثَلًا، إِذْ يُمْكِنُكَ تَحْويلُ أَيِّ مَبْلَغٍ مِنَ المالِ بِشَكْلٍ مُباشِرٍ ودونَ دَفْعِ أَيِّ عُمُولَةٍ.\n\n"
            "أَمَّا سَلْبِيّاتُ اسْتِخْدامِ عُمْلَةِ البَتْكويْن فَهِيَ عَدِيدَةٌ، مِنْها:\n"
            "* عَدَمُ اسْتِقْرارِ قِيمَتِها، وسِعْرُها المُسْتَقْبَلِيُّ غَيْرُ مَعْرُوفٍ.\n"
            "* لا تَسْتَخْدِمُها الشَّرِكاتُ؛ لأنَّ سِعْرَها مُتَغَيِّرٌ وغَيْرُ مَعْرُوفٍ.\n"
            "* مِن أَكْبَرِ سَلْبِيّاتِها، أَنَّها مُعَرَّضَةٌ لِلغِشِّ والسَّرِقَةِ.\n\n"
            "هَلْ تَعْرِفُ أَنَّهُ ظَهَرَ عَدَدٌ مِنَ العُمْلَاتِ الرَّقْمِيَّةِ، لَكِنْ تَظَلُّ البَتْكويْنُ هيَ الْأَشْهَرُ، "
            "ومَعَ ذَلِكَ يَتَعامَلُ النَّاسُ مَعَها بِحَذَرٍ شَدِيدٍ؟!"
        )

        if p34:
            p34.printed_page = 34
            p34.ocr_text_ar = text_34
            p34.review_status = "reviewed"
            p34.confidence = 0.99
            print("✓ Updated page 34 with authentic Bitcoin text.")
        else:
            p34 = ScannedPage(
                book_edition_id="moe_gr6_vol1_2023",
                pdf_page=34,
                printed_page=34,
                ocr_text_ar=text_34,
                review_status="reviewed",
                confidence=0.99
            )
            db.add(p34)
            print("✓ Created page 34 record.")

        db.commit()
        print("✓ All changes successfully committed to database!")

    except Exception as e:
        db.rollback()
        print(f"Error updating database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    fix_grade6_mapping()

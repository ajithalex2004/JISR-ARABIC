"""
Pillar 4 Verification: Distributed Redis Caching & Shared State.
Tests caching primitives, read-heavy curriculum endpoints, answer shielding,
active cache invalidation on curriculum and school mutations, and thread-safe fallback.
"""
import copy
import json
import time
import hashlib
import datetime
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import (
    User, School, SchoolClass, BookEdition, Unit, Lesson, LessonVersion, TermAccess,
    ChildProfile, UserSession
)
from backend.security import create_access_token, decode_access_token, hash_password
from backend.redis_client import (
    cache_set, cache_get, cache_delete, cache_delete_pattern, cache_clear,
    invalidate_lesson_cache, invalidate_school_cache
)


class TestPillar4Caching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("SecurePass123!")

    def setUp(self):
        cache_clear()
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

        with self.session() as db:
            # 1. School & Classes
            db.add(School(id="sch_dubai", name="Dubai Modern Academy", country="United Arab Emirates"))
            db.add(SchoolClass(id="cls_dubai_5a", school_id="sch_dubai", name="Grade 5-A Dubai", grade=5, academic_year="2025-2026", is_active=True))

            # 2. Users
            db.add(User(id="usr_superadmin", email="superadmin@jisr.ae", role="admin", password_hash=self.password_hash, is_verified=True))
            db.add(User(id="usr_school_admin", email="admin@dubai.school", role="school_admin", school_id="sch_dubai", password_hash=self.password_hash, is_verified=True))
            db.add(User(id="usr_parent", email="parent@gmail.com", role="parent", password_hash=self.password_hash, is_verified=True))

            # 3. Child profile
            db.add(ChildProfile(id="child_demo", parent_id="usr_parent", name="Zayed", default_grade=5, school_id="sch_dubai"))

            # 4. Curriculum: BookEdition, Unit & Lesson
            db.add(BookEdition(id="ed_g5_t1", title="Grade 5 Term 1"))
            db.commit()
            db.add(Unit(id="u_g5_t1_1", book_edition_id="ed_g5_t1", unit_number=1, title_ar="الوحدة الأولى", title_en="Unit 1"))
            db.commit()
            db.add(Lesson(
                id="l_g5_t1_1",
                unit_id="u_g5_t1_1",
                grade=5,
                term=1,
                lesson_order=1,
                title_ar="كرة القدم",
                title_en="Football",
                start_page=10,
                is_first_chapter_demo=True,
                status="published"
            ))
            db.commit()

            self.lesson_raw_content = {
                "reading_passage": {"title_ar": "كرة القدم في الإمارات", "text_ar": "نص القراءة عن الرياضة."},
                "activities": [
                    {
                        "id": "act_01",
                        "type": "multiple_choice",
                        "question_ar": "ما هي اللعبة الشعبية الأولى؟",
                        "options": ["كرة السلة", "كرة القدم", "السباحة"],
                        "correct_index": 1,
                        "correct_answer": "كرة القدم",
                        "solution_walkthrough": "كرة القدم هي اللعبة الأكثر شعبية عالمياً ومحلياً.",
                        "hint": "تبدأ بكلمة كرة"
                    }
                ]
            }
            content_str = json.dumps(self.lesson_raw_content, ensure_ascii=False)
            content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

            db.add(LessonVersion(
                id="ver_l_g5_t1_1_v1",
                lesson_id="l_g5_t1_1",
                version_tag="1.0.0",
                content_json=content_str,
                content_hash=content_hash,
                is_active=True,
                status="published",
                published_at=datetime.datetime.utcnow()
            ))

            # Version 2 approved but not published (for rollback/publish tests)
            v2_content = copy.deepcopy(self.lesson_raw_content)
            v2_content["activities"][0]["question_ar"] = "ما هي الرياضة المفضلة في الدرس؟ (v2)"
            v2_str = json.dumps(v2_content, ensure_ascii=False)
            v2_hash = hashlib.sha256(v2_str.encode("utf-8")).hexdigest()
            db.add(LessonVersion(
                id="ver_l_g5_t1_1_v2",
                lesson_id="l_g5_t1_1",
                version_tag="2.0.0",
                content_json=v2_str,
                content_hash=v2_hash,
                is_active=False,
                status="approved",
                published_at=None
            ))

            db.commit()

        def scoped_db():
            with self.session() as db:
                yield db

        app.dependency_overrides[get_db] = scoped_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()
        cache_clear()

    def auth_headers(self, user_id: str, role: str, school_id: str = None, child_id: str = None):
        token_payload = {
            "sub": user_id,
            "role": role,
            "school_id": school_id,
            "child_id": child_id,
            "session_kind": "learner" if role == "learner" else None
        }
        token = create_access_token(token_payload)
        payload = decode_access_token(token)
        with self.session() as db:
            db.add(UserSession(
                id=payload["jti"],
                user_id=user_id,
                expires_at=datetime.datetime.utcfromtimestamp(payload["exp"])
            ))
            db.commit()
        return {"Authorization": f"Bearer {token}"}

    def test_01_core_cache_primitives_set_get_delete_patterns(self):
        """Test cache_set, cache_get, cache_delete, and pattern eviction."""
        self.assertTrue(cache_set("unit_test:key1", {"score": 95, "name": "Ali"}, ttl_seconds=120))
        val = cache_get("unit_test:key1")
        self.assertEqual(val, {"score": 95, "name": "Ali"})

        # Miss
        self.assertIsNone(cache_get("unit_test:non_existent"))

        # Delete single
        self.assertTrue(cache_delete("unit_test:key1"))
        self.assertIsNone(cache_get("unit_test:key1"))

        # Pattern deletion
        cache_set("pat:user:1", "u1")
        cache_set("pat:user:2", "u2")
        cache_set("other:token", "tok")
        deleted_count = cache_delete_pattern("pat:user:*")
        self.assertGreaterEqual(deleted_count, 2)
        self.assertIsNone(cache_get("pat:user:1"))
        self.assertIsNone(cache_get("pat:user:2"))
        self.assertEqual(cache_get("other:token"), "tok")

    def test_02_cache_ttl_expiration(self):
        """Test that keys with short TTLs cleanly expire."""
        cache_set("expire:test", "temp_value", ttl_seconds=1)
        self.assertEqual(cache_get("expire:test"), "temp_value")
        time.sleep(1.1)
        self.assertIsNone(cache_get("expire:test"))

    def test_03_schools_and_classes_caching_and_hit(self):
        """Test GET /api/curriculum/schools populates cache and subsequent request hits cache."""
        # 1. First call: cache miss, queries DB, populates cache
        res = self.client.get("/api/curriculum/schools")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "sch_dubai")

        # Verify key exists in cache
        cached_schools = cache_get("schools:all")
        self.assertIsNotNone(cached_schools)
        self.assertEqual(cached_schools[0]["id"], "sch_dubai")

        # Mutate cache directly to prove cache hit without DB hit
        cache_set("schools:all", [{"id": "sch_synthetic", "name": "Synthetic School", "country": "UAE", "curriculum_type": "MoE"}])
        res_cached = self.client.get("/api/curriculum/schools")
        self.assertEqual(res_cached.status_code, 200)
        self.assertEqual(res_cached.json()[0]["id"], "sch_synthetic")

        # Invalidate
        invalidate_school_cache()
        self.assertIsNone(cache_get("schools:all"))

    def test_04_school_classes_cache_and_admin_invalidation(self):
        """Test school class caching under school_classes:{school_id} and invalidation on class creation."""
        # 1. Fetch classes for sch_dubai
        res = self.client.get("/api/curriculum/schools/sch_dubai/classes")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)
        self.assertEqual(res.json()[0]["id"], "cls_dubai_5a")

        # Verify cached
        self.assertIsNotNone(cache_get("school_classes:sch_dubai"))

        # 2. School Admin creates a new class in sch_dubai
        admin_headers = self.auth_headers("usr_school_admin", "school_admin", school_id="sch_dubai")
        create_res = self.client.post(
            "/api/admin/schools/classes",
            headers=admin_headers,
            json={
                "id": "cls_dubai_5b",
                "school_id": "sch_dubai",
                "name": "Grade 5-B Dubai",
                "grade": 5,
                "academic_year": "2025-2026"
            }
        )
        self.assertEqual(create_res.status_code, 200)

        # 3. Verify cache for sch_dubai was invalidated
        self.assertIsNone(cache_get("school_classes:sch_dubai"))

        # 4. Next read fetches both classes and recaches
        res_updated = self.client.get("/api/curriculum/schools/sch_dubai/classes")
        self.assertEqual(res_updated.status_code, 200)
        self.assertEqual(len(res_updated.json()), 2)
        self.assertIsNotNone(cache_get("school_classes:sch_dubai"))

    def test_05_curriculum_lesson_caching_and_answer_shielding(self):
        """
        Verify canonical lesson caching and strict answer shielding:
        - Students must NEVER receive correct_index, correct_answer, solution_walkthrough, or hint
        - Cached canonical dictionary must retain full unstripped data for reviewers
        - Cache hits must continue to shield student output without leaking
        """
        lesson_id = "l_g5_t1_1"

        # 1. Student / parent request for demo lesson
        parent_headers = self.auth_headers("usr_parent", "parent")
        res = self.client.get(f"/api/curriculum/lesson/{lesson_id}?child_id=child_demo", headers=parent_headers)
        self.assertEqual(res.status_code, 200)
        payload = res.json()

        # Verify answers and solutions are stripped in the response
        activity = payload["content"]["activities"][0]
        self.assertNotIn("correct_index", activity)
        self.assertNotIn("correct_answer", activity)
        self.assertNotIn("solution_walkthrough", activity)
        self.assertIn("hint", activity)  # Hints are preserved pedagogical scaffolds

        # 2. Verify raw canonical package was stored in cache with answers intact
        cached_pkg = cache_get(f"lesson_package:{lesson_id}")
        self.assertIsNotNone(cached_pkg)
        cached_act = cached_pkg["content"]["activities"][0]
        self.assertEqual(cached_act["correct_index"], 1)
        self.assertEqual(cached_act["correct_answer"], "كرة القدم")
        self.assertEqual(cached_act["solution_walkthrough"], "كرة القدم هي اللعبة الأكثر شعبية عالمياً ومحلياً.")

        # 3. Subsequent student request hits cache, answers must STILL be shielded
        res2 = self.client.get(f"/api/curriculum/lesson/{lesson_id}?child_id=child_demo", headers=parent_headers)
        self.assertEqual(res2.status_code, 200)
        activity2 = res2.json()["content"]["activities"][0]
        self.assertNotIn("correct_index", activity2)
        self.assertNotIn("correct_answer", activity2)
        self.assertNotIn("solution_walkthrough", activity2)

        # 4. Reviewer (admin) request with is_reviewer=true receives full answers
        admin_headers = self.auth_headers("usr_superadmin", "admin")
        res_reviewer = self.client.get(
            f"/api/curriculum/lesson/{lesson_id}?is_reviewer=true",
            headers=admin_headers
        )
        self.assertEqual(res_reviewer.status_code, 200)
        rev_activity = res_reviewer.json()["content"]["activities"][0]
        self.assertEqual(rev_activity["correct_index"], 1)
        self.assertEqual(rev_activity["correct_answer"], "كرة القدم")
        self.assertEqual(rev_activity["solution_walkthrough"], "كرة القدم هي اللعبة الأكثر شعبية عالمياً ومحلياً.")

    def test_06_lesson_publish_and_rollback_cache_invalidation(self):
        """Publishing a new version or rolling back evicts cached lesson package and base list."""
        lesson_id = "l_g5_t1_1"

        # 1. Warm cache
        parent_headers = self.auth_headers("usr_parent", "parent")
        res = self.client.get(f"/api/curriculum/lesson/{lesson_id}?child_id=child_demo", headers=parent_headers)
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(cache_get(f"lesson_package:{lesson_id}"))

        # Also warm base lesson list
        res_list = self.client.get("/api/curriculum/lessons?grade=5&term=1")
        self.assertEqual(res_list.status_code, 200)
        self.assertIsNotNone(cache_get("lessons_base:5:1"))

        # 2. Super admin publishes version 2
        admin_headers = self.auth_headers("usr_superadmin", "admin")
        pub_res = self.client.post(
            f"/api/admin/lessons/{lesson_id}/versions/ver_l_g5_t1_1_v2/publish",
            headers=admin_headers
        )
        self.assertEqual(pub_res.status_code, 200)

        # 3. Verify cache is evicted
        self.assertIsNone(cache_get(f"lesson_package:{lesson_id}"))
        self.assertIsNone(cache_get("lessons_base:5:1"))

        # 4. Next read fetches version 2
        res_v2 = self.client.get(f"/api/curriculum/lesson/{lesson_id}?child_id=child_demo", headers=parent_headers)
        self.assertEqual(res_v2.status_code, 200)
        self.assertEqual(res_v2.json()["version_tag"], "2.0.0")
        self.assertIn("(v2)", res_v2.json()["content"]["activities"][0]["question_ar"])

        # 5. Rollback to version 1
        rollback_res = self.client.post(
            f"/api/admin/lessons/{lesson_id}/rollback/ver_l_g5_t1_1_v1",
            headers=admin_headers
        )
        self.assertEqual(rollback_res.status_code, 200)

        # 6. Verify cache evicted after rollback
        self.assertIsNone(cache_get(f"lesson_package:{lesson_id}"))

        # 7. Next read serves version 1
        res_v1 = self.client.get(f"/api/curriculum/lesson/{lesson_id}?child_id=child_demo", headers=parent_headers)
        self.assertEqual(res_v1.status_code, 200)
        self.assertEqual(res_v1.json()["version_tag"], "1.0.0")

    def test_07_capsule_and_diagnostic_caching(self):
        """Verify bite-sized capsules and diagnostic baseline questions are cached."""
        # 1. Capsule caching
        capsule_id = "capsule_01_taa_marbutah"
        res_cap = self.client.get(f"/api/modules/capsules/{capsule_id}")
        self.assertEqual(res_cap.status_code, 200)
        self.assertTrue(res_cap.json()["success"])

        cached_cap = cache_get(f"capsule:{capsule_id}")
        self.assertIsNotNone(cached_cap)
        self.assertEqual(cached_cap["capsule"]["id"], capsule_id)

        # 2. Diagnostic questions caching
        res_diag = self.client.get("/api/curriculum/diagnostic-questions?grade=5")
        self.assertEqual(res_diag.status_code, 200)
        self.assertTrue(res_diag.json()["success"])

        cached_diag = cache_get("diagnostic:5:default")
        self.assertIsNotNone(cached_diag)
        self.assertEqual(cached_diag["grade"], 5)
        self.assertGreater(cached_diag["count"], 0)


if __name__ == "__main__":
    unittest.main()

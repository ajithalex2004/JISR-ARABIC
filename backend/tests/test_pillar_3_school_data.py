"""Pillar 3 Verification: Multi-Tenant School Scoping, school_admin Permissions, and Membership Audit Trail."""
import datetime
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import (
    User, School, SchoolClass, ClassMembership, TutorClassAssignment,
    MembershipAuditEvent, ChildProfile, TutorSubmission, UserSession
)
from backend.security import create_access_token, decode_access_token, hash_password
from backend.modules.identity.access import Principal, visible_children, require_class_scope, require_school_scope


class TestPillar3SchoolData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("SecurePass123!")

    def setUp(self):
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
            # 1. Create 2 distinct schools
            db.add(School(id="sch_dubai", name="Dubai Modern Academy", country="United Arab Emirates"))
            db.add(School(id="sch_rak", name="RAK International Academy", country="United Arab Emirates"))

            # 2. Create users across roles and schools
            # Super Admin
            db.add(User(id="usr_superadmin", email="superadmin@jisr.ae", role="admin", password_hash=self.password_hash, is_verified=True))
            
            # School Admins
            db.add(User(id="usr_admin_dubai", email="admin@dubai.school", role="school_admin", school_id="sch_dubai", password_hash=self.password_hash, is_verified=True))
            db.add(User(id="usr_admin_rak", email="admin@rak.school", role="school_admin", school_id="sch_rak", password_hash=self.password_hash, is_verified=True))
            
            # Tutors
            db.add(User(id="usr_tutor_dubai", email="tutor@dubai.school", role="tutor", school_id="sch_dubai", password_hash=self.password_hash, is_verified=True))
            db.add(User(id="usr_tutor_rak", email="tutor@rak.school", role="tutor", school_id="sch_rak", password_hash=self.password_hash, is_verified=True))
            
            # Parents
            db.add(User(id="usr_parent_dubai", email="parent_dubai@gmail.com", role="parent", password_hash=self.password_hash, is_verified=True))
            db.add(User(id="usr_parent_rak", email="parent_rak@gmail.com", role="parent", password_hash=self.password_hash, is_verified=True))
            db.commit()

            # 3. Create children
            db.add(ChildProfile(id="child_d1", parent_id="usr_parent_dubai", name="Rashid Dubai", default_grade=5, school_id="sch_dubai"))
            db.add(ChildProfile(id="child_d2", parent_id="usr_parent_dubai", name="Mariam Dubai", default_grade=5, school_id="sch_dubai"))
            db.add(ChildProfile(id="child_r1", parent_id="usr_parent_rak", name="Sultan RAK", default_grade=5, school_id="sch_rak"))
            db.commit()

            # 4. Create Classes
            db.add(SchoolClass(id="cls_dubai_5a", school_id="sch_dubai", name="Grade 5-A Dubai", grade=5, academic_year="2025-2026", is_active=True))
            db.add(SchoolClass(id="cls_rak_5b", school_id="sch_rak", name="Grade 5-B RAK", grade=5, academic_year="2025-2026", is_active=True))
            db.commit()

            # 5. Enroll child_d1 in cls_dubai_5a and child_r1 in cls_rak_5b
            db.add(ClassMembership(class_id="cls_dubai_5a", child_id="child_d1", role="learner"))
            db.add(ClassMembership(class_id="cls_rak_5b", child_id="child_r1", role="learner"))

            # 6. Assign tutor_dubai to cls_dubai_5a and tutor_rak to cls_rak_5b
            db.add(TutorClassAssignment(tutor_id="usr_tutor_dubai", class_id="cls_dubai_5a"))
            db.add(TutorClassAssignment(tutor_id="usr_tutor_rak", class_id="cls_rak_5b"))
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

    def test_01_school_admin_authentication_and_profile(self):
        """School admin session contains school_id and role='school_admin'."""
        headers = self.auth_headers("usr_admin_dubai", "school_admin", school_id="sch_dubai")
        resp = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["role"], "school_admin")
        self.assertEqual(data["school_id"], "sch_dubai")
        self.assertEqual(data["email"], "admin@dubai.school")

    def test_02_school_admin_can_create_classes_in_own_school_only(self):
        """School admin can create classes in their own school, but rejected for other schools."""
        dubai_headers = self.auth_headers("usr_admin_dubai", "school_admin", school_id="sch_dubai")

        # 1. Creating class for own school -> Success (200)
        payload_own = {
            "id": "cls_dubai_6a",
            "school_id": "sch_dubai",
            "name": "Grade 6-A Dubai",
            "grade": 6,
            "academic_year": "2025-2026"
        }
        res_own = self.client.post("/api/admin/schools/classes", headers=dubai_headers, json=payload_own)
        self.assertEqual(res_own.status_code, 200)
        self.assertEqual(res_own.json()["id"], "cls_dubai_6a")

        # 2. Creating class for another school -> Forbidden (403)
        payload_other = {
            "id": "cls_rak_6a",
            "school_id": "sch_rak",
            "name": "Grade 6-A RAK",
            "grade": 6,
            "academic_year": "2025-2026"
        }
        res_other = self.client.post("/api/admin/schools/classes", headers=dubai_headers, json=payload_other)
        self.assertEqual(res_other.status_code, 403)

        # 3. Super admin can create class in any school -> Success (200)
        super_headers = self.auth_headers("usr_superadmin", "admin")
        res_super = self.client.post("/api/admin/schools/classes", headers=super_headers, json=payload_other)
        self.assertEqual(res_super.status_code, 200)

        # 4. Tutors and Parents cannot create classes -> Forbidden (403)
        tutor_headers = self.auth_headers("usr_tutor_dubai", "tutor", school_id="sch_dubai")
        parent_headers = self.auth_headers("usr_parent_dubai", "parent")
        self.assertEqual(self.client.post("/api/admin/schools/classes", headers=tutor_headers, json=payload_own).status_code, 403)
        self.assertEqual(self.client.post("/api/admin/schools/classes", headers=parent_headers, json=payload_own).status_code, 403)

    def test_03_visible_children_enforces_school_isolation(self):
        """visible_children scopes queries strictly by tenant."""
        with self.session() as db:
            dubai_admin = Principal(id="usr_admin_dubai", email="admin@dubai.school", role="school_admin", is_verified=True, school_id="sch_dubai")
            rak_admin = Principal(id="usr_admin_rak", email="admin@rak.school", role="school_admin", is_verified=True, school_id="sch_rak")
            super_admin = Principal(id="usr_superadmin", email="superadmin@jisr.ae", role="admin", is_verified=True)

            dubai_kids = [c.id for c in visible_children(db, dubai_admin).all()]
            self.assertIn("child_d1", dubai_kids)
            self.assertIn("child_d2", dubai_kids)
            self.assertNotIn("child_r1", dubai_kids)

            rak_kids = [c.id for c in visible_children(db, rak_admin).all()]
            self.assertIn("child_r1", rak_kids)
            self.assertNotIn("child_d1", rak_kids)
            self.assertNotIn("child_d2", rak_kids)

            all_kids = [c.id for c in visible_children(db, super_admin).all()]
            self.assertEqual(len(all_kids), 3)

    def test_04_cross_school_class_management_forbidden(self):
        """School admin cannot manage, activate, roster, or modify another school's class."""
        dubai_headers = self.auth_headers("usr_admin_dubai", "school_admin", school_id="sch_dubai")

        # Accessing RAK class roster -> 403
        roster_res = self.client.get("/api/admin/schools/classes/cls_rak_5b/roster", headers=dubai_headers)
        self.assertEqual(roster_res.status_code, 403)

        # Accessing Dubai class roster -> 200
        dubai_roster = self.client.get("/api/admin/schools/classes/cls_dubai_5a/roster", headers=dubai_headers)
        self.assertEqual(dubai_roster.status_code, 200)
        self.assertEqual(len(dubai_roster.json()["learners"]), 1)
        self.assertEqual(dubai_roster.json()["learners"][0]["id"], "child_d1")

        # Toggling active state on RAK class -> 403
        toggle_res = self.client.put("/api/admin/schools/classes/cls_rak_5b/active?active=false", headers=dubai_headers)
        self.assertEqual(toggle_res.status_code, 403)

        # Enrolling student into RAK class -> 403
        enroll_res = self.client.post("/api/admin/schools/classes/cls_rak_5b/learners", headers=dubai_headers, json={"child_id": "child_d2"})
        self.assertEqual(enroll_res.status_code, 403)

        # Enrolling student from RAK school into Dubai class -> 403
        cross_enroll = self.client.post("/api/admin/schools/classes/cls_dubai_5a/learners", headers=dubai_headers, json={"child_id": "child_r1"})
        self.assertEqual(cross_enroll.status_code, 403)

        # Enrolling Dubai student into Dubai class -> 200
        valid_enroll = self.client.post("/api/admin/schools/classes/cls_dubai_5a/learners", headers=dubai_headers, json={"child_id": "child_d2"})
        self.assertEqual(valid_enroll.status_code, 200)

    def test_05_tutor_assignments_scoped_by_school(self):
        """Assigning tutors to classes enforces school boundaries."""
        dubai_headers = self.auth_headers("usr_admin_dubai", "school_admin", school_id="sch_dubai")

        # School admin assigning RAK tutor to Dubai class -> 403
        res_cross_tutor = self.client.post(
            "/api/admin/schools/classes/cls_dubai_5a/tutors",
            headers=dubai_headers,
            json={"tutor_id": "usr_tutor_rak"}
        )
        self.assertEqual(res_cross_tutor.status_code, 403)

        # School admin assigning Dubai tutor to RAK class -> 403
        res_cross_class = self.client.post(
            "/api/admin/schools/classes/cls_rak_5b/tutors",
            headers=dubai_headers,
            json={"tutor_id": "usr_tutor_dubai"}
        )
        self.assertEqual(res_cross_class.status_code, 403)

        # Tutor viewing only their own assigned classes
        dubai_tutor_headers = self.auth_headers("usr_tutor_dubai", "tutor", school_id="sch_dubai")
        tutor_classes_res = self.client.get("/api/admin/tutors/usr_tutor_dubai/classes", headers=dubai_tutor_headers)
        self.assertEqual(tutor_classes_res.status_code, 200)
        self.assertEqual([c["id"] for c in tutor_classes_res.json()], ["cls_dubai_5a"])

        # Dubai tutor attempting to view RAK tutor classes -> 403
        self.assertEqual(self.client.get("/api/admin/tutors/usr_tutor_rak/classes", headers=dubai_tutor_headers).status_code, 403)

    def test_06_audit_trail_recorded_on_membership_changes(self):
        """Enrollment, unenrollment, and tutor assignments produce MembershipAuditEvent entries."""
        dubai_headers = self.auth_headers("usr_admin_dubai", "school_admin", school_id="sch_dubai")

        # 1. Enroll child_d2
        enroll_res = self.client.post("/api/admin/schools/classes/cls_dubai_5a/learners", headers=dubai_headers, json={"child_id": "child_d2"})
        self.assertEqual(enroll_res.status_code, 200)

        # 2. Check audit log endpoint
        audit_res = self.client.get("/api/admin/schools/classes/cls_dubai_5a/audit-log", headers=dubai_headers)
        self.assertEqual(audit_res.status_code, 200)
        events = audit_res.json()
        self.assertTrue(len(events) >= 1)
        self.assertEqual(events[0]["action"], "learner_enrolled")
        self.assertEqual(events[0]["child_id"], "child_d2")
        self.assertEqual(events[0]["actor_id"], "usr_admin_dubai")

        # 3. Remove child_d2
        del_res = self.client.delete("/api/admin/schools/classes/cls_dubai_5a/learners/child_d2", headers=dubai_headers)
        self.assertEqual(del_res.status_code, 200)

        # 4. Check audit log has learner_removed
        audit_res_after = self.client.get("/api/admin/schools/classes/cls_dubai_5a/audit-log", headers=dubai_headers)
        self.assertEqual(audit_res_after.json()[0]["action"], "learner_removed")

        # 5. Dubai school admin cannot view RAK class audit log -> 403
        cross_audit = self.client.get("/api/admin/schools/classes/cls_rak_5b/audit-log", headers=dubai_headers)
        self.assertEqual(cross_audit.status_code, 403)

    def test_07_public_school_and_class_discovery(self):
        """Schools and classes can be listed for enrollment without leaking private student data."""
        # Public school listing
        schools_res = self.client.get("/api/curriculum/schools")
        self.assertEqual(schools_res.status_code, 200)
        school_ids = [s["id"] for s in schools_res.json()]
        self.assertIn("sch_dubai", school_ids)
        self.assertIn("sch_rak", school_ids)

        # Public school classes listing for Dubai
        classes_res = self.client.get("/api/curriculum/schools/sch_dubai/classes")
        self.assertEqual(classes_res.status_code, 200)
        cls_ids = [c["id"] for c in classes_res.json()]
        self.assertIn("cls_dubai_5a", cls_ids)
        self.assertNotIn("cls_rak_5b", cls_ids)


if __name__ == "__main__":
    unittest.main()

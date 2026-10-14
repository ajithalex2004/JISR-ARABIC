"""Tables created by older code are brought up to the current model by adding missing columns."""
import unittest

from sqlalchemy import create_engine, inspect, text

from backend import migrations
from backend.database import Base
import backend.models  # noqa: F401


class TestReconcileColumns(unittest.TestCase):
    def test_missing_columns_are_added_with_defaults(self):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE payment_transactions DROP COLUMN anonymized_parent_id"))
            conn.execute(text("ALTER TABLE child_profiles DROP COLUMN avatar_id"))
            conn.execute(text("INSERT INTO users (id, email, password_hash, role) VALUES ('p1', 'p@t.c', 'x', 'parent')"))
            conn.execute(text("INSERT INTO child_profiles (id, parent_id, name) VALUES ('c1', 'p1', 'Ann')"))
        with engine.connect() as conn:
            self.assertEqual(
                sorted(f"{t}.{c.name}" for t, c in migrations.missing_columns(conn)),
                ["child_profiles.avatar_id", "payment_transactions.anonymized_parent_id"],
            )
            added, skipped = migrations.reconcile_columns(conn)
            conn.commit()
        self.assertEqual(sorted(added), ["child_profiles.avatar_id", "payment_transactions.anonymized_parent_id"])
        self.assertEqual(skipped, [])
        with engine.connect() as conn:
            self.assertEqual(migrations.missing_columns(conn), [])
            self.assertEqual(conn.execute(text("SELECT avatar_id FROM child_profiles")).scalar(), "avatar_falcon")
            self.assertIn("anonymized_parent_id", {c["name"] for c in inspect(conn).get_columns("payment_transactions")})

    def test_not_null_column_without_default_is_skipped(self):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE child_profiles DROP COLUMN name"))
        with engine.connect() as conn:
            added, skipped = migrations.reconcile_columns(conn)
        self.assertEqual((added, skipped), ([], ["child_profiles.name"]))


if __name__ == "__main__":
    unittest.main()

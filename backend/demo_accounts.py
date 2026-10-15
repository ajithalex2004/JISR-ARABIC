"""Remove the demo and test accounts from a live database.

The demo fixtures (``curriculum_seed`` with ``FAHIM_SEED_DEMO=1``) create accounts whose
passwords are in the source code, and test sign-ups leave throwaway families behind. Neither
belongs on the live site, so the production container removes them on start-up:

    python -m backend.demo_accounts

Each account goes through the normal account deletion, so its students and their progress
are removed and its payments are kept anonymised for VAT records. Running it again does nothing.
"""
import logging
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.models import User

logger = logging.getLogger("fahim.demo_accounts")

DEMO_EMAILS = ("parent@fahim.ae", "tutor@fahim.ae", "cohort.parents@sunrise.ae")
# Throwaway families created by sign-up tests ("Parent of Zayed", student_test_<timestamp>@...).
TEST_EMAIL_PREFIXES = ("student_test_",)


def demo_accounts(db: Session) -> List[User]:
    conditions = [User.email.in_(DEMO_EMAILS)]
    conditions += [User.email.like(prefix.replace("_", r"\_") + "%", escape="\\") for prefix in TEST_EMAIL_PREFIXES]
    # Never touch an admin, whatever its address.
    return db.query(User).filter(or_(*conditions), User.role != "admin").all()


def remove_demo_accounts(db: Session) -> List[str]:
    from backend.modules.identity.service import delete_account

    removed = []
    for user in demo_accounts(db):
        email = user.email
        delete_account(user=user, db=db)
        removed.append(email)
        logger.info("Removed demo account %s", email)
    return removed


def main() -> None:
    from backend.database import SessionLocal

    db = SessionLocal()
    try:
        removed = remove_demo_accounts(db)
    finally:
        db.close()
    print(f">> Demo accounts removed: {', '.join(removed) if removed else 'none'}")


if __name__ == "__main__":
    main()

# Test package
#
# AI calls record usage in the ai_usage table. Point that at a private in-memory database for the
# test run, so usage from repeated runs never accumulates (and trips the daily AI limit).
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.ai import usage as _ai_usage
from backend.models import AIUsage as _AIUsage

_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
_AIUsage.__table__.create(_engine)
_ai_usage.set_session_factory(sessionmaker(bind=_engine))

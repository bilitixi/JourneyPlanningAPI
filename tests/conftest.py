import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlalchemy import text
from db import Base, engine, SessionLocal


@pytest.fixture(scope='function')
def db_session():
    """Create a clean test database session."""

    # 🔥 FIX: disable FK checks (MySQL issue)
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
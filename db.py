import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MySQL Database Configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'journey_planning')

# Create MySQL connection string
# For Docker container, use container name or 'host.docker.internal' if needed
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use this in your routes to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    Call this function when starting the application.
    """
    from models.user import User
    from models.journey import Journey
    from models.api_usage_log import APIUsageLog
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def test_connection():
    """
    Test the MySQL database connection.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("MySQL database connection successful!")
            return True
    except Exception as e:
        print(f"MySQL database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test connection when running db.py directly
    test_connection()

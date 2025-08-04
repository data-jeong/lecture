import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import StaticPool

from .models import Base


class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self, database_url: Optional[str] = None):
        if database_url is None:
            db_path = Path("grade_system.db")
            database_url = f"sqlite:///{db_path}"
            
        self.database_url = database_url
        self.engine = self._create_engine()
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        
    def _create_engine(self) -> Engine:
        """Create database engine with proper configuration"""
        if self.database_url.startswith("sqlite"):
            # SQLite specific configuration
            engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
            
            # Enable foreign key constraints for SQLite
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        else:
            # PostgreSQL/MySQL configuration
            engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=False
            )
            
        return engine
        
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        
    def drop_tables(self):
        """Drop all database tables"""
        Base.metadata.drop_all(bind=self.engine)
        
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
        
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope for database operations"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    def close(self):
        """Close database connection"""
        self.SessionLocal.remove()
        self.engine.dispose()


# Global database instance
_db_connection: Optional[DatabaseConnection] = None


def init_database(database_url: Optional[str] = None) -> DatabaseConnection:
    """Initialize database connection"""
    global _db_connection
    
    if _db_connection is None:
        _db_connection = DatabaseConnection(database_url)
        _db_connection.create_tables()
        
    return _db_connection


def get_session() -> Session:
    """Get database session"""
    if _db_connection is None:
        init_database()
        
    return _db_connection.get_session()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Get database session with context manager"""
    if _db_connection is None:
        init_database()
        
    with _db_connection.session_scope() as session:
        yield session


def close_database():
    """Close database connection"""
    global _db_connection
    
    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None
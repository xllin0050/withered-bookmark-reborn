from datetime import datetime, timezone

from sqlalchemy import (  # noqa: F401
    JSON,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./bookmarks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=True)  # 頁面主要內容
    keywords = Column(JSON, default=list)  # 使用 JSON 類型
    from datetime import timezone

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    tfidf_vector = Column(Text)  # JSON 字符串，存儲 TF-IDF 向量


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 建立所有表
def create_tables():
    Base.metadata.create_all(bind=engine)

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class BookmarkBase(BaseModel):
    url: HttpUrl
    title: str
    description: Optional[str] = ""


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class BookmarkResponse(BookmarkBase):
    id: int
    content: Optional[str]
    keywords: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    access_count: int
    last_accessed: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10


class SearchResult(BaseModel):
    bookmark: BookmarkResponse
    relevance_score: float
    matched_keywords: List[str]


class AnalyzeUrlRequest(BaseModel):
    url: HttpUrl


class AnalyzeUrlResponse(BaseModel):
    title: str
    content: str
    keywords: List[str]
    summary: str

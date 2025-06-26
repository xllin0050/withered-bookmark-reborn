from datetime import datetime
from typing import List, Optional

import ast
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


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

    @field_validator("keywords", mode="before")
    @classmethod
    def parse_keywords(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                # ast.literal_eval 可以安全地解析 Python 字面值字串 (例如 '["a", "b"]' 或 "['a', 'b']")
                result = ast.literal_eval(v)
                if isinstance(result, list):
                    return result
            except (ValueError, SyntaxError):
                # 如果解析失敗 (例如，它是一個普通字串)，則返回空列表
                return []
        # 如果不是字串 (例如 None) 或解析失敗，返回原值或空列表
        return v if v is not None else []


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

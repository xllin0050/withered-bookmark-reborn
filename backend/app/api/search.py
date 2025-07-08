from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session

from app.models.database import Bookmark, get_db
from app.models.schemas import (
    AnalyzeUrlRequest,
    AnalyzeUrlResponse,
    BookmarkResponse,
    SearchRequest,
    SearchResult,
)

router = APIRouter()


@router.post("/", response_model=List[SearchResult])
async def search_bookmarks(search_request: SearchRequest, db: Session = Depends(get_db)):
    """搜尋書籤"""
    query = search_request.query
    limit = search_request.limit

    if not query:
        return []

    # 建立基礎查詢
    search_query = db.query(Bookmark).filter(
        or_(
            Bookmark.title.ilike(f"%{query}%"),
            Bookmark.description.ilike(f"%{query}%"),
            Bookmark.content.ilike(f"%{query}%"),
            cast(Bookmark.keywords, String).ilike(f"%{query}%"),
        )
    )

    # 獲取查詢結果
    found_bookmarks = search_query.limit(limit).all()

    # 格式化結果
    results: List[SearchResult] = []
    for bookmark in found_bookmarks:
        # 找出匹配的關鍵字
        matched_keywords = []
        if bookmark.keywords and isinstance(bookmark.keywords, list):
            for keyword in bookmark.keywords:
                if query.lower() in keyword.lower():
                    matched_keywords.append(keyword)

        # 建立 BookmarkResponse
        bookmark_response = BookmarkResponse.model_validate(bookmark)

        results.append(
            SearchResult(
                bookmark=bookmark_response,
                relevance_score=1.0,  # Phase 1: 暫時使用靜態相關性分數
                matched_keywords=matched_keywords,
            )
        )

    return results

@router.post("/analyze-url", response_model=AnalyzeUrlResponse)
async def analyze_url(request: AnalyzeUrlRequest):
    """分析 URL 內容"""
    # TODO: 實現網頁內容分析
    # 這裡先返回模擬數據，後續實現
    return AnalyzeUrlResponse(
        title="示例標題",
        content="示例內容",
        keywords=["示例", "關鍵字"],
        summary="這是一個示例摘要"
    )

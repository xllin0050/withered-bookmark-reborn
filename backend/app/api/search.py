import json
from typing import List, Tuple

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
from app.services.content_enricher import ContentEnricher
from app.services.tfidf_vectorizer import get_vectorizer

router = APIRouter()
content_enricher = ContentEnricher()


def _semantic_search(query: str, bookmarks: List[Bookmark], limit: int = 20) -> List[Tuple[Bookmark, float]]:
    """
    執行語義搜索，返回按相關性排序的書籤列表
    
    Args:
        query: 搜索查詢
        bookmarks: 候選書籤列表
        limit: 返回結果數量限制
        
    Returns:
        (書籤, 相關性分數) 的列表，按相關性降序排列
    """
    try:
        # 為查詢生成向量
        query_vector = content_enricher.generate_tfidf_vector_for_query(query)
        if not query_vector:
            return [(bookmark, 1.0) for bookmark in bookmarks[:limit]]

        vectorizer = get_vectorizer()
        results = []
        
        for bookmark in bookmarks:
            try:
                # 解析書籤的 TF-IDF 向量
                bookmark_vector = None
                if bookmark.tfidf_vector:
                    if isinstance(bookmark.tfidf_vector, str):
                        bookmark_vector = json.loads(bookmark.tfidf_vector)
                    else:
                        bookmark_vector = bookmark.tfidf_vector
                
                # 計算相似度
                if bookmark_vector:
                    # 確保兩個向量都是字符串格式
                    bookmark_vector_str = bookmark_vector if isinstance(bookmark_vector, str) else json.dumps(bookmark_vector)
                    query_vector_str = query_vector if isinstance(query_vector, str) else json.dumps(query_vector)
                    
                    similarity = vectorizer.calculate_similarity(query_vector_str, bookmark_vector_str)
                    # 為確保有基本相關性，給關鍵字匹配增加權重
                    keyword_bonus = _calculate_keyword_bonus(query, bookmark)
                    final_score = similarity * 0.7 + keyword_bonus * 0.3
                else:
                    # 沒有向量的情況下，只使用關鍵字匹配分數
                    final_score = _calculate_keyword_bonus(query, bookmark)
                
                results.append((bookmark, final_score))
                
            except Exception as e:
                print(f"Error calculating similarity for bookmark {bookmark.id}: {e}")
                results.append((bookmark, 0.1))  # 給一個低分數
        
        # 按相關性分數排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
        
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return [(bookmark, 1.0) for bookmark in bookmarks[:limit]]


def _calculate_keyword_bonus(query: str, bookmark: Bookmark) -> float:
    """
    計算基於關鍵字匹配的獎勵分數
    
    Args:
        query: 搜索查詢
        bookmark: 書籤對象
        
    Returns:
        關鍵字匹配分數 (0-1)
    """
    query_lower = query.lower()
    score = 0.0
    
    # 標題匹配 (權重最高)
    if bookmark.title and query_lower in bookmark.title.lower():
        score += 0.5
    
    # 描述匹配
    if bookmark.description and query_lower in bookmark.description.lower():
        score += 0.3
    
    # 關鍵字匹配
    if bookmark.keywords and isinstance(bookmark.keywords, list):
        for keyword in bookmark.keywords:
            if query_lower in keyword.lower():
                score += 0.2
                break  # 只計算一次關鍵字匹配
    
    return min(score, 1.0)  # 確保分數不超過 1.0


@router.post("/", response_model=List[SearchResult])
async def search_bookmarks(search_request: SearchRequest, db: Session = Depends(get_db)):
    """智能搜尋書籤 - 結合關鍵字搜索和語義搜索"""
    query = search_request.query
    limit = search_request.limit

    if not query:
        return []

    try:
        # 先用關鍵字搜索獲取候選集合 (擴大搜索範圍)
        keyword_query = db.query(Bookmark).filter(
            or_(
                Bookmark.title.ilike(f"%{query}%"),
                Bookmark.description.ilike(f"%{query}%"),
                Bookmark.content.ilike(f"%{query}%"),
                cast(Bookmark.keywords, String).ilike(f"%{query}%"),
            )
        )
        
        keyword_bookmarks = keyword_query.limit(limit * 3).all()  # 獲取更多候選項
        
        if not keyword_bookmarks:
            return []
        
        # 檢查是否有訓練好的向量化器
        vectorizer = get_vectorizer()
        if not vectorizer.vectorizer:
            # 如果向量化器未訓練，嘗試使用現有書籤訓練
            all_bookmarks = db.query(Bookmark).filter(
                Bookmark.content.isnot(None),
                Bookmark.content != ""
            ).all()
            
            if all_bookmarks:
                texts = []
                for bm in all_bookmarks:
                    text_parts = []
                    if bm.title:
                        text_parts.append(bm.title)
                    if bm.description:
                        text_parts.append(bm.description)
                    if bm.content:
                        text_parts.append(bm.content)
                    if bm.keywords and isinstance(bm.keywords, list):
                        text_parts.extend(bm.keywords)
                    
                    if text_parts:
                        texts.append(" ".join(text_parts))
                
                if texts:
                    vectorizer.fit(texts)
        
        # 執行語義搜索
        semantic_results = _semantic_search(query, keyword_bookmarks, limit)
        
        # 格式化結果
        results: List[SearchResult] = []
        for bookmark, relevance_score in semantic_results:
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
                    relevance_score=round(relevance_score, 3),
                    matched_keywords=matched_keywords,
                )
            )

        return results
        
    except Exception as e:
        print(f"Error in search: {e}")
        # 降級到基本關鍵字搜索
        basic_query = db.query(Bookmark).filter(
            or_(
                Bookmark.title.ilike(f"%{query}%"),
                Bookmark.description.ilike(f"%{query}%"),
                Bookmark.content.ilike(f"%{query}%"),
                cast(Bookmark.keywords, String).ilike(f"%{query}%"),
            )
        )
        
        found_bookmarks = basic_query.limit(limit).all()
        
        results: List[SearchResult] = []
        for bookmark in found_bookmarks:
            matched_keywords = []
            if bookmark.keywords and isinstance(bookmark.keywords, list):
                for keyword in bookmark.keywords:
                    if query.lower() in keyword.lower():
                        matched_keywords.append(keyword)

            bookmark_response = BookmarkResponse.model_validate(bookmark)
            results.append(
                SearchResult(
                    bookmark=bookmark_response,
                    relevance_score=1.0,
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

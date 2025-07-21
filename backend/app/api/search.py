import json
import logging
import time
from typing import List, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
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

logger = logging.getLogger(__name__)

router = APIRouter()
content_enricher = ContentEnricher()


def _semantic_search(query: str, bookmarks: List[Bookmark], limit: int = 20) -> Tuple[List[Tuple[Bookmark, float]], dict]:
    """
    執行語義搜索，返回按相關性排序的書籤列表和性能指標
    
    Args:
        query: 搜索查詢
        bookmarks: 候選書籤列表
        limit: 返回結果數量限制
        
    Returns:
        ((書籤, 相關性分數) 的列表，性能指標字典)
    """
    start_time = time.time()
    metrics = {
        "total_candidates": len(bookmarks),
        "vector_generation_time": 0,
        "similarity_calculations": 0,
        "similarity_calculation_time": 0,
        "vectors_found": 0,
        "vectors_missing": 0
    }
    
    try:
        # 為查詢生成向量
        vector_start = time.time()
        query_vector = content_enricher.generate_tfidf_vector_for_query(query)
        metrics["vector_generation_time"] = time.time() - vector_start
        
        if not query_vector:
            logger.warning(f"Failed to generate vector for query: {query}")
            metrics["total_time"] = time.time() - start_time
            return [(bookmark, 1.0) for bookmark in bookmarks[:limit]], metrics

        vectorizer = get_vectorizer()
        results = []
        similarity_start = time.time()
        
        # 準備批量相似度計算的數據
        bookmark_vectors = []
        bookmarks_by_id = {}
        
        for bookmark in bookmarks:
            if bookmark.tfidf_vector:
                bookmark_vectors.append((str(bookmark.id), bookmark.tfidf_vector))
                bookmarks_by_id[str(bookmark.id)] = bookmark
        
        # 使用批量相似度計算（更高效）
        if bookmark_vectors:
            similarity_results = vectorizer.calculate_batch_similarity(query_vector, bookmark_vectors)
            
            for bookmark_id, similarity_score in similarity_results:
                bookmark = bookmarks_by_id.get(bookmark_id)
                if bookmark:
                    # 為確保有基本相關性，給關鍵字匹配增加權重
                    keyword_bonus = _calculate_keyword_bonus(query, bookmark)
                    final_score = similarity_score * 0.7 + keyword_bonus * 0.3
                    results.append((bookmark, final_score))
                    metrics["similarity_calculations"] += 1
                    metrics["vectors_found"] += 1
        
        # 處理沒有向量的書籤
        for bookmark in bookmarks:
            if not bookmark.tfidf_vector or str(bookmark.id) not in bookmarks_by_id:
                metrics["vectors_missing"] += 1
                final_score = _calculate_keyword_bonus(query, bookmark)
                results.append((bookmark, final_score))
        
        metrics["similarity_calculation_time"] = time.time() - similarity_start
        
        # 按相關性分數排序
        results.sort(key=lambda x: x[1], reverse=True)
        metrics["total_time"] = time.time() - start_time
        
        logger.info(f"Semantic search completed: {metrics}")
        return results[:limit], metrics
        
    except Exception as e:
        metrics["total_time"] = time.time() - start_time
        logger.error(f"Error in semantic search: {e}")
        return [(bookmark, 1.0) for bookmark in bookmarks[:limit]], metrics


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
    
    # 開始計時總體性能
    total_start_time = time.time()
    logger.info(f"Starting search for query: '{query}' (limit: {limit})")

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
        semantic_results, search_metrics = _semantic_search(query, keyword_bookmarks, limit)
        
        # 記錄搜尋性能指標
        total_time = time.time() - total_start_time
        logger.info(
            f"Search completed in {total_time:.3f}s - "
            f"Keyword candidates: {len(keyword_bookmarks)}, "
            f"Semantic results: {len(semantic_results)}, "
            f"Search metrics: {search_metrics}"
        )
        
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
        total_time = time.time() - total_start_time
        logger.error(f"Error in semantic search after {total_time:.3f}s: {e}")
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

@router.get("/health")
async def search_health_check(db: Session = Depends(get_db)):
    """搜尋系統健康檢查"""
    try:
        vectorizer = get_vectorizer()
        
        # 檢查資料庫連接
        total_bookmarks = db.query(Bookmark).count()
        bookmarks_with_vectors = db.query(Bookmark).filter(
            Bookmark.tfidf_vector.isnot(None),
            Bookmark.tfidf_vector != ""
        ).count()
        
        # 獲取向量化器狀態
        is_vectorizer_trained = vectorizer.vectorizer is not None
        cache_stats = vectorizer.get_cache_stats()
        
        # 系統狀態
        system_status = "healthy"
        issues = []
        
        if not is_vectorizer_trained and total_bookmarks > 0:
            system_status = "degraded"
            issues.append("Vectorizer not trained but bookmarks exist")
        
        if total_bookmarks > 0 and bookmarks_with_vectors / total_bookmarks < 0.5:
            system_status = "degraded" 
            issues.append(f"Low vectorization coverage: {bookmarks_with_vectors}/{total_bookmarks}")
        
        return {
            "status": system_status,
            "timestamp": time.time(),
            "database": {
                "total_bookmarks": total_bookmarks,
                "vectorized_bookmarks": bookmarks_with_vectors,
                "vectorization_coverage": bookmarks_with_vectors / total_bookmarks if total_bookmarks > 0 else 0
            },
            "vectorizer": {
                "is_trained": is_vectorizer_trained,
                "feature_count": len(vectorizer.feature_names),
                "max_features": vectorizer.max_features
            },
            "cache": cache_stats,
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e),
            "issues": ["Health check failed"]
        }

@router.get("/vectorizer/stats")
async def get_vectorizer_stats():
    """獲取向量化器統計資訊"""
    try:
        vectorizer = get_vectorizer()
        cache_stats = vectorizer.get_cache_stats()
        
        return {
            "vectorizer": {
                "is_trained": vectorizer.vectorizer is not None,
                "feature_count": len(vectorizer.feature_names),
                "max_features": vectorizer.max_features,
                "min_df": vectorizer.min_df,
                "max_df": vectorizer.max_df
            },
            "cache": cache_stats,
            "stop_words_count": len(vectorizer.stop_words)
        }
        
    except Exception as e:
        logger.error(f"Error getting vectorizer stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting vectorizer statistics: {str(e)}"
        )

@router.post("/vectorizer/clear-cache")
async def clear_vectorizer_cache():
    """清空向量化器快取"""
    try:
        vectorizer = get_vectorizer()
        old_size = len(vectorizer.similarity_cache)
        vectorizer.clear_cache()
        
        logger.info(f"Cleared vectorizer cache (removed {old_size} entries)")
        return {
            "success": True,
            "message": f"Cleared {old_size} cache entries",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error clearing vectorizer cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )

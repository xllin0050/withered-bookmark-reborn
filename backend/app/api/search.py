from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import AnalyzeUrlRequest, AnalyzeUrlResponse, SearchRequest, SearchResult

router = APIRouter()

@router.post("/", response_model=List[SearchResult])
async def search_bookmarks(search_request: SearchRequest, db: Session = Depends(get_db)):
    """搜尋書籤"""
    # TODO: 實現語義搜尋邏輯
    # 這裡先返回空結果，後續實現
    return []

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

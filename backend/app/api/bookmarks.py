from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.database import Bookmark, get_db
from app.models.schemas import BookmarkCreate, BookmarkResponse, BookmarkUpdate  # noqa: F401
from app.services.bookmark_importer import parse_and_import_bookmarks
from app.services.content_enricher import ContentEnricher
from app.services.tfidf_vectorizer import get_vectorizer, reset_vectorizer

router = APIRouter()

# 初始化內容豐富化服務
content_enricher = ContentEnricher()


@router.post("/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark: BookmarkCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """創建新書籤"""
    try:
        # 檢查是否已存在相同 URL
        existing = db.query(Bookmark).filter(Bookmark.url == str(bookmark.url)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bookmark with this URL already exists",
            )

        db_bookmark = Bookmark(
            url=str(bookmark.url), title=bookmark.title, description=bookmark.description
        )
        db.add(db_bookmark)
        db.commit()
        db.refresh(db_bookmark)

        # 添加背景任務來豐富內容
        background_tasks.add_task(
            enrich_bookmark_content, bookmark_id=db_bookmark.id, url=db_bookmark.url
        )

        return db_bookmark
    except HTTPException as http_exc:
        db.rollback()
        raise http_exc
    except Exception as e:
        db.rollback()
        print(f"Error creating bookmark: {str(e)}")  # 在日誌中記錄錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating bookmark: {str(e)}",
        )


@router.get("/bookmarks", response_model=List[BookmarkResponse])
async def get_bookmarks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """獲取書籤列表"""
    bookmarks = db.query(Bookmark).offset(skip).limit(limit).all()
    return bookmarks


@router.get("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """獲取單個書籤"""
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark


@router.put("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int, bookmark: BookmarkUpdate, db: Session = Depends(get_db)
):
    """更新指定ID的書籤"""
    db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db_bookmark.title = bookmark.title
    db_bookmark.description = bookmark.description
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


@router.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """刪除指定ID的書籤"""
    try:
        # 查詢書籤是否存在
        db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
        if not db_bookmark:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

        # 刪除書籤
        db.delete(db_bookmark)
        db.commit()
        return None  # 204 No Content 不返回內容

    except Exception as e:
        db.rollback()
        print(f"Error deleting bookmark: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting bookmark: {str(e)}",
        )


@router.post("/bookmarks/upload", status_code=status.HTTP_201_CREATED)
async def upload_bookmarks_file(
    background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    上傳並匯入書籤檔案 (HTML 格式)。
    """
    if not file.filename.endswith(".html"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an HTML file.",
        )

    try:
        # 呼叫服務層的函式來處理檔案
        imported_bookmarks = parse_and_import_bookmarks(db, file.file)

        # 為每個新書籤添加背景豐富化任務
        for bookmark_info in imported_bookmarks:
            background_tasks.add_task(
                enrich_bookmark_content, bookmark_id=bookmark_info["id"], url=bookmark_info["url"]
            )

        imported_count = len(imported_bookmarks)
        return {
            "message": f"Successfully imported {imported_count} bookmarks. Enrichment tasks are running in the background.",
            "count": imported_count,
        }
    except Exception as e:
        # 捕獲服務層可能拋出的任何異常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the file: {str(e)}",
        )


@router.post("/bookmarks/{bookmark_id}/enrich", status_code=status.HTTP_202_ACCEPTED)
async def enrich_bookmark(
    bookmark_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """手動觸發書籤內容豐富化"""
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    # 添加背景任務
    background_tasks.add_task(enrich_bookmark_content, bookmark_id=bookmark.id, url=bookmark.url)

    return {"message": "Content enrichment started"}


@router.post("/bookmarks/batch-vectorize", status_code=status.HTTP_202_ACCEPTED)
async def batch_vectorize_bookmarks(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """批量為所有書籤生成 TF-IDF 向量"""
    
    # 計算需要處理的書籤數量
    total_bookmarks = db.query(Bookmark).filter(
        Bookmark.content.isnot(None),
        Bookmark.content != ""
    ).count()
    
    if total_bookmarks == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No bookmarks with content found for vectorization"
        )
    
    # 添加背景任務
    background_tasks.add_task(batch_vectorize_task)
    
    return {
        "message": f"Batch vectorization started for {total_bookmarks} bookmarks",
        "total_bookmarks": total_bookmarks
    }


@router.post("/bookmarks/retrain-vectorizer", status_code=status.HTTP_202_ACCEPTED)
async def retrain_vectorizer(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """重新訓練 TF-IDF 向量化器並為所有書籤生成新向量"""
    
    total_bookmarks = db.query(Bookmark).filter(
        Bookmark.content.isnot(None),
        Bookmark.content != ""
    ).count()
    
    if total_bookmarks == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No bookmarks with content found for training"
        )
    
    # 重置向量化器並添加重新訓練任務
    reset_vectorizer()
    background_tasks.add_task(retrain_and_vectorize_task)
    
    return {
        "message": f"Vectorizer retraining started for {total_bookmarks} bookmarks",
        "total_bookmarks": total_bookmarks
    }


def batch_vectorize_task():
    """背景任務：為現有書籤批量生成向量"""
    from app.models.database import SessionLocal
    
    db = SessionLocal()
    try:
        print("Starting batch vectorization...")
        
        # 獲取所有有內容的書籤
        bookmarks = db.query(Bookmark).filter(
            Bookmark.content.isnot(None),
            Bookmark.content != ""
        ).all()
        
        if not bookmarks:
            print("No bookmarks found for vectorization")
            return
        
        # 確保向量化器已訓練
        vectorizer = get_vectorizer()
        if not vectorizer.vectorizer:
            print("Training vectorizer with existing bookmarks...")
            texts = []
            for bookmark in bookmarks:
                text_parts = []
                if bookmark.title:
                    text_parts.append(bookmark.title)
                if bookmark.description:
                    text_parts.append(bookmark.description)
                if bookmark.content:
                    text_parts.append(bookmark.content)
                if bookmark.keywords and isinstance(bookmark.keywords, list):
                    text_parts.extend(bookmark.keywords)
                
                if text_parts:
                    texts.append(" ".join(text_parts))
            
            if texts:
                vectorizer.fit(texts)
                print(f"Vectorizer trained with {len(texts)} texts")
        
        # 為每個書籤生成向量
        processed_count = 0
        error_count = 0
        
        for bookmark in bookmarks:
            try:
                # 生成 TF-IDF 向量
                tfidf_vector = content_enricher.generate_tfidf_vector(
                    bookmark.title or "",
                    bookmark.description or "",
                    bookmark.content or "",
                    bookmark.keywords or []
                )
                
                if tfidf_vector:
                    bookmark.tfidf_vector = tfidf_vector
                    bookmark.updated_at = datetime.now(timezone.utc)
                    processed_count += 1
                else:
                    print(f"Failed to generate vector for bookmark {bookmark.id}")
                    error_count += 1
                    
            except Exception as e:
                print(f"Error processing bookmark {bookmark.id}: {e}")
                error_count += 1
        
        # 批量提交更改
        try:
            db.commit()
            print(f"Batch vectorization completed: {processed_count} processed, {error_count} errors")
        except Exception as e:
            db.rollback()
            print(f"Error committing batch updates: {e}")
            
    except Exception as e:
        print(f"Error in batch vectorization task: {e}")
    finally:
        db.close()


def retrain_and_vectorize_task():
    """背景任務：重新訓練向量化器並生成所有向量"""
    from app.models.database import SessionLocal
    
    db = SessionLocal()
    try:
        print("Starting vectorizer retraining and batch vectorization...")
        
        # 獲取所有有內容的書籤
        bookmarks = db.query(Bookmark).filter(
            Bookmark.content.isnot(None),
            Bookmark.content != ""
        ).all()
        
        if not bookmarks:
            print("No bookmarks found for retraining")
            return
        
        # 收集所有文本用於訓練
        print("Collecting texts for training...")
        texts = []
        for bookmark in bookmarks:
            text_parts = []
            if bookmark.title:
                text_parts.append(bookmark.title)
            if bookmark.description:
                text_parts.append(bookmark.description)
            if bookmark.content:
                text_parts.append(bookmark.content)
            if bookmark.keywords and isinstance(bookmark.keywords, list):
                text_parts.extend(bookmark.keywords)
            
            if text_parts:
                texts.append(" ".join(text_parts))
        
        if not texts:
            print("No texts found for training")
            return
        
        # 重新訓練向量化器
        print(f"Training vectorizer with {len(texts)} texts...")
        vectorizer = get_vectorizer()
        vectorizer.fit(texts)
        print("Vectorizer training completed")
        
        # 為所有書籤生成新向量
        print("Generating vectors for all bookmarks...")
        processed_count = 0
        error_count = 0
        
        for bookmark in bookmarks:
            try:
                tfidf_vector = content_enricher.generate_tfidf_vector(
                    bookmark.title or "",
                    bookmark.description or "",
                    bookmark.content or "",
                    bookmark.keywords or []
                )
                
                if tfidf_vector:
                    bookmark.tfidf_vector = tfidf_vector
                    bookmark.updated_at = datetime.now(timezone.utc)
                    processed_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Error processing bookmark {bookmark.id}: {e}")
                error_count += 1
        
        # 提交所有更改
        try:
            db.commit()
            print(f"Retraining and vectorization completed: {processed_count} processed, {error_count} errors")
        except Exception as e:
            db.rollback()
            print(f"Error committing updates: {e}")
            
    except Exception as e:
        print(f"Error in retraining task: {e}")
    finally:
        db.close()


def enrich_bookmark_content(bookmark_id: int, url: str):
    """背景任務：抓取並處理網頁內容"""
    import asyncio

    from app.models.database import SessionLocal

    db = SessionLocal()
    try:
        # 獲取書籤
        bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
        if not bookmark:
            return

        # 抓取內容 - 在同步函數中執行異步操作
        content_data = asyncio.run(content_enricher.extract_content(url))

        if content_data:
            # 更新書籤內容
            bookmark.content = content_data.get("content", "")
            # 直接將列表賦值給 JSON 欄位
            bookmark.keywords = content_data.get("keywords", [])
            if content_data.get("title") and not bookmark.title:
                bookmark.title = content_data["title"]
            if content_data.get("description") and not bookmark.description:
                bookmark.description = content_data["description"]

            # 更新 TF-IDF 向量
            if content_data.get("tfidf_vector"):
                bookmark.tfidf_vector = content_data["tfidf_vector"]

            bookmark.updated_at = datetime.now(timezone.utc)
            db.commit()

    except Exception as e:
        print(f"Error enriching bookmark {bookmark_id}: {str(e)}")
    finally:
        db.close()

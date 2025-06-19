from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import Bookmark, get_db
from app.models.schemas import BookmarkCreate, BookmarkResponse, BookmarkUpdate  # noqa: F401

router = APIRouter()

@router.post("/", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(bookmark: BookmarkCreate, db: Session = Depends(get_db)):
    """創建新書籤"""
    try:
        # 檢查是否已存在相同 URL
        existing = db.query(Bookmark).filter(Bookmark.url == str(bookmark.url)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bookmark with this URL already exists"
            )
        
        db_bookmark = Bookmark(
            url=str(bookmark.url),
            title=bookmark.title,
            description=bookmark.description
        )
        db.add(db_bookmark)
        db.commit()
        db.refresh(db_bookmark)
        return db_bookmark
    except Exception as e:
        db.rollback()
        print(f"Error creating bookmark: {str(e)}")  # 在日誌中記錄錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating bookmark: {str(e)}"
        )

@router.get("/", response_model=List[BookmarkResponse])
async def get_bookmarks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """獲取書籤列表"""
    bookmarks = db.query(Bookmark).offset(skip).limit(limit).all()
    return bookmarks

@router.get("/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """獲取單個書籤"""
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark

@router.put("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(bookmark_id: int, bookmark: BookmarkUpdate, db: Session = Depends(get_db)):
    """更新指定ID的書籤"""
    db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not db_bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db_bookmark.title = bookmark.title
    db_bookmark.description = bookmark.description
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """刪除指定ID的書籤"""
    try:
        # 查詢書籤是否存在
        db_bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
        if not db_bookmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found"
            )
        
        # 刪除書籤
        db.delete(db_bookmark)
        db.commit()
        return None  # 204 No Content 不返回內容
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting bookmark: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting bookmark: {str(e)}"
        )

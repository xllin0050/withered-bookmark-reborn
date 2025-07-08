from typing import IO, Dict, List

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.database import Bookmark


def parse_and_import_bookmarks(db: Session, file: IO[bytes]) -> List[Dict[str, any]]:
    """
    解析 HTML 書籤檔案並將其匯入資料庫。

    Args:
        db: SQLAlchemy Session 物件。
        file: HTML 檔案物件。

    Returns:
        一個包含新書籤 id 和 url 的字典列表。
    """
    try:
        content = file.read().decode("utf-8")
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all("a")
        
        imported_count = 0
        new_bookmarks = []

        for link in links:
            url = link.get("href")
            title = link.string

            if not url or not title:
                continue

            # 檢查 URL 是否已存在
            exists = db.query(Bookmark).filter(Bookmark.url == url).first()
            if not exists:
                new_bookmark = Bookmark(
                    url=url,
                    title=title.strip(),
                    description=""
                )
                new_bookmarks.append(new_bookmark)
        
        imported_bookmarks = []
        if new_bookmarks:
            db.add_all(new_bookmarks)
            db.commit()
            for bookmark in new_bookmarks:
                db.refresh(bookmark)  # 確保獲取到資料庫分配的 ID
                imported_bookmarks.append({"id": bookmark.id, "url": bookmark.url})

        return imported_bookmarks

    except Exception as e:
        db.rollback()
        # 可以在這裡加入日誌記錄
        print(f"Error importing bookmarks: {e}")
        raise e

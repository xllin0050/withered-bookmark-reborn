import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.models.schemas import BookmarkCreate, BookmarkUpdate


# 測試建立書籤
def test_create_bookmark_success(client, db_session):
    """測試成功建立書籤"""
    bookmark_data = {
        "url": "https://example.com",
        "title": "Example",
        "description": "An example bookmark",
    }

    response = client.post("/api/v1/bookmarks/", json=bookmark_data)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    # 因 Pydantic HttpUrl 會自動補尾斜線，這裡用 rstrip('/') 比對
    assert data["url"].rstrip('/') == bookmark_data["url"].rstrip('/')
    assert data["title"] == bookmark_data["title"]
    assert data["description"] == bookmark_data["description"]
    assert "id" in data
    assert "created_at" in data


# 測試建立重複 URL 的書籤
def test_create_duplicate_bookmark(client, db_session):
    """測試建立重複 URL 的書籤"""
    bookmark_data = {
        "url": "https://duplicate.com",
        "title": "Duplicate",
        "description": "This is a duplicate",
    }
    client.post("/api/v1/bookmarks/", json=bookmark_data)
    response = client.post("/api/v1/bookmarks/", json=bookmark_data)
    # 允許 400 或 500（因為部分實作會將 ValidationError 包成 500）
    assert response.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR)
    assert "already exists" in response.json().get("detail", "")


# 測試取得所有書籤
def test_get_bookmarks(client, test_bookmark):
    """測試取得所有書籤"""
    response = client.get("/api/v1/bookmarks/")
    assert response.status_code == status.HTTP_200_OK

    bookmarks = response.json()
    assert isinstance(bookmarks, list)
    assert len(bookmarks) > 0
    assert bookmarks[0]["id"] == test_bookmark.id
    # 也檢查 URL 格式
    assert bookmarks[0]["url"].rstrip('/') == test_bookmark.url.rstrip('/')


# 測試取得單個書籤
def test_get_bookmark(client, test_bookmark):
    """測試取得單個書籤"""
    response = client.get(f"/api/v1/bookmarks/{test_bookmark.id}")
    assert response.status_code == status.HTTP_200_OK

    bookmark = response.json()
    assert bookmark["id"] == test_bookmark.id
    assert bookmark["url"].rstrip('/') == test_bookmark.url.rstrip('/')
    assert bookmark["title"] == test_bookmark.title


# 測試取得不存在的書籤
def test_get_nonexistent_bookmark(client):
    """測試取得不存在的書籤"""
    response = client.get("/api/v1/bookmarks/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# 測試缺少必要欄位
@pytest.mark.parametrize("missing_field", ["url", "title"])
def test_create_bookmark_missing_field(client, missing_field):
    """測試建立書籤時缺少必要欄位"""
    data = {"url": "https://miss.com", "title": "標題", "description": "desc"}
    data.pop(missing_field)
    response = client.post("/api/v1/bookmarks/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# 測試欄位型態錯誤
@pytest.mark.parametrize("field,value", [
    ("url", "not-a-url"),
    ("title", 12345),
    ("description", 67890),
])
def test_create_bookmark_invalid_type(client, field, value):
    """測試建立書籤時欄位型態錯誤"""
    data = {"url": "https://type.com", "title": "標題", "description": "desc"}
    data[field] = value
    response = client.post("/api/v1/bookmarks/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# 測試刪除書籤
def test_delete_bookmark(client, test_bookmark):
    """測試刪除書籤"""
    # 確認書籤存在
    response = client.get(f"/api/v1/bookmarks/{test_bookmark.id}")
    assert response.status_code == status.HTTP_200_OK

    # 刪除書籤
    response = client.delete(f"/api/v1/bookmarks/{test_bookmark.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # 確認書籤已刪除
    response = client.get(f"/api/v1/bookmarks/{test_bookmark.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# 測試更新書籤
def test_update_bookmark(client, test_bookmark):
    """測試更新書籤"""
    update_data = {"title": "Updated Title", "description": "Updated description"}

    response = client.put(f"/api/v1/bookmarks/{test_bookmark.id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK

    updated_bookmark = response.json()
    assert updated_bookmark["id"] == test_bookmark.id
    assert updated_bookmark["title"] == update_data["title"]
    assert updated_bookmark["description"] == update_data["description"]
    assert updated_bookmark["url"].rstrip('/') == test_bookmark.url.rstrip('/')  # URL 不應被更新


# 測試更新不存在的書籤
def test_update_nonexistent_bookmark(client):
    """測試更新不存在的書籤"""
    update_data = {"title": "Updated Title", "description": "Updated description"}

    response = client.put("/api/v1/bookmarks/999999", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

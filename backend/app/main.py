import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.bookmarks import router as bookmarks_router
from app.api.search import router as search_router
from app.models.database import create_tables
from app.services.tfidf_vectorizer import train_vectorizer_if_needed

# 設定日誌記錄
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app):
    # 啟動時執行的初始化程式碼
    create_tables()  # 啟動時自動建立資料表
    train_vectorizer_if_needed()  # 啟動時訓練 TF-IDF 模型
    yield
    # 關閉時執行的清理程式碼


app = FastAPI(
    title="Withered Bookmark Reborn API",
    description="枯枝逢生 - 後端API",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3008", "http://localhost:5173", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(bookmarks_router, prefix="/api/v1", tags=["bookmarks"])
app.include_router(search_router, prefix="/api/v1/search", tags=["search"])


@app.get("/")
async def root():
    return {
        "message": "Withered Bookmark Reborn API",
        "description": "枯枝逢生 - 讓書籤重新發揮價值",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

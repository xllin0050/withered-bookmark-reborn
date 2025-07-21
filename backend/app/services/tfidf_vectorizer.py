"""
TF-IDF 向量化服務
提供文本向量化、相似度計算等核心功能
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import jieba
import numpy as np
from jieba import analyse
from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class TFIDFVectorizer:
    """TF-IDF 向量化器，集成中文分詞和向量相似度計算"""
    
    def __init__(self, max_features: int = 5000, min_df: int = 2, max_df: float = 0.8):
        """
        初始化 TF-IDF 向量化器
        
        Args:
            max_features: 最大特徵數量
            min_df: 最小文檔頻率
            max_df: 最大文檔頻率
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.vectorizer: Optional[SklearnTfidfVectorizer] = None
        self.feature_names: List[str] = []
        
        # 中文停用詞列表
        self.stop_words = {
            '的', '是', '在', '了', '和', '有', '我', '你', '他', '她', '它', '們',
            '這', '那', '這個', '那個', '上', '下', '中', '內', '外', '前', '後',
            '左', '右', '大', '小', '高', '低', '長', '短', '好', '壞', '新', '舊',
            '多', '少', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
            '會', '能', '要', '可以', '應該', '必須', '可能', '也許', '但是', '然而',
            '因為', '所以', '如果', '那麼', '雖然', '除了', '除非', '直到', '當',
            'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are',
            'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might',
            'must', 'shall', 'to', 'of', 'in', 'for', 'with', 'by', 'from'
        }
        
    def _preprocess_text(self, text: str) -> str:
        """
        預處理文本：分詞、去停用詞、清理
        
        Args:
            text: 原始文本
            
        Returns:
            處理後的文本
        """
        if not text or not text.strip():
            return ""
            
        # 使用 jieba 分詞
        words = jieba.lcut(text.lower())
        
        # 過濾停用詞和短詞
        filtered_words = [
            word.strip() for word in words 
            if word.strip() and len(word.strip()) > 1 and word.strip() not in self.stop_words
        ]
        
        return " ".join(filtered_words)
    
    def fit(self, texts: List[str]) -> None:
        """
        使用文本語料庫訓練 TF-IDF 向量化器
        
        Args:
            texts: 文本列表
        """
        if not texts:
            logger.warning("No texts provided for TF-IDF training")
            return
            
        # 預處理所有文本
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        # 過濾空文本
        processed_texts = [text for text in processed_texts if text.strip()]
        
        if not processed_texts:
            logger.warning("No valid texts after preprocessing")
            return
            
        # 創建 TF-IDF 向量化器
        self.vectorizer = SklearnTfidfVectorizer(
            max_features=self.max_features,
            min_df=self.min_df,
            max_df=self.max_df,
            tokenizer=str.split,  # 因為已經預處理過了
            lowercase=False,  # 已經轉小寫了
            stop_words=None  # 已經去停用詞了
        )
        
        # 訓練向量化器
        try:
            self.vectorizer.fit(processed_texts)
            self.feature_names = self.vectorizer.get_feature_names_out().tolist()
            logger.info(f"TF-IDF vectorizer trained with {len(self.feature_names)} features")
        except Exception as e:
            logger.error(f"Error training TF-IDF vectorizer: {e}")
            self.vectorizer = None
    
    def transform(self, text: str) -> Optional[str]:
        """
        將文本轉換為 TF-IDF 向量

        Args:
            text: 輸入文本

        Returns:
            包含向量資訊的 JSON 字串或 None
        """
        if not self.vectorizer:
            logger.warning("TF-IDF vectorizer not trained")
            return None

        if not text or not text.strip():
            return None

        processed_text = self._preprocess_text(text)
        if not processed_text.strip():
            return None

        try:
            # 生成 TF-IDF 向量
            vector_matrix = self.vectorizer.transform([processed_text])
            vector_dense = vector_matrix.toarray()[0]

            # 轉換為稀疏格式（只保存非零值）
            sparse_vector = {}
            for idx, value in enumerate(vector_dense):
                if value > 0:
                    sparse_vector[str(idx)] = float(value)

            vector_data = {
                "vector": sparse_vector,
                "feature_count": len(self.feature_names),
                "non_zero_count": len(sparse_vector)
            }
            
            return json.dumps(vector_data)

        except Exception as e:
            logger.error(f"Error transforming text to vector: {e}")
            return None
    
    def calculate_similarity(self, vector1_json: str, vector2_json: str) -> float:
        """
        計算兩個 JSON 格式向量之間的餘弦相似度

        Args:
            vector1_json: 第一個向量的 JSON 字串
            vector2_json: 第二個向量的 JSON 字串

        Returns:
            相似度分數 (0-1)
        """
        if not vector1_json or not vector2_json:
            return 0.0

        if not self.vectorizer:
            return 0.0

        try:
            vector1 = json.loads(vector1_json)
            vector2 = json.loads(vector2_json)

            # 提取稀疏向量
            sparse1 = vector1.get("vector", {})
            sparse2 = vector2.get("vector", {})

            if not sparse1 or not sparse2:
                return 0.0

            feature_count = max(vector1.get("feature_count", 0), vector2.get("feature_count", 0), len(self.feature_names))
            if feature_count == 0:
                return 0.0

            # 轉換為密集向量
            dense1 = np.zeros(feature_count)
            dense2 = np.zeros(feature_count)

            for idx_str, value in sparse1.items():
                idx = int(idx_str)
                if idx < feature_count:
                    dense1[idx] = value

            for idx_str, value in sparse2.items():
                idx = int(idx_str)
                if idx < feature_count:
                    dense2[idx] = value

            # 計算餘弦相似度
            similarity = cosine_similarity([dense1], [dense2])[0][0]
            return float(similarity)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def get_top_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        提取文本的關鍵詞及其 TF-IDF 分數
        
        Args:
            text: 輸入文本
            top_k: 返回前 k 個關鍵詞
            
        Returns:
            (關鍵詞, 分數) 的列表
        """
        if not self.vectorizer or not text:
            return []
            
        processed_text = self._preprocess_text(text)
        if not processed_text.strip():
            return []
            
        try:
            # 生成向量
            vector_matrix = self.vectorizer.transform([processed_text])
            vector_dense = vector_matrix.toarray()[0]
            
            # 獲取詞-分數對
            word_scores = []
            for idx, score in enumerate(vector_dense):
                if score > 0 and idx < len(self.feature_names):
                    word_scores.append((self.feature_names[idx], float(score)))
            
            # 按分數排序並返回前 k 個
            word_scores.sort(key=lambda x: x[1], reverse=True)
            return word_scores[:top_k]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []

# 全局實例
_vectorizer_instance: Optional[TFIDFVectorizer] = None

def get_vectorizer() -> TFIDFVectorizer:
    """
    獲取全局 TF-IDF 向量化器實例
    
    Returns:
        TFIDFVectorizer 實例
    """
    global _vectorizer_instance
    if _vectorizer_instance is None:
        _vectorizer_instance = TFIDFVectorizer()
    return _vectorizer_instance

def reset_vectorizer() -> None:
    """重置全局向量化器實例（用於重新訓練）"""
    global _vectorizer_instance
    _vectorizer_instance = None

def train_vectorizer_if_needed():
    """
    如果向量化器尚未訓練且資料庫中有數據，則進行訓練。
    """
    from app.models.database import Bookmark, SessionLocal

    vectorizer = get_vectorizer()
    if vectorizer.vectorizer:
        logger.info("TF-IDF vectorizer is already trained.")
        return

    db = SessionLocal()
    try:
        logger.info("Checking for data to train TF-IDF vectorizer...")
        bookmarks = (
            db.query(Bookmark)
            .filter(Bookmark.content.isnot(None), Bookmark.content != "")
            .all()
        )

        if not bookmarks:
            logger.info(
                "No bookmarks with content found for training. Vectorizer remains untrained."
            )
            return

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
            logger.info(f"Found {len(texts)} documents. Training TF-IDF vectorizer...")
            vectorizer.fit(texts)
            logger.info("TF-IDF vectorizer training complete.")
        else:
            logger.info("No text data found for training.")

    except Exception as e:
        logger.error(f"An error occurred during vectorizer training: {e}")
    finally:
        db.close()
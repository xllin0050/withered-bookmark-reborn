"""
TF-IDF 向量化服務
提供文本向量化、相似度計算等核心功能
"""

import hashlib
import json
import logging
import time
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

        # 相似度計算快取
        self.similarity_cache: Dict[str, Tuple[float, float]] = {}  # key -> (similarity, timestamp)
        self.cache_max_size = 10000  # 最大快取條目數
        self.cache_ttl = 3600  # 快取存活時間（秒）

        # 中文停用詞列表
        self.stop_words = {
            "的",
            "是",
            "在",
            "了",
            "和",
            "有",
            "我",
            "你",
            "他",
            "她",
            "它",
            "們",
            "這",
            "那",
            "這個",
            "那個",
            "上",
            "下",
            "中",
            "內",
            "外",
            "前",
            "後",
            "左",
            "右",
            "大",
            "小",
            "高",
            "低",
            "長",
            "短",
            "好",
            "壞",
            "新",
            "舊",
            "多",
            "少",
            "一",
            "二",
            "三",
            "四",
            "五",
            "六",
            "七",
            "八",
            "九",
            "十",
            "會",
            "能",
            "要",
            "可以",
            "應該",
            "必須",
            "可能",
            "也許",
            "但是",
            "然而",
            "因為",
            "所以",
            "如果",
            "那麼",
            "雖然",
            "除了",
            "除非",
            "直到",
            "當",
            "the",
            "is",
            "at",
            "which",
            "on",
            "and",
            "a",
            "an",
            "as",
            "are",
            "was",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "can",
            "may",
            "might",
            "must",
            "shall",
            "to",
            "of",
            "in",
            "for",
            "with",
            "by",
            "from",
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
            word.strip()
            for word in words
            if word.strip() and len(word.strip()) > 1 and word.strip() not in self.stop_words
        ]

        return " ".join(filtered_words)

    def _generate_cache_key(self, vector1_json: str, vector2_json: str) -> str:
        """
        生成快取鍵值

        Args:
            vector1_json: 第一個向量的 JSON 字串
            vector2_json: 第二個向量的 JSON 字串

        Returns:
            快取鍵值
        """
        # 確保一致的順序（較小的哈希值在前）
        hash1 = hashlib.md5(vector1_json.encode()).hexdigest()
        hash2 = hashlib.md5(vector2_json.encode()).hexdigest()

        if hash1 < hash2:
            return f"{hash1}:{hash2}"
        else:
            return f"{hash2}:{hash1}"

    def _cleanup_cache(self) -> None:
        """清理過期的快取條目"""
        current_time = time.time()
        expired_keys = []

        for key, (similarity, timestamp) in self.similarity_cache.items():
            if current_time - timestamp > self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.similarity_cache[key]

        # 如果快取仍然太大，移除最舊的條目
        if len(self.similarity_cache) > self.cache_max_size:
            sorted_items = sorted(self.similarity_cache.items(), key=lambda x: x[1][1])
            items_to_remove = len(sorted_items) - self.cache_max_size + 100  # 額外清理100個

            for key, _ in sorted_items[:items_to_remove]:
                del self.similarity_cache[key]

        logger.debug(f"Cache cleanup completed. Current size: {len(self.similarity_cache)}")

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
            stop_words=None,  # 已經去停用詞了
        )

        # 訓練向量化器
        try:
            self.vectorizer.fit(processed_texts)
            self.feature_names = self.vectorizer.get_feature_names_out().tolist()
            logger.info(
                f"TF-IDF vectorizer trained with {len(self.feature_names)} features from {len(processed_texts)} documents"
            )

            # 清空快取（因為特徵空間改變了）
            self.clear_cache()

        except ValueError as e:
            logger.error(
                f"ValueError during vectorizer training - insufficient or invalid text data: {e}"
            )
            self.vectorizer = None
        except MemoryError as e:
            logger.error(
                f"MemoryError during vectorizer training - consider reducing max_features: {e}"
            )
            self.vectorizer = None
        except Exception as e:
            logger.error(f"Unexpected error training TF-IDF vectorizer: {e}", exc_info=True)
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

            if not sparse_vector:
                logger.warning(f"Generated empty vector for text: '{text[:50]}...'")
                return None

            vector_data = {
                "vector": sparse_vector,
                "feature_count": len(self.feature_names),
                "non_zero_count": len(sparse_vector),
            }

            return json.dumps(vector_data)

        except ValueError as e:
            logger.error(
                f"ValueError in vector transformation - likely due to untrained vectorizer: {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Unexpected error transforming text to vector: {e}", exc_info=True)
            return None

    def calculate_similarity(self, vector1_json: str, vector2_json: str) -> float:
        """
        計算兩個 JSON 格式向量之間的餘弦相似度（支援快取）

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

        # 檢查快取
        cache_key = self._generate_cache_key(vector1_json, vector2_json)
        current_time = time.time()

        if cache_key in self.similarity_cache:
            similarity, timestamp = self.similarity_cache[cache_key]
            if current_time - timestamp <= self.cache_ttl:
                logger.debug("Cache hit for similarity calculation")
                return similarity

        try:
            # 解析 JSON 向量
            try:
                vector1 = json.loads(vector1_json)
                vector2 = json.loads(vector2_json)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in vector data: {e}")
                return 0.0

            # 提取稀疏向量
            sparse1 = vector1.get("vector", {})
            sparse2 = vector2.get("vector", {})

            if not sparse1 or not sparse2:
                logger.debug("One or both vectors are empty")
                return 0.0

            # 確保特徵數量一致
            feature_count = max(
                vector1.get("feature_count", 0),
                vector2.get("feature_count", 0),
                len(self.feature_names),
            )
            if feature_count == 0:
                logger.warning("Feature count is 0 - vectorizer may not be properly trained")
                return 0.0

            # 轉換為密集向量
            try:
                dense1 = np.zeros(feature_count)
                dense2 = np.zeros(feature_count)

                for idx_str, value in sparse1.items():
                    try:
                        idx = int(idx_str)
                        if 0 <= idx < feature_count:
                            dense1[idx] = float(value)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid index or value in vector1: {idx_str}={value}")

                for idx_str, value in sparse2.items():
                    try:
                        idx = int(idx_str)
                        if 0 <= idx < feature_count:
                            dense2[idx] = float(value)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid index or value in vector2: {idx_str}={value}")

            except MemoryError as e:
                logger.error(
                    f"MemoryError creating dense vectors (feature_count={feature_count}): {e}"
                )
                return 0.0

            # 檢查向量是否有效（非全零）
            if np.allclose(dense1, 0) or np.allclose(dense2, 0):
                logger.debug("One or both dense vectors are all zeros")
                return 0.0

            # 計算餘弦相似度
            try:
                similarity = cosine_similarity([dense1], [dense2])[0][0]

                # 檢查相似度是否為有效數值
                if np.isnan(similarity) or np.isinf(similarity):
                    logger.warning("Similarity calculation resulted in NaN or Inf")
                    return 0.0

                similarity_float = float(similarity)

                # 確保相似度在合理範圍內
                similarity_float = max(0.0, min(1.0, similarity_float))

            except Exception as e:
                logger.error(f"Error in cosine similarity calculation: {e}")
                return 0.0

            # 儲存到快取
            self.similarity_cache[cache_key] = (similarity_float, current_time)

            # 定期清理快取（每100次計算清理一次）
            if len(self.similarity_cache) % 100 == 0:
                self._cleanup_cache()

            logger.debug(f"Calculated and cached similarity: {similarity_float:.4f}")
            return similarity_float

        except Exception as e:
            logger.error(f"Unexpected error calculating similarity: {e}", exc_info=True)
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

    def calculate_batch_similarity(
        self, query_vector_json: str, bookmark_vectors: List[Tuple[str, str]]
    ) -> List[Tuple[str, float]]:
        """
        批量計算查詢向量與多個書籤向量的相似度

        Args:
            query_vector_json: 查詢向量的 JSON 字串
            bookmark_vectors: (bookmark_id, vector_json) 的列表

        Returns:
            (bookmark_id, similarity_score) 的列表
        """
        if not query_vector_json or not bookmark_vectors:
            return []

        if not self.vectorizer:
            logger.warning("Vectorizer not trained for batch similarity calculation")
            return [(bid, 0.0) for bid, _ in bookmark_vectors]

        try:
            # 解析查詢向量
            query_vector = json.loads(query_vector_json)
            query_sparse = query_vector.get("vector", {})

            if not query_sparse:
                return [(bid, 0.0) for bid, _ in bookmark_vectors]

            # 確定特徵空間大小
            feature_count = max(query_vector.get("feature_count", 0), len(self.feature_names))

            if feature_count == 0:
                return [(bid, 0.0) for bid, _ in bookmark_vectors]

            # 轉換查詢向量為密集格式
            query_dense = np.zeros(feature_count)
            for idx_str, value in query_sparse.items():
                try:
                    idx = int(idx_str)
                    if 0 <= idx < feature_count:
                        query_dense[idx] = float(value)
                except (ValueError, TypeError):
                    continue

            # 檢查查詢向量是否有效
            if np.allclose(query_dense, 0):
                return [(bid, 0.0) for bid, _ in bookmark_vectors]

            results = []
            valid_vectors = []
            valid_ids = []
            current_time = time.time()

            # 批量處理書籤向量
            for bookmark_id, vector_json in bookmark_vectors:
                # 首先檢查快取
                cache_key = self._generate_cache_key(query_vector_json, vector_json)
                if cache_key in self.similarity_cache:
                    similarity, timestamp = self.similarity_cache[cache_key]
                    if current_time - timestamp <= self.cache_ttl:
                        results.append((bookmark_id, similarity))
                        continue

                # 解析書籤向量
                try:
                    bookmark_vector = json.loads(vector_json)
                    bookmark_sparse = bookmark_vector.get("vector", {})

                    if not bookmark_sparse:
                        results.append((bookmark_id, 0.0))
                        continue

                    # 轉換為密集向量
                    bookmark_dense = np.zeros(feature_count)
                    for idx_str, value in bookmark_sparse.items():
                        try:
                            idx = int(idx_str)
                            if 0 <= idx < feature_count:
                                bookmark_dense[idx] = float(value)
                        except (ValueError, TypeError):
                            continue

                    if np.allclose(bookmark_dense, 0):
                        results.append((bookmark_id, 0.0))
                        continue

                    valid_vectors.append(bookmark_dense)
                    valid_ids.append((bookmark_id, cache_key))

                except (json.JSONDecodeError, Exception) as e:
                    logger.warning(f"Error parsing bookmark vector for {bookmark_id}: {e}")
                    results.append((bookmark_id, 0.0))

            # 批量計算餘弦相似度
            if valid_vectors:
                try:
                    # 使用 sklearn 的向量化相似度計算
                    similarities = cosine_similarity([query_dense], valid_vectors)[0]

                    for i, (bookmark_id, cache_key) in enumerate(valid_ids):
                        similarity = float(similarities[i])

                        # 確保相似度在合理範圍內
                        if np.isnan(similarity) or np.isinf(similarity):
                            similarity = 0.0
                        else:
                            similarity = max(0.0, min(1.0, similarity))

                        results.append((bookmark_id, similarity))

                        # 儲存到快取
                        self.similarity_cache[cache_key] = (similarity, current_time)

                    logger.debug(f"Batch calculated {len(valid_vectors)} similarities")

                except Exception as e:
                    logger.error(f"Error in batch cosine similarity calculation: {e}")
                    # 回退到個別計算
                    for bookmark_id, _ in valid_ids:
                        results.append((bookmark_id, 0.0))

            # 定期清理快取
            if len(self.similarity_cache) % 100 == 0:
                self._cleanup_cache()

            return results

        except Exception as e:
            logger.error(f"Error in batch similarity calculation: {e}", exc_info=True)
            return [(bid, 0.0) for bid, _ in bookmark_vectors]

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        獲取快取統計資訊

        Returns:
            快取統計資訊字典
        """
        current_time = time.time()
        expired_count = 0

        for similarity, timestamp in self.similarity_cache.values():
            if current_time - timestamp > self.cache_ttl:
                expired_count += 1

        return {
            "cache_size": len(self.similarity_cache),
            "max_cache_size": self.cache_max_size,
            "expired_entries": expired_count,
            "cache_ttl_seconds": self.cache_ttl,
            "cache_utilization": len(self.similarity_cache) / self.cache_max_size,
        }

    def clear_cache(self) -> None:
        """清空相似度快取"""
        self.similarity_cache.clear()
        logger.info("Similarity cache cleared")


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
            db.query(Bookmark).filter(Bookmark.content.isnot(None), Bookmark.content != "").all()
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

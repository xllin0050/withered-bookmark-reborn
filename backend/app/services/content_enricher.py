import asyncio
import json
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
import jieba
import jieba.analyse
from bs4 import BeautifulSoup

from .tfidf_vectorizer import get_vectorizer


class ContentEnricher:
    def __init__(self):
        """初始化內容增強器"""
        # 設定請求超時時間
        self.timeout = aiohttp.ClientTimeout(total=30)

        # 設定請求標頭，模擬瀏覽器
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        # 初始化 jieba 分詞器
        jieba.initialize()

        # 停用詞列表（可以擴充）
        self.stop_words = set(
            [
                "的",
                "了",
                "在",
                "是",
                "我",
                "有",
                "和",
                "就",
                "不",
                "人",
                "都",
                "一",
                "一個",
                "上",
                "也",
                "很",
                "到",
                "說",
                "要",
                "去",
                "你",
                "會",
                "著",
                "沒有",
                "看",
                "好",
                "自己",
                "這",
                "那",
                "些",
                "個",
                "中",
                "們",
            ]
        )

    async def extract_content(self, url: str) -> Optional[Dict[str, any]]:
        """
        從網頁抓取並處理內容

        Args:
            url: 要抓取的網頁 URL

        Returns:
            包含處理後內容的字典，或 None（如果抓取失敗）
        """
        try:
            # 抓取網頁內容
            html_content = await self._fetch_page(url)
            if not html_content:
                return None

            # 解析 HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # 提取基本資訊
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            image_url = self._extract_image_url(soup, url)
            content = self._extract_main_content(soup)

            # 清理內容文字
            clean_content = self._clean_text(content)

            # 提取關鍵字
            keywords = self.extract_keywords(clean_content)

            # 生成摘要
            summary = self.generate_summary(clean_content)

            # 生成 TF-IDF 向量
            tfidf_vector = self.generate_tfidf_vector(title, description, clean_content, keywords)

            return {
                "title": title,
                "description": description or summary,  # 如果沒有 description，使用摘要
                "image_url": image_url,
                "content": clean_content,
                "keywords": keywords,  # 直接返回列表
                "summary": summary,
                "tfidf_vector": tfidf_vector,
            }

        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

    async def _fetch_page(self, url: str) -> Optional[str]:
        """
        抓取網頁內容

        Args:
            url: 要抓取的網頁 URL

        Returns:
            網頁 HTML 內容，或 None（如果抓取失敗）
        """
        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout, cookie_jar=aiohttp.CookieJar(unsafe=True)
            ) as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        # 自動偵測編碼
                        text = await response.text()
                        return text
                    else:
                        print(f"Failed to fetch {url}: HTTP {response.status}")
                        return None
        except asyncio.TimeoutError:
            print(f"Timeout fetching {url}")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取網頁標題"""
        # 優先使用 og:title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # 其次使用 title 標籤
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.text.strip()

        # 最後使用 h1 標籤
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.text.strip()

        return "無標題"

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """提取網頁描述"""
        # 優先使用 og:description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()

        # 其次使用 meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()

        return None

    def _extract_image_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """提取網頁的代表性圖片 URL"""
        # 1. 優先使用 og:image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return urljoin(base_url, og_image["content"])

        # 2. 其次使用 twitter:image
        twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_image and twitter_image.get("content"):
            return urljoin(base_url, twitter_image["content"])

        # 3. 接著使用 <link rel="image_src">
        image_src_link = soup.find("link", rel="image_src")
        if image_src_link and image_src_link.get("href"):
            return urljoin(base_url, image_src_link["href"])

        # 4. 最後嘗試尋找 favicon
        apple_touch_icon = soup.find("link", rel="apple-touch-icon")
        if apple_touch_icon and apple_touch_icon.get("href"):
            return urljoin(base_url, apple_touch_icon["href"])

        favicon_link = soup.find("link", rel="icon")
        if favicon_link and favicon_link.get("href"):
            return urljoin(base_url, favicon_link["href"])

        shortcut_icon = soup.find("link", rel="shortcut icon")
        if shortcut_icon and shortcut_icon.get("href"):
            return urljoin(base_url, shortcut_icon["href"])

        return None

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        提取網頁主要內容

        使用啟發式方法提取可能是正文的內容
        """
        # 移除不需要的標籤
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        # 優先尋找文章標籤
        article = soup.find("article")
        if article:
            return article.get_text(strip=True, separator=" ")

        # 尋找主要內容區域
        main_content = soup.find("main") or soup.find(
            "div", class_=re.compile("content|article|post|entry")
        )
        if main_content:
            return main_content.get_text(strip=True, separator=" ")

        # 最後使用 body 內容
        body = soup.find("body")
        if body:
            return body.get_text(strip=True, separator=" ")

        return soup.get_text(strip=True, separator=" ")

    def _clean_text(self, text: str) -> str:
        """清理文字內容"""  # 移除多餘的空白
        text = re.sub(r"\s+", " ", text)

        # 移除特殊字符（保留中文、英文、數字和基本標點）
        text = re.sub(r"[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\w\s\.\,\!\?\;\:\-\(\)]", "", text)

        # 移除多餘的標點符號
        text = re.sub(r"[\.]{2,}", ".", text)
        text = re.sub(r"[\,]{2,}", ",", text)
        text = re.sub(r"[\!]{2,}", "!", text)
        text = re.sub(r"[\?]{2,}", "?", text)

        return text.strip()

    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        提取關鍵字

        Args:
            text: 要分析的文字
            top_k: 要提取的關鍵字數量

        Returns:
            關鍵字列表
        """
        if not text:
            return []

        # 使用 jieba 的 TF-IDF 算法提取關鍵字
        keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
        # 過濾停用詞
        keywords = [k for k in keywords if k not in self.stop_words and len(k) > 1]

        return keywords

    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """
        生成摘要

        Args:
            text: 要生成摘要的文字
            max_sentences: 摘要的最大句數

        Returns:
            摘要文字
        """
        if not text:
            return ""

        # 分割句子（支援中文和英文句號）
        sentences = re.split(r"[。！？\.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

        if not sentences:
            return text[:200] + "..." if len(text) > 200 else text

        # 如果句子數量少於需要的摘要句數，返回全部
        if len(sentences) <= max_sentences:
            return "。".join(sentences) + "。"
        # 計算每個句子的重要性分數
        # 使用簡單的詞頻統計
        word_freq = {}
        for sentence in sentences:
            words = jieba.cut(sentence)
            for word in words:
                if word not in self.stop_words and len(word) > 1:
                    word_freq[word] = word_freq.get(word, 0) + 1

        # 計算句子分數
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            words = list(jieba.cut(sentence))
            word_count = len(words)

            if word_count > 0:
                for word in words:
                    if word in word_freq:
                        score += word_freq[word]
                # 正規化分數
                score = score / word_count
                # 給前面的句子稍微高一點的權重
                score = score * (1 + 0.1 * (len(sentences) - i) / len(sentences))

            sentence_scores[i] = score

        # 選擇分數最高的句子
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[
            :max_sentences
        ]
        # 按原始順序排序選中的句子
        top_sentences = sorted([idx for idx, _ in top_sentences])

        # 組合摘要
        summary_sentences = [sentences[idx] for idx in top_sentences]
        summary = "。".join(summary_sentences)

        # 確保摘要以句號結尾
        if summary and not summary.endswith(("。", "！", "？", ".", "!", "?")):
            summary += "。"

        return summary

    def generate_tfidf_vector(self, title: str, description: str, content: str, keywords: List[str]) -> Optional[str]:
        """
        生成書籤的 TF-IDF 向量
        
        Args:
            title: 書籤標題
            description: 書籤描述
            content: 書籤內容
            keywords: 關鍵字列表
            
        Returns:
            TF-IDF 向量 JSON 字符串或 None
        """
        try:
            # 組合所有文本內容
            combined_text = []
            
            # 標題權重較高，重複 3 次
            if title:
                combined_text.extend([title] * 3)
                
            # 描述權重中等，重複 2 次
            if description:
                combined_text.extend([description] * 2)
                
            # 關鍵字權重較高，重複 2 次
            if keywords:
                keywords_text = " ".join(keywords)
                combined_text.extend([keywords_text] * 2)
                
            # 內容權重正常，添加 1 次
            if content:
                combined_text.append(content)
                
            if not combined_text:
                return None
                
            # 合併所有文本
            full_text = " ".join(combined_text)
            
            # 使用向量化器生成向量
            vectorizer = get_vectorizer()
            vector_data = vectorizer.transform(full_text)
            
            return vector_data
            
        except Exception as e:
            print(f"Error generating TF-IDF vector: {str(e)}")
            return None

    def generate_tfidf_vector_for_query(self, query: str) -> Optional[str]:
        """
        為搜索查詢生成 TF-IDF 向量
        
        Args:
            query: 搜索查詢文本
            
        Returns:
            TF-IDF 向量 JSON 字符串或 None
        """
        try:
            if not query or not query.strip():
                return None
                
            vectorizer = get_vectorizer()
            vector_data = vectorizer.transform(query.strip())
            
            return vector_data
            
        except Exception as e:
            print(f"Error generating TF-IDF vector for query: {str(e)}")
            return None

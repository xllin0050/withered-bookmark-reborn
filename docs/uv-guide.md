# uv 使用指南

`uv` 是一個極快的 Python 包管理器，作為 pip 的現代替代品。

## 🚀 快速開始

### 安裝 uv
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 專案設定
```bash
# 一鍵設定整個開發環境
scripts/setup.bat    # Windows
./scripts/setup.sh   # Linux/Mac

# 或手動設定後端
cd backend
uv venv              # 建立虛擬環境
uv pip install -e . # 安裝專案和依賴
```

## 📦 常用命令

### 依賴管理
```bash
# 安裝單個包
uv pip install fastapi

# 安裝開發依賴
uv pip install -e ".[dev]"

# 更新所有依賴
uv pip install --upgrade -e .

# 顯示已安裝的包
uv pip list

# 生成需求文件 (如果需要)
uv pip freeze > requirements.txt
```

### 運行命令
```bash
# 在虛擬環境中運行命令
uv run python app/main.py
uv run uvicorn app.main:app --reload

# 運行測試
uv run pytest

# 運行代碼格式化
uv run black .
uv run isort .
```

### 虛擬環境管理
```bash
# 建立虛擬環境
uv venv

# 建立指定 Python 版本的環境
uv venv --python 3.11

# 啟動虛擬環境 (如果需要手動啟動)
# Windows
.venv\Scripts\activate
# Linux/Mac  
source .venv/bin/activate

# 刪除虛擬環境
rm -rf .venv
```

## 🔧 專案配置

我們使用 `pyproject.toml` 來配置專案：

```toml
[project]
name = "withered-bookmark-reborn-backend"
dependencies = [
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0",
    # ... 其他依賴
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "black>=23.0.0",
    # ... 開發依賴
]
```

## ⚡ uv 的優勢

1. **速度極快**: 比 pip 快 10-100 倍
2. **磁碟空間少**: 智能快取和硬連結
3. **更好的依賴解析**: 避免依賴衝突
4. **現代化**: 原生支援 pyproject.toml
5. **兼容性**: 完全兼容 pip 和 PyPI

## 🛠️ 開發工作流

```bash
# 1. 設定專案
scripts/setup.bat

# 2. 啟動開發環境
scripts/dev.bat

# 3. 添加新依賴
cd backend
uv pip install new-package
# 然後更新 pyproject.toml

# 4. 運行測試
uv run pytest

# 5. 格式化代碼
uv run black .
uv run isort .
```

## 🔄 從 pip 遷移

如果你習慣使用 pip，對應的 uv 命令：

| pip 命令 | uv 命令 |
|----------|---------|
| `pip install package` | `uv pip install package` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip install -e .` | `uv pip install -e .` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |
| `python script.py` | `uv run python script.py` |

## 📚 更多資源

- [uv 官方文檔](https://github.com/astral-sh/uv)
- [pyproject.toml 指南](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

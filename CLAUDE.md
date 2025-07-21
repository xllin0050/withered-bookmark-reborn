# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Primary Commands (via justfile)
- `just install` - Install all dependencies (backend with uv, frontend with npm)
- `just dev` - Start both backend and frontend development servers concurrently
- `just backend` - Start FastAPI server on port 8000 with auto-reload
- `just frontend` - Start Vite dev server on port 3008
- `just test-backend` - Run pytest tests
- `just clean` - Clean node_modules and Python cache files

### Frontend Commands
- `npm run build` - TypeScript compilation + Vite production build
- `npm run lint` - ESLint with auto-fix for Vue/TypeScript files

## Architecture Overview

This is a full-stack intelligent bookmark management system with the core concept of making "withered bookmarks reborn" through active content recommendation during web searches.

### Backend (FastAPI + SQLAlchemy)
- **Entry Point**: `backend/app/main.py`
- **API Prefix**: `/api/v1` 
- **Database**: SQLite with automatic table creation on startup
- **Package Management**: Uses `uv` (modern Python package manager)

#### Key Services
- **Content Enricher** (`services/content_enricher.py`): Automatically extracts web content, performs Chinese text analysis with Jieba, generates TF-IDF keywords, and creates content summaries
- **Bookmark Importer** (`services/bookmark_importer.py`): Parses HTML bookmark files
- **Background Tasks**: Automatic content enrichment when bookmarks are created

#### Database Schema
The `Bookmark` model includes both basic fields (url, title, description) and intelligent analysis fields (content, keywords as JSON, tfidf_vector, access tracking).

### Frontend (Vue 3 + TypeScript)
- **Framework**: Vue 3 Composition API with Vite
- **State**: Pinia stores for bookmarks and search
- **Styling**: TailwindCSS v4 with custom "viridian-green" color system
- **Dev Server**: Port 3008 with proxy to backend port 8000

#### Component Architecture
- **Pages**: Route-level components (`BookmarksView`, `SearchView`, `HomeView`)
- **Base Components**: `Modal`, `TheHeader` with reusable patterns
- **Feature Components**: `BookmarkList` (with virtual scrolling), `SearchBar`, modal forms
- **Composables**: `useBookmarkModal`, `useBookmarkSearch` for state logic

#### API Communication
- **Service Layer**: `services/api.ts` with centralized HTTP client
- **Error Handling**: Unified error responses and interceptors
- **File Uploads**: Multipart form data for HTML bookmark imports

### Extension (Currently Paused)
Chrome Extension Manifest V3 structure is in place but development is paused. Designed to inject bookmark recommendations into Google/Baidu search results.

## Development Patterns

### Type Safety
- Shared TypeScript types in `/shared/types/`
- Full type coverage from API responses to component props
- Path alias `@/` for frontend src directory

### State Management Flow
1. User interaction in Vue component
2. Pinia store action with API call via axios service  
3. FastAPI backend processing with SQLAlchemy
4. Background task for content enrichment (non-blocking)
5. Reactive UI updates via store state changes

### Content Intelligence
The system automatically enriches bookmarks with:
- Web content extraction using BeautifulSoup
- Chinese text segmentation with Jieba
- TF-IDF keyword extraction
- Content summarization
- Similarity scoring for search

### Testing Setup
- **Backend**: pytest with FastAPI TestClient and in-memory SQLite
- **Fixtures**: Session-scoped database with function-scoped transaction rollback
- **Test Location**: `backend/tests/`

## Development Notes

### Performance Optimizations
- Virtual scrolling for large bookmark lists (`vue-virtual-scroller`)
- Background content enrichment to avoid blocking UI
- Response caching in API interceptors

### Bilingual Support
Designed for Chinese/English content with specialized text processing for Chinese using Jieba segmentation.

### Startup Requirements
- Python 3.8+ with uv package manager
- Node.js 16+ for frontend
- Both servers run concurrently via `just dev`

### Important File Locations
- **API Routes**: `backend/app/api/`
- **Database Models**: `backend/app/models/database.py`
- **Content Processing**: `backend/app/services/content_enricher.py`
- **Vue Stores**: `frontend/src/stores/`
- **API Service**: `frontend/src/services/api.ts`
- **Component Library**: `frontend/src/components/`
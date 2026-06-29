# Image Search Engine

<p>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=fff" alt="Python">
  <img src="https://img.shields.io/badge/JavaScript-ES2024-F7DF1E?logo=javascript&logoColor=000" alt="JavaScript">
  <img src="https://img.shields.io/badge/Vue_3-4DD49B?logo=vue.js&logoColor=000" alt="Vue 3">
  <img src="https://img.shields.io/badge/Nuxt_4-00DC82?logo=nuxt&logoColor=000" alt="Nuxt 4">
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=fff" alt="FastAPI">
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=fff" alt="PyTorch">
  <img src="https://img.shields.io/badge/FAISS-655FF0?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHJlY3QgeD0iNCIgeT0iNCIgd2lkdGg9IjYiIGhlaWdodD0iNiByeD0iMSIvPjxyZWN0IHg9IjE0IiB5PSI0IiB3aWR0aD0iNiBoZWlnaHQ9IjYgICAgcnk9IjEiLz48cmVjdCB4PSI0IiB5PSIxNCIgd2lkdGg9IjYiIGhlaWdodD0iNiByeD0iMSIvPjxyZWN0IHg9IjE0IiB5PSIxNCIgd2FkdGg9IjYiIGhlaWdodD0iNiAgICAgcnk9IjEiLz48L3N2Zz4=&logoColor=fff" alt="FAISS">
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=fff" alt="SQLite">
  <img src="https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=fff" alt="CSS3">
  <img src="https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=fff" alt="HTML5">
  <img src="https://img.shields.io/badge/license-MIT-4CAF50" alt="MIT License">
</p>

基于 **Xception + FAISS** 的以图搜图引擎。后端 Python/FastAPI，前端 Vue3/Nuxt 4。

## 功能

| 功能 | 说明 |
|------|------|
| **入库** | 上传图片，Xception 提取 2048 维特征向量，存入 SQLite + FAISS |
| **搜索** | 单张/多张图片上传，FAISS 搜索 Top-K 相似图，支持结果导出 |
| **标签** | 上传时打标签，支持标签筛选与内联编辑 |
| **图库** | 分页浏览、批量选中删除、键盘导航放大预览 |
| **EXIF** | 入库时自动提取 EXIF 信息，支持侧边栏查看 |
| **HDR** | 自动检测 HDR 格式（HEIC/AVIF + EXIF 信号），图库中显示图标 |
| **HEIC/AVIF** | 浏览器上传后服务端自动转为 JPEG 存储，预览/下载时实时转换 |
| **日志** | 完整记录所有入库操作及时间 |
| **深色模式** | CSS 变量实现日间/夜间主题切换 |
| **CLI 工具** | 批量导入（文件夹名→标签）、批量搜索（Top-5 结果表格） |
| **预览接口** | `POST /api/images/preview` — 将任意格式（含 HEIC）转为 JPEG 预览 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.12+ / FastAPI |
| 特征提取 | PyTorch + timm (Xception, 2048-d) |
| 向量检索 | FAISS (IndexFlatIP, 余弦相似度) |
| 数据库 | SQLite 3 + SQLAlchemy 2.0 |
| 前端框架 | Vue 3 / Nuxt 4 |
| 图片处理 | Pillow + pillow-heif |
| 包管理 | uv (后端) / npm (前端) |
| 测试 | pytest (后端) / Vitest (前端) |

## 项目结构

```
Image_Search/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── main.py                  # 入口，路由注册，HEIF opener
│   │   ├── config.py                # 路径/常量配置
│   │   ├── database.py              # SQLAlchemy 引擎/会话/迁移
│   │   ├── models.py                # ORM 模型 (ImageRecord, FeatureVector, IngestionLog)
│   │   ├── schemas.py               # Pydantic 响应/请求模型
│   │   ├── exif_utils.py            # EXIF 提取、HDR 检测、HEIC→PIL 转换
│   │   ├── feature_extractor.py     # Xception 特征提取 (timm)
│   │   ├── faiss_manager.py         # FAISS 索引管理 (add/rebuild/search)
│   │   ├── routers/
│   │   │   ├── ingest.py            # POST /api/ingest (含 HEIC→JPEG 转换)
│   │   │   ├── search.py            # POST /api/search
│   │   │   └── images.py            # 图片 CRUD + EXIF + 预览 + 文件服务
│   │   └── __init__.py
│   ├── cli.py                       # 命令行工具 (ingest / search)
│   ├── tests/                       # pytest 测试
│   │   ├── conftest.py              # 夹具 (TestClient, DB, mock 特征)
│   │   ├── test_cli.py              # CLI 工具测试
│   │   ├── test_ingest.py           # 入库端点测试
│   │   ├── test_search.py           # 搜索端点测试
│   │   ├── test_images.py           # 图片 CRUD 测试
│   │   ├── test_models.py           # ORM 模型测试
│   │   ├── test_schemas.py          # Schema 测试
│   │   ├── test_faiss_manager.py    # FAISS 索引测试
│   │   └── test_feature_extractor.py
│   ├── uploads/                     # 存储的图片文件 (.gitkeep)
│   ├── data/                        # SQLite DB + FAISS 索引 (.gitkeep)
│   └── pyproject.toml
├── frontend/                        # Nuxt 4 前端
│   ├── app/
│   │   ├── pages/
│   │   │   ├── index.vue           # 图库 (分页/选择/删除/预览/标签筛选)
│   │   │   ├── upload.vue          # 上传 (标签/HEIC支持/结果展示)
│   │   │   ├── search.vue          # 搜索 (多查询/结果对比/导出/HEIC预览)
│   │   │   └── logs.vue            # 入库日志
│   │   ├── components/
│   │   │   ├── NavBar.vue          # 顶部导航栏
│   │   │   ├── ImageCard.vue       # 图片卡片 (水印/错误占位)
│   │   │   ├── ImagePreview.vue    # 毛玻璃放大预览 (键盘导航/HDR徽章/EXIF/标签编辑)
│   │   │   ├── ExifPanel.vue       # EXIF 侧边栏 (分组展示)
│   │   │   ├── HdrBadge.vue        # HDR 格式徽章
│   │   │   └── AppFooter.vue       # 页脚 (GitHub 链接)
│   │   ├── composables/useTheme.js # 主题切换 (light/dark)
│   │   ├── utils/image.js          # getImageSrc() 图片 URL 路由
│   │   ├── layouts/default.vue     # 默认布局 (NavBar + Footer)
│   │   ├── assets/main.css         # CSS 变量/主题/全局样式
│   │   └── __tests__/              # Vitest 前端测试
│   ├── nuxt.config.ts
│   ├── vitest.config.ts
│   └── package.json
├── openspec/                        # OpenSpec 变更记录
│   ├── changes/
│   │   ├── batch-cli-tool/         # CLI 工具变更
│   │   └── archive/                # 已归档变更
│   └── specs/                      # 规格说明
├── start.bat                        # Windows 一键启动
└── README.md
```

## 快速开始

### 后端

```bash
cd backend

# 1. 安装依赖
uv sync

# 2. 启动服务
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

首次启动会自动：
- 创建 SQLite 数据库和表
- 下载 Xception ImageNet 预训练权重
- 从数据库恢复 FAISS 索引

> **WSL 用户注意**：若遇到 hardlink 错误，设置 `UV_LINK_MODE=copy`。

### 前端

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

默认访问 `http://localhost:3000`。

> **Windows 原生环境**：若 `npm install` 报 `@oxc-parser/binding-win32-x64-msvc` 缺失，请确保在 Native Windows CMD/PowerShell 中执行，不要在 WSL 中操作前端。

### 一键启动（Windows）

项目根目录下双击 `start.bat` 即可同时启动后端（8000 端口）和前端（3000 端口）。

### HEIC/AVIF 支持

上传 HEIC/HEIF/AVIF 文件时：
- 后端自动将 HEIC 转为 JPEG 存储在磁盘上（保留 EXIF）
- 库中原有的 .heic 文件通过 `GET /api/images/{id}/file` 实时转换为 JPEG 提供
- 搜索时上传 HEIC 查询图，后端使用 `pillow-heif` 实时解码
- 前端搜索页对 HEIC 查询图调用 `POST /api/images/preview` 获取 JPEG 预览

### CLI 命令行工具

```bash
cd backend

# 批量导入：文件夹名作为标签
uv run python cli.py ingest /path/to/dataset
# 例如：dataset/cats/a.jpg → tags="cats"

# 批量搜索
uv run python cli.py search /path/to/queries
uv run python cli.py search /path/to/queries -k 10  # Top-10

# 自定义服务器地址
uv run python cli.py --url http://other-server:8000 ingest /path/to/dataset
```

## 环境变量

### 后端

| 变量 | 说明 | 默认值 |
|------|------|--------|
| — | 所有配置在 `app/config.py` 中 | — |

### 前端

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `NUXT_PUBLIC_API_BASE_URL` | 后端 API 地址 | `http://localhost:8000` |
| `NUXT_PUBLIC_GITHUB_REPO` | GitHub 仓库 (`owner/repo`) | 空 |

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 健康检查 |
| `POST` | `/api/ingest` | 上传图片入库（支持批量 + 标签 + HEIC 自动转换） |
| `POST` | `/api/search` | 以图搜图（支持 HEIC 查询图） |
| `GET` | `/api/images` | 图片列表（分页，支持 `?tag=` 筛选） |
| `GET` | `/api/images/count` | 图片总数（支持 `?tag=` 筛选） |
| `DELETE` | `/api/images` | 批量删除图片（`?image_ids=1,2,3`） |
| `DELETE` | `/api/images/{id}` | 删除单张图片 |
| `PATCH` | `/api/images/{id}` | 更新标签 |
| `GET` | `/api/images/logs` | 入库日志 |
| `GET` | `/api/images/{id}/exif` | 获取 EXIF 信息 |
| `GET` | `/api/images/{id}/file` | 获取图片文件（HEIC 实时转 JPEG） |
| `POST` | `/api/images/preview` | 上传任意图片返回 JPEG 预览（HEIC→JPEG） |

## 测试

### 后端

```bash
cd backend
uv run pytest tests/ -v
```

后端包含 50+ 测试，覆盖模型、Schema、API 端点、FAISS 索引管理、特征提取。

### 前端

```bash
cd frontend
npm run test
```

前端包含 30+ Vitest 测试，覆盖组件、Composable、工具函数、页面逻辑。

## 构建部署

### 后端

Python/FastAPI 无构建步骤，直接运行即可：

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

生产环境可增加 workers 或使用 gunicorn：

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端

**SSR 模式构建**（需 Node 服务器运行）：

```bash
cd frontend
NUXT_PUBLIC_API_BASE_URL=https://your-api-url npm run build
node .output/server/index.mjs
```

**静态导出**（无需 Node 服务器，输出到 `.output/public/`）：

```bash
cd frontend
NUXT_PUBLIC_API_BASE_URL=https://your-api-url npm run generate
# 将 .output/public/ 部署到任意静态托管服务 (Nginx, S3, Cloudflare Pages 等)
```

> 构建前务必设置 `NUXT_PUBLIC_API_BASE_URL` 环境变量指向后端 API 地址，否则前端会默认请求 `http://localhost:8000`。

---

> 特征向量维度: 2048 | FAISS 索引: IndexFlatIP (余弦相似度) | 输入尺寸: 299×299

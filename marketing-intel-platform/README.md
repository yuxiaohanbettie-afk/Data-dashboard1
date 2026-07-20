# Marketing Intelligence Platform (Local DB + AI-ready)

一个面向 **Google Ads / Meta Ads** 的桌面优先营销数据工作台：只从你上传的 **固定结构 Excel** 导入数据，持续追加到本地数据库（SQLite），并在每次导入后自动刷新指标与异常提示。

本仓库是“可直接放到 GitHub 开始实现/迭代”的工程骨架（不是 Excel 可视化工具，也不是一次性 Demo）。

## 目录结构

- `backend/`：FastAPI + SQLAlchemy（本地数据库、导入流水线、Adapter 层、Campaign Name 解析、异常检测、指标 API）
- `frontend/`：Next.js + Tailwind（Upload Center、首页 KPI + Alerts，后续扩展各分析页）
- `data/`：运行时生成（SQLite 文件等，已在 `.gitignore` 忽略）

## 快速开始（本地）

### 1) 启动后端

```bash
cd backend
python -m pip install -r requirements.txt --break-system-packages
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

后端默认把 SQLite 存到仓库根目录下的 `data/mi.db`（运行时自动创建；不会覆盖/删除历史数据）。

### 2) 启动前端

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

打开 `http://localhost:3000`。

### 3) 导入 Excel

进入 `Upload Center`，拖拽/选择 `.xlsx`。

导入完成会展示：
- `Rows Imported`
- `Rows Skipped`（重复数据自动跳过）
- `Database Total Rows`
- `Latest Upload Time`

## 数据导入原则（你要求的“永不覆盖/永不删除”）

- 每一行都会计算 `row_hash`（基于原始 Excel 字段），并在 SQLite 上做唯一约束。
- 同一个 Excel 或同一批数据重复上传：会被 `OR IGNORE` 自动跳过，不会覆盖历史记录。
- 数据看板只读数据库，不会每次从 Excel 直接读。

## Excel Adapter 层（不改你的 Excel）

目前已内置你这份样例文件对应的固定 schema：

- `backend/app/adapters/excel_cb1_7d_mkt_seller_v1.py`

它负责：
1. 校验列顺序/列名是否一致（固定结构识别）
2. 字段归一化（如 `Impression` → `impression`）
3. 统一生成可入库 records

后续你上传“同结构”文件会自动识别并复用；如果未来出现新结构，只需要新增一个 adapter 文件（无需你改 Excel）。

## Campaign Name 解析（可配置）

- 配置：`backend/config/campaign_parser.json`
- 代码：`backend/app/services/campaign_parser.py`
- 入库字段：`ad_fact_daily` 表的 `business_unit / ad_type / country / industry / promotion / language / campaign_goal / optimization_target / campaign_date_code`

当前版本采用“先拆分、再用正则/字典识别”的策略，并把所有 tokens 写入 `campaign_dims_json`，便于你后续迭代命名规则时回溯与增强。

## 已实现的 API（v0）

- `POST /api/upload/excel`：上传并导入 Excel（含去重、Campaign 解析）
- `GET /api/metrics/kpi_compare`：任意两段时间 KPI 对比（支持平台/国家/BU/AdType 等过滤）
- `GET /api/anomalies`：异常列表（导入后自动跑一轮国家级别异常）

## 下一步你要我继续做什么

你可以直接把后续 Excel 样例继续上传，我会：
1. 验证 schema 是否一致（或生成新的 Adapter）
2. 把 Campaign Name 规则固化到配置，并让解析字段更稳定
3. 补齐各分析页面（Country/Industry/AdType/Campaign/Trend/Platform）
4. 加入“根因解释”与 AI Chat（基于数据库查询 + 业务推理，而不是关键词匹配）


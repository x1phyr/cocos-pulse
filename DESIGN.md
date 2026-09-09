# Cocos Pulse · 站点设计文档

> Night Dispatch 霓虹编辑风 · 纯静态多页站  
> 品牌：COCOS / PULSE · 标语：听引擎的心跳

---

## 1. 信息架构（Sitemap）

```
/                       → index.html          首页（今日刊 + 近刊 + 专题入口）
/archive.html           → 历史刊列表（按月分组）
/about.html             → 关于本刊
/topics/                → 专题枢纽
/topics/pink.html       → PinK / Agent 赛道
/topics/spine.html      → Spine 相关
/topics/cocos4-cli.html → COCOS 4 + CLI 工具链
/topics/creator-3x.html → Creator 3.x / engine
/issues/YYYY-MM-DD.html → 日刊正文
/YYYY-MM-DD.html        → 旧路径薄跳转 → issues/...
```

导航（全站顶栏）：Logo → **今日**（最新刊）· **历史** · **专题** · **关于**  
页脚固定文案：`COCOS PULSE · NIGHT DISPATCH · WEEKDAYS 09:56 CST`

---

## 2. 页面职责

| 页面 | 角色 | 内容要点 |
|------|------|----------|
| `index.html` | 门户 | Hero + 今日刊卡片（3 头条）+ 近刊列表 + 专题四宫格 + 信源条 |
| `archive.html` | 目录 | 按月分组；行内：日期、标题线、2–3 标签、链到日刊 |
| `issues/*.html` | 日刊 | Mast + Ticker + 3 Headlines + FORUM / REPOS / RELEASES；prev/next；相关专题 chips |
| `topics/index.html` | 专题枢纽 | 四个专题卡 + 「样例聚合」说明 |
| `topics/*.html` | 专题页 | 从已有日刊诚实聚合条目；每条回链日刊（及外链） |
| `about.html` | 元信息 | 定位、信源、更新节奏、静态部署模型、论坛摘要深度 |
| `DESIGN.md` | 给开发者 | 本文档 |

**约束**：不虚构日刊；目前仅 `2026-09-08`、`2026-09-09`。专题页标注「样例聚合，后续日刊自动回填」。

---

## 3. 视觉系统（Night Dispatch）

### 字体（Google Fonts）
- **Orbitron** 600/800 — 品牌、区块标题、标签、导航
- **Noto Sans SC** 400/500/700/900 — 正文中文
- **JetBrains Mono** 400/600 — ticker、仓库名、mono 片段、页脚

### 色板
| Token | Hex | 用途 |
|-------|-----|------|
| neon | `#00ffa3` | 主强调、链接、LIVE |
| hot | `#ff2d95` | 头条 feature、强信号 |
| volt | `#7c5cff` | 区块渐变、专题 code |
| amber | `#ffc857` | ticker 加粗、月份标题、样例提示 |
| cyan | `#3de7ff` | 仓库名、次级强调 |
| fog | `#9aa4c7` | 次要文案 |
| white | `#f4f6ff` | 主文字 |
| ink/bg | `#05060a` 起 | 径向霓虹 + 深色渐变底 |

### 组件约定
- **Scanline**：`body::before` 固定扫描线叠加
- **斜切 masthead**：`clip-path` 右上切角
- **Ticker**：双份内容 + CSS marquee；`site.js` 可补克隆
- **Pills**：PINK / STORE / ENG / CLI / BUG / MOOD / OHOS 等
- **区块头**：`FORUM //`、`REPOS //`、`RELEASES //`（英文 section code 保留）

共享样式：`assets/site.css`  
可选行为：`assets/site.js`（active nav、ticker 补全）

---

## 4. 内容深度与规则

### 日刊结构（固定）
1. Mast：品牌 + deck（当日主线一句话）+ ISSUE DATE stamp + 信源元数据  
2. Ticker：当日关键词滚动  
3. 三头条：01 HEADLINE（feature）/ 02 SIGNAL / 03 第三轴  
4. FORUM：论坛帖摘要（标题链原文，1–2 句速览）  
5. REPOS：engine / cocos4 / cocos-cli / docs 窗口内动静  
6. RELEASES：版本表  
7. 相关专题 chips + prev/next  

### 深度原则
- **论坛**：摘要级，不抄全文；给原帖链接  
- **仓库**：PR/issue 号 + 一句话；保留真实 URL  
- **不编造**发布或帖子；窗口外静音如实写「无新 commit」  
- 中文面向用户文案；section code 可用英文

### 专题聚合
- 仅从已发布日刊抽条；每条注明来源刊号并回链  
- 页顶固定提示：样例聚合，后续日刊自动回填  

---

## 5. 目录布局

```
cocos-pulse/
  DESIGN.md
  assets/
    site.css
    site.js
  index.html
  archive.html
  about.html
  topics/
    index.html
    pink.html
    spine.html
    cocos4-cli.html
    creator-3x.html
  issues/
    2026-09-08.html
    2026-09-09.html
  2026-09-08.html      # meta refresh → issues/
  2026-09-09.html
```

相对路径约定（便于 GitHub Pages 子路径）：
- 根页：`assets/site.css`、`issues/...`、`topics/...`
- `issues/`、`topics/`：`../assets/site.css`、`../index.html` 等

---

## 6. 发布 / CI 模型

- **纯静态**：无构建步骤，无数据库，无服务端  
- **托管**：GitHub Pages（或任意静态宿主）；仓库根或 `/docs` / `gh-pages` 分支指向本目录  
- **节奏**：工作日约 **09:56 CST** 出刊  
- **发布流程（建议）**  
  1. 新建 `issues/YYYY-MM-DD.html`（复用模板 + 当日内容）  
  2. 更新 `index.html`「今日刊 / 近刊」  
  3. 在 `archive.html` 对应月份追加一行  
  4. 可选：脚本把日刊条目追加进相关 `topics/*.html`  
  5. 根目录保留或新增 `YYYY-MM-DD.html` 薄跳转，避免旧链失效  
  6. `git commit` → push → Pages 自动部署  
- **CI**：可选 GitHub Action 仅做 HTML 链接检查 / 部署；不强制打包工具  

---

## 7. 信源

- https://forum.cocos.org  
- https://github.com/cocos/cocos-engine  
- https://github.com/cocos/cocos4  
- https://github.com/cocos/cocos-cli  
- https://github.com/cocos/cocos-docs  

---

## 8. 给开发者的交接清单

- [ ] 本地打开 `index.html`，顶栏四处跳转正常  
- [ ] 今日刊 → `issues/2026-09-09.html`，正文与原日刊实质一致  
- [ ] `archive` / `topics` / `about` 相对链接可用  
- [ ] 根 `2026-09-08.html` / `2026-09-09.html` 跳转到 `issues/`  
- [ ] 新增日刊时同步首页、归档、专题（或脚本化）  
- [ ] 部署到 Pages 后确认子路径下 CSS/JS 仍相对可用  

— END OF DESIGN —

# 日刊模版 · Daily Issue Template

每天更新只填 **JSON**，再用脚本渲成 HTML。不要从零手写整页。

## 文件

| 文件 | 用途 |
|------|------|
| `issue.example.json` | 字段说明 + 示例（复制改名） |
| `issue.html` | Night Dispatch 日刊 HTML 壳（`{{PLACEHOLDER}}`） |
| `../scripts/render_issue.py` | JSON → `issues/YYYY-MM-DD.html` + 根目录跳转页 |

## 每日流程（工作日 09:56）

1. 抓 forum.cocos.org + `gh`（engine / cocos4 / cli / docs）
2. 新建 `data/YYYY-MM-DD.json`（照 example 填，**只写真实链接**）
3. 跑：`python3 scripts/render_issue.py data/YYYY-MM-DD.json`
4. 脚本会：
   - 写出 `issues/YYYY-MM-DD.html`
   - 写出根目录 `YYYY-MM-DD.html` 跳转页
   - 提示你更新 `index.html` 今日卡 / 近刊、`archive.html` 新行、上一刊的「下一刊」链接
5. `git commit` + `git push` → GitHub Pages
6. 聊天里再发一版中文摘要 + HTML 附件

## 必填字段速查

- `date` / `date_mmdd` / `year` / `window` / `deck`
- `prev`（可 null）/ `next`（新刊一般为 null）
- `topics[]`：`pink` | `spine` | `cocos4-cli` | `creator-3x`
- `ticker[]`：5 条左右英文/中英关键词
- `headlines`：恰好 3 条（第一条 `feature: true`）
- `forum[]`：pill + title + url + summary（重点帖可 `deep: true` 并写长一点）
- `repos[]`：四仓；无动态写「窗口内无提交」
- `releases[]`：无则一行说明正式版仍为 …
- `home_blurb` / `home_tags` / `archive_title`：给首页与历史页用

## 内容纪律

- 论坛默认摘要级；重点帖 = 楼主要点 + 官方/高赞一句
- 不编假 PR / 假帖
- 平静日：三头条可写「较平静」+ 仍值得盯的旧热点，勿灌水

## CI/CD

推送 `data/*.json` 会触发 `.github/workflows/render.yml` 自动渲染并回写站点；`.github/workflows/pages.yml` 部署 Pages。

# CI/CD

| Workflow | Trigger | Does |
|----------|---------|------|
| `render.yml` | push `data/*.json` / templates / script，或手动 | 渲日刊、同步首页/历史、commit 回 main |
| `pages.yml` | push main | 部署 GitHub Pages |

## 日常用法
1. 提交 `data/YYYY-MM-DD.json`（照 `templates/issue.example.json`）
2. Actions 自动渲染并推送静态页
3. Pages 自动更新 https://x1phyr.github.io/cocos-pulse/

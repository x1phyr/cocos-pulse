# Cocos Pulse

> 听引擎的心跳 · Night Dispatch 霓虹编辑风日刊站

纯静态多页站：论坛 + 引擎仓 + 工具链心跳速览。工作日约 **09:56 CST** 出刊。

## 本地预览

直接打开入口：

```text
file:///workspace/cocos-pulse/index.html
```

或任意静态服务器（注意相对路径，适合 GitHub Pages 项目站 `/cocos-pulse/`）：

```bash
npx serve .
# 或 python -m http.server 8080
```

## 结构

```text
index.html / archive.html / about.html
issues/YYYY-MM-DD.html   # 日刊正文
topics/                  # 专题聚合（样例种子）
assets/site.css|.js
DESIGN.md                # 中文设计文档（IA / 视觉 / 发布）
YYYY-MM-DD.html          # 旧路径 → issues/ 薄跳转
```

## 部署

推送到 [x1phyr/cocos-pulse](https://github.com/x1phyr/cocos-pulse)，开启 GitHub Pages（部署根目录即可）。链接均为相对路径，无 `/` 绝对根路径。

详见 `DESIGN.md`。

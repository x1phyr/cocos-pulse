#!/usr/bin/env python3
"""Render Cocos Pulse daily issue HTML from JSON + templates/issue.html."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "templates" / "issue.html"
ISSUES = ROOT / "issues"

TOPIC_LABEL = {
    "pink": ("PINK", "../topics/pink.html"),
    "spine": ("SPINE", "../topics/spine.html"),
    "cocos4-cli": ("COCOS4 / CLI", "../topics/cocos4-cli.html"),
    "creator-3x": ("CREATOR 3.X", "../topics/creator-3x.html"),
}


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render(data: dict) -> str:
    html = TPL.read_text(encoding="utf-8")
    date = data["date"]
    mmdd = data["date_mmdd"]
    year = data["year"]
    window = data["window"]
    window_short = window.split("·")[0].strip() if "·" in window else window

    prev = data.get("prev")
    if prev:
        prev_link = f'<a href="{prev["date"]}.html">← 上一刊 {prev["mmdd"]}</a>'
    else:
        prev_link = '<span class="disabled">← 上一刊</span>'

    nxt = data.get("next")
    if nxt:
        next_link = f'<a href="{nxt["date"]}.html">下一刊 {nxt["mmdd"]} →</a>'
    else:
        next_link = '<span class="disabled">下一刊 →</span>'

    chips = []
    for key in data.get("topics") or []:
        if key in TOPIC_LABEL:
            label, href = TOPIC_LABEL[key]
            chips.append(f'<a href="{href}">{label}</a>')
    topic_chips = "\n      ".join(chips) if chips else ""

    ticker_items = data.get("ticker") or []
    # duplicate for marquee
    spans = []
    for t in ticker_items:
        if "·" in t:
            left, right = t.split("·", 1)
            spans.append(f"<span><b>{esc(left.strip())}</b> {esc(right.strip())}</span>")
        else:
            spans.append(f"<span>{esc(t)}</span>")
    ticker_html = "\n        ".join(spans + spans)

    heads = []
    for i, h in enumerate(data.get("headlines") or [], 1):
        feature = " feature" if h.get("feature") else ""
        style = ""
        if h.get("glow") and not h.get("feature"):
            style = f' style="--glow: {h["glow"]}"'
        heads.append(
            f"""      <article class="head{feature}"{style}>
        <div class="idx"><em>{i:02d}</em> / {esc(h.get("role", "SIGNAL"))}</div>
        <h3>{esc(h["title"])}</h3>
        <p>{h["body"]}</p>
      </article>"""
        )
    headlines_html = "\n".join(heads)

    forum_rows = []
    for f in data.get("forum") or []:
        pill = esc(f.get("pill", "NOTE"))
        pill_class = esc(f.get("pill_class", "eng"))
        title = esc(f["title"])
        url = f["url"]
        summary = f["summary"]
        forum_rows.append(
            f"""        <div class="row-item">
          <span class="pill {pill_class}">{pill}</span>
          <div>
            <h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
            <p>{summary}</p>
          </div>
        </div>"""
        )
    forum_html = "\n".join(forum_rows) if forum_rows else "        <p class=\"deck\">今日论坛较平静。</p>"

    repo_blocks = []
    for r in data.get("repos") or []:
        name = esc(r["name"])
        status = r.get("status") or ""
        label = f"{name}" + (f" · {esc(status)}" if status else "")
        items = r.get("items_html") or ["窗口内无动态。"]
        lis = "\n".join(f"          <li>{it}</li>" for it in items)
        repo_blocks.append(
            f"""      <div class="repo">
        <div class="name">{label}</div>
        <ul>
{lis}
        </ul>
      </div>"""
        )
    repos_html = "\n".join(repo_blocks)

    rel_rows = []
    for rel in data.get("releases") or []:
        rel_rows.append(
            f"""          <tr>
            <td>{rel["artifact"]}</td>
            <td>{rel["status"]}</td>
            <td>{rel["link_html"]}</td>
          </tr>"""
        )
    releases_html = "\n".join(rel_rows) if rel_rows else "          <tr><td colspan=\"3\">窗口内无新版本。</td></tr>"

    repl = {
        "{{DATE}}": date,
        "{{DATE_MMDD}}": mmdd,
        "{{YEAR}}": year,
        "{{WINDOW}}": esc(window),
        "{{WINDOW_SHORT}}": esc(window_short),
        "{{DECK}}": data["deck"],
        "{{PREV_LINK}}": prev_link,
        "{{NEXT_LINK}}": next_link,
        "{{TOPIC_CHIPS}}": topic_chips,
        "{{TICKER_HTML}}": ticker_html,
        "{{HEADLINES_HTML}}": headlines_html,
        "{{FORUM_HTML}}": forum_html,
        "{{REPOS_HTML}}": repos_html,
        "{{RELEASES_HTML}}": releases_html,
    }
    out = html
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def write_redirect(date: str) -> None:
    path = ROOT / f"{date}.html"
    path.write_text(
        f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta http-equiv="refresh" content="0; url=issues/{date}.html" />
<title>Redirect · {date}</title>
<link rel="canonical" href="issues/{date}.html" />
</head>
<body>
  <p><a href="issues/{date}.html">Cocos Pulse · {date}</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: render_issue.py data/YYYY-MM-DD.json", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    data = json.loads(src.read_text(encoding="utf-8"))
    date = data["date"]
    ISSUES.mkdir(parents=True, exist_ok=True)
    out_path = ISSUES / f"{date}.html"
    out_path.write_text(render(data), encoding="utf-8")
    write_redirect(date)
    print(f"Wrote {out_path.relative_to(ROOT)}")
    print(f"Wrote {date}.html (redirect)")
    print("TODO: update index.html (今日卡 + 近刊), archive.html, prev issue next-link, topics if needed.")
    print(f"home_blurb: {data.get('home_blurb', '')}")
    print(f"archive_title: {data.get('archive_title', '')}")
    print(f"home_tags: {data.get('home_tags', [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

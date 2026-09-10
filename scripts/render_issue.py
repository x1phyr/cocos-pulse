#!/usr/bin/env python3
"""Render Cocos Pulse daily issue HTML from JSON + templates/issue.html.

Also syncs index.html / archive.html / prev-issue next link when --sync-site.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "templates" / "issue.html"
ISSUES = ROOT / "issues"
DATA = ROOT / "data"

TOPIC_LABEL = {
    "pink": ("PINK", "../topics/pink.html"),
    "spine": ("SPINE", "../topics/spine.html"),
    "cocos4-cli": ("COCOS4 / CLI", "../topics/cocos4-cli.html"),
    "creator-3x": ("CREATOR 3.X", "../topics/creator-3x.html"),
}

PILL_CLASS = {
    "PINK": "pink",
    "SPINE": "spine",
    "CLI": "cli",
    "COCOS4": "eng",
    "3.X": "bug",
    "ENGINE": "eng",
    "UI/AI": "mood",
    "OHOS": "ohos",
    "STORE": "store",
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
    topic_chips = "\n      ".join(chips)

    ticker_items = data.get("ticker") or []
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
        style = f' style="--glow: {h["glow"]}"' if h.get("glow") and not h.get("feature") else ""
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
        forum_rows.append(
            f"""        <div class="row-item">
          <span class="pill {esc(f.get("pill_class", "eng"))}">{esc(f.get("pill", "NOTE"))}</span>
          <div>
            <h3><a href="{f["url"]}" target="_blank" rel="noopener">{esc(f["title"])}</a></h3>
            <p>{f["summary"]}</p>
          </div>
        </div>"""
        )
    forum_html = "\n".join(forum_rows) if forum_rows else '        <p class="deck">今日论坛较平静。</p>'

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
    releases_html = "\n".join(rel_rows) if rel_rows else '          <tr><td colspan="3">窗口内无新版本。</td></tr>'

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
    (ROOT / f"{date}.html").write_text(
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


def replace_marked(text: str, start: str, end: str, body: str) -> str:
    pat = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end))
    if not pat.search(text):
        raise SystemExit(f"Missing markers {start} .. {end}")
    return pat.sub(start + "\n" + body + "\n    " + end, text, count=1)


def patch_prev_next(data: dict) -> None:
    prev = data.get("prev")
    if not prev:
        return
    path = ISSUES / f"{prev['date']}.html"
    if not path.exists():
        return
    t = path.read_text(encoding="utf-8")
    mmdd = data["date_mmdd"]
    date = data["date"]
    new_next = f'<a href="{date}.html">下一刊 {mmdd} →</a>'
    t2, n = re.subn(
        r'<span class="disabled">下一刊 →</span>|<a href="[^"]+\.html">下一刊 [^<]+ →</a>',
        new_next,
        t,
    )
    if n:
        path.write_text(t2, encoding="utf-8")
        print(f"Patched next-link on {path.name}")


def sync_nav_today(latest: str) -> None:
    """Point every topnav 今日 link to the latest issue."""
    for path in ROOT.rglob("*.html"):
        if path.name.endswith(".html") and "issues" in path.parts or path.parent == ROOT or path.parent.name == "topics":
            pass
        else:
            continue
    for path in list(ROOT.glob("*.html")) + list((ROOT / "topics").glob("*.html")) + list(ISSUES.glob("*.html")):
        t = path.read_text(encoding="utf-8")
        if 'data-section="today"' not in t:
            continue
        if path.parent == ISSUES:
            href = f"{latest}.html"
        elif path.parent.name == "topics":
            href = f"../issues/{latest}.html"
        else:
            href = f"issues/{latest}.html"
        t2 = re.sub(
            r'(<a href=")[^"]+(" data-section="today">今日</a>)',
            rf"\g<1>{href}\g<2>",
            t,
        )
        if t2 != t:
            path.write_text(t2, encoding="utf-8")


def sync_index(data: dict) -> None:
    path = ROOT / "index.html"
    t = path.read_text(encoding="utf-8")
    date = data["date"]
    mmdd = data["date_mmdd"]
    heads = data.get("headlines") or []
    title = " · ".join(h["title"] for h in heads[:3]) if heads else data.get("archive_title", date)
    lis = "\n".join(f"        <li>{esc(h['title'])} — {h['body'][:48]}{'…' if len(h['body'])>48 else ''}</li>" for h in heads[:3])
    today = f"""    <a class="today-card" href="issues/{date}.html">
      <div class="tc-kicker">{date} · NIGHT DISPATCH</div>
      <h2>{esc(title)}</h2>
      <ul>
{lis}
      </ul>
      <div class="tc-go">READ ISSUE →</div>
    </a>"""

    # rebuild recent from all data/*.json + known issues
    recent_rows = []
    dates = sorted({*list_issue_dates(), data["date"]}, reverse=True)
    for d in dates[:7]:
        meta = load_data_for(d) or synthesize_from_issue(d)
        if not meta:
            continue
        recent_rows.append(
            f"""      <a class="recent-row" href="issues/{meta['date']}.html">
        <span class="rd">{meta['date_mmdd']}</span>
        <span><span class="rt">{esc(meta.get('archive_title') or meta.get('home_blurb') or meta['date'])}</span><br /><span class="rs">{esc(meta.get('home_blurb') or '')}</span></span>
        <span class="ra">OPEN →</span>
      </a>"""
        )
    recent = "    <div class=\"recent-list\">\n" + "\n".join(recent_rows) + "\n    </div>"

    t = replace_marked(t, "<!-- PULSE:TODAY_START -->", "<!-- PULSE:TODAY_END -->", today)
    t = replace_marked(t, "<!-- PULSE:RECENT_START -->", "<!-- PULSE:RECENT_END -->", recent)
    # stamp latest on home
    t = re.sub(r'(<div class="big">)\d{2}\.\d{2}(</div>)', rf"\g<1>{mmdd}\2", t, count=1)
    path.write_text(t, encoding="utf-8")
    print("Synced index.html")


def list_issue_dates() -> list[str]:
    dates = [p.stem for p in ISSUES.glob("????-??-??.html")]
    dates += [p.stem for p in DATA.glob("????-??-??.json")]
    return sorted(set(dates))


def load_data_for(date: str) -> dict | None:
    p = DATA / f"{date}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def synthesize_from_issue(date: str) -> dict | None:
    path = ISSUES / f"{date}.html"
    if not path.exists():
        return None
    parts = date.split("-")
    mmdd = f"{parts[1]}.{parts[2]}"
    return {
        "date": date,
        "date_mmdd": mmdd,
        "archive_title": date,
        "home_blurb": "",
        "home_tags": [],
    }


def sync_archive(data: dict) -> None:
    path = ROOT / "archive.html"
    t = path.read_text(encoding="utf-8")
    y, m, _ = data["date"].split("-")
    marker_s = f"<!-- PULSE:ARCHIVE_{y}_{m}_START -->"
    marker_e = f"<!-- PULSE:ARCHIVE_{y}_{m}_END -->"
    if marker_s not in t:
        # insert new month block before footer
        block = f"""    <div class="month-h">{y}-{m} // {month_name(m)}</div>
    {marker_s}
    {marker_e}
"""
        t = t.replace('    <footer class="site-footer">', block + "\n    <footer class=\"site-footer\">", 1)

    tags = data.get("home_tags") or []
    pills = []
    for tag in tags:
        cls = PILL_CLASS.get(tag.upper(), PILL_CLASS.get(tag, "eng"))
        pills.append(f'          <span class="pill {cls}">{esc(tag)}</span>')
    pills_html = "\n".join(pills)
    row = f"""    <a class="archive-row" href="issues/{data['date']}.html">
      <span class="ad">{data['date_mmdd']}</span>
      <span>
        <div class="at">{esc(data.get('archive_title') or data['date'])}</div>
        <div class="atags">
{pills_html}
        </div>
        <p style="margin:10px 0 0;color:var(--fog);font-size:13px;line-height:1.55">{esc(data.get('home_blurb') or '')}</p>
      </span>
      <span class="ago">OPEN →</span>
    </a>"""

    # Rebuild month rows from all issues in that month, newest first
    month_dates = [d for d in list_issue_dates() if d.startswith(f"{y}-{m}")]
    month_dates = sorted(set(month_dates + [data["date"]]), reverse=True)
    rows = []
    for d in month_dates:
        meta = load_data_for(d)
        if meta:
            rows.append(make_archive_row(meta))
        elif d == data["date"]:
            rows.append(row)
        else:
            syn = synthesize_from_issue(d)
            if syn:
                # keep existing row if present
                m_exist = re.search(
                    rf'<a class="archive-row" href="issues/{d}\.html">[\s\S]*?</a>',
                    t,
                )
                if m_exist:
                    rows.append("    " + m_exist.group(0) if not m_exist.group(0).startswith(" ") else m_exist.group(0))
                else:
                    rows.append(make_archive_row(syn))
    body = "\n".join(rows)
    t = replace_marked(t, marker_s, marker_e, body)
    # soften deck copy
    t = t.replace("目前只有两期——后续工作日追加，不补假刊。", "工作日追加日刊，不补假刊。")
    path.write_text(t, encoding="utf-8")
    print("Synced archive.html")


def make_archive_row(meta: dict) -> str:
    tags = meta.get("home_tags") or []
    pills = []
    for tag in tags:
        cls = PILL_CLASS.get(str(tag).upper(), "eng")
        pills.append(f'          <span class="pill {cls}">{esc(str(tag))}</span>')
    pills_html = "\n".join(pills) if pills else "          <span class=\"pill eng\">ISSUE</span>"
    return f"""    <a class="archive-row" href="issues/{meta['date']}.html">
      <span class="ad">{meta['date_mmdd']}</span>
      <span>
        <div class="at">{esc(meta.get('archive_title') or meta['date'])}</div>
        <div class="atags">
{pills_html}
        </div>
        <p style="margin:10px 0 0;color:var(--fog);font-size:13px;line-height:1.55">{esc(meta.get('home_blurb') or '')}</p>
      </span>
      <span class="ago">OPEN →</span>
    </a>"""


def month_name(m: str) -> str:
    names = {
        "01": "JANUARY", "02": "FEBRUARY", "03": "MARCH", "04": "APRIL",
        "05": "MAY", "06": "JUNE", "07": "JULY", "08": "AUGUST",
        "09": "SEPTEMBER", "10": "OCTOBER", "11": "NOVEMBER", "12": "DECEMBER",
    }
    return names.get(m, m)


def render_one(path: Path, sync_site: bool) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    date = data["date"]
    ISSUES.mkdir(parents=True, exist_ok=True)
    out_path = ISSUES / f"{date}.html"
    out_path.write_text(render(data), encoding="utf-8")
    write_redirect(date)
    print(f"Wrote {out_path.relative_to(ROOT)}")
    print(f"Wrote {date}.html (redirect)")
    if sync_site:
        patch_prev_next(data)
        sync_index(data)
        sync_archive(data)
        sync_nav_today(date)


def main() -> int:
    ap = argparse.ArgumentParser(description="Render Cocos Pulse issue(s)")
    ap.add_argument("json_paths", nargs="*", help="data/YYYY-MM-DD.json files")
    ap.add_argument("--all", action="store_true", help="Render every data/*.json")
    ap.add_argument("--sync-site", action="store_true", help="Update index/archive/nav/prev-next")
    args = ap.parse_args()

    paths: list[Path] = []
    if args.all:
        paths = sorted(DATA.glob("????-??-??.json"))
    else:
        paths = [Path(p) for p in args.json_paths]

    if not paths:
        print("Usage: render_issue.py data/YYYY-MM-DD.json [--sync-site]", file=sys.stderr)
        print("   or: render_issue.py --all --sync-site", file=sys.stderr)
        return 2

    # render oldest→newest so prev/next patches apply in order when syncing many
    payloads = []
    for p in paths:
        payloads.append((p, json.loads(p.read_text(encoding="utf-8"))))
    payloads.sort(key=lambda x: x[1]["date"])

    for p, data in payloads:
        # re-write via render_one using path
        render_one(p, sync_site=False)
        if args.sync_site:
            patch_prev_next(data)

    if args.sync_site and payloads:
        latest = payloads[-1][1]
        sync_index(latest)
        # rebuild archive months for all rendered
        months = {}
        for _, data in payloads:
            sync_archive(data)
        sync_nav_today(latest["date"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

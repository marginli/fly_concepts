#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生網站：每個 entries/<id>/ 的 index.html（由 meta.json＋desc.html 組成）與首頁 index.html。

entries/<id>/meta.json：
  {"title": "...", "date": "YYYY-MM-DD", "dataset": "MaleCNS v1.0", "tags": ["蕈狀體", ...],
   "summary": "首頁卡片上的一句話", "scene": "scene.json"（有 3D 才寫）,
   "figs": [{"src": "a.png", "caption": "..."}]（有平面圖才寫）}
entries/<id>/desc.html：說明文字（HTML 片段）。
"""
import hashlib
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ENT = os.path.join(HERE, "entries")
IMPORTMAP = """<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>"""


def head(title, css):
    return f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title>
<link rel="stylesheet" href="{css}"></head><body><div class="wrap">"""


def entry_page(eid, m):
    d = os.path.join(ENT, eid)
    desc = open(os.path.join(d, "desc.html"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "desc.html")) else ""
    out = [head(m["title"] + "｜果蠅概念圖庫", "../../lib/style.css"),
           '<p><a href="../../">← 回條目清單</a></p>',
           f'<header><h1>{html.escape(m["title"])}</h1><p class="sub">{html.escape(m.get("date", ""))}　資料：{html.escape(m.get("dataset", ""))}</p></header>']
    if m.get("scene"):
        out.append('<div class="stage"><div id="view"></div><div id="panel"></div></div>'
                   '<p class="hint">滑鼠左鍵拖曳＝旋轉，滾輪＝縮放，右鍵拖曳＝平移；手機用手指。右邊的勾選框可以開關各部分。</p>')
    for fg in m.get("figs", []):
        out.append(f'<figure><img src="{html.escape(fg["src"])}" alt=""><figcaption>{html.escape(fg.get("caption", ""))}</figcaption></figure>')
    out.append(f'<div class="desc">{desc}</div>')
    out.append(f'<p class="meta">條目編號 {eid}。產生這一頁的程式：<a href="make.py">make.py</a>。</p></div>')
    if m.get("scene"):
        out.append(IMPORTMAP)
        ver = hashlib.md5(open(os.path.join(HERE, "lib", "viewer.js"), "rb").read()).hexdigest()[:8]   # 改了 viewer 就換網址，避免瀏覽器用舊版
        out.append(f'<script type="module">import {{mount}} from "../../lib/viewer.js?v={ver}"; mount("{m["scene"]}?v={ver}");</script>')
    out.append("</body></html>")
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


def main():
    items = []
    for eid in sorted(os.listdir(ENT)):
        mp = os.path.join(ENT, eid, "meta.json")
        if not os.path.exists(mp):
            continue
        m = json.load(open(mp, encoding="utf-8"))
        entry_page(eid, m)
        items.append((eid, m))
    items.sort(key=lambda x: (x[1].get("date", ""), x[0]), reverse=True)
    cards = []
    for eid, m in items:
        tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in m.get("tags", []) + [m.get("dataset", "")] if t)
        key = html.escape(" ".join([m["title"], m.get("summary", ""), " ".join(m.get("tags", [])), m.get("dataset", "")]).lower())
        cards.append(f'<a class="card" href="entries/{eid}/" data-k="{key}"><h2>{html.escape(m["title"])}</h2>'
                     f'<p>{html.escape(m.get("summary", ""))}</p><div class="tags"><span class="tag">{m.get("date", "")}</span>{tags}</div></a>')
    page = [head("果蠅概念圖庫", "lib/style.css"),
            '<header><h1>果蠅概念圖庫</h1><p class="sub">工作中想看的果蠅腦結構或概念，每個條目一頁，用本機的連接體資料畫成圖或可旋轉的 3D。'
            f'目前 {len(items)} 個條目，新的在前面。</p></header>',
            '<input class="search" id="q" placeholder="搜尋條目（標題、標籤、資料來源）">',
            '<div class="cards" id="cards">' + "\n".join(cards) + "</div>" if cards else '<p class="sub">還沒有條目。</p>',
            "</div><script>const q=document.getElementById('q');q&&q.addEventListener('input',()=>{const s=q.value.trim().toLowerCase();"
            "document.querySelectorAll('.card').forEach(c=>c.style.display=!s||c.dataset.k.includes(s)?'':'none')});</script></body></html>"]
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(page))
    print(f"首頁 {len(items)} 個條目")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生網站：每個 entries/<id>/ 的 index.html（由 meta.json＋desc.html 組成）與首頁 index.html。

entries/<id>/meta.json：
  {"title": "...", "date": "YYYY-MM-DD", "dataset": "MaleCNS v1.0", "tags": ["蕈狀體", ...],
   "summary": "首頁卡片上的一句話", "scene": "scene.json"（有 3D 才寫）,
   "figs": [{"src": "a.png", "caption": "..."}]（有平面圖才寫）,
   "embed": {"src": "demo.html", "height": 1900}（互動 DEMO 頁，用 iframe 嵌入；選用）,
   "desc_wide": true（說明欄和上方同寬，不限 760px；選用）,
   "desc_collapse": true（說明欄除第一節外，每節做成可收合；選用）}
entries/<id>/desc.html：說明文字（HTML 片段）。
"""
import hashlib
import html
import json
import os
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ENT = os.path.join(HERE, "entries")
REPO = "https://github.com/marginli/fly_concepts"
IMPORTMAP = """<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>"""


def _collapse(desc):
    """說明欄：第一個 <h2> 那節照常顯示，之後每一節包成可收合的 <details>（標題當 summary），預設收合。"""
    import re
    parts = re.split(r'(?=<h2>)', desc)
    out, first = [], True
    for part in parts:
        mm = re.match(r'<h2>(.*?)</h2>(.*)', part, re.S)
        if not mm or first:
            out.append(part); first = first and not mm; continue
        out.append(f'<details class="sec"><summary>{mm.group(1)}</summary>{mm.group(2)}</details>')
    return "".join(out)


def _ver(path):
    """檔案內容的短雜湊，加在 iframe 網址後面，改了 demo 瀏覽器就會抓新版。"""
    import hashlib
    try: return hashlib.md5(open(path, "rb").read()).hexdigest()[:8]
    except OSError: return "0"


def head(title, css, full=False):
    return f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title>
<link rel="stylesheet" href="{css}?v={_ver(os.path.join(HERE, "lib", "style.css"))}"></head><body><div class="wrap{' full' if full else ''}">"""


def entry_page(eid, m):
    d = os.path.join(ENT, eid)
    desc = open(os.path.join(d, "desc.html"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "desc.html")) else ""
    out = [head(m["title"] + "｜果蠅概念圖庫", "../../lib/style.css", m.get("full_width")),
           '<p><a href="../../">← 回條目清單</a></p>',
           f'<header><h1>{html.escape(m["title"])}</h1><p class="sub">{html.escape(m.get("date", ""))}　資料：{html.escape(m.get("dataset", ""))}</p></header>']
    if m.get("scene"):
        out.append('<div class="stage"><div id="view"></div><div id="panel"></div></div>'
                   '<p class="hint">滑鼠左鍵拖曳＝旋轉，滾輪＝縮放，右鍵拖曳＝平移；手機用手指。右邊的勾選框可以開關各部分。</p>')
    if m.get("embed"):
        em = m["embed"]
        out.append(f'<p class="hint"><a href="{html.escape(em["src"])}" target="_blank">在新分頁全螢幕開啟 DEMO</a></p>'
                   f'<iframe src="{html.escape(em["src"])}?v={_ver(os.path.join(d, em["src"]))}" style="width:100%;height:{int(em.get("height", 1600))}px;border:0" loading="lazy"></iframe>'
                   + '<script>addEventListener("message",e=>{if(e.data&&e.data.demoH)for(const f of document.querySelectorAll("iframe"))if(f.contentWindow===e.source)f.style.height=(e.data.demoH+4)+"px"})</script>')
    for fg in m.get("figs", []):
        out.append(f'<figure><img src="{html.escape(fg["src"])}" alt=""><figcaption>{html.escape(fg.get("caption", ""))}</figcaption></figure>')
    if m.get("desc_collapse"):
        desc = _collapse(desc)
    out.append(f'<div class="desc{" wide" if m.get("desc_wide") else ""}">{desc}</div>')
    out.append(f'<p class="meta">條目編號 {eid}。產生這一頁的程式：<a href="make.py">make.py</a>。</p>')
    # 刪除按鈕：開一個預填好的 GitHub issue，站主送出後由 .github/workflows/delete-entry.yml 刪除
    del_url = (f"{REPO}/issues/new?title={quote('刪除條目 ' + eid)}"
               f"&body={quote('送出後會自動刪除這個條目並更新網站（約一兩分鐘）。不想刪就直接關掉這一頁。只有站主帳號送出才有效。')}")
    out.append(f'<p class="meta"><a class="del" href="{del_url}" target="_blank" rel="noopener">刪除這個條目</a>'
               '　會開一個 GitHub 頁面，按綠色的送出鈕（Create）就會刪除，約一兩分鐘後網站更新。</p></div>')
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

# -*- coding: utf-8 -*-
# 本條目 demo.html 的產生程式。
# 原始檔在 otf_port 移植包（實驗室工作站上）：fly_multiwork/onthefly/anim/
#   1. run_sq.py（ARENA=corner SHOCK_MODE=rand TURN=S SINGLE=1，野生型 20＋關掉學習 20）→ out/sq1_main_S_corner8c5_rand.npz/.json
#   2. export_anim.py sq1_main_S_corner8c5_rand 18 23 anim_data.json
#      取兩組各自最接近組平均的那一隻（第 19、24 隻），輸出每 0.05 秒的位置、電擊、S、權重等
#   3. 本程式：把 anim_data.json 包進 flyanim.html 成單檔（不必另外載入資料），
#      再加上「告訴條目頁自己多高」的 script，iframe 會自動調整高度。
# 同一份網頁也放在 https://marginli.github.io/fly-otf-animation/
# 用法：python3 make.py <anim 資料夾>   （預設為上述移植包在本機的位置）
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANIM = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/work/from_desktopTC/otf_port_20261119/extracted/otf_port/fly_multiwork/onthefly/anim")

src = open(os.path.join(ANIM, "flyanim.html"), encoding="utf-8").read()
data = open(os.path.join(ANIM, "anim_data.json"), encoding="utf-8").read().strip()

head = ('<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n')
src = src.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
# flyanim.html 是沒有 <head>/<body> 的片段：前面是 <title>/<style>，後面是內容與 script
i = src.index("</style>") + len("</style>")
j = src.index("<script>")
body_html, script = src[i:j], src[j:]
script = script.replace('fetch("anim_data.json").then(r => r.json())',
                        'Promise.resolve(JSON.parse(document.getElementById("anim-data").textContent))')
assert "anim-data" in script, "flyanim.html 的資料載入寫法變了，要更新本程式"
height = """<script>
// 在條目頁的 iframe 裡時，告訴外層自己的高度，iframe 會自動調整
function sendH(){ if (parent !== window) parent.postMessage({demoH: document.documentElement.scrollHeight}, "*"); }
addEventListener("load", sendH); addEventListener("resize", sendH); setTimeout(sendH, 500);
</script>
"""
out = (head + src[:i] + "\n<style>*{box-sizing:border-box}</style>\n</head>\n<body>\n" + body_html +
       f'<script type="application/json" id="anim-data">{data}</script>\n' + script + "\n" + height +
       "</body>\n</html>\n")
open(os.path.join(HERE, "demo.html"), "w", encoding="utf-8").write(out)
print("demo.html", len(out.encode()), "bytes")

# -*- coding: utf-8 -*-
"""產生 data.js：0.50 倍 MaleCNS 全腦模擬（多行為計畫第 8.26 節，hd_test.py 第二次執行）的 EPG 各橋格逐時間放電。
來源：~/work/from_desktopTC/multibehavior_20261119/out/hd_test.json（每批 10 隻平均，0.1 秒一段）。
只取前 23 段（2.3 秒）：B 條件是 背景 0.5 秒 → 推 0.3 秒 → 放開 1.5 秒；A（只有背景）取同樣長度。"""
import json, os
SRC = os.path.expanduser("~/work/from_desktopTC/multibehavior_20261119/out/hd_test.json")
R = json.load(open(SRC, encoding="utf-8"))
key = {"A 只有背景": "bg", "B 推 L2 每秒 100": "L2_100", "B 推 L2 每秒 200": "L2_200", "B 推 L6 每秒 100": "L6_100", "B 推 L6 每秒 200": "L6_200"}
out = {}
for r in R:
    k = key[r["label"]]; g = r["EPG 各格逐時間"]
    out[k] = {"L": [[round(v, 1) for v in g[f"L{n}"][:23]] for n in range(1, 9)],
              "R": [[round(v, 1) for v in g[f"R{n}"][:23]] for n in range(1, 9)],
              "cL": [None if v != v else round(v, 2) for v in r["集中度"]["L"][:23]],
              "cR": [None if v != v else round(v, 2) for v in r["集中度"]["R"][:23]]}
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.js"), "w", encoding="utf-8").write(
    "window.HD = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("ok", {k: max(max(max(x) for x in v["L"]), max(max(x) for x in v["R"])) for k, v in out.items()})

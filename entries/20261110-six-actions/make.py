#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""條目：六件動作同時給的平台（2026-11-10；MaleCNS v1.0 全腦 LIF 模擬）。
正式資料：~/claude_yilan/fly_multiwork/demo/d2_grid6.py 的 out/grid6.npz（追閃退吃梳唱各「關、弱、中、強」4 檔，4,096 種組合，各 4 次平均）。
--prelim：網格還沒跑完時，用第十一節 v2 的 256 組合（只有「關」與校準強度）暫代，只供開發測試。
用法：python3 make.py [--prelim]   → data.json"""
import os, sys, json, itertools, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["追", "閃", "退", "吃", "梳", "唱"]
if "--prelim" in sys.argv:
    g = np.load(os.path.expanduser("~/claude_yilan/fly_multiwork/stage3/out/grid8_mean_v2.npz"), allow_pickle=True)
    rate = g["rate"].astype(np.float32); cond8 = g["cond"].astype(int); n8 = list(g["names"]); typ = g["typ"].astype(str); side = g["side"].astype(str)
    T = lambda t, s=None: (typ == t) & ((side == s) if s else True)
    grp = {"DNa02_R": T("DNa02", "R"), "DNa02_L": T("DNa02", "L"), "DNp01": T("DNp01"), "MDN": T("MDN"), "MN9": T("MN9"), "aDN": T("DNg62") | T("DNge078"), "pIP10": T("pIP10")}
    col = [n8.index(n) for n in NAMES]; other = [i for i in range(8) if i not in col]
    conds = list(itertools.product(range(4), repeat=6)); mean = {k: np.full(4096, np.nan, np.float32) for k in grp}
    for k8 in range(len(cond8)):
        if cond8[k8, other].any(): continue
        c6 = tuple(2 * cond8[k8, col])              # 校準強度暫放在「中」（2）
        k = int(np.ravel_multi_index(c6, (4,) * 6))
        for nm, m in grp.items(): mean[nm][k] = rate[m, k8].mean()
    hz = [[None, 50, None], [None, 10, None], [None, 100, None], [None, 200, None], [None, 25, None], [None, 50, None]]; rep = 10; prelim = True   # 暫代：只有校準強度，放在「中」
else:
    g = np.load(os.path.expanduser("~/claude_yilan/fly_multiwork/demo/out/grid6.npz"), allow_pickle=True)
    gn = list(g["grp_names"]); mean = {k: g["mean"][gn.index(k)] for k in ["DNa02_R", "DNa02_L", "DNp01", "MDN", "MN9", "aDN", "pIP10"]}
    hz = g["hz"].tolist(); rep = int(g["rep"]); prelim = False
    assert list(g["names"]) == NAMES
    tr = g["trial"]; sem = {k: (tr[gn.index(k)].std(1, ddof=1) / np.sqrt(rep)) for k in mean}
ro = {"追": mean["DNa02_R"] - mean["DNa02_L"], "閃": mean["DNp01"], "退": mean["MDN"], "吃": mean["MN9"], "梳": mean["aDN"], "唱": mean["pIP10"]}
r1 = lambda a: [None if not np.isfinite(x) else round(float(x), 1) for x in a]
data = {"names": NAMES, "hz": hz, "rep": rep, "prelim": prelim, "ro": {k: r1(v) for k, v in ro.items()},
        "raw": {"dnR": r1(mean["DNa02_R"]), "dnL": r1(mean["DNa02_L"])}}
json.dump(data, open(os.path.join(HERE, "data.json"), "w"), ensure_ascii=False, separators=(",", ":"))
print("data.json", round(os.path.getsize(os.path.join(HERE, "data.json")) / 1e3), "KB", "（暫代資料）" if prelim else "")

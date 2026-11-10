#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""條目：嗅、追、閃同時給的場地展示（第二版，2026-11-10；MaleCNS v1.0 全腦 LIF 模擬）。
資料來源：~/claude_yilan/fly_multiwork/demo/d1_grid.py 的 out/demo2_grid.npz
  （嗅 5 級 × 追 7 種〔關、右眼 3 級、左眼 3 級〕× 閃 5 級 ＝ 175 種組合，每 50 毫秒一格，8 次平均；DNa02、DNa10 有 10 mV 背景）。
傳遞圖的連結：model.load("malecns") 的接線（突觸數、正負號）。
用法：~/claude_yilan/MB/MB_simulation/.venv/bin/python make.py   → data.json"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser("~/claude_yilan/MB/MB_simulation/sim"))
import model
g = np.load(os.path.expanduser("~/claude_yilan/fly_multiwork/demo/out/demo2_grid.npz"), allow_pickle=True)
grp = g["grp"]; names = list(g["grp_names"]); gn = g["grp_n"]; G, K, NB = grp.shape
cond = g["cond"].astype(int); typ = g["typ"].astype(str); side = g["side"].astype(str)
kidx = lambda o, v, l: (o + 1) * 35 + (v + 1) * 5 + (l + 1)
assert all(kidx(*c) == i for i, c in enumerate(cond))
gi = {n: i for i, n in enumerate(names)}
# 讀出：MBON 加總＝平均 × 顆數
mbon = grp[gi["MBON11"]] * gn[gi["MBON11"]] + grp[gi["MBON12"]] * gn[gi["MBON12"]]
RO = {"mbon": mbon, "dnR": grp[gi["DNa02_R"]], "dnL": grp[gi["DNa02_L"]], "gf": grp[gi["DNp01"]],
      "aoR": grp[gi["AOTU019_R"]], "aoL": grp[gi["AOTU019_L"]]}
# 傳遞圖（左右分開畫追的路徑）
c = model.load("malecns"); a = c.ann; assert (np.asarray(c.ids) == g["ids"]).all()
cls = a["class"].fillna("").astype(str).values; nt = a["nt"].fillna("").astype(str).values
T = lambda t, s=None: (typ == t) & ((side == s) if s else True)
MASK = {"ORN": cls == "olfactory", "PN": cls == "ALPN", "KC": cls == "Kenyon_Cell", "MBON11": T("MBON11"), "MBON12": T("MBON12"),
        "LC10a_R": T("LC10a", "R"), "LC10a_L": T("LC10a", "L"), "AOTU019_R": T("AOTU019", "R"), "AOTU019_L": T("AOTU019", "L"),
        "PS049_R": T("PS049", "R"), "PS049_L": T("PS049", "L"), "PS059_R": T("PS059", "R"), "PS059_L": T("PS059", "L"),
        "DNa02_R": T("DNa02", "R"), "DNa02_L": T("DNa02", "L"), "LC4": T("LC4"), "LPLC2": T("LPLC2"), "PVLP122": T("PVLP122"),
        "PVLP010": T("PVLP010"), "LHAD1g1": T("LHAD1g1"), "DNp70": T("DNp70"), "DNp103": T("DNp103"), "DNp01": T("DNp01")}
LAB = {"ORN": "嗅覺受器 ORN", "PN": "投射神經元 PN", "KC": "Kenyon 細胞 KC", "LC10a_R": "LC10a（右眼）", "LC10a_L": "LC10a（左眼）",
       "AOTU019_R": "AOTU019（右）", "AOTU019_L": "AOTU019（左）", "PS049_R": "PS049（右）", "PS049_L": "PS049（左）", "PS059_R": "PS059（右）",
       "PS059_L": "PS059（左）", "DNa02_R": "DNa02（右）", "DNa02_L": "DNa02（左）", "DNp01": "巨纖維 DNp01"}
# (群, 工作 0嗅 1追 2閃, x, y)
NODES = [("ORN", 0, 0.00, 0.02), ("PN", 0, 0.30, 0.02), ("KC", 0, 0.62, 0.02), ("MBON11", 0, 1.00, 0.00), ("MBON12", 0, 1.00, 0.11),
         ("LC10a_R", 1, 0.00, 0.26), ("AOTU019_R", 1, 0.30, 0.26), ("PS049_R", 1, 0.62, 0.22), ("PS059_R", 1, 0.62, 0.33), ("DNa02_R", 1, 1.00, 0.26),
         ("LC10a_L", 1, 0.00, 0.48), ("AOTU019_L", 1, 0.30, 0.48), ("PS049_L", 1, 0.62, 0.44), ("PS059_L", 1, 0.62, 0.55), ("DNa02_L", 1, 1.00, 0.48),
         ("LC4", 2, 0.00, 0.72), ("LPLC2", 2, 0.00, 0.93), ("PVLP122", 2, 0.30, 0.68), ("PVLP010", 2, 0.30, 0.84), ("LHAD1g1", 2, 0.30, 0.99),
         ("DNp70", 2, 0.62, 0.74), ("DNp103", 2, 0.62, 0.92), ("DNp01", 2, 1.00, 0.83)]
gid = np.full(len(typ), -1)
for i, (nm, *_ ) in enumerate(NODES):
    assert MASK[nm].sum() > 0, nm; gid[MASK[nm] & (gid < 0)] = i
nodes = []
for nm, task, x, y in NODES:
    m = MASK[nm]; inh = float(np.isin(nt[m], ["gaba", "glutamate"]).mean()) > 0.5
    nodes.append({"label": f"{LAB.get(nm, nm)}（{int(m.sum())}）", "n": int(m.sum()), "task": task, "x": x, "y": y, "inh": inh, "g": gi[nm]})
sg = np.asarray(c.sign)[c.pre]; gp, gq = gid[c.pre], gid[c.post]; m = (gp >= 0) & (gq >= 0) & (gp != gq)
W = {}
for p, q, w, s in zip(gp[m], gq[m], c.raw_count[m], sg[m]):
    W.setdefault((int(p), int(q)), [0, 0]); W[(int(p), int(q))][0 if s > 0 else 1] += int(w)
best = {}
for (p, q), ws in W.items():
    for w in ws:
        if w > 0: best[q] = max(best.get(q, 0), w)
edges = [{"s": p, "t": q, "w": w, "sign": s} for (p, q), (e, i_) in W.items() for w, s in ((e, 1), (i_, -1)) if w >= 50 or (w > 0 and w == best[q])]
node_rate = np.stack([grp[n["g"]] for n in nodes], 1)            # (K, nodes, NB)
node_max = np.maximum(node_rate.max((0, 2)), 1.0)
r1 = lambda x: np.round(np.asarray(x, np.float32), 1).tolist()
data = {"bin_ms": int(g["bin_ms"]), "warm_ms": int(g["warm_ms"]), "nbin": NB, "conc": g["conc"].tolist(), "tgt_hz": g["tgt_hz"].tolist(),
        "loom_hz": g["loom_hz"].tolist(), "bg_mv": float(g["bg_mv"]), "rep": int(g["rep"]),
        "ro": {k: r1(v) for k, v in RO.items()},                                  # 每個 (K, NB)
        "nodes": nodes, "edges": edges, "node_rate": r1(np.transpose(node_rate, (0, 1, 2))), "node_max": r1(node_max),
        "columns": [{"label": "輸入", "x": 0}, {"label": "第一站", "x": 0.30}, {"label": "中繼", "x": 0.62}, {"label": "讀出", "x": 1}]}
json.dump(data, open(os.path.join(HERE, "data.json"), "w"), ensure_ascii=False, separators=(",", ":"))
print("data.json", round(os.path.getsize(os.path.join(HERE, "data.json")) / 1e6, 2), "MB；連結", len(edges))

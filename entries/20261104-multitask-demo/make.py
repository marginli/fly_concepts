#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""條目：嗅、追、閃三種工作同時進行的動畫 DEMO（MaleCNS v1.0 全腦 LIF 模擬）。

資料來源：~/claude_yilan/fly_multiwork/stage2/s2_demo_grid.py 的結果 out/demo_grid_malecns.npz
  （125 種組合 × 每 50 毫秒一格 × 全部 164,587 顆神經元，8 次平均），
  神經元位置：syn_centroid.py 算的每顆神經元突觸點平均位置（MaleCNS 原生座標，8 nm → µm）。
傳遞圖的細胞群與連結：model.load("malecns") 的接線（突觸數、正負號），細胞群是手挑的（各工作從輸入到讀出最強的中繼型，
  2026-11-04 探勘：讀出神經元上游「突觸數 × 放電變化」最大的型，用第一階段 sweep 結果）。
用法：~/claude_yilan/MB/MB_simulation/.venv/bin/python make.py
輸出：data.json、pos.bin（int16 x,y,z µm × N）、c/<k>.bin（每組合一檔：uint32 M、uint32 索引[M]、uint8 放電率[M×格數]，單位 Q Hz）"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser("~/claude_yilan/MB/MB_simulation/sim"))
import model

GRID = os.path.expanduser("~/claude_yilan/fly_multiwork/stage2/out/demo_grid_malecns.npz")
Q = 2.5   # 每 50 毫秒一格、8 次平均時，放電率的最小單位是 2.5 次/秒

g = np.load(GRID)
rate = g["rate"]                      # (N, 125, nbin) float16
cond = [tuple(x) for x in g["cond"]]
N, K, NB = rate.shape
ids, typ, side = g["ids"], g["typ"].astype(str), g["side"].astype(str)
bin_ms, warm_ms = int(g["bin_ms"]), int(g["warm_ms"])
kidx = lambda o, v, l: (o + 1) * 25 + (v + 1) * 5 + (l + 1)
assert all(kidx(*c) == i for i, c in enumerate(cond))

# ---------- 位置 ----------
cz = np.load(os.path.expanduser("~/claude_yilan/fly_multiwork/stage2/out/syn_centroid_mcns.npz"))
pos_map = dict(zip(cz["body"], np.stack([cz["x"], cz["y"], cz["z"]], 1) * 0.008))
P = np.array([pos_map.get(int(b), [np.nan] * 3) for b in ids])
miss = np.isnan(P[:, 0]); print("沒有突觸位置的神經元", int(miss.sum()))
P[miss] = np.nanmedian(P, 0)
pos = np.round(P).astype(np.int16)
pos.tofile(os.path.join(HERE, "pos.bin"))
bbox = [np.percentile(P, 0.05, 0).round().tolist(), np.percentile(P, 99.95, 0).round().tolist()]

# ---------- 每組合的全腦放電 ----------
os.makedirs(os.path.join(HERE, "c"), exist_ok=True)
tot = 0
for k in range(K):
    r = np.minimum(np.round(rate[:, k, :].astype(np.float32) / Q), 255).astype(np.uint8)
    act = np.where(r.max(1) > 0)[0].astype(np.uint32)
    with open(os.path.join(HERE, "c", f"{k}.bin"), "wb") as fh:
        np.array([len(act)], np.uint32).tofile(fh); act.tofile(fh); r[act].tofile(fh)
    tot += os.path.getsize(os.path.join(HERE, "c", f"{k}.bin"))
print(f"組合檔共 {tot / 1e6:.1f} MB")

# ---------- 傳遞圖 ----------
c = model.load("malecns"); a = c.ann
cls = a["class"].fillna("").astype(str).values; nt = a["nt"].fillna("").astype(str).values
assert (np.asarray(c.ids) == ids).all()
def T(t, s=None): return (typ == t) & ((side == s) if s else True)
# (標籤, 遮罩, 工作 0嗅 1追 2閃, x 欄, y)
NODES = [
    ("嗅覺受器 ORN", cls == "olfactory", 0, 0.00, 0.03),
    ("投射神經元 PN", cls == "ALPN", 0, 0.30, 0.03),
    ("Kenyon 細胞 KC", cls == "Kenyon_Cell", 0, 0.62, 0.03),
    ("MBON11", T("MBON11"), 0, 1.00, 0.00),
    ("MBON12", T("MBON12"), 0, 1.00, 0.13),
    ("LC10a（右）", T("LC10a", "R"), 1, 0.00, 0.37),
    ("AOTU019（右）", T("AOTU019", "R"), 1, 0.30, 0.29),
    ("AOTU041", T("AOTU041"), 1, 0.30, 0.45),
    ("PS049", T("PS049"), 1, 0.62, 0.27),
    ("PS306", T("PS306"), 1, 0.62, 0.41),
    ("DNa02（右）", T("DNa02", "R"), 1, 1.00, 0.31),
    ("DNa02（左）", T("DNa02", "L"), 1, 1.00, 0.45),
    ("PS059", T("PS059"), 2, 0.62, 0.56),
    ("LC4", T("LC4"), 2, 0.00, 0.72),
    ("LPLC2", T("LPLC2"), 2, 0.00, 0.93),
    ("PVLP122", T("PVLP122"), 2, 0.30, 0.66),
    ("PVLP010", T("PVLP010"), 2, 0.30, 0.82),
    ("LHAD1g1", T("LHAD1g1"), 2, 0.30, 0.98),
    ("DNp70", T("DNp70"), 2, 0.62, 0.74),
    ("PVLP151", T("PVLP151"), 2, 0.62, 0.92),
    ("巨纖維 DNp01", T("DNp01"), 2, 1.00, 0.83),
]
gid = np.full(N, -1)
for i, nd in enumerate(NODES):
    assert nd[1].sum() > 0, nd[0]
    gid[nd[1] & (gid < 0)] = i
nodes, node_rate = [], []
for i, (lab, m, task, x, y) in enumerate(NODES):
    inh = float(np.isin(nt[m], ["gaba", "glutamate"]).mean()) > 0.5
    nodes.append({"label": f"{lab}（{int(m.sum())}）", "n": int(m.sum()), "task": task, "x": x, "y": y, "inh": inh})
nr = np.stack([rate[NODES[i][1]].astype(np.float32).mean(0) for i in range(len(NODES))], 1)   # (K, nodes, NB)
node_max = np.maximum(nr.max((0, 2)), 1.0)
sg = np.asarray(c.sign)[c.pre]; gp, gq = gid[c.pre], gid[c.post]
m = (gp >= 0) & (gq >= 0) & (gp != gq)
W = {}
for p, q, w, s in zip(gp[m], gq[m], c.raw_count[m], sg[m]):
    W.setdefault((int(p), int(q)), [0, 0]); W[(int(p), int(q))][0 if s > 0 else 1] += w
edges = []
best_in = {}
for (p, q), (e, i_) in W.items():
    for w, s in ((e, 1), (i_, -1)):
        if w > 0:
            best_in[q] = max(best_in.get(q, 0), w)
for (p, q), (e, i_) in W.items():
    for w, s in ((e, 1), (i_, -1)):
        if w >= 50 or (w > 0 and w == best_in[q]):
            edges.append({"s": p, "t": q, "w": int(w), "sign": s})
print("傳遞圖", len(nodes), "群", len(edges), "條連結")

# ---------- 讀出 ----------
def grp_mean(msk): return rate[msk].astype(np.float32).mean(0)       # (K, NB)
RO = [("MBON11＋12 放電總和（嗅的讀出）", rate[T("MBON11") | T("MBON12")].astype(np.float32).sum(0), 0, "次/秒"),
      ("轉向指令 DNa02 右減左（追）", grp_mean(T("DNa02", "R")) - grp_mean(T("DNa02", "L")), 1, "次/秒"),
      ("AOTU019（右）（追的第一站）", grp_mean(T("AOTU019", "R")), 1, "次/秒"),
      ("巨纖維 DNp01（閃）", grp_mean(T("DNp01")), 2, "次/秒")]
ro = np.stack([r[1] for r in RO], 1)       # (K, 4, NB)

data = {"bin_ms": bin_ms, "warm_ms": warm_ms, "nbin": NB, "q": Q, "bbox": bbox,
        "tasks": [{"name": "嗅", "what": "聞 3-octanol（果蠅討厭的氣味）", "levels": [f"濃度 {x:g}" for x in g["conc"]]},
                  {"name": "追", "what": "右眼前方的小移動目標（刺激右側 LC10a）", "levels": [f"每顆 {x:g} 次/秒" for x in g["hz"]]},
                  {"name": "閃", "what": "逼近的黑影（刺激兩側 LC4、LPLC2）", "levels": [f"每顆 {x:g} 次/秒" for x in g["hz"]]}],
        "columns": [{"label": "輸入", "x": 0}, {"label": "第一站", "x": 0.30}, {"label": "中繼", "x": 0.62}, {"label": "讀出", "x": 1}],
        "nodes": nodes, "edges": edges, "node_rate": np.round(nr, 1).tolist(), "node_max": node_max.round(1).tolist(),
        "node_scale": (12.0 / node_max).round(4).tolist(),
        "readouts": [{"label": r[0], "task": r[2], "unit": r[3]} for r in RO], "ro": np.round(ro, 1).tolist()}
json.dump(data, open(os.path.join(HERE, "data.json"), "w"), ensure_ascii=False, separators=(",", ":"))
print("data.json", round(os.path.getsize(os.path.join(HERE, "data.json")) / 1e6, 2), "MB")

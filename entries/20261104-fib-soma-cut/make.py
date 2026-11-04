#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""條目：纖維版找切點時，胞體旁的短線讓切點落在胞體上（A1_fib 1-3c 的問題，MaleCNS v1.0）。

全部用 A1 管線框（原點 −480,−410,−175，1 µm）：分區＝A1_maleCNS_103/mcns/d03_mcns（正式 80 區＋腹神經索 23，
也就是 A1_fib 計算用的那一份）；骨架＝swc_pipe_103（同框）。切點的兩種找法照 CMU_research/skeleton/fib_lib.py：
  突觸版（A1_syn 的 SYN-W12）：第一個「側枝在別區有突觸」的分枝點；沒有就扣到進入點。
  纖維版（A1_fib 2026-11-04 改）：第一個「側枝的骨架伸進別區」的分枝點（別區＝主腦區以外的分區，分區外不算）。
reach 與份額都用和 fib_lib 相同的算法。用法：python3 make.py
"""
import os, sys, json
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from flylib import mesh_item, lines_item, points_item, write_scene, BD_BUILD
sys.path.insert(0, BD_BUILD)
from export_meshes import mask_mesh
SK = "/home/wanjuli/claude_linux/CMU_research/skeleton"
sys.path.insert(0, SK); sys.path.insert(0, "/home/wanjuli/claude_linux/CMU_research/A1_syn")
from fib_lib import Skel, label_at                       # noqa: E402
from reach_syn import read_swc, region_surface           # noqa: E402
from atlases import load_names                           # noqa: E402
from sklearn.decomposition import PCA                    # noqa: E402

import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.collections import LineCollection
FP = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"; font_manager.fontManager.addfont(FP)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=FP).get_name()

ORIG = np.array([-480.0, -410.0, -175.0])
LAB = np.load("/home/wanjuli/claude_linux/CMU_research/A1_maleCNS_103/mcns/d03_mcns/work/labels_fc_1um.npy", mmap_mode="r")
NAMES = ["分區外"] + load_names("80")
SWC = "/mnt/sda1/work1/male_cns/swc_pipe_103"
SYNP = "/mnt/sda1/work1/a1_syn/syn_points"
OFF = np.load(f"{SYNP}/offsets.npy"); SXYZ = np.load(f"{SYNP}/xyz.npy", mmap_mode="r"); SLAB = np.load(f"{SYNP}/lab80.npy", mmap_mode="r")
FIB = pd.read_csv(f"{SK}/data/fib_80.csv").set_index("name")
REACH = pd.read_csv(f"{SK}/data/reach_80.csv").set_index("name")
ANN = pd.read_feather("/mnt/sda1/work1/male_cns/raw/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather").set_index("bodyId")

# 兩個例子：(bodyId, 主腦區, 胞體所在情形的說明)
EX = [(36778, "LOP_L", "胞體落在別區（ME_L）裡"),
      (906015, "LegNp_T2_R", "胞體在分區外，旁邊的短線伸進隔壁區（LegNp_T3_R）")]

C_DROP, C_KEEP, C_STUB, C_SOMA = "#b8b8b8", "#1f5fa8", "#d62728", "#111111"


def subtree(sk, c):
    st, out = [c], []
    while st:
        u = st.pop(); out.append(u); st.extend(sk.children[u])
    return out


def analyse(bid, main):
    xyz, par = read_swc(f"{SWC}/{bid}_swc.swc")
    sk = Skel(xyz, par, np.zeros((0, 3)))
    vl = label_at(xyz, LAB)
    m = NAMES.index(main)
    root = int(np.flatnonzero(par < 0)[0])
    cand = np.flatnonzero(vl == m); e = int(cand[np.argmin(sk.dist[cand])])
    path = []; u = par[e]
    while u >= 0:
        path.append(int(u)); u = par[u]
    path.reverse()
    nxt = {path[i]: (path[i + 1] if i + 1 < len(path) else e) for i in range(len(path))}

    def keep_from(flag):                                   # flag[v]：頂點 v 是否算「伸進別區」的點
        sub = flag.astype(int).copy()
        for u in reversed(sk.order):
            if par[u] >= 0:
                sub[par[u]] += sub[u]
        cut = None
        for u in path:
            if any(sub[c] > 0 for c in sk.children[u] if c != nxt[u]):
                cut = u; break
        keep = np.ones(len(xyz), bool)
        drop = path if cut is None else path[:path.index(cut)]
        ds = set(drop); keep[drop] = False
        st = [c for u in drop for c in sk.children[u] if c not in ds and c != nxt[u]]
        while st:
            u = st.pop(); keep[u] = False; st.extend(sk.children[u])
        return keep, cut

    # 突觸版：用 A1_syn 的突觸點（屬於這顆的、落在主腦區以外分區的）
    nid = int(FIB.loc[bid, "nid"])
    sxyz = np.asarray(SXYZ[OFF[nid]:OFF[nid + 1]]); sl = np.asarray(SLAB[OFF[nid]:OFF[nid + 1]])
    flag_syn = np.zeros(len(xyz), bool)
    o = (sl > 0) & (sl != m)
    if o.any():
        flag_syn[cKDTree(xyz).query(sxyz[o])[1]] = True
    keep_syn, cut_syn = keep_from(flag_syn)
    keep_fib, cut_fib = keep_from((vl > 0) & (vl != m))
    # 觸發纖維版切點的側枝
    stubs = []
    if cut_fib is not None:
        for c in sk.children[cut_fib]:
            if c == nxt[cut_fib]:
                continue
            nodes = subtree(sk, c)
            lv = vl[nodes]
            if ((lv > 0) & (lv != m)).any():
                L = sum(np.linalg.norm(xyz[u] - xyz[par[u]]) for u in nodes)
                stubs.append(dict(nodes=[cut_fib] + nodes, length=L, region=NAMES[int(np.bincount(lv[(lv > 0) & (lv != m)]).argmax())]))
    member = np.zeros(len(NAMES), bool); member[m] = True
    tree = cKDTree(region_surface(np.asarray(LAB), m))
    r_syn, r_fib = sk.reach(keep_syn, LAB, member, tree), sk.reach(keep_fib, LAB, member, tree)

    def share(keep):
        ek = keep[sk.edges[:, 0]] & keep[sk.edges[:, 1]]
        pk = ek[sk.piece_edge]; pl = label_at(sk.piece_xyz[pk], LAB); w = sk.piece_len[pk]
        inn = w[pl > 0].sum()
        return w[pl == m].sum() / inn, w.sum()
    return dict(bid=bid, main=main, xyz=xyz, par=par, sk=sk, vl=vl, root=root, e=e, trunk=float(sk.dist[e]),
                soma_region=NAMES[vl[root]], keep_syn=keep_syn, keep_fib=keep_fib, cut_syn=cut_syn, cut_fib=cut_fib,
                d_cut_syn=float(sk.dist[cut_syn]) if cut_syn is not None else float(sk.dist[e]),
                d_cut_fib=float(sk.dist[cut_fib]) if cut_fib is not None else float(sk.dist[e]),
                stubs=stubs, r_syn=r_syn, r_fib=r_fib, share_syn=share(keep_syn), share_fib=share(keep_fib),
                type=str(ANN.loc[bid, "type"]), reach_tab=float(REACH.loc[bid, "reach"]) if bid in REACH.index else np.nan)


RES = [analyse(b, m) for b, m, _ in EX]
for r in RES:
    print(r["bid"], r["type"], "主腦區", r["main"], "胞體區", r["soma_region"], "主幹", round(r["trunk"], 1),
          "突觸版切點距胞體", round(r["d_cut_syn"], 1), "reach", round(r["r_syn"], 1), "(表上", r["reach_tab"], ")",
          "纖維版切點距胞體", round(r["d_cut_fib"], 1), "reach", round(r["r_fib"], 1),
          "短線", [(s["region"], round(s["length"], 1)) for s in r["stubs"]],
          "份額 突觸版", np.round(r["share_syn"], 3), "纖維版", np.round(r["share_fib"], 3))


# ---------------- 平面圖：每個例子一張，左＝突觸版、右＝纖維版，右下角放大胞體 ----------------
def segs(r, keep):
    xyz, par = r["xyz"], r["par"]
    ch = np.flatnonzero(par >= 0)
    k = keep[ch] & keep[par[ch]]
    return xyz[ch[k]], xyz[par[ch[k]]], xyz[ch[~k]], xyz[par[ch[~k]]]


def region_outline(ax, r, proj, reg, color, ls, label, zoom=None):
    """把區 reg 在骨架附近的 1 µm 標籤，沿看的方向投影成輪廓。zoom＝(中心, 半寬) 時只取胞體附近一片薄層。"""
    rid = NAMES.index(reg)
    lo = np.floor(r["xyz"].min(0) - 25 - ORIG).astype(int); hi = np.ceil(r["xyz"].max(0) + 25 - ORIG).astype(int)
    if zoom is not None:
        c, h = zoom
        lo = np.floor(c - h - ORIG).astype(int); hi = np.ceil(c + h - ORIG).astype(int)
    lo = np.maximum(lo, 0); hi = np.minimum(hi, np.array(LAB.shape)[::-1])
    sub = np.asarray(LAB[lo[2]:hi[2], lo[1]:hi[1], lo[0]:hi[0]]) == rid       # [z, y, x]
    pts = np.argwhere(sub)[:, ::-1] + lo + ORIG                                  # x, y, z µm
    if not len(pts):
        return
    if zoom is not None:                                                          # 只留胞體所在深度 ±1 µm 的薄層
        d = proj.transform_depth(pts); pts = pts[np.abs(d - proj.transform_depth(zoom[0][None])[0]) <= 1.0]
    if not len(pts):
        return
    p2 = proj.transform(pts)
    g = 1.0
    ij = np.floor((p2 - p2.min(0)) / g).astype(int)
    img = np.zeros(ij.max(0) + 1, bool); img[ij[:, 0], ij[:, 1]] = True
    from scipy import ndimage
    img = ndimage.binary_closing(img, iterations=2)
    xs = p2.min(0)[0] + np.arange(img.shape[0]) * g; ys = p2.min(0)[1] + np.arange(img.shape[1]) * g
    ax.contourf(xs, ys, img.T.astype(float), levels=[0.5, 1.5], colors=[color], alpha=0.16)
    ax.contour(xs, ys, img.T.astype(float), levels=[0.5], colors=[color], linewidths=1.0, linestyles=ls)
    ax.plot([], [], color=color, lw=6, alpha=0.3, label=label)


class Proj:
    """用整顆骨架的 PCA 前兩軸當看的平面；第三軸是深度。"""
    def __init__(self, xyz):
        self.p = PCA(3).fit(xyz)

    def transform(self, x):
        return self.p.transform(x)[:, :2]

    def transform_depth(self, x):
        return self.p.transform(x)[:, 2]


def draw(ax, r, keep, cut, title, proj, show_stub, zoom=None):
    a, b, c, d = segs(r, keep)
    A, B, Cc, D = (proj.transform(v) if len(v) else np.zeros((0, 2)) for v in (a, b, c, d))
    ax.add_collection(LineCollection(np.stack([Cc, D], 1), colors=C_DROP, linewidths=1.6 if zoom else 1.0, label="扣掉（不算進份額與 reach）"))
    ax.add_collection(LineCollection(np.stack([A, B], 1), colors=C_KEEP, linewidths=1.6 if zoom else 0.8, label="留下（算進份額與 reach）"))
    if show_stub:
        for s in r["stubs"]:
            P = proj.transform(r["xyz"][s["nodes"]])
            ax.plot(P[:, 0], P[:, 1], color=C_STUB, lw=3.0 if zoom else 2.2, solid_capstyle="round",
                    label=f"觸發切點的短線（{s['length']:.1f} µm，伸進 {s['region']}）")
    s0 = proj.transform(r["xyz"][[r["root"]]])[0]
    ax.plot(*s0, "o", ms=9 if zoom else 7, mfc="white", mec=C_SOMA, mew=1.6, label="胞體", zorder=5)
    if True:                                               # 沒有分枝點時，切點＝進入主腦區的點
        q = proj.transform(r["xyz"][[cut if cut is not None else r["e"]]])[0]
        ax.plot(*q, "x", ms=7 if zoom else 9, color="#000", mew=1.6, label="切點", zorder=4)
    e = proj.transform(r["xyz"][[r["e"]]])[0]
    ax.plot(*e, "D", ms=5, mfc="#ffcc00", mec="#000", label="進入主腦區的點", zorder=6)
    ax.set_title(title, fontsize=10.5)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])


def figure(r, desc, fname, tag):
    proj = Proj(r["xyz"])
    fig = plt.figure(figsize=(13.5, 7.4))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.62], height_ratios=[1, 1], wspace=0.06, hspace=0.18)
    axL = fig.add_subplot(gs[:, 0]); axR = fig.add_subplot(gs[:, 1]); axZ1 = fig.add_subplot(gs[0, 2]); axZ2 = fig.add_subplot(gs[1, 2])
    other = r["stubs"][0]["region"] if r["stubs"] else None
    for ax in (axL, axR):
        region_outline(ax, r, proj, r["main"], "#1f5fa8", "-", f"主腦區 {r['main']}")
        if other:
            region_outline(ax, r, proj, other, "#d62728", "--", f"別區 {other}")
    draw(axL, r, r["keep_syn"], r["cut_syn"],
         f"突觸版（A1_syn）：切點在進入主腦區處，主幹 {r['d_cut_syn']:.0f} µm 被扣掉\nreach {r['r_syn']:.1f} µm → 算局部神經元（≤ 20）", proj, False)
    draw(axR, r, r["keep_fib"], r["cut_fib"],
         f"纖維版（A1_fib）：切點就在胞體，主幹一點都沒扣\nreach {r['r_fib']:.1f} µm → " + ("不算局部神經元（> 20）" if r["r_fib"] > 20 else "仍算局部神經元"), proj, True)
    for ax in (axL, axR):
        ax.autoscale_view()
    # 讓左右兩張同一個範圍
    xl = (min(axL.get_xlim()[0], axR.get_xlim()[0]), max(axL.get_xlim()[1], axR.get_xlim()[1]))
    yl = (min(axL.get_ylim()[0], axR.get_ylim()[0]), max(axL.get_ylim()[1], axR.get_ylim()[1]))
    for ax in (axL, axR):
        ax.set_xlim(xl); ax.set_ylim(yl)
    # 比例尺
    L = 20 if (xl[1] - xl[0]) < 250 else 50
    axL.plot([xl[0] + 8, xl[0] + 8 + L], [yl[0] + 8] * 2, color="k", lw=2); axL.text(xl[0] + 8 + L / 2, yl[0] + 11, f"{L} µm", ha="center", fontsize=9)
    # 胞體放大：上＝突觸版、下＝纖維版；背景是胞體所在深度 ±1 µm 那一薄片的標籤
    s0 = r["xyz"][r["root"]]
    near = np.flatnonzero(np.linalg.norm(r["xyz"] - s0, axis=1) <= 15)
    stubn = [n for st in r["stubs"] for n in st["nodes"]]
    proj_z = Proj(np.concatenate([r["xyz"][near], np.repeat(r["xyz"][stubn], 20, 0)]))   # 胞體附近的局部視角，短線加權讓它攤開
    H = max(6.0, 1.3 * max([st["length"] for st in r["stubs"]] + [0]))
    proj = proj_z
    for ax, keep, cut, stub, t in ((axZ1, r["keep_syn"], r["cut_syn"], False, "胞體附近放大（突觸版，換一個視角）"),
                                   (axZ2, r["keep_fib"], r["cut_fib"], True, "胞體附近放大（纖維版，換一個視角）")):
        region_outline(ax, r, proj, r["main"], "#1f5fa8", "-", "", zoom=(s0, H + 4))
        if other:
            region_outline(ax, r, proj, other, "#d62728", "--", "", zoom=(s0, H + 4))
        draw(ax, r, keep, cut, t, proj, stub, zoom=True)
        c2 = proj.transform(s0[None])[0]
        ax.set_xlim(c2[0] - H, c2[0] + H); ax.set_ylim(c2[1] - H, c2[1] + H)
        ax.plot([c2[0] - H * 0.9, c2[0] - H * 0.9 + 2], [c2[1] - H * 0.88] * 2, color="k", lw=2); ax.text(c2[0] - H * 0.9 + 1, c2[1] - H * 0.8, "2 µm", ha="center", fontsize=8)
    # 共用圖例
    h, l = axR.get_legend_handles_labels()
    seen = {}
    for hh, ll in zip(h, l):
        if ll and ll not in seen:
            seen[ll] = hh
    fig.legend(seen.values(), seen.keys(), loc="lower center", ncol=4, fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle(f"{tag}　{r['type']}（bodyId {r['bid']}）：{desc}；主腦區 {r['main']}", fontsize=12, y=0.995)
    fig.savefig(os.path.join(HERE, fname), dpi=130, bbox_inches="tight"); plt.close(fig)
    print("寫出", fname)


figure(RES[0], EX[0][2], "ex1.png", "圖 1")
figure(RES[1], EX[1][2], "ex2.png", "圖 2")


# ---------------- 3D：例子 1（LPi34），兩區外形＋三段骨架 ----------------
def mesh(names, faces=1800, sigma=1.0, around=None):
    ids = [NAMES.index(n) for n in names]
    c = np.isin(np.asarray(LAB[::4, ::4, ::4]), ids); idx = np.argwhere(c)
    lo = np.maximum(idx.min(0) * 4 - 6, 0); hi = np.minimum(idx.max(0) * 4 + 10, LAB.shape)
    m = np.isin(np.asarray(LAB[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]), ids)
    return mask_mesh(m, list(lo), ORIG, 1.0, faces, sigma=sigma)


def poly(r, keep_mask_edges):
    xyz, par = r["xyz"], r["par"]
    ch = np.flatnonzero(par >= 0)
    sel = ch[keep_mask_edges[ch]]
    return [np.stack([xyz[c], xyz[par[c]]]) for c in sel]


r = RES[0]
ch_mask_keep = np.zeros(len(r["xyz"]), bool); ch_mask_drop = np.zeros(len(r["xyz"]), bool)
ch = np.flatnonzero(r["par"] >= 0)
ks = r["keep_syn"]
ch_mask_keep[ch] = ks[ch] & ks[r["par"][ch]]
ch_mask_drop[ch] = ~(ks[ch] & ks[r["par"][ch]])
stub_nodes = set(r["stubs"][0]["nodes"][1:])
stub_mask = np.zeros(len(r["xyz"]), bool); stub_mask[list(stub_nodes)] = True
groups = [
    {"name": "腦區", "items": [
        mesh_item(f"主腦區 {r['main']}（小葉板）", *mesh([r["main"]]), color="#1f5fa8", opacity=0.18),
        mesh_item(f"胞體所在的 {r['soma_region']}（髓質）", *mesh([r["soma_region"]]), color="#d62728", opacity=0.12)]},
    {"name": f"{r['type']}（{r['bid']}）", "items": [
        lines_item("分支（兩版都算）", poly(r, ch_mask_keep), color="#1f5fa8", width=1.5),
        lines_item(f"主幹 {r['d_cut_syn']:.0f} µm（突觸版扣掉，纖維版沒扣）", poly(r, ch_mask_drop & ~stub_mask), color="#777777", width=2.5),
        lines_item(f"胞體旁的短線 {r['stubs'][0]['length']:.1f} µm（伸進 {r['stubs'][0]['region']}）", poly(r, stub_mask), color="#d62728", width=4),
        points_item("胞體", r["xyz"][[r["root"]]], color="#111111", size=8)]},
]
write_scene(os.path.join(HERE, "scene.json"), "纖維版切點落在胞體：LPi34", groups)
json.dump({str(x["bid"]): dict(type=x["type"], main=x["main"], soma_region=x["soma_region"], trunk=round(x["trunk"], 1),
                                d_cut_syn=round(x["d_cut_syn"], 1), d_cut_fib=round(x["d_cut_fib"], 1),
                                r_syn=round(x["r_syn"], 1), r_fib=round(x["r_fib"], 1),
                                share_syn=round(x["share_syn"][0], 3), share_fib=round(x["share_fib"][0], 3),
                                stubs=[(s["region"], round(s["length"], 1)) for s in x["stubs"]]) for x in RES},
          open(os.path.join(HERE, "numbers.json"), "w"), ensure_ascii=False, indent=1)

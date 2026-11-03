#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""條目：官方 Ito 分區的前腦橋（PB）在邊界法 200 區的 LPU 分法下，LPU 由哪些 200 區組成（MaleCNS v1.0）。
全部用 A1 管線框（原點 −480,−410,−175，1 µm）的標籤：200 區＝A1_syn_200/tpl/d03_tpl、併區切分後＝A1_syn_200/split/d03_200_r{T}、
官方 80 區＝A1_maleCNS_103/mcns/d03_mcns；骨架＝swc_pipe_103（同框）。用法：python3 make.py"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from flylib import mesh_item, lines_item, points_item, write_scene, swc_polylines, read_swc, BD_BUILD
sys.path.insert(0, BD_BUILD)
from export_meshes import mask_mesh

CMU = "/home/wanjuli/claude_linux/CMU_research"
ORIG = [-480.0, -410.0, -175.0]
def vol(d):
    return np.load(f"{d}/work/labels_fc_1um.npy", mmap_mode="r"), json.load(open(f"{d}/D03_labels_meta.json"))["names"]
L200, N200 = vol(f"{CMU}/A1_syn_200/tpl/d03_tpl")
L80, N80 = vol(f"{CMU}/A1_maleCNS_103/mcns/d03_mcns")

def mesh(L, names, sel, faces=1500, sigma=1.0):
    ids = [names.index(n) + 1 for n in sel]
    # 先在 4 µm 粗格找包圍盒，再取 1 µm 遮罩
    c = np.isin(np.asarray(L[::4, ::4, ::4]), ids); idx = np.argwhere(c)
    lo = np.maximum(idx.min(0) * 4 - 6, 0); hi = np.minimum(idx.max(0) * 4 + 10, L.shape)
    m = np.isin(np.asarray(L[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]), ids)
    return mask_mesh(m, list(lo), np.array(ORIG), 1.0, faces, sigma=sigma)

REG = [("E052_PB", "#1f5fa8"), ("E077_PB", "#6fa8dc"), ("E060_IB", "#e69138"), ("E065_IB", "#f6b26b"), ("E012_SPS_L", "#38a169")]
pb = [mesh_item("官方 Ito 分區的前腦橋 PB", *mesh(L80, N80, ["PB"], 2000), color="#222222", opacity=0.55)]
regs = [mesh_item(f"{n}", *mesh(L200, N200, [n], 1500), color=c, opacity=0.28) for n, c in REG]
u20 = [mesh_item("r20 的 LPU：E052＋E077＋E060＋E065", *mesh(L200, N200, [n for n, _ in REG[:4]], 2500), color="#2f9e5b", opacity=0.3)]
u30 = [mesh_item("r30 的 LPU：上面 4 區＋E012", *mesh(L200, N200, [n for n, _ in REG], 3000), color="#2f9e5b", opacity=0.3)]
for it in u20 + u30:
    it["visible"] = False

ann = pd.read_feather("/mnt/sda1/work1/male_cns/raw/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather").set_index("bodyId")
ln = pd.read_csv(f"{CMU}/A1_syn_200/data/ln_200_r20.csv"); g = ln[ln.region == "E052_PB"].name.astype(int)
d7 = [b for b in g if ann.loc[b, "type"] == "Delta7"][:8]
cols = ["#c0392b", "#8e44ad", "#d35400", "#16a085", "#7f8c00", "#b03a2e", "#5b2c6f", "#1b4f72"]
neur = [lines_item(f"Δ7（{b}）", swc_polylines(read_swc(f"/mnt/sda1/work1/male_cns/swc_pipe_103/{b}_swc.swc"), 3), color=c) for b, c in zip(d7, cols)]

bl = np.asarray(L200[::4, ::4, ::4]); vnc = set(N200[-23:])
brain = np.isin(bl, [i + 1 for i, n in enumerate(N200) if n not in vnc])
zz = np.nonzero(brain.any((1, 2)))[0]; brain = brain[: zz.max() + 2]
bv, bf = mask_mesh(brain, [0, 0, 0], np.array(ORIG), 4.0, 4000, sigma=1.5)
ref = [mesh_item("全腦輪廓", bv, bf, color="#999999", opacity=0.05, ref=True)]

# ---- 突觸密度：同事切 200 區時用的 5 µm 方格突觸數（npz 的 syn 欄），方格中心換到管線框 ----
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm, colors as mcolors
NPZ = np.load(f"{CMU}/A1_syn_200/tpl/_npz/male_MaleCNS_edge_200regions.npz", allow_pickle=False)
FR = json.load(open(f"{CMU}/A1_syn_200/tpl/d03_tpl/frame.json"))
SHIFT = np.array(FR["shift_um"])                       # 管線 µm＝5 µm 方格索引×5＋shift（偏移 0，見 tpl/t1_labels.py）
VXYZ = NPZ["vox_xyz"].astype(float) * 5.0 + SHIFT + 2.5   # 方格中心
SYN = NPZ["syn"].astype(float); LAB = NPZ["label"]
DEN = SYN / 125.0                                      # 每立方微米的突觸數
sel_all = np.isin(LAB, [int(n[1:4]) for n, _ in REG])
lo_d, hi_d = np.percentile(DEN[sel_all], [2, 98])
norm = mcolors.LogNorm(vmin=max(lo_d, 1e-3), vmax=hi_d); cmap = matplotlib.colormaps["inferno"]
dens = []; dstat = []
for n, c in REG:
    m = LAB == int(n[1:4])
    rgb = cmap(norm(np.clip(DEN[m], norm.vmin, norm.vmax)))[:, :3] * 0.92
    dens.append(points_item(f"{n} 突觸密度", VXYZ[m], color=c, size=5.5, colors=rgb, visible=False))
    dstat.append((n, int(m.sum()), int(SYN[m].sum()), DEN[m]))
DSTAT = dstat

write_scene(os.path.join(HERE, "scene.json"), "前腦橋 PB 的 LPU 與 200 區",
            [{"name": "官方前腦橋", "items": pb},
             {"name": "蓋到前腦橋的 5 個 200 區", "items": regs},
             {"name": "LPU（預設關閉）", "items": u20 + u30},
             {"name": "各區的突觸密度（預設關閉）", "items": dens},
             {"name": f"r20 LPU 的 Δ7（抽 {len(d7)} 顆）", "items": neur},
             {"name": "參考", "items": ref}])

# ---- 平面圖：組成表 ----
from matplotlib import font_manager
FP = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"; font_manager.fontManager.addfont(FP)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=FP).get_name()
rows = [("E052_PB", "34%", "38%"), ("E077_PB", "20%", "37%"), ("E060_IB", "12%", "5%"), ("E065_IB", "11%", "6%"),
        ("E012_SPS_L", "10%", "1%"), ("E069_ICL_L 等小區", "5%", "—"), ("不在任何 200 區", "8%", "—")]
st = {"r10": ["hub"] * 5 + ["hub", "—"], "r20": ["LPU"] * 4 + ["hub", "hub", "—"], "r30": ["LPU"] * 5 + ["hub", "—"]}
fig, ax = plt.subplots(figsize=(9, 3.6)); ax.axis("off")
head = ["200 區", "佔官方 PB", "這區有多少\n在 PB 內", "r10", "r20", "r30"]
cell = [[r[0], r[1], r[2], st["r10"][i], st["r20"][i], st["r30"][i]] for i, r in enumerate(rows)]
tb = ax.table(cellText=cell, colLabels=head, loc="center", cellLoc="center")
tb.auto_set_font_size(False); tb.set_fontsize(9); tb.scale(1, 1.6)
for (i, j), c in tb.get_celld().items():
    if i == 0: c.set_facecolor("#eeeeee"); c.set_text_props(weight="bold")
    elif j >= 3:
        t = c.get_text().get_text()
        c.set_facecolor({"LPU": "#bfe3cb", "hub": "#dddddd"}.get(t, "white"))
ax.set_title("官方前腦橋 PB 被哪些 200 區蓋到，各門檻下歸屬為何（綠＝同一個 LPU 聯集的成員）", fontsize=10)
fig.savefig(os.path.join(HERE, "composition.png"), dpi=160, bbox_inches="tight")
print("Δ7", d7)

# ---- 平面圖：各區突觸密度分布＋色標 ----
fig, (ax, cax) = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw=dict(width_ratios=[20, 0.6], wspace=0.04))
pos = np.arange(len(DSTAT))
vp = ax.violinplot([d[3] for d in DSTAT], positions=pos, showmedians=True, widths=0.8)
for b, (n, c) in zip(vp["bodies"], REG):
    b.set_facecolor(c); b.set_alpha(0.55)
ax.set_yscale("log"); ax.set_xticks(pos)
ax.set_xticklabels([f"{n}\n{nv:,} 格\n{ns:,} 個突觸\n中位數 {np.median(d):.1f}" for n, nv, ns, d in DSTAT], fontsize=8)
from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
TK = [2, 3, 5, 10, 20, 30]
ax.yaxis.set_major_locator(FixedLocator(TK)); ax.yaxis.set_major_formatter(FixedFormatter([str(t) for t in TK])); ax.yaxis.set_minor_formatter(NullFormatter())
ax.set_ylabel("突觸密度（每立方微米的突觸數，對數軸）")
ax.axhspan(norm.vmin, norm.vmax, color="#f4f4f4", zorder=-1)
ax.set_title("組成前腦橋 LPU 的 5 個 200 區：每個 5 µm 方格的突觸密度分布", fontsize=10)
cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax); cb.set_label("3D 圖點的顏色（灰底範圍）", fontsize=8)
cb.set_ticks([3, 5, 10, 20]); cb.set_ticklabels(["3", "5", "10", "20"]); cb.minorticks_off()
fig.savefig(os.path.join(HERE, "density.png"), dpi=160, bbox_inches="tight")
print("密度色標", norm.vmin, norm.vmax, [(n, nv, ns, round(float(np.median(d)), 3)) for n, nv, ns, d in DSTAT])


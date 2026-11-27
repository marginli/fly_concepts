#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fly_concepts：三份連結體（MaleCNS、FlyWire、BANC）共用的讀取工具，給「神經元畫板」等條目用。

每份資料各自的座標框（不同框的東西不放同一個 scene）：
  mcns  MaleCNS v1.0：A1 管線 µm 框；腦區＝官方 v5 腦 80 區（brain_division 標籤，z 原點 −191，見 flylib）；
        骨架 /mnt/sda1/work1/male_cns/swc_pipe；上＝−y、前＝−z。
  fw    FlyWire v783：FC12 框（每格約 0.73／0.75／1.12 µm）；腦區＝官方 78 區（A1/em/d03_em_r78，
        由官方逐突觸腦區名稱多數決建成；用 thre/t8_fw_extend.py 在 x 方向加寬的版本，原版切掉部分 lamina）；
        骨架 swc_fc（同框）；上＝+y、前＝+z。
        注意：這套仿射是「左右名字對調」版（A1 U2 裁示），畫面左右與另兩份相反。
  banc  BANC v888：原生座標（µm）；腦區＝腦 75 區（Ito）＋腹神經索 26 區（MANC），
        由 MB/MB_simulation/thre/t5_banc.py 建成（腦部用官方外形、其餘用官方逐突觸名稱投票）；
        骨架 swc_banc_space（nm → µm；有 _skeleton 用它，否則 _l2 粗骨架）；上＝+z、前＝−y（腹神經索往 +y）。
方向（上、前）是 2026-11-27 用 MB_CA_R、MB 葉、AL_R、GNG 的重心實測：前＝萼→葉、嗅葉的方向，上＝GNG→萼的方向。
左右：MaleCNS 與 BANC 的右側在畫面左邊（從正面看果蠅），FlyWire 相反。
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flylib as FL   # noqa: E402

CMU = "/home/wanjuli/claude_linux/CMU_research"
THRE = "/home/wanjuli/claude_yilan/MB/MB_simulation/thre/data"
CACHE = os.path.expanduser("~/.cache/fly_concepts")


def _banc_meta():
    return json.load(open(f"{THRE}/banc_lab_meta.json", encoding="utf-8"))


DS = {
    "mcns": dict(label="MaleCNS v1.0", lab=FL.MCNS_LABELS, origin=list(FL.LABEL_ORIGIN), step=1.0,
                 names=lambda: FL.mcns_region_names(), up=[0, -1, 0], front=[0, 0, -1], unit="µm"),
    "fw": dict(label="FlyWire v783", lab=f"{THRE}/fw_lab_ext.npy", origin=[-590.0, -410.0, -175.0], step=1.0,
               names=lambda: json.load(open(f"{CMU}/A1/em/d03_em_r78/D03_labels_meta.json", encoding="utf-8"))["names"],
               up=[0, 1, 0], front=[0, 0, 1], unit="FC12 格"),
    "banc": dict(label="BANC v888", lab=f"{THRE}/banc_lab_final.npy", origin=None, step=1.0,
                 names=lambda: _banc_meta()["names"], up=[0, 0, 1], front=[0, -1, 0], unit="µm"),
}
_cache = {}


def origin(ds):
    o = DS[ds]["origin"]
    return np.array(o if o is not None else _banc_meta()["origin_um"], float)


def labels(ds):
    if ("lab", ds) not in _cache:
        _cache[("lab", ds)] = np.load(DS[ds]["lab"], mmap_mode="r")
    return _cache[("lab", ds)]


def names(ds):
    if ("names", ds) not in _cache:
        _cache[("names", ds)] = list(DS[ds]["names"]())
    return _cache[("names", ds)]


def region_at(ds, xyz):
    """座標（該資料的框）N×3 → 標籤值（0＝腦區外）。"""
    lab = labels(ds)
    i = np.round((np.asarray(xyz, float) - origin(ds)) / DS[ds]["step"]).astype(int)[:, ::-1]
    ok = (i >= 0).all(1) & (i < lab.shape).all(1)
    v = np.zeros(len(i), int)
    v[ok] = np.asarray(lab)[tuple(i[ok].T)]
    return v


# ---------- 註記：型別 → 神經元編號 ----------

def annotations(ds):
    import pandas as pd
    if ("ann", ds) in _cache:
        return _cache[("ann", ds)]
    if ds == "mcns":
        a = pd.read_feather(FL.MCNS_ANN, columns=["bodyId", "type", "instance", "somaSide", "superclass"])
        a = a.rename(columns={"bodyId": "id", "somaSide": "side"})
        a["side"] = a.side.map({"R": "R", "L": "L"}).fillna("")
    elif ds == "fw":
        a = pd.read_csv("/mnt/sda1/work1/flywire_783/Supplemental_file1_neuron_annotations.tsv", sep="\t",
                        usecols=["root_id", "cell_type", "side", "super_class"], dtype=str)
        a = a.rename(columns={"root_id": "id", "cell_type": "type", "super_class": "superclass"})
        a["instance"] = a["type"]
        a["side"] = a.side.map({"right": "R", "left": "L"}).fillna("")
    else:
        a = pd.read_feather("/mnt/sda1/work1/banc_888/banc_888_meta.feather",
                            columns=["banc_888_id", "cell_type", "side", "super_class", "proofread"])
        a = a[a.proofread == "TRUE"].rename(columns={"banc_888_id": "id", "cell_type": "type", "super_class": "superclass"})
        a["instance"] = a["type"]
        a["side"] = a.side.map({"right": "R", "left": "L"}).fillna("")
    a["id"] = a["id"].astype(str)
    a = a.drop_duplicates("id").fillna("")
    _cache[("ann", ds)] = a
    return a


def find(ds, query, side=None, limit=20):
    """query：一個神經元編號，或型別名（比對 type 或 instance，大小寫相符）。回傳 [(編號, 型別, 側)]。"""
    a = annotations(ds)
    q = str(query).strip()
    if q.isdigit():
        r = a[a.id == q]
        if r.empty:
            return [(q, "", "")]
    else:
        r = a[(a.type == q) | (a.instance == q)]
    if side:
        r = r[r.side == side]
    return [(x.id, x.type, x.side) for x in r.head(limit).itertuples()]


# ---------- 突觸（索引由 build_syn_index.py 建成） ----------
SYN_DIR = "/mnt/sda1/work1/fly_concepts_syn"


def synapses(ds, nid, end):
    """某顆神經元的突觸位置 N×3（該資料的框）。end＝pre（輸出點）或 post（輸入點）。
    fw、banc 的 pre 來源是一個連結一列，這裡把同一位置的重複列去掉，只留送出點本身。"""
    k = ("syn", ds, end)
    if k not in _cache:
        d = f"{SYN_DIR}/{ds}"
        if not os.path.exists(f"{d}/{end}_ids.npy"):
            raise FileNotFoundError(f"{ds} 的突觸索引還沒建：python3 lib/build_syn_index.py {ds}")
        _cache[k] = tuple(np.load(f"{d}/{end}_{n}.npy", mmap_mode="r") for n in ("ids", "start", "xyz"))
    ids, start, xyz = _cache[k]
    i = int(np.searchsorted(ids, int(nid)))
    if i >= len(ids) or ids[i] != int(nid):
        return np.zeros((0, 3), np.float32)
    p = np.asarray(xyz[start[i]:start[i + 1]], np.float32)
    if end == "pre" and ds in ("fw", "banc") and len(p):
        p = np.unique(np.round(p, 2), axis=0)
    return p


def region_counts(ds, pts):
    """點 → {標籤值: 個數}（不含 0＝腦區外）。"""
    if len(pts) == 0:
        return {}
    c = np.bincount(region_at(ds, pts), minlength=len(names(ds)) + 1)
    return {i: int(c[i]) for i in range(1, len(c)) if c[i] > 0}


# ---------- 連結對象（上游／下游） ----------
# 連結數＝兩顆神經元之間的突觸數，各資料用官方的連結表：
#   mcns connectome-weights traced-only（weight；只含已追蹤完成的神經元）
#   fw   proofread_connections_783（syn_count，依腦區分列，這裡加總；只含校對過的神經元）
#   banc banc_888_edgelist_simple_v3（count）
EDGES = {
    "mcns": ("/mnt/sda1/work1/male_cns/raw/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5-traced-only.feather",
             "body_pre", "body_post", "weight"),
    "fw": ("/mnt/sda1/work1/flywire_783/proofread_connections_783.feather", "pre_pt_root_id", "post_pt_root_id", "syn_count"),
    "banc": ("/mnt/sda1/work1/banc_888/banc_888_edgelist_simple_v3.feather", "pre", "post", "count"),
}


def partners(ds, nids, direction):
    """nids（一或多顆）的連結對象。direction＝up（送訊號給它們的上游）或 down（接收它們訊號的下游）。
    回傳 [(對象編號字串, 連結數)]，連結數由多到少；不含 nids 自己。"""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.ipc as ipc
    path, cpre, cpost, cw = EDGES[ds]
    me, other = (cpost, cpre) if direction == "up" else (cpre, cpost)
    r = ipc.open_file(pa.memory_map(path))
    typ = r.schema.field(me).type
    vs = pa.array([str(n) for n in nids]) if pa.types.is_string(typ) else pa.array([int(n) for n in nids], pa.int64())
    acc = {}
    for i in range(r.num_record_batches):
        b = r.get_batch(i).select([me, other, cw])
        b = b.filter(pc.is_in(b.column(me), value_set=vs))
        for o, w in zip(b.column(other).to_pylist(), b.column(cw).to_pylist()):
            acc[str(o)] = acc.get(str(o), 0) + int(w)
    own = {str(n) for n in nids}
    return sorted(((o, w) for o, w in acc.items() if o not in own), key=lambda x: -x[1])


def neuron_info(ds, nid):
    """(型別, 側)；註記裡沒有就回空字串。"""
    a = annotations(ds)
    if ("annidx", ds) not in _cache:
        _cache[("annidx", ds)] = a.set_index("id")[["type", "side"]]
    t = _cache[("annidx", ds)]
    return tuple(t.loc[str(nid)]) if str(nid) in t.index else ("", "")


# ---------- 骨架 ----------

def swc_path(ds, nid):
    nid = str(nid)
    if ds == "mcns":
        return os.path.join(FL.MCNS_SWC, f"{nid}_swc.swc")
    if ds == "fw":
        return f"/mnt/sda1/work1/flywire_783/swc_fc/{nid}_swc.swc"
    d = "/mnt/sda1/work1/banc_888/swc_banc_space"
    for k in ("skeleton", "l2"):
        p = f"{d}/{nid}_{k}.swc"
        if os.path.exists(p):
            return p
    return f"{d}/{nid}_skeleton.swc"


def read_skeleton(ds, nid):
    """回傳 SWC 陣列（欄：id type x y z r parent），座標已換成該資料的框。"""
    import pandas as pd
    a = pd.read_csv(swc_path(ds, nid), sep=r"\s+", comment="#", header=None, usecols=range(7)).to_numpy(float)
    if ds == "banc":
        a[:, 2:5] /= 1000.0
    return a


def neuron_lines(ds, nid, max_points=40000):
    a = read_skeleton(ds, nid)
    keep = max(1, int(np.ceil(len(a) / max_points)))
    return FL.swc_polylines(a, keep_every=keep), a


def region_lengths(ds, a):
    """骨架每條邊的中點查腦區，回傳 {標籤值: 長度}（不含 0＝腦區外）。"""
    ids = a[:, 0].astype(np.int64); par = a[:, 6].astype(np.int64); xyz = a[:, 2:5]
    row = {i: k for k, i in enumerate(ids)}
    ch = [k for k in range(len(a)) if par[k] in row]
    pk = np.array([row[par[k]] for k in ch], int); ck = np.array(ch, int)
    if len(ck) == 0:
        return {}
    mid = (xyz[ck] + xyz[pk]) / 2
    ln = np.linalg.norm(xyz[ck] - xyz[pk], axis=1)
    lab = region_at(ds, mid)
    out = np.bincount(lab, weights=ln, minlength=len(names(ds)) + 1)
    return {i: float(out[i]) for i in range(1, len(out)) if out[i] > 0}


# ---------- 腦區外形 ----------

def _mask_mesh(mask, lo, step, faces, sigma, org):
    sys.path.insert(0, FL.BD_BUILD)
    from export_meshes import mask_mesh
    return mask_mesh(mask, lo, org, step, faces, sigma=sigma)


def region_mesh(ds, name, faces=1500):
    """某資料的一個腦區 → (verts, faces)，存快取。"""
    os.makedirs(CACHE, exist_ok=True)
    cp = os.path.join(CACHE, f"{ds}_{name}_{faces}.npz")
    if os.path.exists(cp):
        z = np.load(cp)
        return z["v"], z["f"]
    rid = names(ds).index(name) + 1
    lab = labels(ds)
    idx = np.argwhere(np.asarray(lab) == rid)
    lo = np.maximum(idx.min(0) - 3, 0)
    hi = np.minimum(idx.max(0) + 4, lab.shape)
    mask = np.asarray(lab[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]) == rid
    v, f = _mask_mesh(mask, list(lo), DS[ds]["step"], faces, 1.0, origin(ds))
    np.savez_compressed(cp, v=v, f=f)
    return v, f


def outline_mesh(ds, faces=4000):
    """全部腦區聯集的粗輪廓（BANC 含腹神經索），存快取。"""
    from scipy import ndimage
    os.makedirs(CACHE, exist_ok=True)
    cp = os.path.join(CACHE, f"{ds}__outline_{faces}.npz")
    if os.path.exists(cp):
        z = np.load(cp)
        return z["v"], z["f"]
    m = np.asarray(labels(ds))[::2, ::2, ::2] > 0
    m = ndimage.binary_closing(m, iterations=2)
    v, f = _mask_mesh(m, [0, 0, 0], DS[ds]["step"] * 2, faces, 1.5, origin(ds))
    np.savez_compressed(cp, v=v, f=f)
    return v, f

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""神經元畫板用：把三份資料的突觸位置整理成「依神經元排序」的索引，畫圖時可以一次查出某顆神經元的全部 pre／post。

輸出 SYN_DIR/<ds>/<end>_{ids,start,xyz}.npy（end＝pre／post）：
  ids   排序後的神經元編號（int64，不重複）
  start 長度 len(ids)+1；第 i 顆的點是 xyz[start[i]:start[i+1]]
  xyz   float32，已換成畫板用的座標框（同 flyds.DS 的骨架）
來源與換算：
  mcns  syn-points-male-cns-v1.0-minconf-0.5.feather（kind＝PreSyn／PostSyn，一列一個突觸端點；
        pre＝T-bar）；8 nm 體素 → 管線 µm，用 A1_maleCNS d03 frame.json（同 m3_skeleton／m4_synapses）
  fw    syn_w5（A1 T0 篩過、兩端都是校對過的神經元；一列一個突觸連結）；nm → FC12，用 t1_affine
        「左右名字對調的對照」（同 thre/t4_flywire.py）
  banc  banc_888_synapses_v3_enriched.parquet（一列一個突觸連結）；體素 ×(16,16,45) nm → µm（同 thre/t5_banc.py）
fw、banc 的 pre 是「每個連結一列」，同一個送出點連到幾顆下游就重複幾次；畫圖時 flyds.synapses() 會去重。
用法：python3 build_syn_index.py mcns fw banc
"""
import json
import os
import sys
import time

import numpy as np

SYN_DIR = "/mnt/sda1/work1/fly_concepts_syn"
CMU = "/home/wanjuli/claude_linux/CMU_research"
T0 = time.time()


def save(ds, end, owner, xyz):
    d = os.path.join(SYN_DIR, ds)
    os.makedirs(d, exist_ok=True)
    o = np.argsort(owner, kind="stable")
    owner = owner[o]
    xyz = xyz[o]
    ids, first = np.unique(owner, return_index=True)
    start = np.r_[first, len(owner)].astype(np.int64)
    np.save(f"{d}/{end}_ids.npy", ids)
    np.save(f"{d}/{end}_start.npy", start)
    np.save(f"{d}/{end}_xyz.npy", xyz.astype(np.float32))
    print(f"[{ds}] {end}：{len(owner):,} 點、{len(ids):,} 顆神經元（{time.time() - T0:.0f}s）", flush=True)


def build_mcns():
    import pyarrow.ipc as ipc
    src = "/mnt/sda1/work1/male_cns/raw/flat-connectome/syn-points-male-cns-v1.0-minconf-0.5.feather"
    fr = json.load(open(f"{CMU}/A1_maleCNS/mcns/d03_mcns/frame.json"))
    perm, shift, vnm = fr["perm"], np.array(fr["shift_um"]), fr["swc_voxel_nm"]
    fh = open(src, "rb")
    fh.seek(8)
    rd = ipc.open_stream(fh)
    est = os.path.getsize(src) // (65536 * 85) + 1   # 粗估批數，只給進度用
    acc = {"pre": ([], []), "post": ([], [])}
    for k, b in enumerate(rd, 1):
        body = b.column("body").to_numpy().astype(np.int64)
        kd = b.column("kind")
        names = kd.dictionary.to_pylist()
        code = kd.indices.to_numpy()
        P = np.stack([b.column(c).to_numpy() for c in ("x", "y", "z")], 1).astype(np.float64)
        F = ((P * vnm / 1000.0)[:, perm] + shift).astype(np.float32)
        for end, nm in (("pre", "PreSyn"), ("post", "PostSyn")):
            if nm in names:
                m = (code == names.index(nm)) & (body > 0)
                acc[end][0].append(body[m]); acc[end][1].append(F[m])
        if k % 200 == 0:
            print(f"第 {k}/{est} 批（mcns，{time.time() - T0:.0f}s）", flush=True)
    for end, (o, x) in acc.items():
        save("mcns", end, np.concatenate(o), np.concatenate(x))
        acc[end] = None


def build_fw():
    W5 = "/mnt/sda1/work1/flywire_783/syn_w5"
    t1 = json.load(open(f"{CMU}/A1/out/t1_affine.json"))["左右名字對調的對照"]
    A, t = np.array(t1["A_每微米幾格"]), np.array(t1["t_格"])
    used = np.load(f"{W5}/proofread_ids_used.npy").astype(np.int64)
    for end in ("pre", "post"):
        P = np.load(f"{W5}/{end}_xyz.npy", mmap_mode="r")
        I = np.load(f"{W5}/{end}_idx.npy", mmap_mode="r")
        M, CH = len(I), 10_000_000
        xyz = np.empty((M, 3), np.float32)
        for b in range(0, M, CH):
            s = slice(b, min(M, b + CH))
            xyz[s] = (np.asarray(P[s], np.float64) / 1000.0) @ A.T + t
            print(f"第 {b // CH + 1}/{(M + CH - 1) // CH} 批（fw {end}，{time.time() - T0:.0f}s）", flush=True)
        save("fw", end, used[np.asarray(I)], xyz)


def build_banc():
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    pf = pq.ParquetFile("/mnt/sda1/work1/banc_888/banc_888_synapses_v3_enriched.parquet")
    S = np.array([16.0, 16.0, 45.0], np.float32) / 1000.0
    G = pf.num_row_groups
    acc = {"pre": ([], []), "post": ([], [])}
    for g in range(G):
        t = pf.read_row_group(g, columns=["pre_root_id", "post_root_id", "presyn_x", "presyn_y", "presyn_z",
                                          "postsyn_x", "postsyn_y", "postsyn_z"])
        for end, who, e in (("pre", "pre_root_id", "presyn"), ("post", "post_root_id", "postsyn")):
            o = pc.cast(t[who], "int64").to_numpy()
            x = np.stack([t[f"{e}_{c}"].to_numpy() for c in "xyz"], 1).astype(np.float32) * S
            acc[end][0].append(o); acc[end][1].append(x)
        if (g + 1) % 50 == 0 or g + 1 == G:
            print(f"第 {g + 1}/{G} 批（banc，{time.time() - T0:.0f}s）", flush=True)
    for end, (o, x) in acc.items():
        save("banc", end, np.concatenate(o), np.concatenate(x))
        acc[end] = None


if __name__ == "__main__":
    for ds in sys.argv[1:] or ["mcns", "fw", "banc"]:
        {"mcns": build_mcns, "fw": build_fw, "banc": build_banc}[ds]()
    print("完成", flush=True)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fly_concepts 共用工具：從本機資料取腦區外形、神經元骨架、點雲，寫成網頁 3D 檢視器讀的 scene.json。

座標：一律用 A1 管線的 µm 框（brain_division 同框）：x 左右、y 背腹、z 前後。
  MaleCNS：腦區標籤 /mnt/sda1/work1/brain_division/malecns_v5/labels_fc_1um.npy（[z,y,x]，origin −480,−410,−175，1 µm）
           骨架 /mnt/sda1/work1/male_cns/swc_pipe/<bodyId>_swc.swc（已在同一框，µm）
           方向 up = −y（背側朝 −y）、front = −z
  FlyWire／hemibrain／BANC：之後用到時再加 loader（見 CLAUDE.md）。

scene.json 格式：
{ "title": str, "up": [x,y,z], "front": [x,y,z],
  "groups": [ { "name": str, "items": [
      {"kind": "mesh", "name", "color", "opacity", "v": [x,y,z,...], "f": [i,j,k,...]},
      {"kind": "lines", "name", "color", "width", "seg": [[x,y,z, x,y,z, ...] 每條折線], "visible": bool},
      {"kind": "points", "name", "color", "size", "p": [x,y,z,...], "c": [r,g,b,...]（選用，每點顏色）} ] } ] }
"""
import json
import os
import sys

import numpy as np

BD_BUILD = os.path.expanduser("~/claude_linux/learning/brain_division/build")
MCNS_LABELS = "/mnt/sda1/work1/brain_division/malecns_v5/labels_fc_1um.npy"
MCNS_NAMES = "/mnt/sda1/work1/brain_division/malecns_v5/names.json"
MCNS_SWC = "/mnt/sda1/work1/male_cns/swc_pipe"
MCNS_ANN = "/mnt/sda1/work1/male_cns/raw/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather"
ORIGIN = np.array([-480.0, -410.0, -175.0])          # 管線框原點（骨架 µm 座標用這個框）
# MaleCNS 標籤體積（391×440×758）比管線框（375×440×750）在 z 前端多 16 格：
# 標籤第 0 格的 z = −191 µm。2026-11-03 用 KC 落在對應葉的比例實測（位移 0 時 37%、z+16 時 76%）。
LABEL_ORIGIN = np.array([-480.0, -410.0, -191.0])
STEP = 1.0
MCNS_UP, MCNS_FRONT = [0, -1, 0], [0, 0, -1]

_lab = None


def mcns_labels():
    global _lab
    if _lab is None:
        _lab = np.load(MCNS_LABELS, mmap_mode="r")
    return _lab


def mcns_region_at(xyz):
    """骨架座標（管線框 µm，N×3）→ 每點所在的 MaleCNS 區名（不在任何區為 None）。"""
    lab = mcns_labels(); names = mcns_region_names()
    i = np.round((np.asarray(xyz) - LABEL_ORIGIN) / STEP).astype(int)[:, ::-1]
    ok = (i >= 0).all(1) & (i < lab.shape).all(1)
    v = np.zeros(len(i), int); v[ok] = np.asarray(lab)[tuple(i[ok].T)]
    return [names[x - 1] if x else None for x in v]


def mcns_region_names():
    return json.load(open(MCNS_NAMES, encoding="utf-8"))["names"]


def mcns_annotations():
    import pandas as pd
    return pd.read_feather(MCNS_ANN)


def _mesh_from_mask(mask, lo, faces, sigma=1.0):
    sys.path.insert(0, BD_BUILD)
    from export_meshes import mask_mesh
    v, f = mask_mesh(mask, lo, LABEL_ORIGIN, STEP, faces, sigma=sigma)
    return v, f


def mcns_region_mesh(name, faces=1500):
    """MaleCNS 80 區之一（名稱見 mcns_region_names()，例 MB_CA_R）→ (verts µm, faces)。"""
    names = mcns_region_names()
    rid = names.index(name) + 1
    lab = mcns_labels()
    idx = np.argwhere(lab == rid)
    lo = np.maximum(idx.min(0) - 3, 0)
    hi = np.minimum(idx.max(0) + 4, lab.shape)
    mask = np.asarray(lab[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]) == rid
    return _mesh_from_mask(mask, list(lo), faces)


def mcns_brain_mesh(faces=3000):
    """全腦輪廓（所有區聯集、粗平滑）。"""
    from scipy import ndimage
    lab = np.asarray(mcns_labels())[::2, ::2, ::2] > 0
    lab = ndimage.binary_closing(lab, iterations=2)
    sys.path.insert(0, BD_BUILD)
    from export_meshes import mask_mesh
    v, f = mask_mesh(lab, [0, 0, 0], LABEL_ORIGIN, 2.0, faces, sigma=1.5)
    return v, f


def read_swc(path):
    a = np.loadtxt(path, comments="#", ndmin=2)
    return a  # 欄：id type x y z r parent


def swc_polylines(a, keep_every=3):
    """SWC → 折線列表；分枝點與末端一定保留，中間每 keep_every 點留一點。"""
    ids = a[:, 0].astype(np.int64)
    par = a[:, 6].astype(np.int64)
    xyz = a[:, 2:5]
    row = {i: k for k, i in enumerate(ids)}
    nchild = {}
    for p in par:
        if p >= 0:
            nchild[p] = nchild.get(p, 0) + 1
    # 從每個「末端或分枝點」往上走到下一個分枝點／根，形成一段
    lines = []
    for k, i in enumerate(ids):
        if nchild.get(i, 0) == 1:
            continue  # 中間點，不是段起點
        seg = [k]
        j = par[k]
        while j >= 0 and j in row:
            kk = row[j]
            seg.append(kk)
            if nchild.get(j, 0) != 1 or par[kk] < 0:
                break
            j = par[kk]
        if len(seg) < 2:
            continue
        keep = [seg[0]] + seg[1:-1][::keep_every] + [seg[-1]]
        lines.append(xyz[keep])
    return lines


def mcns_neuron_lines(body_id, keep_every=3):
    return swc_polylines(read_swc(os.path.join(MCNS_SWC, f"{int(body_id)}_swc.swc")), keep_every)


# ---------- scene 組裝 ----------

def _r(arr, nd=1):
    return np.round(np.asarray(arr, dtype=float).ravel(), nd).tolist()


def mesh_item(name, v, f, color="#888888", opacity=0.25, ref=False):
    """ref=True：參考物（如全腦輪廓），開頁時鏡頭不以它取景。"""
    return {"kind": "mesh", "name": name, "color": color, "opacity": opacity, "ref": ref,
            "v": _r(v), "f": np.asarray(f, dtype=int).ravel().tolist()}


def lines_item(name, polylines, color="#d33", width=1.5, visible=True):
    return {"kind": "lines", "name": name, "color": color, "width": width, "visible": visible,
            "seg": [_r(p) for p in polylines]}


def points_item(name, pts, color="#333", size=2.0, colors=None, opacity=None, visible=True):
    """colors（選用）：N×3 的 RGB（0–1），每點各自上色；color 仍用於面板上的色塊。"""
    it = {"kind": "points", "name": name, "color": color, "size": size, "p": _r(pts), "visible": visible}
    if colors is not None:
        it["c"] = np.round(np.asarray(colors, dtype=float).ravel(), 2).tolist()
    if opacity is not None:
        it["opacity"] = opacity
    return it


def write_scene(path, title, groups, up=MCNS_UP, front=MCNS_FRONT):
    scene = {"title": title, "up": up, "front": front, "groups": groups}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(scene, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"寫出 {path}（{os.path.getsize(path) / 1e6:.2f} MB）")

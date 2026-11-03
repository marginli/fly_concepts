#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""條目：嗅葉到蕈狀體的投射神經元（MaleCNS v1.0，右腦）。用法：python3 make.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from flylib import *

regions = [mesh_item("嗅葉（AL）", *mcns_region_mesh("AL_R", 1500), color="#d9822b", opacity=0.25),
           mesh_item("蕈狀體萼（CA）", *mcns_region_mesh("MB_CA_R", 1200), color="#8e7cc3", opacity=0.3),
           mesh_item("側角（LH）", *mcns_region_mesh("LH_R", 1500), color="#3c9d5d", opacity=0.25)]
mb_rest = [mesh_item(lab, *mcns_region_mesh(n, 800), color="#aaaaaa", opacity=0.15)
           for n, lab in [("MB_PED_R", "柄"), ("MB_aL_R", "α 葉"), ("MB_apL_R", "α′ 葉"),
                          ("MB_bL_R", "β 葉"), ("MB_bpL_R", "β′ 葉"), ("MB_gL_R", "γ 葉")]]
bv, bf = mcns_brain_mesh(faces=4000)
brain = [mesh_item("全腦輪廓", bv, bf, color="#999999", opacity=0.05, ref=True)]

ann = mcns_annotations()
pn = ann[(ann["class"] == "ALPN") & (ann.somaSide == "R")]
# 單一嗅小球、胞體在嗅葉前背側（adPN）或外側（lPN）的投射神經元
uni = pn[pn.type.astype(str).str.match(r"^[A-Z0-9]+[a-z]?\d?[a-z]?_(ad|l)PN\d?$")]
featured = [("DA1_lPN", "DA1", "#c0392b"), ("DL3_lPN", "DL3", "#1f5fa8", 24660), ("VA1v_adPN", "VA1v", "#16a085"),
            ("DM6_adPN", "DM6", "#8e44ad"), ("DL2d_adPN", "DL2d", "#d35400"), ("VM5d_adPN", "VM5d", "#7f8c00")]
feat = []
# DL3 的第一個（20496）不進萼，示範改用同型、有進萼的 24660
for t, g, c, *pick in featured:
    b = pick[0] if pick else int(pn[pn.type == t].bodyId.iloc[0])
    feat.append(lines_item(f"{g} 嗅小球的投射神經元（{b}）", mcns_neuron_lines(b, 3), color=c))
allpn = [lines_item(f"{t}（{b}）", mcns_neuron_lines(b, 10), color="#7a6a9a", visible=False)
         for t, b in zip(uni.type, uni.bodyId)]
print(f"單一嗅小球投射神經元（右）：{len(uni)} 個、{uni.type.nunique()} 種")

write_scene(os.path.join(HERE, "scene.json"), "嗅葉到蕈狀體的投射神經元",
            [{"name": "腦區", "items": regions},
             {"name": "6 個嗅小球各一個投射神經元", "items": feat},
             {"name": f"全部 {len(uni)} 個（預設關閉）", "items": allpn},
             {"name": "蕈狀體其他部分", "items": mb_rest},
             {"name": "參考", "items": brain}])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""條目：蕈狀體的分區與三類 KC（MaleCNS v1.0，右腦）。用法：python3 make.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from flylib import *

parts = [("MB_CA_R", "萼（CA）", "#8e7cc3"), ("MB_PED_R", "柄（PED）", "#a0a0a0"),
         ("MB_aL_R", "α 葉", "#e07b39"), ("MB_bL_R", "β 葉", "#e0a939"),
         ("MB_apL_R", "α′ 葉", "#3c9d5d"), ("MB_bpL_R", "β′ 葉", "#7cc36a"),
         ("MB_gL_R", "γ 葉", "#3d7fc1")]
mb = [mesh_item(lab, *mcns_region_mesh(n, faces=1200), color=c, opacity=0.28) for n, lab, c in parts]
bv, bf = mcns_brain_mesh(faces=4000)
brain = [mesh_item("全腦輪廓", bv, bf, color="#999999", opacity=0.05, ref=True)]

ann = mcns_annotations()
kcs = [("KCg-m", "γ 型 KC", "#1f5fa8"), ("KCa'b'-m", "α′/β′ 型 KC", "#1e7a3c"), ("KCab-m", "α/β 型 KC", "#c0392b")]
neu = []
for t, lab, c in kcs:
    ids = ann[(ann.type == t) & (ann.somaSide == "R")].bodyId.tolist()[:3]
    for i, b in enumerate(ids):
        neu.append(lines_item(f"{lab} #{i+1}（{b}）", mcns_neuron_lines(b), color=c))

write_scene(os.path.join(HERE, "scene.json"), "蕈狀體與 KC",
            [{"name": "蕈狀體分區（右）", "items": mb}, {"name": "KC 神經元", "items": neu},
             {"name": "參考", "items": brain}])

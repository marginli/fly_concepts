# 每顆 MaleCNS 神經元的突觸點重心（原生座標，8 nm 體素）。逐批讀 13 GB 的 syn-points，只取 x,y,z,body。
import os, pyarrow.ipc as ipc, pyarrow as pa, numpy as np, pandas as pd, time
F = "/mnt/sda1/work1/male_cns/raw/flat-connectome/syn-points-male-cns-v1.0-minconf-0.5.feather"
r = ipc.open_file(pa.memory_map(F)); t0 = time.time()
acc = {}
S = None; bodies = []
sums = []
for i in range(r.num_record_batches):
    b = r.get_batch(i).select(["x", "y", "z", "body"]).to_pandas()
    g = b.groupby("body").agg(x=("x", "sum"), y=("y", "sum"), z=("z", "sum"), n=("x", "size"))
    sums.append(g)
    if len(sums) >= 200:
        sums = [pd.concat(sums).groupby(level=0).sum()]
    if i % 500 == 0: print(i, round(time.time() - t0), flush=True)
g = pd.concat(sums).groupby(level=0).sum()
out = pd.DataFrame({"body": g.index.values, "x": g.x / g.n, "y": g.y / g.n, "z": g.z / g.n, "n": g.n})
out.to_parquet(os.path.expanduser("~/claude_yilan/fly_multiwork/stage2/out/syn_centroid.parquet"))
print("完成", len(out), round(time.time() - t0))

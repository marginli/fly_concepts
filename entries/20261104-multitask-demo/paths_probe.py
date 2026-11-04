# 探勘：用第一階段 sweep 結果（MaleCNS）找每件工作的上游中繼細胞型
import sys, os, numpy as np, collections
sys.path.insert(0, os.path.expanduser("~/claude_yilan/MB/MB_simulation/sim"))
import model
c = model.load("malecns"); a = c.ann
typ = a["type"].fillna("").astype(str).values; cls = a["class"].fillna("").astype(str).values
side = a["somaSide"].fillna("").astype(str).values
d = np.load(os.path.expanduser("~/claude_yilan/fly_multiwork/stage1/out/malecns_sweep.npz"))
cond = [tuple(x) for x in d["cond"]]; M = d["mean"]
k = {x: cond.index(x) for x in [(-1,-1,-1),(2,-1,-1),(-1,2,-1),(-1,-1,2),(2,2,2)]}
base = M[:, k[(-1,-1,-1)]]
grp = np.where(cls == "olfactory", "ORN", np.where(cls == "ALPN", "PN", np.where(cls == "Kenyon_Cell", "KC", typ)))
sg = np.asarray(c.sign)[c.pre]; w = c.raw_count * sg
def ups(target_mask, cond_key, n=10):
    resp = (M[:, k[cond_key]] - base)
    m = target_mask[c.post]
    cnt = collections.defaultdict(float); act = collections.defaultdict(list)
    for p, ww in zip(c.pre[m], w[m]): cnt[grp[p]] += ww
    for g in list(cnt):
        ix = np.where(grp == g)[0]; act[g] = resp[ix].mean()
    # 有效驅動 ≈ 突觸數 × 上游平均變化
    sc = sorted(cnt, key=lambda g: -abs(cnt[g] * act[g]))
    return [(g, int(cnt[g]), round(float(act[g]),1)) for g in sc[:n]]
T = {"MBON11+12": (np.isin(typ, ["MBON11","MBON12"]), (2,-1,-1)),
     "AOTU019_R": ((typ=="AOTU019")&(side=="R"), (-1,2,-1)),
     "DNa02_R(追)": ((typ=="DNa02")&(side=="R"), (-1,2,-1)),
     "DNa02_R(追閃)": ((typ=="DNa02")&(side=="R"), (2,2,2)),
     "DNp01": (typ=="DNp01", (-1,-1,2))}
for nm, (msk, ck) in T.items():
    print(nm, ups(msk, ck))
# 二層：AOTU019 與 DNa02 的上游的上游
for g in ["AOTU019", "DNa02"]:
    pass

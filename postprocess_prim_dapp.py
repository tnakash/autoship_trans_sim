# postprocess_prim_dapp.py
import os
import numpy as np
import pandas as pd

# --- 路径 ---
SIM_NAME = "dapp"
DIR = os.path.join("result","multiple",SIM_NAME)
IN_CSV = os.path.join(DIR, "multiple.csv")

# --- 読み込み ---
df = pd.read_csv(IN_CSV)

# ---- 1) 戦略（政策）とシナリオのIDを整備 ----
df["strategy"] = (
    df["policy_subsidy"].astype(str) + "|" +
    df["policy_reg_year"].astype(str) + "|" +
    df["policy_share"].astype(str) + "|" +
    df["policy_insurance"].astype(str)
)
key_unc_cols = [
    "u_ship_growth","u_TRL_Berth","u_TRL_Navi","u_TRL_Moni",
    "u_crew_cost_growth","u_ope_TRL_factor"
]

# ---- 2) KPI 定義（最小化方向）----
KPI_COLS = {
    "accidents_yr": "Estimated num of Accident (case/year)",
    "crew_2040": "Number of crew at 2040",
    "subsidy_usd": "Subsidy (USD)",
    "intro_full_year": "Introduction Year (Full)",
    "intro_auto_year": "Introduction Year (Auto)",
    "auto_ratio_2040": "Autonomous Ship introduction ratio at 2040 (-)",
    "full_ratio_2040": "Full Autonomous Ship introduction ratio at 2040 (-)",
}
# ここでは最小化でそろえる（大きいほど良い指標は符号を反転）
#   - 導入率は「1−率」をKPIにして“最小化”へ
SENSE = {k:"min" for k in KPI_COLS}
df["_kpi_auto_ratio_gap"] = 1.0 - (df[KPI_COLS["auto_ratio_2040"]] / 100.0)
df["_kpi_full_ratio_gap"] = 1.0 - (df[KPI_COLS["full_ratio_2040"]] / 100.0)

# 後悔計算に使う実KPI列（最小化）
KPI_USE = {
    "accidents_yr": df[KPI_COLS["accidents_yr"]],
    "crew_2040": df[KPI_COLS["crew_2040"]],
    "subsidy_usd": df[KPI_COLS["subsidy_usd"]],
    "intro_full_year": df[KPI_COLS["intro_full_year"]].fillna(9999),
    "intro_auto_year": df[KPI_COLS["intro_auto_year"]].fillna(9999),
    "auto_ratio_gap": df["_kpi_auto_ratio_gap"].clip(0,1),
    "full_ratio_gap": df["_kpi_full_ratio_gap"].clip(0,1),
}

# ---- 3) Minimax 後悔（シナリオごとに最良を基準）----
def minimax_regret(df):
    out_rows = []
    # シナリオの同一性：scenario_id 列で揃えた前提
    for strat, g in df.groupby("strategy"):
        row = {"strategy": strat}
        for name, series in KPI_USE.items():
            # シナリオごとの最小値を引く（= regret）
            tmp = pd.DataFrame({
                "scenario_id": df["scenario_id"],
                "strategy": df["strategy"],
                name: series
            })
            # その KPI の「シナリオ最良（最小）」を取得
            best = tmp.groupby("scenario_id")[name].min()
            # 当該戦略の regret
            rg = tmp[tmp["strategy"]==strat].set_index("scenario_id")[name] - best
            row[f"worst_regret_{name}"] = float(rg.max())
        out_rows.append(row)
    tbl = pd.DataFrame(out_rows)
    # Pareto 非劣フラグ
    cols = [c for c in tbl.columns if c.startswith("worst_regret_")]
    mat = tbl[cols].values
    is_dom = np.zeros(len(tbl), dtype=bool)
    for i in range(len(tbl)):
        for j in range(len(tbl)):
            if i==j: continue
            if np.all(mat[j] <= mat[i]) and np.any(mat[j] < mat[i]):
                is_dom[i] = True; break
    tbl["pareto"] = ~is_dom
    return tbl

worst_tbl = minimax_regret(df)
worst_tbl.to_csv(os.path.join(DIR,"worst_regret_per_kpi.csv"), index=False)

# ベース戦略は「後悔の合計」が最小のもの（自動選定）
sum_regret = worst_tbl.filter(like="worst_regret_").sum(axis=1)
baseline_strategy = worst_tbl.loc[sum_regret.idxmin(),"strategy"]
print(f"[INFO] Baseline strategy auto-selected: {baseline_strategy}")

# ---- 4) PRIM：ベース戦略の“脆弱箱”抽出 ----
# ラベル定義：事故が上位20% or Full導入率が低い(<=50%) or 補助金が上位20% → リスク=1
subB = df[df["strategy"]==baseline_strategy].copy()
q_acc = subB[KPI_COLS["accidents_yr"]].quantile(0.80)
q_sub = subB[KPI_COLS["subsidy_usd"]].quantile(0.80)
risk = (
    (subB[KPI_COLS["accidents_yr"]] >= q_acc) |
    (subB[KPI_COLS["full_ratio_2040"]] <= 50.0) |
    (subB[KPI_COLS["subsidy_usd"]] >= q_sub)
).astype(int).values

X = subB[key_unc_cols].copy()

# --- 簡易PRIM（前に共有した実装の簡略版） ---
def in_box(X, bounds):
    m = np.ones(len(X), dtype=bool)
    for f,(lo,hi) in bounds.items():
        m &= (X[f] >= lo) & (X[f] <= hi)
    return m

def prim_single(X, y, peeling_alpha=0.1, min_mass=0.1, min_density=0.6, max_iters=60):
    bounds = {f:(X[f].min(), X[f].max()) for f in X.columns}
    n = len(X)
    for _ in range(max_iters):
        mask = in_box(X,bounds)
        if mask.sum()/n < min_mass: break
        dens = y[mask].mean() if mask.sum()>0 else 0.0
        best_gain = 0.0; best_bounds=None
        for f in X.columns:
            vals = X.loc[mask,f].values
            qL, qH = np.quantile(vals, peeling_alpha), np.quantile(vals, 1-peeling_alpha)
            # peel lower
            b1 = dict(bounds); b1[f]=(max(bounds[f][0],qL),bounds[f][1])
            m1 = in_box(X,b1)
            if m1.sum()/n >= min_mass:
                d1 = y[m1].mean() if m1.sum()>0 else 0.0
                if d1-dens > best_gain+1e-6: best_gain=d1-dens; best_bounds=b1
            # peel upper
            b2 = dict(bounds); b2[f]=(bounds[f][0],min(bounds[f][1],qH))
            m2 = in_box(X,b2)
            if m2.sum()/n >= min_mass:
                d2 = y[m2].mean() if m2.sum()>0 else 0.0
                if d2-dens > best_gain+1e-6: best_gain=d2-dens; best_bounds=b2
        if best_bounds is None: break
        bounds = best_bounds
    mask = in_box(X,bounds)
    n_in = int(mask.sum())
    if n_in==0: return None
    dens = float(risk[mask].mean())
    mass = n_in/len(X)
    if dens < min_density or mass < min_mass: return None
    return bounds, mass, dens, n_in

# 連続箱を最大3つまで
boxes = []
Xwork = X.copy(); ywork = risk.copy()
for _ in range(3):
    r = prim_single(Xwork, ywork, peeling_alpha=0.1, min_mass=0.08, min_density=0.6)
    if not r: break
    b, mass, dens, nin = r
    m = in_box(Xwork,b)
    boxes.append({"bounds":b,"mass":mass,"density":dens,"n_in":nin})
    # カバーした陽性を除去
    keep = ~(m & (ywork==1))
    Xwork = Xwork.loc[keep].reset_index(drop=True); ywork = ywork[keep]
    if ywork.sum()==0: break

prim_rows = []
for i,box in enumerate(boxes,1):
    conds = [f"{f} in [{lo:.3g}, {hi:.3g}]" for f,(lo,hi) in box["bounds"].items()]
    prim_rows.append({
        "BoxID": f"B{i}",
        "conditions": " & ".join(conds),
        "mass": box["mass"], "density": box["density"], "n_in": box["n_in"]
    })
prim_df = pd.DataFrame(prim_rows)
prim_df.to_csv(os.path.join(DIR,"prim_boxes_baseline.csv"), index=False)

# ---- 5) DAPP：箱ごとの“乗り換え先”を推奨 ----
# 箱に入る行を抽出し、その内部で「加重スコア」が最小の戦略を探す
#   score = 標準化(事故) + 0.3*標準化(補助金) + 0.3*標準化(乗員) + 0.3*標準化(Full導入年)
from math import isfinite

def zscore(x):
    x = np.array(x, dtype=float)
    m, s = np.nanmean(x), np.nanstd(x)+1e-9
    return (x-m)/s

rows=[]
for _,r in prim_df.iterrows():
    # マスク生成
    bounds={}
    for token in r["conditions"].split("&"):
        token = token.strip()
        # "u_TRL_Berth in [x, y]" をパース
        f, rng = token.split(" in ")
        lo, hi = rng.strip("[]").split(",")
        bounds[f.strip()] = (float(lo), float(hi))
    m = np.ones(len(df), dtype=bool)
    for f,(lo,hi) in bounds.items():
        m &= (df[f] >= lo) & (df[f] <= hi)
    sub = df[m].copy()
    if sub.empty:
        continue
    # スコア化
    s_acc = zscore(sub[KPI_COLS["accidents_yr"]])
    s_sub = zscore(sub[KPI_COLS["subsidy_usd"]])
    s_crw = zscore(sub[KPI_COLS["crew_2040"]])
    s_yr  = zscore(sub[KPI_COLS["intro_full_year"]].fillna(9999))
    score = s_acc + 0.3*s_sub + 0.3*s_crw + 0.3*s_yr
    sub = sub.assign(_score=score)
    # baseline以外で最良を選ぶ
    cand = sub[sub["strategy"]!=baseline_strategy]
    if cand.empty:
        continue
    best = cand.groupby("strategy")["_score"].mean().sort_values().index[0]
    rows.append({
        "pathway": f"{baseline_strategy} → {best}",
        "ATP_KPI": "複合（事故/補助金/乗員/導入年）",
        "trigger_threshold": "移動平均で基準超（詳細はsignals参照）",
        "signals": r["conditions"],
        "monitoring_freq": "四半期",
        "data_source": "事故統計・技術TRL・船腹需要・人件費",
        "lead_time": "1–3年（要現場確認）",
        "switch_action": f"{best}へ政策切替",
        "option_traits": "可逆性中／拡張余地大",
        "rough_cost_duration": "（別紙見積）",
        "owner": "関係部局",
        "review_cycle": "年1回"
    })

dapp = pd.DataFrame(rows)
dapp.to_csv(os.path.join(DIR,"dapp_plan.csv"), index=False)

print("[OK] Exported:",
      "worst_regret_per_kpi.csv, prim_boxes_baseline.csv, dapp_plan.csv",
      f"in {DIR}")

# ===== 6) シナリオ・クラスタリング（X+Y：不確実性 + 基準政策のKPI） =====
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score

# 1) 基準政策（baseline_strategy）は既に上で自動選定済み
base = df[df["strategy"] == baseline_strategy].copy()

# 2) 特徴ベクトルを作成（X+Y）
X_cols = key_unc_cols  # 不確実性
# KPI（Y）は “小さいほど良い” に揃えるため、導入率は 1-率 に変換
base["_auto_gap"] = 1.0 - (base[KPI_COLS["auto_ratio_2040"]] / 100.0)
base["_full_gap"] = 1.0 - (base[KPI_COLS["full_ratio_2040"]] / 100.0)

# 「導入年」の NaN は “未導入=大きな年” で埋める（意味づけ一貫）
# 9999 で十分ですが、気になる場合は end_year+1 にしてもOK
base[KPI_COLS["intro_full_year"]] = base[KPI_COLS["intro_full_year"]].fillna(9999)
base[KPI_COLS["intro_auto_year"]] = base[KPI_COLS["intro_auto_year"]].fillna(9999)

Y_cols = [
    KPI_COLS["accidents_yr"],
    KPI_COLS["crew_2040"],
    KPI_COLS["subsidy_usd"],
    KPI_COLS["intro_full_year"],
    KPI_COLS["intro_auto_year"],
    "_auto_gap",
    "_full_gap",
]

feat = base[["scenario_id"] + X_cols + Y_cols].drop_duplicates("scenario_id").reset_index(drop=True)

# 3) NaN/inf の前処理
feat = feat.replace([np.inf, -np.inf], np.nan)

# 4) メディアン補完 → 標準化
imputer = SimpleImputer(strategy="median")
scaler  = StandardScaler()

XY = feat[X_cols + Y_cols].values
XY_imp = imputer.fit_transform(XY)
Z      = scaler.fit_transform(XY_imp)

# 念のためチェック
if np.isnan(Z).any():
    # 極端なケースで全欠損列があると median も NaN になる可能性に備える
    # その場合は 0 で埋める（標準化後なので 0 は列の中心）
    Z = np.nan_to_num(Z, nan=0.0, posinf=0.0, neginf=0.0)

# 5) K の自動選定（3〜8でシルエット最大）
best_k, best_s, best_model = None, -1, None
for k in range(3, 9):
    km = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(Z)
    s = silhouette_score(Z, km.labels_)
    if s > best_s:
        best_k, best_s, best_model = k, s, km

labels  = best_model.labels_
centers = best_model.cluster_centers_
feat["cluster"] = labels

# 6) “メドイド”代表（中心に最も近いシナリオ）を各クラスタで1つ
def nearest_index(points, center):
    d = np.linalg.norm(points - center, axis=1)
    return int(np.argmin(d))

medoids = []
for cl in range(best_k):
    idx = feat.index[feat["cluster"] == cl]
    points = Z[idx, :]
    med_idx_local = nearest_index(points, centers[cl])
    medoids.append(int(feat.loc[idx[med_idx_local], "scenario_id"]))

# 7) 出力
cluster_map = feat[["scenario_id","cluster"]].copy()
cluster_map["is_medoid"] = cluster_map["scenario_id"].isin(medoids)
cluster_map.to_csv(os.path.join(DIR, "scenario_clusters.csv"), index=False)

rep = feat[feat["scenario_id"].isin(medoids)].copy().sort_values("cluster")
rep.to_csv(os.path.join(DIR, "representative_scenarios.csv"), index=False)

print(f"[OK] Scenario clustering: K={best_k}, silhouette={best_s:.3f}")
print(f"[OK] Medoids (scenario_id): {medoids}")

# ===== 7) PRIM箱のカバレッジ補完（代表に箱代表を追加） =====
def scenarios_in_box(box_conditions_df, all_df):
    res = []
    for _, r in box_conditions_df.iterrows():
        bounds = {}
        for token in r["conditions"].split("&"):
            token = token.strip()
            if " in " not in token: 
                continue
            f, rng = token.split(" in ")
            lo, hi = rng.strip("[]").split(",")
            bounds[f.strip()] = (float(lo), float(hi))
        m = np.ones(len(all_df), dtype=bool)
        for f,(lo,hi) in bounds.items():
            if f in all_df.columns:
                m &= (all_df[f] >= lo) & (all_df[f] <= hi)
        scen_in = all_df.loc[m, "scenario_id"].tolist()
        res.append(scen_in)
    return res

box_scenarios = scenarios_in_box(prim_df, feat)
rep_set = set(medoids)
for clist in box_scenarios:
    if not clist:
        continue
    if rep_set.isdisjoint(clist):
        sub = feat[feat["scenario_id"].isin(clist)]
        idx = sub.index
        # 所属クラスタ中心との距離が最小の点を追加
        d = np.array([np.linalg.norm(Z[i,:] - centers[sub.at[i,"cluster"]]) for i in idx])
        add_id = int(sub.loc[idx[np.argmin(d)], "scenario_id"])
        rep_set.add(add_id)

rep_final = feat[feat["scenario_id"].isin(rep_set)].copy().sort_values("cluster")
rep_final.to_csv(os.path.join(DIR, "representative_with_prim_coverage.csv"), index=False)
print(f"[OK] Representatives incl. PRIM coverage: {sorted(list(rep_set))}")

# ===== 8) 可視化（シナリオ・不確実性・後悔・PRIM箱） =====
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from pandas.plotting import scatter_matrix, parallel_coordinates
from sklearn.decomposition import PCA

FIGDIR = os.path.join(DIR, "fig")
os.makedirs(FIGDIR, exist_ok=True)

def _tight_save(fig, path):
    try:
        fig.savefig(path, bbox_inches="tight", dpi=160)
        print(f"[FIG] saved: {path}")
    finally:
        plt.close(fig)

# --- 8-1) Minimax後悔の可視化（KPI別ヒートマップ + サマリ棒）---
try:
    tbl = worst_tbl.copy()
    if not tbl.empty:
        # 列の並びを揃える
        kpi_cols = [c for c in tbl.columns if c.startswith("worst_regret_")]
        # ヒートマップ（戦略×KPI）
        fig, ax = plt.subplots(figsize=(min(14, 2+0.32*len(kpi_cols)), 0.5*len(tbl)+2))
        im = ax.imshow(tbl[kpi_cols].values, aspect="auto")
        ax.set_xticks(range(len(kpi_cols)))
        ax.set_xticklabels([c.replace("worst_regret_", "") for c in kpi_cols], rotation=45, ha="right")
        ax.set_yticks(range(len(tbl)))
        ax.set_yticklabels(tbl["strategy"])
        ax.set_title("Minimax Regret per KPI (lower is better)")
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label("regret")
        # ベースライン枠
        if baseline_strategy in tbl["strategy"].values:
            i = tbl.index[tbl["strategy"]==baseline_strategy][0]
            ax.add_patch(Rectangle((-0.5, i-0.5), len(kpi_cols), 1, fill=False, lw=2.0, ec="tab:red"))
        _tight_save(fig, os.path.join(FIGDIR, "regret_heatmap.png"))

        # サマリ棒（合計後悔）
        s = tbl[kpi_cols].sum(axis=1)
        order = np.argsort(s.values)
        fig, ax = plt.subplots(figsize=(10, max(3, 0.3*len(tbl))))
        ax.barh(range(len(tbl)), s.values[order])
        ax.set_yticks(range(len(tbl)))
        ax.set_yticklabels(tbl["strategy"].values[order])
        ax.set_xlabel("Sum of worst regrets across KPIs")
        ax.set_title("Strategy ranking by total minimax regret")
        # ベースライン強調
        if baseline_strategy in tbl["strategy"].values:
            j = list(tbl["strategy"].values[order]).index(baseline_strategy)
            ax.barh(j, s.values[order][j], edgecolor="tab:red", linewidth=2, fill=False)
        _tight_save(fig, os.path.join(FIGDIR, "regret_summary_bar.png"))
except Exception as e:
    print("[WARN] regret visualization skipped:", e)

# --- 8-2) 不確実性の散布行列（シナリオ全体）---
try:
    if len(key_unc_cols) >= 2 and not df.empty:
        fig = plt.figure(figsize=(1.8*len(key_unc_cols), 1.8*len(key_unc_cols)))
        scatter_matrix(df[key_unc_cols], figsize=(1.8*len(key_unc_cols), 1.8*len(key_unc_cols)), diagonal='hist')
        fig.suptitle("Uncertainties - scatter matrix", y=1.02)
        _tight_save(fig, os.path.join(FIGDIR, "uncertainties_scatter_matrix.png"))
except Exception as e:
    print("[WARN] scatter matrix skipped:", e)

# --- 8-3) クラスタの2次元可視化（PCA）---
try:
    if not feat.empty:
        # Z は上で標準化済み（X+Y）
        pca = PCA(n_components=2, random_state=42)
        XY2 = pca.fit_transform(Z)
        fig, ax = plt.subplots(figsize=(9, 7))
        # 色はデフォルト循環（指定しない）
        for cl in range(best_k):
            idx = np.where(feat["cluster"].values == cl)[0]
            ax.scatter(XY2[idx,0], XY2[idx,1], s=16, alpha=0.6, label=f"Cluster {cl}")
        # メドイド強調
        med_idx = feat["scenario_id"].isin(medoids)
        ax.scatter(XY2[med_idx,0], XY2[med_idx,1], s=80, marker="D", edgecolors="k", linewidths=1.0, label="Medoids")
        ax.set_xlabel("PCA-1")
        ax.set_ylabel("PCA-2")
        ax.set_title("Scenario clusters in PCA space (X + KPI under baseline)")
        ax.legend(loc="best", fontsize=9)
        _tight_save(fig, os.path.join(FIGDIR, "clusters_pca.png"))
except Exception as e:
    print("[WARN] PCA cluster plot skipped:", e)

# --- 8-4) PRIM箱の可視化（代表的2変数ペアに境界を重ね描き）---
# 代表ペアは、不確実性の分散が大きい上位2つを自動選定
try:
    if not prim_df.empty and len(key_unc_cols) >= 2:
        var_sorted = df[key_unc_cols].var().sort_values(ascending=False).index.tolist()
        f1, f2 = var_sorted[:2]
        fig, ax = plt.subplots(figsize=(8, 6))
        # 背景点はベース戦略のシナリオ
        subB = df[df["strategy"]==baseline_strategy]
        ax.scatter(subB[f1], subB[f2], s=12, alpha=0.5, label="Baseline strategy scenarios")
        # 箱を描画
        colors = ["none"]*len(prim_df)  # 塗りつぶし無し
        for i, r in prim_df.iterrows():
            bounds = {}
            for token in r["conditions"].split("&"):
                token = token.strip()
                if " in " not in token: continue
                f, rng = token.split(" in ")
                lo, hi = rng.strip("[]").split(",")
                bounds[f.strip()] = (float(lo), float(hi))
            if f1 in bounds and f2 in bounds:
                (x0,x1),(y0,y1) = bounds[f1], bounds[f2]
                rect = Rectangle((x0,y0), x1-x0, y1-y0, fill=False, linewidth=2)
                ax.add_patch(rect)
                ax.text(x0, y1, r["BoxID"], fontsize=10, va="bottom")
        ax.set_xlabel(f1); ax.set_ylabel(f2)
        ax.set_title("PRIM boxes (projected on two uncertainties)")
        _tight_save(fig, os.path.join(FIGDIR, "prim_boxes_projection.png"))
except Exception as e:
    print("[WARN] PRIM boxes projection skipped:", e)

# --- 8-5) クラスタ別のレーダー/並列座標（不確実性＋KPIギャップの要約）---
# Matplotlib標準の parallel_coordinates を使用（カテゴリ列が必要なので cluster を指定）
try:
    if not feat.empty:
        # 可視化用にいくつかの代表列のみ（多すぎると見づらい）
        vis_cols = key_unc_cols[:min(4, len(key_unc_cols))] + ["_auto_gap","_full_gap"]
        data_pc = feat[vis_cols + ["cluster"]].copy()
        # クラスタごと中央値に要約（線が煩雑になり過ぎないように）
        agg = data_pc.groupby("cluster").median().reset_index()
        # cluster をカテゴリ化
        agg["cluster"] = agg["cluster"].astype(str)
        fig = plt.figure(figsize=(1.8*len(vis_cols)+3, 6))
        parallel_coordinates(agg, "cluster")
        plt.title("Cluster median profiles (selected uncertainties + adoption gaps)")
        plt.xticks(rotation=30, ha="right")
        _tight_save(fig, os.path.join(FIGDIR, "cluster_parallel_coordinates.png"))
except Exception as e:
    print("[WARN] parallel coordinates skipped:", e)

# --- 8-6) PRIM箱のカバレッジ（シナリオ数と密度の棒グラフ）---
try:
    if not prim_df.empty:
        fig, ax = plt.subplots(figsize=(8, max(3, 0.5*len(prim_df))))
        y = np.arange(len(prim_df))
        ax.barh(y, prim_df["n_in"].values, alpha=0.8, label="n_in (scenarios)")
        # 密度は第2軸
        ax2 = ax.twiny()
        ax2.plot(prim_df["density"].values, y, marker="o", linestyle="-", label="density")
        ax.set_yticks(y); ax.set_yticklabels(prim_df["BoxID"])
        ax.set_xlabel("Scenarios covered")
        ax2.set_xlabel("Density (risk share)")
        ax.set_title("PRIM box coverage & density")
        # 凡例
        h1 = Line2D([0],[0], color="C0", lw=8)
        h2 = Line2D([0],[0], marker="o", color="C1")
        ax.legend([h1,h2], ["n_in", "density"], loc="lower right")
        _tight_save(fig, os.path.join(FIGDIR, "prim_coverage_density.png"))
except Exception as e:
    print("[WARN] PRIM coverage plot skipped:", e)

# --- 8-7) 参考：クラスタ規模の棒グラフ ---
try:
    if not feat.empty:
        cnt = feat["cluster"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(range(len(cnt)), cnt.values)
        ax.set_xticks(range(len(cnt)))
        ax.set_xticklabels([f"{i}" for i in cnt.index])
        ax.set_xlabel("Cluster"); ax.set_ylabel("#Scenarios")
        ax.set_title("Cluster sizes")
        _tight_save(fig, os.path.join(FIGDIR, "cluster_sizes.png"))
except Exception as e:
    print("[WARN] cluster size plot skipped:", e)

print("[OK] Visualization exported into:", FIGDIR)

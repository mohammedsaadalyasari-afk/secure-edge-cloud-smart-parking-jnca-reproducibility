from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

BASE = Path(".")
OUT = BASE / "revised_figures_by_rounds"
(OUT / "figures").mkdir(parents=True, exist_ok=True)
(OUT / "tables").mkdir(parents=True, exist_ok=True)
(OUT / "cleaned").mkdir(parents=True, exist_ok=True)

# =========================
# EDIT THESE IF NEEDED
# =========================
LATENCY_TARGET_MS = 250
INFERENCE_TARGET_MS = 1000
TIMEOUT_CUTOFF_MS = 60000
MAX_PHASES = 3
THROUGHPUT_SMOOTHING = 5

# If resource_log.csv does not contain scenario tags, map dates to scenarios here.
# Example:
# RESOURCE_SCENARIO_DATE_MAP = {
#     "2026-02-02": "S1",
#     "2026-02-03": "S2",
#     "2026-02-04": "S3",
#     "2026-02-05": "S4",
# }
RESOURCE_SCENARIO_DATE_MAP = {
    # "2026-02-02": "S1",
    # "2026-02-03": "S2",
    # "2026-02-04": "S3",
    # "2026-02-05": "S4",
}

SCENARIO_ORDER = ["S1", "S2", "S3", "S4"]

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "legend.fontsize": 9,
})


def summarize(df, value_col):
    g = df.groupby(["scenario", "phase"])[value_col]
    s = g.agg(["count", "mean", "median", "std", "min", "max"]).reset_index()
    s["q1"] = g.quantile(0.25).values
    s["q3"] = g.quantile(0.75).values
    s["p90"] = g.quantile(0.90).values
    return s[["scenario", "phase", "count", "mean", "median", "std", "q1", "q3", "p90", "min", "max"]]


def save_csv(df, name):
    df.to_csv(OUT / "tables" / name, index=False)


def assign_phases(df, ts_col="timestamp", scenario_col="scenario", max_phases=3):
    out = df.copy()
    out[ts_col] = pd.to_datetime(out[ts_col], errors="coerce", utc=True)
    out = out.dropna(subset=[ts_col, scenario_col]).copy()
    out["date_key"] = out[ts_col].dt.strftime("%Y-%m-%d")

    phase_frames = []
    for scenario, grp in out.groupby(scenario_col):
        grp = grp.sort_values(ts_col).copy()
        date_counts = grp["date_key"].value_counts().sort_index()

        if len(date_counts) >= 2:
            ordered_dates = list(date_counts.index)[:max_phases]
            phase_map = {d: f"P{i+1}" for i, d in enumerate(ordered_dates)}
            grp["phase"] = grp["date_key"].map(phase_map)
            grp = grp.dropna(subset=["phase"]).copy()
        else:
            n = len(grp)
            if n == 0:
                continue
            bins = np.array_split(np.arange(n), min(max_phases, n))
            phase = np.empty(n, dtype=object)
            for i, idx in enumerate(bins):
                phase[idx] = f"P{i+1}"
            grp["phase"] = phase

        phase_frames.append(grp)

    if not phase_frames:
        out["phase"] = pd.Series(dtype=str)
        return out

    return pd.concat(phase_frames, ignore_index=True)


def get_phase_order(df):
    return [p for p in ["P1", "P2", "P3"] if p in set(df["phase"].dropna().astype(str))]


def grouped_bar_with_error(summary_df, value_col, lo_col, hi_col, title, ylabel, filename_png, filename_pdf, target=None, annotate=True):
    scenarios = SCENARIO_ORDER
    phases = get_phase_order(summary_df)
    if not phases:
        return

    width = 0.24
    x = np.arange(len(scenarios))
    offsets = np.linspace(-width, width, len(phases))

    plt.figure(figsize=(9.5, 5.5))
    all_hi = pd.to_numeric(summary_df[hi_col], errors="coerce")
    bump = 0.01 * np.nanmax(all_hi.to_numpy(dtype=float)) if len(all_hi.dropna()) else 1.0

    for j, ph in enumerate(phases):
        sub = summary_df[summary_df["phase"] == ph].set_index("scenario").reindex(scenarios)
        y = pd.to_numeric(sub[value_col], errors="coerce").to_numpy(dtype=float)
        lo = pd.to_numeric(sub[lo_col], errors="coerce").to_numpy(dtype=float)
        hi = pd.to_numeric(sub[hi_col], errors="coerce").to_numpy(dtype=float)
        yerr = np.vstack([np.maximum(y - lo, 0), np.maximum(hi - y, 0)])
        bars = plt.bar(x + offsets[j], y, width=width, yerr=yerr, capsize=4, label=ph)
        if annotate:
            for b, val in zip(bars, y):
                if pd.notna(val):
                    plt.text(b.get_x() + b.get_width() / 2, b.get_height() + bump, f"{val:.0f}", ha="center", va="bottom", fontsize=8)

    if target is not None:
        plt.axhline(target, linestyle="--", linewidth=1.4, label=f"Target = {target}")
    plt.xticks(x, scenarios)
    plt.xlabel("Scenario")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "figures" / filename_png, dpi=300)
    plt.savefig(OUT / "figures" / filename_pdf)
    plt.close()


def parse_latency():
    lat = pd.read_csv(BASE / "e2e_latency_log.csv")
    lat.columns = ["timestamp", "run_id", "scenario", "mode", "optional", "e2e_latency_ms"]
    lat["scenario"] = lat["scenario"].astype(str).str.extract(r"(S[1-4])", expand=False)
    lat["e2e_latency_ms"] = pd.to_numeric(lat["e2e_latency_ms"], errors="coerce")
    lat = lat.dropna(subset=["scenario", "e2e_latency_ms"]).copy()
    lat = lat[lat["e2e_latency_ms"] > 0].copy()
    return assign_phases(lat, "timestamp", "scenario", MAX_PHASES)


def parse_throughput_log():
    rows = []
    json_pat = re.compile(
        r'\{"timestamp":"([^"]+)","scenario":"(S[1-4])","deployment":"([^"]+)","security":"([^"]+)","msg_rate":([0-9.]+)\}'
    )
    csv_pat = re.compile(r'^([^,]+),(S[1-4]),([^,]+),([^,]+),([0-9.]+)$')

    with open(BASE / "throughput_log.csv", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("timestamp,"):
                continue
            m = json_pat.match(line) or csv_pat.match(line)
            if m:
                rows.append(m.groups())

    th = pd.DataFrame(rows, columns=["timestamp", "scenario", "deployment", "security", "msg_rate"])
    th["msg_rate"] = pd.to_numeric(th["msg_rate"], errors="coerce")
    th = th.dropna(subset=["msg_rate"]).copy()
    return assign_phases(th, "timestamp", "scenario", MAX_PHASES)


def parse_inference():
    ai_path = BASE / "ai_inference_log.csv"
    if ai_path.exists():
        try:
            ai = pd.read_csv(ai_path)
            cols_lower = {c.lower(): c for c in ai.columns}
            if "latency_ms" in cols_lower and "mode" in cols_lower and len(ai) > 0:
                lat_col = cols_lower["latency_ms"]
                mode_col = cols_lower["mode"]
                ts_col = cols_lower.get("timestamp", None)
                ai[lat_col] = pd.to_numeric(ai[lat_col], errors="coerce")
                ai["scenario"] = ai[mode_col].astype(str).str.extract(r"(S[1-4])", expand=False)
                if ts_col is None:
                    ai["timestamp"] = pd.Timestamp("1970-01-01", tz="UTC")
                else:
                    ai["timestamp"] = ai[ts_col]
                inf = ai.rename(columns={lat_col: "inference_latency_ms"})[["timestamp", "scenario", "inference_latency_ms"]]
                inf = inf.dropna().copy()
                inf = inf[inf["inference_latency_ms"] > 0].copy()
                inf = assign_phases(inf, "timestamp", "scenario", MAX_PHASES)
                if len(inf) > 0:
                    return inf, True
        except Exception:
            pass

    metric_files = {
        "S1": "metrics_sim_S1.csv",
        "S2": "metrics_sim_S2.csv",
        "S3": "metrics_hw_S3.csv",
        "S4": "metrics_hw_S4.csv",
    }
    parts = []
    for scenario, fname in metric_files.items():
        df = pd.read_csv(BASE / fname, header=None)
        df[7] = pd.to_numeric(df[7], errors="coerce")
        ts = pd.to_datetime(df[0], errors="coerce", utc=True)
        tmp = pd.DataFrame({
            "timestamp": ts,
            "scenario": scenario,
            "inference_latency_ms": df[7],
        })
        tmp = tmp.dropna().copy()
        tmp = tmp[tmp["inference_latency_ms"] > 0].copy()
        parts.append(tmp)

    inf = pd.concat(parts, ignore_index=True)
    inf = assign_phases(inf, "timestamp", "scenario", MAX_PHASES)
    return inf, False


def parse_resource():
    p = BASE / "resource_log.csv"
    if p.exists():
        rl = pd.read_csv(p, header=None)
        if rl.shape[1] >= 4:
            rl = rl.iloc[:, :4].copy()
            rl.columns = ["timestamp", "scenario", "cpu_pct", "mem_mb"]
            rl["timestamp"] = pd.to_datetime(rl["timestamp"], errors="coerce", utc=True)
            rl["cpu_pct"] = pd.to_numeric(rl["cpu_pct"], errors="coerce")
            rl["mem_mb"] = pd.to_numeric(rl["mem_mb"], errors="coerce")

            if rl["scenario"].astype(str).str.contains(r"S[1-4]").sum() == 0 and len(RESOURCE_SCENARIO_DATE_MAP) > 0:
                rl["date_key"] = rl["timestamp"].dt.strftime("%Y-%m-%d")
                rl["scenario"] = rl["date_key"].map(RESOURCE_SCENARIO_DATE_MAP)

            rl["scenario"] = rl["scenario"].astype(str).str.extract(r"(S[1-4])", expand=False)
            rl = rl.dropna(subset=["timestamp", "scenario", "cpu_pct", "mem_mb"]).copy()
            if len(rl) > 0:
                rl = assign_phases(rl, "timestamp", "scenario", MAX_PHASES)
                return rl

    sp = BASE / "resource_summary_S3_S4.csv"
    if sp.exists():
        rs = pd.read_csv(sp)
        rs.columns = [c.strip() for c in rs.columns]
        scenecol = next((c for c in rs.columns if "scenario" in c.lower()), None)
        cpucol = next((c for c in rs.columns if "cpu" in c.lower() and "mean" in c.lower()), None)
        memcol = next((c for c in rs.columns if "mem" in c.lower() and "mean" in c.lower()), None)
        if scenecol and cpucol and memcol:
            rs = rs.rename(columns={scenecol: "scenario", cpucol: "cpu_pct", memcol: "mem_mb"})
            rs["scenario"] = rs["scenario"].astype(str).str.extract(r"(S[1-4])", expand=False)
            rs["cpu_pct"] = pd.to_numeric(rs["cpu_pct"], errors="coerce")
            rs["mem_mb"] = pd.to_numeric(rs["mem_mb"], errors="coerce")
            rs = rs.dropna(subset=["scenario", "cpu_pct", "mem_mb"]).copy()
            if len(rs) > 0:
                rs["phase"] = "P1"
                rs["timestamp"] = pd.Timestamp("1970-01-01", tz="UTC")
                return rs[["timestamp", "scenario", "phase", "cpu_pct", "mem_mb"]]

    return pd.DataFrame(columns=["timestamp", "scenario", "phase", "cpu_pct", "mem_mb"])


lat = parse_latency()
th = parse_throughput_log()
inf, used_direct_ai = parse_inference()
res = parse_resource()

lat_full = lat.copy()
lat_plot = lat[lat["e2e_latency_ms"] < TIMEOUT_CUTOFF_MS].copy()
lat_timeout = lat[lat["e2e_latency_ms"] >= TIMEOUT_CUTOFF_MS].copy()

inf_full = inf.copy()
inf_plot = inf[inf["inference_latency_ms"] < TIMEOUT_CUTOFF_MS].copy()
inf_timeout = inf[inf["inference_latency_ms"] >= TIMEOUT_CUTOFF_MS].copy()

lat_full.to_csv(OUT / "cleaned" / "latency_full.csv", index=False)
lat_plot.to_csv(OUT / "cleaned" / "latency_mainplot.csv", index=False)
lat_timeout.to_csv(OUT / "cleaned" / "latency_timeout_like.csv", index=False)
th.to_csv(OUT / "cleaned" / "throughput_clean.csv", index=False)
inf_full.to_csv(OUT / "cleaned" / "inference_full.csv", index=False)
inf_plot.to_csv(OUT / "cleaned" / "inference_mainplot.csv", index=False)
inf_timeout.to_csv(OUT / "cleaned" / "inference_timeout_like.csv", index=False)
res.to_csv(OUT / "cleaned" / "resource_clean.csv", index=False)

lat_sum_full = summarize(lat_full, "e2e_latency_ms")
lat_sum_plot = summarize(lat_plot, "e2e_latency_ms")
lat_timeout_counts = lat_full.groupby(["scenario", "phase"]).apply(
    lambda x: (x["e2e_latency_ms"] >= TIMEOUT_CUTOFF_MS).sum(), include_groups=False
).reset_index(name="timeout_like_count")

th_sum = summarize(th, "msg_rate")

inf_sum_full = summarize(inf_full, "inference_latency_ms")
inf_sum_plot = summarize(inf_plot, "inference_latency_ms")
inf_timeout_counts = inf_full.groupby(["scenario", "phase"]).apply(
    lambda x: (x["inference_latency_ms"] >= TIMEOUT_CUTOFF_MS).sum(), include_groups=False
).reset_index(name="timeout_like_count")

save_csv(lat_sum_full, "Table_4_2_latency_by_phase_full.csv")
save_csv(lat_sum_plot, "Table_4_2_latency_by_phase_mainplot.csv")
save_csv(lat_timeout_counts, "Table_4_2_latency_timeout_counts_by_phase.csv")
save_csv(th_sum, "Table_4_3_throughput_by_phase.csv")
save_csv(inf_sum_full, "Table_4_4_inference_by_phase_full.csv")
save_csv(inf_sum_plot, "Table_4_4_inference_by_phase_mainplot.csv")
save_csv(inf_timeout_counts, "Table_4_4_inference_timeout_counts_by_phase.csv")

if len(res) > 0:
    cpu_sum = summarize(res, "cpu_pct")
    mem_sum = summarize(res, "mem_mb")
    save_csv(cpu_sum, "Table_4_4a_cpu_by_phase.csv")
    save_csv(mem_sum, "Table_4_4b_memory_by_phase.csv")

security_overhead = pd.DataFrame({
    "comparison": [
        "Simulation secure over non-secure (S2 vs S1)",
        "Hardware secure over non-secure (S4 vs S3)",
    ],
    "Latency_pct": [
        ((lat_plot.loc[lat_plot["scenario"] == "S2", "e2e_latency_ms"].mean() - lat_plot.loc[lat_plot["scenario"] == "S1", "e2e_latency_ms"].mean()) / lat_plot.loc[lat_plot["scenario"] == "S1", "e2e_latency_ms"].mean()) * 100,
        ((lat_plot.loc[lat_plot["scenario"] == "S4", "e2e_latency_ms"].mean() - lat_plot.loc[lat_plot["scenario"] == "S3", "e2e_latency_ms"].mean()) / lat_plot.loc[lat_plot["scenario"] == "S3", "e2e_latency_ms"].mean()) * 100,
    ],
    "Throughput_pct": [
        ((th.loc[th["scenario"] == "S2", "msg_rate"].mean() - th.loc[th["scenario"] == "S1", "msg_rate"].mean()) / th.loc[th["scenario"] == "S1", "msg_rate"].mean()) * 100,
        ((th.loc[th["scenario"] == "S4", "msg_rate"].mean() - th.loc[th["scenario"] == "S3", "msg_rate"].mean()) / th.loc[th["scenario"] == "S3", "msg_rate"].mean()) * 100,
    ],
    "Inference_pct": [
        ((inf_plot.loc[inf_plot["scenario"] == "S2", "inference_latency_ms"].mean() - inf_plot.loc[inf_plot["scenario"] == "S1", "inference_latency_ms"].mean()) / inf_plot.loc[inf_plot["scenario"] == "S1", "inference_latency_ms"].mean()) * 100,
        ((inf_plot.loc[inf_plot["scenario"] == "S4", "inference_latency_ms"].mean() - inf_plot.loc[inf_plot["scenario"] == "S3", "inference_latency_ms"].mean()) / inf_plot.loc[inf_plot["scenario"] == "S3", "inference_latency_ms"].mean()) * 100,
    ],
})

if len(res) > 0:
    cpu_sim_base = res.loc[res["scenario"] == "S1", "cpu_pct"].mean()
    cpu_hw_base = res.loc[res["scenario"] == "S3", "cpu_pct"].mean()
    mem_sim_base = res.loc[res["scenario"] == "S1", "mem_mb"].mean()
    mem_hw_base = res.loc[res["scenario"] == "S3", "mem_mb"].mean()
    security_overhead["CPU_pct"] = [
        ((res.loc[res["scenario"] == "S2", "cpu_pct"].mean() - cpu_sim_base) / cpu_sim_base) * 100 if pd.notna(cpu_sim_base) and cpu_sim_base != 0 else np.nan,
        ((res.loc[res["scenario"] == "S4", "cpu_pct"].mean() - cpu_hw_base) / cpu_hw_base) * 100 if pd.notna(cpu_hw_base) and cpu_hw_base != 0 else np.nan,
    ]
    security_overhead["Memory_pct"] = [
        ((res.loc[res["scenario"] == "S2", "mem_mb"].mean() - mem_sim_base) / mem_sim_base) * 100 if pd.notna(mem_sim_base) and mem_sim_base != 0 else np.nan,
        ((res.loc[res["scenario"] == "S4", "mem_mb"].mean() - mem_hw_base) / mem_hw_base) * 100 if pd.notna(mem_hw_base) and mem_hw_base != 0 else np.nan,
    ]

save_csv(security_overhead, "Table_4_5_security_overhead_corrected.csv")

grouped_bar_with_error(
    lat_sum_plot,
    "median",
    "q1",
    "q3",
    "Figure 4.1. Median end-to-end latency by scenario and real phase",
    "End-to-end latency (ms)",
    "Fig_4_1_latency_distribution_clean_by_phase.png",
    "Fig_4_1_latency_distribution_clean_by_phase.pdf",
    target=LATENCY_TARGET_MS,
)

fig, axes = plt.subplots(2, 2, figsize=(11, 6.5), sharey=True)
axes = axes.flatten()
phase_order = get_phase_order(th)

for ax, scenario in zip(axes, SCENARIO_ORDER):
    sub = th[th["scenario"] == scenario].copy().sort_values("timestamp")
    if len(sub) > 0:
        for ph in phase_order:
            ph_df = sub[sub["phase"] == ph].copy().reset_index(drop=True)
            if len(ph_df) == 0:
                continue
            ph_df["sample_idx"] = np.arange(1, len(ph_df) + 1)
            ax.plot(ph_df["sample_idx"], ph_df["msg_rate"], alpha=0.35, label=f"{ph} raw")
            sm = ph_df["msg_rate"].rolling(THROUGHPUT_SMOOTHING, min_periods=1).mean()
            ax.plot(ph_df["sample_idx"], sm, linewidth=2, label=f"{ph} mean")
    ax.set_title(f"{scenario}")
    ax.set_xlabel("Sample index")
    ax.set_ylabel("Throughput (msg/s)")
    ax.legend(ncol=2, fontsize=7)

fig.suptitle("Figure 4.2(a). MQTT throughput time-series by scenario and real phase", y=1.02)
plt.tight_layout()
plt.savefig(OUT / "figures" / "Fig_4_2a_throughput_timeseries_clear_by_phase.png", dpi=300, bbox_inches="tight")
plt.savefig(OUT / "figures" / "Fig_4_2a_throughput_timeseries_clear_by_phase.pdf", bbox_inches="tight")
plt.close()

scenarios = SCENARIO_ORDER
phases = get_phase_order(th_sum)
if phases:
    width = 0.24
    x = np.arange(len(scenarios))
    offsets = np.linspace(-width, width, len(phases))
    plt.figure(figsize=(9.5, 5.5))
    for j, ph in enumerate(phases):
        sub = th_sum[th_sum["phase"] == ph].set_index("scenario").reindex(scenarios)
        y = pd.to_numeric(sub["mean"], errors="coerce").to_numpy(dtype=float)
        err = pd.to_numeric(sub["std"], errors="coerce").fillna(0).to_numpy(dtype=float)
        bars = plt.bar(x + offsets[j], y, width=width, yerr=err, capsize=4, label=ph)
        for b, val in zip(bars, y):
            if pd.notna(val):
                plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.03, f"{val:.2f}", ha="center", va="bottom", fontsize=8)
    plt.xticks(x, scenarios)
    plt.xlabel("Scenario")
    plt.ylabel("Average throughput (msg/s)")
    plt.title("Figure 4.2(b). Average throughput by scenario and real phase")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "figures" / "Fig_4_2b_throughput_summary_by_phase.png", dpi=300)
    plt.savefig(OUT / "figures" / "Fig_4_2b_throughput_summary_by_phase.pdf")
    plt.close()

grouped_bar_with_error(
    inf_sum_plot,
    "median",
    "q1",
    "q3",
    f"Figure 4.3. Median cloud inference time by scenario and real phase ({'ai_inference_log.csv' if used_direct_ai else 'metrics fallback'})",
    "AI inference response time (ms)",
    "Fig_4_3_inference_distribution_clean_by_phase.png",
    "Fig_4_3_inference_distribution_clean_by_phase.pdf",
    target=INFERENCE_TARGET_MS,
)

if len(res) > 0:
    cpu_sum = summarize(res, "cpu_pct")
    mem_sum = summarize(res, "mem_mb")
    scenarios = SCENARIO_ORDER
    phases = get_phase_order(cpu_sum)
    if phases:
        width = 0.24
        x = np.arange(len(scenarios))
        offsets = np.linspace(-width, width, len(phases))

        plt.figure(figsize=(9.5, 5.5))
        for j, ph in enumerate(phases):
            sub = cpu_sum[cpu_sum["phase"] == ph].set_index("scenario").reindex(scenarios)
            y = pd.to_numeric(sub["mean"], errors="coerce").to_numpy(dtype=float)
            err = pd.to_numeric(sub["std"], errors="coerce").fillna(0).to_numpy(dtype=float)
            bars = plt.bar(x + offsets[j], y, width=width, yerr=err, capsize=4, label=ph)
            for b, val in zip(bars, y):
                if pd.notna(val):
                    plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3, f"{val:.1f}", ha="center", va="bottom", fontsize=8)
        plt.xticks(x, scenarios)
        plt.xlabel("Scenario")
        plt.ylabel("CPU utilization (%)")
        plt.title("Figure 4.4(a). CPU utilization by scenario and real phase")
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT / "figures" / "Fig_4_4a_cpu_utilization_by_phase.png", dpi=300)
        plt.savefig(OUT / "figures" / "Fig_4_4a_cpu_utilization_by_phase.pdf")
        plt.close()

        plt.figure(figsize=(9.5, 5.5))
        for j, ph in enumerate(phases):
            sub = mem_sum[mem_sum["phase"] == ph].set_index("scenario").reindex(scenarios)
            y = pd.to_numeric(sub["mean"], errors="coerce").to_numpy(dtype=float)
            err = pd.to_numeric(sub["std"], errors="coerce").fillna(0).to_numpy(dtype=float)
            bars = plt.bar(x + offsets[j], y, width=width, yerr=err, capsize=4, label=ph)
            for b, val in zip(bars, y):
                if pd.notna(val):
                    plt.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5, f"{val:.1f}", ha="center", va="bottom", fontsize=8)
        plt.xticks(x, scenarios)
        plt.xlabel("Scenario")
        plt.ylabel("Memory usage (MB)")
        plt.title("Figure 4.4(b). Memory usage by scenario and real phase")
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT / "figures" / "Fig_4_4b_memory_usage_by_phase.png", dpi=300)
        plt.savefig(OUT / "figures" / "Fig_4_4b_memory_usage_by_phase.pdf")
        plt.close()

metric_cols = [c for c in security_overhead.columns if c != "comparison"]
x = np.arange(len(metric_cols))
width = 0.36
sim_vals = security_overhead.iloc[0][metric_cols].values.astype(float)
hw_vals = security_overhead.iloc[1][metric_cols].values.astype(float)

plt.figure(figsize=(10, 5.5))
plt.bar(x - width / 2, sim_vals, width=width, label="Simulation secure over non-secure (S2 vs S1)")
plt.bar(x + width / 2, hw_vals, width=width, label="Hardware secure over non-secure (S4 vs S3)")
plt.xticks(x, metric_cols, rotation=20, ha="right")
plt.ylabel("Relative change (%)")
plt.title("Figure 4.5. Corrected security overhead comparison")
plt.legend()
plt.tight_layout()
plt.savefig(OUT / "figures" / "Fig_4_5_security_overhead_corrected.png", dpi=300)
plt.savefig(OUT / "figures" / "Fig_4_5_security_overhead_corrected.pdf")
plt.close()

print("Done. Outputs are in:", OUT.resolve())

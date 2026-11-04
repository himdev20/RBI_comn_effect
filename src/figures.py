"""Paper figures (PNG, 200 dpi) in outputs/figures/. Each figure is skipped if its inputs
are missing. Palette: fixed categorical order (blue, orange, aqua), thin marks, light grid,
legends for >= 2 series, one y-axis per panel."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src import config

C1, C2, C3, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e"
GOV_CHANGES = [("2018-12-11", "Das"), ("2024-12-11", "Malhotra")]
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e4e3df", "grid.linewidth": 0.6, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 9, "lines.linewidth": 1.6,
                     "legend.frameon": False})


def _save(f, name):
    f.tight_layout(); f.savefig(config.FIGS / name, dpi=200); plt.close(f)


def _gov_lines(ax):
    for d, lab in GOV_CHANGES:
        ax.axvline(pd.Timestamp(d), color=MUTED, lw=0.8, ls=":")
        ax.text(pd.Timestamp(d), ax.get_ylim()[1], f" {lab}", color=MUTED, fontsize=7, va="top")


def run():
    T, P, F = config.TABLES, config.PROC, config.FIGS
    m = pd.read_csv(P / "meeting_level.csv", parse_dates=["meeting_date"]) if (P / "meeting_level.csv").exists() else None
    if m is not None:
        # 1 tone of the committee vs the Governor
        f, ax = plt.subplots(figsize=(8, 3.4))
        ax.plot(m.meeting_date, m.mean_hawk_exgov, "-o", ms=3, color=C1, label="Other five members (mean)")
        ax.plot(m.meeting_date, m.hawk_gov, "-o", ms=3, color=C2, label="Governor")
        ax.axhline(0, color=MUTED, lw=0.6); ax.set_ylabel("hawkishness (-2 dovish ... +2 hawkish)")
        ax.legend(loc="upper left"); _gov_lines(ax); _save(f, "fig1_tone_committee_vs_governor.png")
        # 2 hidden dissent over time
        if m.hidden_signed.notna().any():
            f, axs = plt.subplots(2, 1, figsize=(8, 4.6), sharex=True)
            v = m.hidden_signed.fillna(0)
            axs[0].bar(m.meeting_date, v, width=25, color=np.where(v >= 0, C2, C1))
            axs[0].axhline(0, color=MUTED, lw=0.6); axs[0].set_ylabel("signed hidden dissent\n(+ hawkish lean)")
            axs[1].bar(m.meeting_date, m.hidden_share.fillna(0), width=25, color=C3)
            axs[1].set_ylabel("share of yes-voters\nwith reservations")
            for a in axs:
                _gov_lines(a)
            _save(f, "fig2_hidden_dissent.png")
    # 3 variance test
    p = T / "variance_test.csv"
    if p.exists():
        v = pd.read_csv(p); v = v[v.days.isin(["minutes", "decision"])]
        ten = list(dict.fromkeys(v.tenor)); x = np.arange(len(ten)); w = 0.27
        f, ax = plt.subplots(figsize=(8, 3.4))
        ctrl = v.drop_duplicates("tenor").set_index("tenor").rms_control_bp.reindex(ten)
        ax.bar(x - w, ctrl, w * 0.92, color=C3, label="ordinary days")
        for k, (dname, col, lab) in enumerate([("minutes", C1, "minutes-reaction days"), ("decision", C2, "decision days")]):
            s = v[v.days == dname].set_index("tenor").rms_event_bp.reindex(ten)
            ax.bar(x + k * w, s, w * 0.92, color=col, label=lab)
        ax.set_xticks(x); ax.set_xticklabels(ten, rotation=30); ax.set_ylabel("RMS daily change (bp / %)")
        ax.legend(); _save(f, "fig3_variance_test.png")
    # 4 event-study coefficients
    p = T / "event_study.csv"
    if p.exists():
        r = pd.read_csv(p)
        for var in ["surprise", "hidden_signed"]:
            q = r[(r.spec == ("with_shocks" if (r.spec == "with_shocks").any() else "surprise_hidden")) & (r["var"] == var) & (r.unit == "bp")]
            if q.empty:
                continue
            f, ax = plt.subplots(figsize=(5.8, 3.6))
            for k, (wdw, col) in enumerate([("1", C1), ("2", C2)]):
                s = q[q.window.astype(str) == wdw]
                y = np.arange(len(s)) + (k - .5) * .25
                ax.errorbar(s.coef_bp, y, xerr=1.96 * s.se, fmt="o", ms=5, color=col, capsize=2, lw=1.2,
                            label=f"{wdw}-day window")
            ax.axvline(0, color=MUTED, lw=0.8)
            ax.set_yticks(np.arange(len(s))); ax.set_yticklabels(s.tenor)
            ax.set_xlabel(f"bp per unit of {var} (95% CI, HC3)"); ax.legend()
            _save(f, f"fig4_event_study_{var}.png")
    # 5 decision-day surprises over time
    p = P / "shocks.csv"
    if p.exists():
        s = pd.read_csv(p, parse_dates=["meeting_date"])
        cols = [(c, col, lab) for c, col, lab in [("target", C1, "target factor"), ("path", C2, "path factor"),
                                                   ("mp_rot", C1, "monetary policy shock"), ("cbi_rot", C2, "information shock")] if c in s]
        if cols:
            f, axs = plt.subplots(len(cols), 1, figsize=(8, 1.7 * len(cols)), sharex=True)
            for a, (c, col, lab) in zip(np.atleast_1d(axs), cols):
                a.bar(s.meeting_date, s[c], width=25, color=col); a.axhline(0, color=MUTED, lw=0.6)
                a.set_ylabel("bp"); a.set_title(lab, fontsize=9, loc="left", color=INK)
            _save(f, "fig5_decision_day_surprises.png")
    # 6 placebo
    p = T / "placebo_coefs.csv"
    if p.exists() and (T / "event_study.csv").exists():
        pl = pd.read_csv(p)
        r = pd.read_csv(T / "event_study.csv").query("spec=='surprise' and var=='surprise' and window==1").set_index("tenor")
        cols = [c for c in pl if c in r.index][:6]
        if cols:
            f, axs = plt.subplots(1, len(cols), figsize=(2.6 * len(cols), 2.6), sharey=True)
            for a, t in zip(np.atleast_1d(axs), cols):
                a.hist(pl[t], bins=30, color="#c9c8c3"); a.axvline(r.loc[t, "coef_bp"], color=C2, lw=1.6)
                a.set_title(t, fontsize=8)
            f.suptitle("Coefficient on random ordinary days (grey) vs minutes days (orange)", fontsize=9)
            _save(f, "fig6_placebo.png")
    # 7 validation
    hp, sp = T / "human_sample.csv", P / "scores_llm.csv"
    if hp.exists() and sp.exists():
        h = pd.read_csv(hp).dropna(subset=["human_hawk"]).merge(pd.read_csv(sp), on="statement_id")
        if len(h):
            f, ax = plt.subplots(figsize=(3.8, 3.6))
            j = np.random.default_rng(0).normal(0, .07, (2, len(h)))
            ax.scatter(h.human_hawk + j[0], h.hawk_llm + j[1], s=14, color=C1, alpha=.7)
            ax.plot([-2, 2], [-2, 2], color=MUTED, lw=0.8, ls="--")
            ax.set_xlabel("human code"); ax.set_ylabel("LLM score"); _save(f, "fig7_validation.png")


if __name__ == "__main__":
    run()

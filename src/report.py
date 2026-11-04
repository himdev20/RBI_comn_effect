"""Collect the key results into outputs/summary.md -- the file to share when discussing
results. Contains no raw text, only tables."""
import pandas as pd
from src import config


def _md(df, cols=None, q=None, n=60):
    if df is None or df.empty:
        return "_not available_\n"
    if q:
        df = df.query(q)
    if cols:
        df = df[[c for c in cols if c in df]]
    return df.head(n).round(3).to_markdown(index=False) + "\n"


def _read(name, proc=False):
    p = (config.PROC if proc else config.TABLES) / name
    return pd.read_csv(p) if p.exists() else None


def run():
    parts = ["# Results summary\n"]
    dc = config.TABLES / "data_check.md"
    if dc.exists():
        parts.append(dc.read_text() + "\n")
    m = _read("meeting_level.csv", proc=True)
    if m is not None:
        parts += ["## Sample\n", f"meetings: {len(m)}; surprise measure: {m.surprise_type.iloc[0]}; "
                  f"hidden dissent source: {m.hidden_source.iloc[0]}\n",
                  _md(m[[c for c in ["mean_hawk", "sd_hawk", "surprise", "hidden_signed", "hidden_share", "n_dissent",
                                     "target", "path", "mp_rot", "cbi_rot"] if c in m]].describe().T.reset_index())]
    parts += ["## Text validation (human vs machine)\n", _md(_read("validation.csv"))]
    sd = _read("shock_diagnostics.csv")
    parts += ["## Decision-day surprise series: diagnostics\n", _md(sd)]
    parts += ["## Decision-day validation regressions\n", _md(_read("decision_day.csv"), q="spec in ['target_path','info_split']")]
    parts += ["## Stage A: volatility on minutes days\n", _md(_read("variance_test.csv"))]
    es = _read("event_study.csv")
    parts += ["## Stage B: minutes-day directional effects (1-day window)\n",
              _md(es, ["tenor", "unit", "spec", "var", "coef_bp", "se", "p", "p_randinf", "p_holm_tenors", "n"],
                  q="window==1 and spec in ['surprise','surprise_hidden','with_shocks'] and var in ['surprise','hidden_signed']"),
              "### 2-day window\n",
              _md(es, ["tenor", "unit", "spec", "var", "coef_bp", "se", "p", "p_randinf", "n"],
                  q="window==2 and spec in ['with_shocks'] and var in ['surprise','hidden_signed']")]
    parts += ["## Stage C: uncertainty channel (|dy|)\n", _md(_read("uncertainty.csv"))]
    parts += ["## Placebo: day before release\n", _md(_read("placebo_preday.csv"))]
    parts += ["## Linkage tests (L1, L3, L4)\n", _md(_read("linkage.csv"))]
    parts += ["## Predictability of the next decision\n", _md(_read("predictability.csv"))]
    parts += ["## Subsamples (main spec, 1-day window)\n", _md(_read("subsamples.csv"))]
    out = config.ROOT / "outputs" / "summary.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts))
    print("wrote", out)


if __name__ == "__main__":
    run()

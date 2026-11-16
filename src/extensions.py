"""Extensions added after the literature check (Nov 2026). No new LLM calls: everything
here uses the existing scores, the votes and the raw text.

E1  replicate_mp       Mahambare & Pathak (2021, Econ. Letters) style: next-day yield change on the
                       tone LEVEL of internal and of external members, in their sample (30 meetings
                       to Aug 2021) and after. Reconciles "external tone matters more" with our result.
E2  news_vs_levels     Is it the gap to the Governor (news) or the level of tone? Restriction test.
E3  covid_interaction  surprise x COVID window instead of dropping the window.
E4  alt_measures       Text measures that do not rely on the LLM hawkishness field:
                       (a) supervised TF-IDF ridge trained on members' own votes, leave-one-year-out;
                       (b) other LLM fields (next move, lean); (c) rank and sign of the surprise.
E5  who                Deputy Governor vs Executive Director vs externals, each minus the Governor.
E6  persistence        Cumulative response over days 0..5 after the reaction day.
E7  jackknife          Leave-one-meeting-out and leave-one-year-out range of the headline coefficient.
E8  narrative          Largest surprises with the realised moves, for a narrative check against press reports.
E9  llm_checks         Reads the same-model prompt variant and date-guess probe if they were run.
E10 forecast_policy    EXPLORATORY: do internal/external gaps forecast the repo path beyond OIS?
E11 dissent_forecast   EXPLORATORY, text-free: external members' signed formal dissent -> repo path.
E12 drift              OIS drift from the reaction day to the eve of the next decision.
"""
import re
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from src import config
from src.event_study import ols, rand_inf, controls, holm

warnings.filterwarnings("ignore")
OIS = ["ois_3m", "ois_6m", "ois_1y", "ois_2y", "ois_5y"]
GSEC = ["tbill_91d", "gsec_1y", "gsec_2y", "gsec_5y", "gsec_10y"]
MP_END = "2021-08-31"        # Mahambare & Pathak: 30 meetings to August 2021


def _load():
    m = pd.read_csv(config.PROC / "meeting_level.csv")
    s = pd.read_csv(config.PROC / "member_level.csv")
    return m, s


def _row(r, x, **kw):
    return dict(coef_bp=r.params[x], se=r.bse[x], p=r.pvalues[x], n=int(r.nobs), **kw)


def _tenors(m, cand):
    return [t for t in cand if f"dy1_{t}" in m and m[f"dy1_{t}"].notna().sum() >= 15]


# ----------------------------------------------------------------------------- E1
def replicate_mp(m, s):
    """Tone levels by member group (no Governor benchmark), next-day change, by sample."""
    g = s.assign(grp=np.where(s.member_type.str.lower().str.startswith("ext"), "ext", "int"))
    lv = g.pivot_table(index="meeting_date", columns="grp", values=["hawk_llm", "hawk_dict"], aggfunc="mean")
    lv.columns = [f"{a.replace('hawk_', '')}_{b}" for a, b in lv.columns]
    m = m.merge(lv, left_on="meeting_date", right_index=True, how="left")
    md = pd.to_datetime(m.meeting_date)
    samples = {"to Aug 2021 (M&P sample)": md <= MP_END, "Sep 2021 onwards": md > MP_END, "full": md.notna()}
    ctl = controls(m, "1")
    rows = []
    for sname, mask in samples.items():
        for meas in ["dict", "llm"]:
            for t in _tenors(m, GSEC + ["ois_1y"]):
                xs = [f"{meas}_int", f"{meas}_ext"]
                r, d = ols(m[mask], f"dy1_{t}", xs + ctl)
                if r is None:
                    continue
                dif = r.t_test(f"{xs[1]} - {xs[0]} = 0")
                for x in xs:
                    rows.append(_row(r, x, sample=sname, measure=meas, tenor=t, group=x.split("_")[1],
                                     p_ext_minus_int=float(dif.pvalue)))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "ext_mp_replication.csv", index=False)
    return out


# ----------------------------------------------------------------------------- E2
def news_vs_levels(m):
    """dy = a + b1*members + b2*governor. Pure 'news' implies b2 = -b1; pure 'level' implies b2 = +b1...
    We report b1, b2 and the p-value of H0: b1 + b2 = 0 (gap restriction)."""
    ctl = controls(m, "1"); rows = []
    for t in _tenors(m, OIS + ["gsec_1y", "gsec_10y"]):
        r, d = ols(m, f"dy1_{t}", ["mean_hawk_exgov", "hawk_gov", "target", "path"] + ctl)
        if r is None:
            continue
        p_gap = float(r.t_test("mean_hawk_exgov + hawk_gov = 0").pvalue)
        rows.append(dict(tenor=t, b_members=r.params["mean_hawk_exgov"], p_members=r.pvalues["mean_hawk_exgov"],
                         b_governor=r.params["hawk_gov"], p_governor=r.pvalues["hawk_gov"],
                         p_gap_restriction=p_gap, n=int(r.nobs)))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "ext_news_vs_levels.csv", index=False)
    return out


# ----------------------------------------------------------------------------- E3
def covid_interaction(m):
    md = pd.to_datetime(m.meeting_date)
    m = m.assign(covid=md.between(*config.COVID_WINDOW).astype(float))
    m["surprise_x_covid"] = m.surprise * m.covid
    m["surprise_x_normal"] = m.surprise * (1 - m.covid)
    ctl = controls(m, "1"); rows = []
    for t in _tenors(m, OIS + ["gsec_1y"]):
        xs = ["surprise_x_normal", "surprise_x_covid", "covid", "target", "path"] + ctl
        r, d = ols(m, f"dy1_{t}", xs)
        if r is None:
            continue
        rows.append(dict(tenor=t, b_normal=r.params["surprise_x_normal"], p_normal=r.pvalues["surprise_x_normal"],
                         b_covid=r.params["surprise_x_covid"], p_covid=r.pvalues["surprise_x_covid"],
                         p_equal=float(r.t_test("surprise_x_covid - surprise_x_normal = 0").pvalue),
                         n=int(r.nobs), n_covid=int(d.covid.sum())))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "ext_covid_interaction.csv", index=False)
    return out


# ----------------------------------------------------------------------------- E4
def supervised_scores(s, seed=0):
    """Non-LLM hawkishness: TF-IDF + ridge trained to predict each member's own preferred rate
    direction (own vote; dissenters get their stated preference). Scores are out-of-sample:
    each calendar year is scored by a model trained on all other years. Names, numbers and
    month names are stripped so the model cannot key on who speaks or when."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import Ridge
    lab = s.decision_dir.astype(float).copy()
    dis = (s.explicit_dissent == 1) & s.explicit_dir.notna() & (s.dissent_kind.astype(str).str.contains("rate"))
    lab[dis] = s.explicit_dir[dis]
    names = set(w.lower() for n in s.member.unique() for w in re.findall(r"[A-Za-z]{3,}", n))
    months = "january february march april may june july august september october november december".split()
    stop = names | set(months) | {"per", "cent", "mpc", "shri", "prof", "governor", "deputy"}

    def clean(t):
        t = re.sub(r"[^A-Za-z ]+", " ", str(t).lower())
        return " ".join(w for w in t.split() if w not in stop and len(w) > 2)

    txt = s.statement.map(clean)
    yr = pd.to_datetime(s.meeting_date).dt.year
    out = pd.Series(np.nan, index=s.index)
    for y in sorted(yr.unique()):
        tr, te = yr != y, yr == y
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=4, max_df=0.9, sublinear_tf=True)
        Xtr = vec.fit_transform(txt[tr]); Xte = vec.transform(txt[te])
        out[te] = Ridge(alpha=1.0, random_state=seed).fit(Xtr, lab[tr]).predict(Xte)
    return out.rename("hawk_sup"), lab.rename("pref_dir")


def alt_measures(m, s, B=1000):
    sup, lab = supervised_scores(s)
    s = s.assign(hawk_sup=sup, pref_dir=lab)
    val = dict(n=len(s), corr_sup_llm=s.hawk_sup.corr(s.hawk_llm), corr_sup_dict=s.hawk_sup.corr(s.hawk_dict),
               corr_sup_prefdir_oos=s.hawk_sup.corr(s.pref_dir), corr_llm_prefdir=s.hawk_llm.corr(s.pref_dir),
               corr_dict_prefdir=s.hawk_dict.corr(s.pref_dir))
    # within-meeting validity: do measures rank members inside a meeting the way the LLM does?
    w = s.assign(**{f"{c}_w": s[c] - s.groupby("meeting_date")[c].transform("mean") for c in ["hawk_sup", "hawk_llm", "hawk_dict"]})
    val.update(within_corr_sup_llm=w.hawk_sup_w.corr(w.hawk_llm_w), within_corr_dict_llm=w.hawk_dict_w.corr(w.hawk_llm_w))
    dd = s[s.explicit_dissent == 1]
    if len(dd) > 5:   # do formal rate dissenters deviate from their meeting in the stated direction?
        for c in ["hawk_sup", "hawk_llm", "hawk_dict"]:
            dev = (w.loc[dd.index, f"{c}_w"] * np.sign(dd.explicit_dir)).dropna()
            val[f"dissent_dir_hit_{c.split('_')[1]}"] = float((dev > 0).mean())
    pd.DataFrame([val]).to_csv(config.TABLES / "ext_supervised_validation.csv", index=False)

    def gap(col):
        a = s[s.governor == 0].groupby("meeting_date")[col].mean()
        b = s[s.governor == 1].groupby("meeting_date")[col].mean()
        return a - b

    extra = pd.DataFrame({"surprise_sup": gap("hawk_sup"), "surprise_dict": gap("hawk_dict"),
                          "surprise_lean": gap("lean_llm"),
                          "surprise_next": s.assign(nm=s.next_move_llm.fillna(0)).pipe(
                              lambda z: z[z.governor == 0].groupby("meeting_date").nm.mean() - z[z.governor == 1].groupby("meeting_date").nm.mean())})
    m = m.merge(extra, left_on="meeting_date", right_index=True, how="left")
    m["surprise_rank"] = m.surprise.rank() / m.surprise.notna().sum() - 0.5
    m["surprise_sign"] = np.sign(m.surprise)
    # composite: average of standardised LLM and supervised gaps (two independent readings of the text)
    z = lambda x: (x - x.mean()) / x.std()
    m["surprise_combo"] = (z(m.surprise) + z(m.surprise_sup)) / 2
    ctl = controls(m, "1"); rows = []
    for t in _tenors(m, OIS + ["gsec_1y"]):
        for x in ["surprise", "surprise_sup", "surprise_combo", "surprise_dict", "surprise_lean", "surprise_next",
                  "surprise_rank", "surprise_sign"]:
            r, d = ols(m, f"dy1_{t}", [x, "target", "path"] + ctl)
            if r is None:
                continue
            rows.append(_row(r, x, tenor=t, measure=x, bp_per_sd=r.params[x] * d[x].std(),
                             p_randinf=rand_inf(d, f"dy1_{t}", x, [x, "target", "path"] + ctl, B=B),
                             corr_with_llm_surprise=d[x].corr(m.loc[d.index, "surprise"])))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "ext_alt_measures.csv", index=False)
    m[["meeting_date", "surprise", "surprise_sup", "surprise_combo", "surprise_dict", "surprise_lean", "surprise_next"]].to_csv(
        config.PROC / "alt_surprises.csv", index=False)
    return out, val


# ----------------------------------------------------------------------------- E5
def who(m, s):
    gv = s[s.governor == 1].set_index("meeting_date").hawk_llm
    parts = {}
    for role, nm in [("DG_MP", "dg"), ("ED_MP", "ed"), ("External", "ext")]:
        parts[f"gap_{nm}"] = s[s.role == role].groupby("meeting_date").hawk_llm.mean() - gv
    m = m.merge(pd.DataFrame(parts), left_on="meeting_date", right_index=True, how="left")
    ctl = controls(m, "1"); rows = []
    for t in _tenors(m, OIS + ["gsec_1y"]):
        xs = ["gap_dg", "gap_ed", "gap_ext"]
        r, d = ols(m, f"dy1_{t}", xs + ["target", "path"] + ctl)
        if r is None:
            continue
        p_int_ext = float(r.t_test("0.5*gap_dg + 0.5*gap_ed - gap_ext = 0").pvalue)
        for x in xs:
            rows.append(_row(r, x, tenor=t, who=x, sd=d[x].std(), share_nonzero=float((d[x] != 0).mean()),
                             p_internal_eq_external=p_int_ext))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "ext_who.csv", index=False)
    eq = []
    md = pd.to_datetime(m.meeting_date); cov = md.between(*config.COVID_WINDOW)
    for sname, mask in [("full", md.notna()), ("ex-COVID", ~cov)]:
        for t in _tenors(m, OIS + ["gsec_1y", "gsec_10y"]):
            r, d = ols(m[mask], f"dy1_{t}", ["surprise_int", "surprise_ext", "target", "path"] + ctl)
            if r is not None:
                eq.append(dict(sample=sname, tenor=t, b_internal=r.params["surprise_int"], p_internal=r.pvalues["surprise_int"],
                               b_external=r.params["surprise_ext"], p_external=r.pvalues["surprise_ext"],
                               p_equal=float(r.t_test("surprise_int - surprise_ext = 0").pvalue), n=int(r.nobs)))
    pd.DataFrame(eq).to_csv(config.TABLES / "ext_int_vs_ext.csv", index=False)
    return out


# ----------------------------------------------------------------------------- E6
def persistence(m, K=5):
    D = pd.read_csv(config.PROC / "daily_changes.csv", parse_dates=["date"]).set_index("date").sort_index()
    ev = pd.to_datetime(m.event_date)
    pos = D.index.get_indexer(ev)
    rows = []
    gl = [c for c in ["d_us10y", "d_vix", "d_brent"] if c in D]
    for t in _tenors(m, ["ois_6m", "ois_1y", "ois_2y"]):
        col = D[f"dy_{t}"].values
        for k in range(0, K + 1):
            y = np.array([np.nan if p < 0 or p + k >= len(D) else col[p:p + k + 1].sum() if not np.isnan(col[p:p + k + 1]).any() else np.nan for p in pos])
            d = pd.DataFrame({"y": y, "surprise": m.surprise.values, "target": m.target.values, "path": m.path.values})
            for c in gl:
                v = D[c].values
                d[c] = [np.nan if p < 0 or p + k >= len(D) else np.nansum(v[p:p + k + 1]) for p in pos]
            r, dd = ols(d, "y", ["surprise", "target", "path"] + gl)
            if r is not None:
                rows.append(_row(r, "surprise", tenor=t, days_after=k))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "ext_persistence.csv", index=False)
    return out


# ----------------------------------------------------------------------------- E7
def jackknife(m):
    ctl = controls(m, "1"); rows = []
    yr = pd.to_datetime(m.meeting_date).dt.year
    for t in _tenors(m, ["ois_6m", "ois_1y", "ois_2y"]):
        xs = ["surprise", "target", "path"] + ctl
        r0, d0 = ols(m, f"dy1_{t}", xs)
        loo = [ols(m.drop(index=i), f"dy1_{t}", xs)[0] for i in d0.index]
        b = np.array([r.params["surprise"] for r in loo]); p = np.array([r.pvalues["surprise"] for r in loo])
        ly = [(y, ols(m[yr != y], f"dy1_{t}", xs)[0]) for y in sorted(yr[d0.index].unique())]
        by = np.array([r.params["surprise"] for _, r in ly]); py = np.array([r.pvalues["surprise"] for _, r in ly])
        worst = ly[int(np.argmin(by))][0]
        rows.append(dict(tenor=t, coef=r0.params["surprise"], loo_min=b.min(), loo_max=b.max(), loo_share_p05=float((p < .05).mean()),
                         loo_share_p10=float((p < .10).mean()), lyo_min=by.min(), lyo_max=by.max(),
                         lyo_share_p10=float((py < .10).mean()), lyo_year_of_min=int(worst), n=int(r0.nobs)))
    out = pd.DataFrame(rows)
    out.to_csv(config.TABLES / "ext_jackknife.csv", index=False)
    return out


# ----------------------------------------------------------------------------- E8
def narrative(m, n=8):
    c = ["meeting_date", "release_date", "event_date", "decision_bp", "surprise", "surprise_int", "surprise_ext", "surprise_res",
         "dy1_ois_1y", "dy1_gsec_10y", "d_us10y_1"]
    c = [x for x in c if x in m]
    top = m.reindex(m.surprise.abs().sort_values(ascending=False).index)[c].head(n)
    press = m[m.release_date.isin(["2018-02-21", "2022-10-14", "2026-08-19"])][c]   # press-documented minutes days
    out = pd.concat([top.assign(why="largest |surprise|"), press.assign(why="press-documented")])
    out.to_csv(config.TABLES / "ext_narrative.csv", index=False)
    return out


# ----------------------------------------------------------------------------- E9 (optional inputs)
def llm_checks(m, s, B=1000):
    """Uses outputs of `python run_pipeline.py llm-checks` if present (same model, no second LLM)."""
    rows = []
    p2 = config.PROC / "scores_llm_v2.csv"
    ctl = controls(m, "1")
    if p2.exists():
        v = s.merge(pd.read_csv(p2)[["statement_id", "hawk_llm_v2"]], on="statement_id", how="left")
        ok = v.dropna(subset=["hawk_llm_v2"])
        gap2 = ok[ok.governor == 0].groupby("meeting_date").hawk_llm_v2.mean() - ok[ok.governor == 1].groupby("meeting_date").hawk_llm_v2.mean()
        mm = m.merge(gap2.rename("surprise_v2"), left_on="meeting_date", right_index=True, how="left")
        base = dict(check="prompt variant (no decision context)", n_statements=len(ok),
                    corr_statement=ok.hawk_llm.corr(ok.hawk_llm_v2), exact_agree=float((ok.hawk_llm == ok.hawk_llm_v2).mean()),
                    within1=float(((ok.hawk_llm - ok.hawk_llm_v2).abs() <= 1).mean()), corr_gap=mm.surprise.corr(mm.surprise_v2))
        for t in _tenors(mm, ["ois_6m", "ois_1y", "ois_2y"]):
            r, d = ols(mm, f"dy1_{t}", ["surprise_v2", "target", "path"] + ctl)
            if r is not None:
                rows.append(dict(base, tenor=t, coef_bp=r.params["surprise_v2"], p=r.pvalues["surprise_v2"],
                                 p_randinf=rand_inf(d, f"dy1_{t}", "surprise_v2", ["surprise_v2", "target", "path"] + ctl, B=B), n=int(r.nobs)))
    pdg = config.PROC / "lookahead_date_guess.csv"
    if pdg.exists():
        g = pd.read_csv(pdg).dropna(subset=["guess_year"])
        g["true_year"] = pd.to_datetime(g.meeting_date).dt.year
        g["err"] = g.guess_year - g.true_year
        rng = np.random.default_rng(0)
        chance = np.mean([np.abs(rng.permutation(g.true_year.values) - g.true_year.values).mean() for _ in range(500)])
        hit = g.assign(hit=(g.err == 0).astype(float)).groupby("meeting_date").hit.mean().rename("dated_share")
        mm = m.merge(hit, left_on="meeting_date", right_index=True, how="left")
        mm["s_dated"] = mm.surprise * (mm.dated_share >= 0.5); mm["s_undated"] = mm.surprise * (mm.dated_share < 0.5)
        base = dict(check="date-guess look-ahead probe", n_statements=len(g), exact_year=float((g.err == 0).mean()),
                    within1_year=float((g.err.abs() <= 1).mean()), mae_years=float(g.err.abs().mean()), mae_chance=float(chance),
                    share_meetings_dated=float((mm.dated_share >= 0.5).mean()))
        for t in _tenors(mm, ["ois_6m", "ois_1y", "ois_2y"]):
            r, d = ols(mm, f"dy1_{t}", ["s_dated", "s_undated", "target", "path"] + ctl)
            if r is not None:
                rows.append(dict(base, tenor=t, coef_bp=r.params["s_undated"], p=r.pvalues["s_undated"],
                                 coef_dated=r.params["s_dated"], p_dated=r.pvalues["s_dated"],
                                 p_equal=float(r.t_test("s_dated - s_undated = 0").pvalue), n=int(r.nobs)))
    out = pd.DataFrame(rows)
    if len(out):
        out.to_csv(config.TABLES / "ext_llm_checks.csv", index=False)
    return out


# ----------------------------------------------------------------------------- E10-E12 (exploratory)
def _hac(d, y, xs, h):
    return sm.OLS(d[y], sm.add_constant(d[xs])).fit(cov_type="HAC", cov_kwds={"maxlags": h, "use_correction": True})


def _ri_hac(d, y, xs, x, h, B, seed=1):
    rng = np.random.default_rng(seed); X = sm.add_constant(d[xs])
    f = lambda Z: sm.OLS(d[y], Z).fit(cov_type="HAC", cov_kwds={"maxlags": h, "use_correction": True}).tvalues[x]
    t0 = f(X); c = 0
    for _ in range(B):
        Xb = X.copy(); Xb[x] = rng.permutation(X[x].values); c += abs(f(Xb)) >= abs(t0)
    return c / B


def _forecast_frame(m, s):
    m = m.sort_values("meeting_date").reset_index(drop=True)
    m["spread"] = m.mkt_level_pre - m.repo_after          # 1y OIS on the eve of the minutes minus the repo rate
    sd = s.assign(sd=np.where(s.explicit_dissent == 1, s.explicit_dir, 0.0))
    for g in ["external", "internal"]:
        m = m.merge(sd[sd.member_type == g].groupby("meeting_date").sd.sum().rename(f"{g[:3]}_dissent"),
                    left_on="meeting_date", right_index=True, how="left")
    for h in range(1, 5):
        m[f"cum{h}"] = (m.repo_after.shift(-h) - m.repo_after) * 100
    return m


def _samples(m):
    md = pd.to_datetime(m.meeting_date)
    return {"full": md.notna(), "ex-COVID": ~md.between(*config.COVID_WINDOW),
            "ex-2022 hiking cycle": ~md.between("2022-04-01", "2023-02-28"), "2022 onwards": md >= "2022-01-01"}


def forecast_policy(m, s, B=1000):
    """Do the text gaps forecast the repo path beyond the current decision and the OIS curve?"""
    m = _forecast_frame(m, s); rows = []
    for nm, mask in _samples(m).items():
        for h in [1, 2, 3, 4]:
            xs = ["surprise_int", "surprise_ext", "decision_bp", "spread"]
            d = m[mask][[f"cum{h}"] + xs].dropna()
            if len(d) < 20:
                continue
            r = _hac(d, f"cum{h}", xs, h)
            rows.append(dict(sample=nm, h=h, b_int=r.params["surprise_int"], p_int=r.pvalues["surprise_int"],
                             b_ext=r.params["surprise_ext"], p_ext=r.pvalues["surprise_ext"],
                             p_equal=float(r.t_test("surprise_int - surprise_ext = 0").pvalue),
                             p_randinf_ext=_ri_hac(d, f"cum{h}", xs, "surprise_ext", h, B) if nm == "full" else np.nan, n=len(d)))
    out = pd.DataFrame(rows); out.to_csv(config.TABLES / "ext_forecast_policy.csv", index=False)
    return out


def dissent_forecast(m, s, B=1000):
    """Text-free: net signed formal dissent of external members (votes only) -> future repo path."""
    m = _forecast_frame(m, s); rows = []
    for nm, mask in _samples(m).items():
        for h in [1, 2, 3, 4]:
            xs = ["ext_dissent", "decision_bp", "spread"]
            d = m[mask][[f"cum{h}"] + xs].dropna()
            if len(d) < 20:
                continue
            r = _hac(d, f"cum{h}", xs, h)
            rows.append(dict(sample=nm, h=h, coef_bp=r.params["ext_dissent"], p=r.pvalues["ext_dissent"],
                             p_randinf=_ri_hac(d, f"cum{h}", xs, "ext_dissent", h, B), n=len(d),
                             n_dissent_meetings=int((d.ext_dissent != 0).sum())))
    for h in [3, 4]:                                       # words beyond votes
        xs = ["surprise_ext", "ext_dissent", "decision_bp", "spread"]
        d = m[[f"cum{h}"] + xs].dropna(); r = _hac(d, f"cum{h}", xs, h)
        rows.append(dict(sample="full: words and votes together", h=h, coef_bp=r.params["ext_dissent"], p=r.pvalues["ext_dissent"],
                         coef_words=r.params["surprise_ext"], p_words=r.pvalues["surprise_ext"], n=len(d),
                         corr_words_votes=d.surprise_ext.corr(d.ext_dissent)))
    out = pd.DataFrame(rows); out.to_csv(config.TABLES / "ext_dissent_forecast.csv", index=False)
    return out


def drift(m):
    """If markets under-use the minutes, OIS should drift between the reaction day and the next decision."""
    Y = pd.read_csv(config.YIELDS_CSV, parse_dates=["date"]).set_index("date").sort_index()
    ev, nd = pd.to_datetime(m.event_date), pd.to_datetime(m.next_meeting_date)
    last = lambda o, d, strict: (o[o.index < d] if strict else o[o.index <= d]).iloc[-1] if pd.notna(d) and len(o[o.index <= d]) else np.nan
    rows = []
    us = Y["us10y"].dropna() if "us10y" in Y else None
    for t in [c for c in ["ois_6m", "ois_1y", "ois_2y"] if c in Y]:
        o = Y[t].dropna()
        d = pd.DataFrame({"drift": [(last(o, b, True) - last(o, a, False)) * 100 for a, b in zip(ev, nd)],
                          "surprise_int": m.surprise_int.values, "surprise_ext": m.surprise_ext.values, "decision_bp": m.decision_bp.values})
        xs = ["surprise_int", "surprise_ext", "decision_bp"]
        if us is not None:
            d["us_drift"] = [(last(us, b, True) - last(us, a, False)) * 100 for a, b in zip(ev, nd)]; xs.append("us_drift")
        r, dd = ols(d, "drift", xs)
        if r is not None:
            rows.append(dict(tenor=t, b_int=r.params["surprise_int"], p_int=r.pvalues["surprise_int"],
                             b_ext=r.params["surprise_ext"], p_ext=r.pvalues["surprise_ext"], sd_drift_bp=dd.drift.std(), n=int(r.nobs)))
    out = pd.DataFrame(rows); out.to_csv(config.TABLES / "ext_drift.csv", index=False)
    return out


def run(B=1000):
    m, s = _load()
    res = {"mp": replicate_mp(m, s), "news": news_vs_levels(m), "covid": covid_interaction(m)}
    res["alt"], res["val"] = alt_measures(m, s, B=B)
    res["who"] = who(m, s); res["persist"] = persistence(m); res["jack"] = jackknife(m); res["narr"] = narrative(m)
    res["llm_checks"] = llm_checks(m, s, B=B)
    res["forecast"] = forecast_policy(m, s, B=B); res["dissent"] = dissent_forecast(m, s, B=B); res["drift"] = drift(m)
    return res


if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    r = run()
    for k, v in r.items():
        print(f"\n=== {k} ===")
        print(v.round(3).to_string() if isinstance(v, pd.DataFrame) else v)

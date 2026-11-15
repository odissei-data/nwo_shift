"""Reading Without Looking. Analysis template for submission through Blind SANE.
Groups change ONLY the block between the two lines of dashes.
The script never writes article text. It writes aggregated counts, and any cell
below MIN_CELL articles (or appearances) is suppressed before output.
"""
import os, re
import numpy as np, pandas as pd

# ------------------------------------------------------------------
GROUP    = "group_1"
QUESTION = "attention_over_time"   # attention_over_time | attention_by_outlet | who_speaks | issue_decay
TERMS    = ["kunstmatige intelligentie", "AI", "algoritme", "chatbot", "taalmodel"]
START, END = "2015-01-01", "2025-12-31"
PERIOD   = "month"                 # week | month | year   (attention_over_time)
SPLIT_BY = "gender"                # gender | actor_type | province | top_actors   (who_speaks)
# Ready made term lists
#   migration     ["migratie", "asiel", "vluchteling", "statushouder", "azc"]
#   mental health ["mentale gezondheid", "psychisch", "ggz", "depressie", "burn-out"]
# ------------------------------------------------------------------

MIN_CELL = 10
DATA = os.environ.get("BLINDSANE_DATA", "corpus")
REF  = os.environ.get("BLINDSANE_REFERENCE", "reference")
OUTD = os.environ.get("BLINDSANE_OUTPUT", "output")
os.makedirs(OUTD, exist_ok=True)

def pattern(terms):
    parts = [r"\b" + re.escape(t) + r"\b" if t.isupper() else "(?i:" + re.escape(t) + ")" for t in terms]
    return re.compile("|".join(parts))

def suppress(df, count_cols, dependent=()):
    """blank every row in which a count is below MIN_CELL"""
    df = df.copy()
    low = (df[list(count_cols)] < MIN_CELL).any(axis=1)
    for col in list(count_cols) + list(dependent):
        df[col] = df[col].astype(object).where(~low, "suppressed")
    df.attrs["n_suppressed"] = int(low.sum())
    return df

art = pd.read_csv(f"{DATA}/articles.csv.gz", parse_dates=["date"])
art = art[(art.date >= START) & (art.date <= END)]
pat = pattern(TERMS)
art["hit"] = (art.headline + " " + art.body).str.contains(pat)
outlets = pd.read_csv(f"{DATA}/outlets.csv")

if QUESTION == "attention_over_time":
    freq = {"week": "W-MON", "month": "MS", "year": "YS"}[PERIOD]
    g = art.groupby(pd.Grouper(key="date", freq=freq, closed="left", label="left")).hit.agg(articles="size", matching="sum").reset_index()
    g["share_pct"] = (100 * g.matching / g.articles).round(2)
    res = suppress(g, ["matching"], ["share_pct"])

elif QUESTION == "attention_by_outlet":
    g = art.merge(outlets, on="outlet_id").groupby(["outlet_name", "outlet_type"]).hit.agg(articles="size", matching="sum").reset_index()
    g["share_pct"] = (100 * g.matching / g.articles).round(2)
    res = suppress(g.sort_values("share_pct", ascending=False), ["matching"], ["share_pct"])

elif QUESTION == "who_speaks":
    men = pd.read_csv(f"{DATA}/mentions.csv.gz").merge(pd.read_csv(f"{DATA}/actors.csv"), on="actor_id")
    men = men.merge(art.loc[art.hit, ["article_id"]], on="article_id")
    if SPLIT_BY == "top_actors":
        g = men.groupby(["name", "function", "gender"]).size().rename("appearances").reset_index()
        g = g.sort_values("appearances", ascending=False)
        g["share_of_all_appearances_pct"] = (100 * g.appearances / len(men)).round(1)
        res = suppress(g.head(10), ["appearances"], ["share_of_all_appearances_pct"])
        print(f"People appearing at least once: {g.shape[0]}. Total appearances: {len(men)}.")
    else:
        g = men.groupby(SPLIT_BY).agg(appearances=("role", "size"), quoted=("role", lambda r: (r == "quoted").sum())).reset_index()
        g["share_of_appearances_pct"] = (100 * g.appearances / g.appearances.sum()).round(1)
        g["share_of_quotes_pct"] = (100 * g.quoted / g.quoted.sum()).round(1)
        dep = ["share_of_appearances_pct", "share_of_quotes_pct"]
        if SPLIT_BY == "province":
            pop = pd.read_csv(f"{REF}/population_by_province.csv")
            g = pop[["province", "population_share"]].merge(g, on="province", how="left").fillna({"appearances": 0, "quoted": 0})
            g["population_share_pct"] = (100 * g.pop("population_share")).round(1)
            g["representation_ratio"] = (g.share_of_appearances_pct / g.population_share_pct).round(2)
            dep.append("representation_ratio")
        res = suppress(g.sort_values("appearances", ascending=False), ["appearances", "quoted"], dep)

elif QUESTION == "issue_decay":
    g = art.groupby(pd.Grouper(key="date", freq="W-MON", closed="left", label="left")).hit.agg(articles="size", matching="sum").reset_index()
    g = g[g.articles >= 0.5 * g.articles.median()].reset_index(drop=True)   # drop incomplete weeks
    g["share_pct"] = 100 * g.matching / g.articles
    smooth = g.share_pct.rolling(3, center=True, min_periods=1).mean()       # three week moving average
    k = int(smooth.idxmax()); peak = smooth[k]
    baseline = g.share_pct[max(0, k - 28):max(1, k - 2)].median()
    after = smooth[k:].reset_index(drop=True)
    half = baseline + (peak - baseline) / 2
    below = np.nonzero((after < half).values)[0]
    weeks = int(below[0]) if len(below) else None
    res = pd.DataFrame([{"peak_week": g.date[k].date(), "matching_in_peak_week": int(g.matching[k]),
        "peak_share_pct": round(peak, 2), "baseline_share_pct": round(baseline, 2),
        "weeks_until_halfway_back_to_baseline": weeks if weeks is not None else "not within window"}])
    res = suppress(res, ["matching_in_peak_week"], ["peak_share_pct", "weeks_until_halfway_back_to_baseline"])
else:
    raise SystemExit("Unknown QUESTION")

res.to_csv(f"{OUTD}/{GROUP}_{QUESTION}.csv", index=False)
print(f"{GROUP} | {QUESTION} | terms {TERMS} | {START} to {END}")
print(f"Articles in window: {len(art)}. Matching: {int(art.hit.sum())}. Rows suppressed (cells under {MIN_CELL}): {res.attrs.get('n_suppressed', 0)}")
print(res.to_string(index=False))

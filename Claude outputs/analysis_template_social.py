"""Reading Without Looking. Social media analysis template for submission through Blind SANE.
Groups change ONLY the block between the two lines of dashes.
The script never writes post text. It writes aggregated counts, suppresses any cell below MIN_CELL,
and names accounts only when they belong to public roles.
"""
import os, re
import numpy as np, pandas as pd

# ------------------------------------------------------------------
GROUP    = "group_1"
QUESTION = "attention_over_time"   # attention_over_time | who_posts | who_gets_amplified | issue_decay | news_vs_social
TERMS    = ["migratie", "asiel", "vluchteling", "statushouder", "azc"]
START, END = "2015-01-01", "2025-12-31"
PERIOD   = "month"                 # week | month | year   (attention_over_time)
SPLIT_BY = "account_type"          # account_type | gender | province | created_year | top_accounts   (who_posts, who_gets_amplified)
# Ready made term lists
#   AI            ["kunstmatige intelligentie", "AI", "algoritme", "chatbot", "taalmodel"]
#   mental health ["mentale gezondheid", "mentalegezondheid", "psychisch", "ggz", "depressie", "burn-out"]
# ------------------------------------------------------------------

MIN_CELL = 10
PUBLIC_ROLES = ["politician", "journalist", "expert", "organisation", "news_outlet"]
SOCIAL = os.environ.get("BLINDSANE_SOCIAL", "corpus_social")
NEWS   = os.environ.get("BLINDSANE_DATA", "corpus")
OUTD   = os.environ.get("BLINDSANE_OUTPUT", "output")
os.makedirs(OUTD, exist_ok=True)

def pattern(terms):
    return re.compile("|".join(r"\b" + re.escape(t) + r"\b" if t.isupper() else "(?i:" + re.escape(t) + ")" for t in terms))

def suppress(df, count_cols, dependent=()):
    df = df.copy(); low = (df[list(count_cols)] < MIN_CELL).any(axis=1)
    for col in list(count_cols) + list(dependent): df[col] = df[col].astype(object).where(~low, "suppressed")
    df.attrs["n_suppressed"] = int(low.sum()); return df

def weekly(df, col):
    g = df.groupby(pd.Grouper(key=col, freq="W-MON", closed="left", label="left")).hit.agg(items="size", matching="sum").reset_index()
    return g[g["items"] >= 0.5 * g["items"].median()].reset_index(drop=True)

pat = pattern(TERMS)
posts = pd.read_csv(f"{SOCIAL}/posts.csv.gz", parse_dates=["timestamp"], keep_default_na=False)
posts = posts[(posts.timestamp >= START) & (posts.timestamp < pd.Timestamp(END) + pd.Timedelta(days=1))]
posts["hit"] = posts.text.str.contains(pat)
acc = pd.read_csv(f"{SOCIAL}/accounts.csv", keep_default_na=False)
acc["created_year"] = acc.created.str[:4]

def breakdown(sel, key_col, what):
    m = sel[[key_col]].rename(columns={key_col: "account_id"}).merge(acc, on="account_id")
    if SPLIT_BY == "top_accounts":
        g = m.groupby(["handle", "account_type", "followers"]).size().rename(what).reset_index().sort_values(what, ascending=False)
        g[f"share_of_{what}_pct"] = (100 * g[what] / len(m)).round(2)
        top = g.head(10).astype({"followers": object}); private = ~top.account_type.isin(PUBLIC_ROLES)
        top.loc[private, "handle"] = "private account, not shown"; top.loc[private, "followers"] = "not shown"
        n1 = max(1, int(round(0.01 * g.shape[0])))
        print(f"Accounts involved: {g.shape[0]}. The most active 1 percent ({n1} accounts) account for {100 * g[what].head(n1).sum() / len(m):.1f} percent of {what}.")
        return suppress(top, [what], [f"share_of_{what}_pct"])
    g = m.groupby(SPLIT_BY).agg(**{what: ("account_id", "size"), "accounts": ("account_id", "nunique")}).reset_index()
    g[f"share_of_{what}_pct"] = (100 * g[what] / g[what].sum()).round(1)
    pool = posts if key_col == "account_id" else posts[posts.post_type == "repost"]
    allm = pool[[key_col]].rename(columns={key_col: "account_id"}).merge(acc, on="account_id")
    ref = (100 * allm[SPLIT_BY].value_counts(normalize=True)).round(1).rename("share_in_all_topics_pct")
    g = g.merge(ref, left_on=SPLIT_BY, right_index=True, how="left")
    return suppress(g.sort_values(what, ascending=False), [what, "accounts"], [f"share_of_{what}_pct"])

if QUESTION == "attention_over_time":
    freq = {"week": "W-MON", "month": "MS", "year": "YS"}[PERIOD]
    g = posts.groupby(pd.Grouper(key="timestamp", freq=freq, closed="left", label="left")).hit.agg(posts="size", matching="sum").reset_index()
    g["share_pct"] = (100 * g.matching / g.posts).round(2)
    res = suppress(g.rename(columns={"timestamp": "date"}), ["matching"], ["share_pct"])

elif QUESTION == "who_posts":
    res = breakdown(posts[posts.hit], "account_id", "posts")

elif QUESTION == "who_gets_amplified":
    res = breakdown(posts[posts.hit & (posts.post_type == "repost")], "refers_to_account_id", "times_reposted")

elif QUESTION == "issue_decay":
    g = weekly(posts, "timestamp"); g["share_pct"] = 100 * g.matching / g["items"]
    smooth = g.share_pct.rolling(3, center=True, min_periods=1).mean()
    k = int(smooth.idxmax()); peak = smooth[k]
    baseline = g.share_pct[max(0, k - 28):max(1, k - 2)].median()
    after = smooth[k:].reset_index(drop=True)
    below = np.nonzero((after < baseline + (peak - baseline) / 2).values)[0]
    res = pd.DataFrame([{"peak_week": g.timestamp[k].date(), "matching_in_peak_week": int(g.matching[k]), "peak_share_pct": round(peak, 2),
        "baseline_share_pct": round(baseline, 2), "weeks_until_halfway_back_to_baseline": int(below[0]) if len(below) else "not within window"}])
    res = suppress(res, ["matching_in_peak_week"], ["peak_share_pct", "weeks_until_halfway_back_to_baseline"])

elif QUESTION == "news_vs_social":
    art = pd.read_csv(f"{NEWS}/articles.csv.gz", parse_dates=["date"])
    art = art[(art.date >= START) & (art.date <= END)]
    art["hit"] = (art.headline + " " + art.body).str.contains(pat)
    posts["date"] = posts.timestamp.dt.normalize()
    daily = lambda df: (df.groupby("date").hit.sum().rolling(14, center=True, min_periods=1).sum() / df.groupby("date").hit.size().rolling(14, center=True, min_periods=1).sum())
    n, s = daily(art), daily(posts)
    lags = range(-300, 301)
    cors = pd.Series({L: n.corr(s.shift(L, freq="D")) for L in lags})
    best = int(cors.idxmax())
    direction = "together" if abs(best) < 3 else ("social media first" if best > 0 else "news first")
    res = pd.DataFrame([{"news_articles_matching": int(art.hit.sum()), "news_share_pct": round(100 * art.hit.mean(), 2),
        "social_posts_matching": int(posts.hit.sum()), "social_share_pct": round(100 * posts.hit.mean(), 2),
        "correlation_same_day": round(cors[0], 2), "best_lag_days": abs(best), "who_moves_first": direction, "correlation_at_best_lag": round(cors[best], 2)}])
    res = suppress(res, ["news_articles_matching", "social_posts_matching"], ["news_share_pct", "social_share_pct", "best_lag_days", "who_moves_first"])
else:
    raise SystemExit("Unknown QUESTION")

res.to_csv(f"{OUTD}/{GROUP}_social_{QUESTION}.csv", index=False)
print(f"{GROUP} | social | {QUESTION} | terms {TERMS} | {START} to {END}")
print(f"Posts in window: {len(posts)}. Matching: {int(posts.hit.sum())}. Rows suppressed (cells under {MIN_CELL}): {res.attrs.get('n_suppressed', 0)}")
print(res.to_string(index=False))

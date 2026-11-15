#!/usr/bin/env python3
"""
Reading Without Looking. Public attention in media archives you cannot open
==========================================================================
Runs every analysis request in the groups/ folder of this repository against
a news corpus and a social media corpus, inside Blind SANE.

Usage (Blind SANE):
    python3 script.py -i <input-dir> -o <output-dir> -t <temp-dir>

Outputs (written to <output-dir>):
    report.html                 self-contained report with every group's table and chart
    <group>/table.csv           the aggregated table for that group
    <group>/chart.png           the chart for that group
    run_log.txt                 what ran, what failed and how many cells were suppressed

Output rules built into the script:
    no article or post text is ever written
    any cell based on fewer than MIN_CELL items is suppressed
    private social media accounts are never named
"""
import argparse, base64, configparser, glob, html, io, os, re, sys, time, traceback

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MIN_CELL = 10
PUBLIC_ROLES = ["politician", "journalist", "expert", "organisation", "news_outlet"]
FILES = {"articles": "articles.csv.gz", "mentions": "mentions.csv.gz", "actors": "actors.csv", "outlets": "outlets.csv",
         "posts": "posts.csv.gz", "accounts": "accounts.csv", "population": "population_by_province.csv"}
QUESTIONS = {"news": ["attention_over_time", "attention_by_outlet", "who_speaks", "issue_decay", "news_vs_social"],
             "social": ["attention_over_time", "who_posts", "who_gets_amplified", "issue_decay", "news_vs_social"]}
COLOUR = "#1a5276"; COLOUR2 = "#e67e22"


def parse_args():
    p = argparse.ArgumentParser(description="Reading Without Looking")
    p.add_argument("-i", "--input", default="/source/", help="Input directory containing the corpus files")
    p.add_argument("-o", "--output", default="/results/", help="Output directory for results")
    p.add_argument("-t", "--temp", default="/tmp/", help="Temporary directory")
    p.add_argument("-g", "--groups", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "groups"), help="Directory with the group request files")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Data access
# ---------------------------------------------------------------------------
class Data:
    """Loads each corpus file once, wherever it sits below the input directory."""
    def __init__(self, root):
        self.root, self.cache = root, {}

    def path(self, key):
        hits = glob.glob(os.path.join(self.root, "**", FILES[key]), recursive=True)
        if not hits:
            raise FileNotFoundError("%s not found below %s" % (FILES[key], self.root))
        return hits[0]

    def get(self, key):
        if key not in self.cache:
            if key == "articles":
                df = pd.read_csv(self.path(key), parse_dates=["date"])
                df["text"] = df["headline"].astype(str) + " " + df["body"].astype(str)
                df = df.drop(columns=["headline", "body"])
            elif key == "posts":
                df = pd.read_csv(self.path(key), parse_dates=["timestamp"], keep_default_na=False)
                df["date"] = df["timestamp"].dt.normalize()
            elif key == "accounts":
                df = pd.read_csv(self.path(key), keep_default_na=False)
                df["created_year"] = df["created"].astype(str).str[:4]
            else:
                df = pd.read_csv(self.path(key))
            self.cache[key] = df
        return self.cache[key]


def pattern(terms):
    parts = [r"\b" + re.escape(t) + r"\b" if t.isupper() else "(?i:" + re.escape(t) + ")" for t in terms]
    return re.compile("|".join(parts))


def suppress(df, count_cols, dependent=()):
    """Blank every row in which a count is below MIN_CELL."""
    df = df.copy()
    low = (df[list(count_cols)] < MIN_CELL).any(axis=1)
    for col in list(count_cols) + list(dependent):
        df[col] = df[col].astype(object).where(~low, "suppressed")
    return df, int(low.sum())


def window(df, col, r):
    out = df[(df[col] >= r["start"]) & (df[col] < pd.Timestamp(r["end"]) + pd.Timedelta(days=1))].copy()
    out["hit"] = out["text"].str.contains(pattern(r["terms"]))
    return out


def items(data, r):
    if r["source"] == "news":
        return window(data.get("articles"), "date", r)
    return window(data.get("posts"), "date", r)


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------
def attention_over_time(data, r):
    df = items(data, r)
    freq = {"week": "W-MON", "month": "MS", "year": "YS"}[r["period"]]
    g = df.groupby(pd.Grouper(key="date", freq=freq, closed="left", label="left"))["hit"].agg(["size", "sum"]).reset_index()
    g.columns = ["date", "items", "matching"]
    g["matching"] = g["matching"].astype(int)
    g["share_pct"] = (100 * g["matching"] / g["items"]).round(2)
    g["date"] = g["date"].dt.date
    res, n = suppress(g, ["matching"], ["share_pct"])
    return res, n, ("line", "date", "share_pct", "Share of %s matching the terms (percent)" % unit(r)), []


def attention_by_outlet(data, r):
    df = items(data, r).merge(data.get("outlets"), on="outlet_id")
    g = df.groupby(["outlet_name", "outlet_type"])["hit"].agg(["size", "sum"]).reset_index()
    g.columns = ["outlet_name", "outlet_type", "articles", "matching"]
    g["matching"] = g["matching"].astype(int)
    g["share_pct"] = (100 * g["matching"] / g["articles"]).round(2)
    res, n = suppress(g.sort_values("share_pct", ascending=False), ["matching"], ["share_pct"])
    return res, n, ("bar", "outlet_name", "share_pct", "Share of articles matching the terms (percent)"), []


def who_speaks(data, r):
    art = items(data, r)
    men = data.get("mentions").merge(data.get("actors"), on="actor_id").merge(art.loc[art["hit"], ["article_id"]], on="article_id")
    split, notes = r["split_by"], []
    if split == "top":
        g = men.groupby(["name", "function", "gender"]).size().rename("appearances").reset_index().sort_values("appearances", ascending=False)
        g["share_of_appearances_pct"] = (100 * g["appearances"] / max(len(men), 1)).round(1)
        notes.append("%d people appear at least once, in %d appearances." % (len(g), len(men)))
        res, n = suppress(g.head(10), ["appearances"], ["share_of_appearances_pct"])
        return res, n, ("bar", "name", "share_of_appearances_pct", "Share of all appearances (percent)"), notes
    g = men.groupby(split).agg(appearances=("role", "size"), quoted=("role", lambda x: int((x == "quoted").sum()))).reset_index()
    g["share_of_appearances_pct"] = (100 * g["appearances"] / g["appearances"].sum()).round(1)
    g["share_of_quotes_pct"] = (100 * g["quoted"] / max(g["quoted"].sum(), 1)).round(1)
    dep, ycol, ylabel = ["share_of_appearances_pct", "share_of_quotes_pct"], "share_of_quotes_pct", "Share of quotes (percent)"
    if split == "province":
        pop = data.get("population")[["province", "population_share"]]
        g = pop.merge(g, on="province", how="left").fillna({"appearances": 0, "quoted": 0})
        g["population_share_pct"] = (100 * g.pop("population_share")).round(1)
        g["representation_ratio"] = (g["share_of_appearances_pct"] / g["population_share_pct"]).round(2)
        dep.append("representation_ratio"); ycol, ylabel = "representation_ratio", "Share of appearances divided by share of population"
    res, n = suppress(g.sort_values("appearances", ascending=False), ["appearances", "quoted"], dep)
    return res, n, ("bar", split, ycol, ylabel), notes


def social_breakdown(data, r, amplified):
    posts, acc = items(data, r), data.get("accounts")
    key, what = ("refers_to_account_id", "times_reposted") if amplified else ("account_id", "posts")
    pool = posts[posts["post_type"] == "repost"] if amplified else posts
    m = pool.loc[pool["hit"], [key]].rename(columns={key: "account_id"}).merge(acc, on="account_id")
    allm = pool[[key]].rename(columns={key: "account_id"}).merge(acc, on="account_id")
    split, notes, share = r["split_by"], [], "share_of_%s_pct" % what
    if split == "top":
        g = m.groupby(["handle", "account_type", "followers"]).size().rename(what).reset_index().sort_values(what, ascending=False)
        g[share] = (100 * g[what] / max(len(m), 1)).round(2)
        n1 = max(1, int(round(0.01 * len(g))))
        notes.append("%d accounts are involved. The top 1 percent (%d accounts) account for %.1f percent of %s." % (len(g), n1, 100 * g[what].head(n1).sum() / max(len(m), 1), what.replace("_", " ")))
        top = g.head(10).astype({"followers": object, "handle": object})
        private = ~top["account_type"].isin(PUBLIC_ROLES)
        top.loc[private, "handle"] = ["private account %d, not shown" % (i + 1) for i in range(int(private.sum()))]
        top.loc[private, "followers"] = "not shown"
        res, n = suppress(top, [what], [share])
        return res, n, ("bar", "handle", share, "Share of %s (percent)" % what.replace("_", " ")), notes
    g = m.groupby(split).agg(**{what: ("account_id", "size"), "accounts": ("account_id", "nunique")}).reset_index()
    g[share] = (100 * g[what] / g[what].sum()).round(1)
    ref = (100 * allm[split].value_counts(normalize=True)).round(1).rename("share_in_all_topics_pct")
    g = g.merge(ref, left_on=split, right_index=True, how="left")
    order = split if split == "created_year" else what
    res, n = suppress(g.sort_values(order, ascending=(split == "created_year")), [what, "accounts"], [share])
    return res, n, ("bar2", split, share, "Percent"), notes


def who_posts(data, r): return social_breakdown(data, r, False)
def who_gets_amplified(data, r): return social_breakdown(data, r, True)


def issue_decay(data, r):
    df = items(data, r)
    g = df.groupby(pd.Grouper(key="date", freq="W-MON", closed="left", label="left"))["hit"].agg(["size", "sum"]).reset_index()
    g.columns = ["date", "items", "matching"]
    g = g[g["items"] >= 0.5 * g["items"].median()].reset_index(drop=True)
    g["share_pct"] = 100 * g["matching"] / g["items"]
    smooth = g["share_pct"].rolling(3, center=True, min_periods=1).mean()
    k = int(smooth.idxmax()); peak = smooth[k]
    baseline = g["share_pct"][max(0, k - 28):max(1, k - 2)].median()
    half = baseline + (peak - baseline) / 2
    after = smooth[k:].reset_index(drop=True)
    below = np.nonzero((after < half).values)[0]
    res = pd.DataFrame([{"peak_week": g["date"][k].date(), "matching_in_peak_week": int(g["matching"][k]), "peak_share_pct": round(peak, 2),
                         "baseline_share_pct": round(baseline, 2),
                         "weeks_until_halfway_back_to_baseline": int(below[0]) if len(below) else "not within window"}])
    res, n = suppress(res, ["matching_in_peak_week"], ["peak_share_pct", "weeks_until_halfway_back_to_baseline"])
    safe = g["matching"].rolling(3, center=True, min_periods=1).sum() >= MIN_CELL
    series = pd.DataFrame({"date": g["date"], "y": smooth.where(safe)})
    return res, n, ("series", series, None, "Share of %s matching the terms, three week average (percent)" % unit(r), {"half": half, "baseline": baseline} if n == 0 else {}), []


def news_vs_social(data, r):
    art = window(data.get("articles"), "date", r); posts = window(data.get("posts"), "date", r)
    def daily(df):
        hit = df.groupby("date")["hit"].sum().rolling(14, center=True, min_periods=1).sum()
        tot = df.groupby("date")["hit"].size().rolling(14, center=True, min_periods=1).sum()
        return (100 * hit / tot), hit
    n_s, n_hit = daily(art); s_s, s_hit = daily(posts)
    span = (pd.Timestamp(r["end"]) - pd.Timestamp(r["start"])).days
    maxlag = int(min(300, max(14, span // 3)))
    cors = pd.Series({L: n_s.corr(s_s.shift(L, freq="D")) for L in range(-maxlag, maxlag + 1)})
    best = int(cors.idxmax())
    first = "together" if abs(best) < 3 else ("social media first" if best > 0 else "news first")
    res = pd.DataFrame([{"news_articles_matching": int(art["hit"].sum()), "news_share_pct": round(100 * art["hit"].mean(), 2),
                         "social_posts_matching": int(posts["hit"].sum()), "social_share_pct": round(100 * posts["hit"].mean(), 2),
                         "correlation_same_day": round(cors[0], 2), "best_lag_days": abs(best), "who_moves_first": first,
                         "correlation_at_best_lag": round(cors[best], 2)}])
    res, n = suppress(res, ["news_articles_matching", "social_posts_matching"], ["news_share_pct", "social_share_pct", "best_lag_days", "who_moves_first"])
    series = pd.DataFrame({"news": n_s.where(n_hit >= MIN_CELL), "social media": s_s.where(s_hit >= MIN_CELL)}).reset_index().rename(columns={"index": "date"})
    return res, n, ("series2", series, None, "Share matching the terms, two week average (percent)"), []


def unit(r): return "articles" if r["source"] == "news" else "posts"

RUN = {"attention_over_time": attention_over_time, "attention_by_outlet": attention_by_outlet, "who_speaks": who_speaks, "who_posts": who_posts,
       "who_gets_amplified": who_gets_amplified, "issue_decay": issue_decay, "news_vs_social": news_vs_social}
SPLITS = {"who_speaks": ["gender", "actor_type", "province", "top"], "who_posts": ["account_type", "gender", "province", "created_year", "top"],
          "who_gets_amplified": ["account_type", "gender", "province", "created_year", "top"]}


# ---------------------------------------------------------------------------
# Requests, charts, report
# ---------------------------------------------------------------------------
def read_request(path):
    cp = configparser.ConfigParser(interpolation=None)
    with open(path, encoding="utf-8") as f:
        cp.read_string("[request]\n" + f.read())
    c = cp["request"]
    r = {"group": c.get("group", os.path.splitext(os.path.basename(path))[0]).strip(), "source": c.get("source", "news").strip().lower(),
         "question": c.get("question", "").strip().lower(), "terms": [t.strip() for t in c.get("terms", "").split(",") if t.strip()],
         "start": c.get("start", "2015-01-01").strip(), "end": c.get("end", "2025-12-31").strip(),
         "period": c.get("period", "month").strip().lower(), "split_by": c.get("split_by", "").strip().lower(),
         "folder": re.sub(r"[^A-Za-z0-9_-]+", "_", os.path.splitext(os.path.basename(path))[0])}
    if r["source"] not in QUESTIONS: raise ValueError("source must be news or social")
    if r["question"] not in QUESTIONS[r["source"]]: raise ValueError("question must be one of %s for source %s" % (", ".join(QUESTIONS[r["source"]]), r["source"]))
    if not r["terms"]: raise ValueError("no search terms given")
    if r["period"] not in ("week", "month", "year"): raise ValueError("period must be week, month or year")
    if r["question"] in SPLITS:
        r["split_by"] = r["split_by"] or SPLITS[r["question"]][0]
        if r["split_by"] not in SPLITS[r["question"]]: raise ValueError("split_by must be one of %s" % ", ".join(SPLITS[r["question"]]))
    pd.Timestamp(r["start"]); pd.Timestamp(r["end"])
    return r


def chart(spec, res, path):
    kind = spec[0]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if kind in ("line", "bar", "bar2"):
        d = res[res[spec[2]].astype(str) != "suppressed"].copy()
        d[spec[2]] = d[spec[2]].astype(float)
        if kind == "line":
            ax.plot(pd.to_datetime(d[spec[1]]), d[spec[2]], color=COLOUR, linewidth=1.8)
        else:
            d = d.iloc[::-1]; y = np.arange(len(d))
            if kind == "bar2":
                ax.barh(y + 0.2, d[spec[2]], height=0.4, color=COLOUR, label="matching the terms")
                ax.barh(y - 0.2, d["share_in_all_topics_pct"].astype(float), height=0.4, color="#b0b7bd", label="all topics")
                ax.legend(frameon=False, fontsize=9)
            else:
                ax.barh(y, d[spec[2]], color=COLOUR)
                if spec[2] == "representation_ratio": ax.axvline(1, color="#666", linestyle="--", linewidth=1)
            ax.set_yticks(y); ax.set_yticklabels(d[spec[1]].astype(str))
    elif kind == "series":
        s = spec[1]; ax.plot(s["date"], s["y"], color=COLOUR, linewidth=1.8)
        extra = spec[4] if len(spec) > 4 else {}
        if extra:
            ax.axhline(extra["baseline"], color="#666", linestyle=":", linewidth=1); ax.axhline(extra["half"], color=COLOUR2, linestyle="--", linewidth=1)
    elif kind == "series2":
        s = spec[1]
        ax.plot(s["date"], s["news"], color=COLOUR, linewidth=1.8, label="news"); ax.plot(s["date"], s["social media"], color=COLOUR2, linewidth=1.8, label="social media")
        ax.legend(frameon=False, fontsize=9)
    ax.set_title(spec[3], fontsize=11, loc="left"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    if kind in ("line", "series", "series2"): ax.set_ylim(0, None)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


CSS = """body{font-family:Ubuntu,Arial,sans-serif;max-width:1000px;margin:40px auto;color:#222;padding:0 16px}h1{color:#1a5276}h2{color:#1a5276;margin-top:48px;border-top:1px solid #ddd;padding-top:24px}
p.meta{color:#666;font-size:.9em}table{border-collapse:collapse;font-size:.9em;margin:12px 0}th{background:#1a5276;color:#fff;padding:6px 10px;text-align:left}
td{padding:5px 10px;border-bottom:1px solid #ddd}img{max-width:100%;border:1px solid #ddd;border-radius:4px}.err{color:#a93226}.sup{background:#fdf2e9;padding:6px 10px;border-left:4px solid #e67e22}"""


def main():
    args = parse_args(); t0 = time.time()
    os.makedirs(args.output, exist_ok=True); os.makedirs(args.temp, exist_ok=True)
    files = sorted(glob.glob(os.path.join(args.groups, "*.txt")))
    if not files:
        print("ERROR: no request files found in %s" % args.groups, file=sys.stderr); sys.exit(1)
    data, log, sections = Data(args.input), [], []
    print("Found %d request(s). Processing...\n" % len(files))
    for path in files:
        name = os.path.basename(path); t1 = time.time()
        try:
            r = read_request(path)
            out = RUN[r["question"]](data, r); res, n_sup, spec, notes = out
            gdir = os.path.join(args.output, r["folder"]); os.makedirs(gdir, exist_ok=True)
            res.to_csv(os.path.join(gdir, "table.csv"), index=False)
            chart(spec, res, os.path.join(gdir, "chart.png"))
            with open(os.path.join(gdir, "chart.png"), "rb") as f: img = base64.b64encode(f.read()).decode()
            desc = "%s | %s | terms %s | %s to %s" % (r["source"], r["question"] + ((" by " + r["split_by"]) if r["split_by"] else ""), ", ".join(r["terms"]), r["start"], r["end"])
            sup = '<p class="sup">%d row(s) were suppressed because a count was below %d.</p>' % (n_sup, MIN_CELL) if n_sup else ""
            sections.append("<h2>%s</h2><p class='meta'>%s</p>%s%s%s<img src='data:image/png;base64,%s' alt='chart'>" % (
                html.escape(r["group"]), html.escape(desc), "".join("<p>%s</p>" % html.escape(x) for x in notes), sup, res.to_html(index=False, border=0), img))
            log.append("OK    %s | %s | rows %d | suppressed %d | %.1fs" % (name, desc, len(res), n_sup, time.time() - t1))
        except Exception as e:  # one faulty request must not stop the others
            sections.append("<h2>%s</h2><p class='err'>This request could not be run. %s</p>" % (html.escape(name), html.escape(str(e))))
            log.append("FAIL  %s | %s\n%s" % (name, e, traceback.format_exc()))
        print(log[-1].splitlines()[0])
    page = "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>Reading Without Looking</title><style>%s</style></head><body><h1>Reading Without Looking</h1><p class='meta'>Results approved for release from Blind SANE. Generated %s. No article or post text is included. Counts below %d are suppressed.</p>%s</body></html>" % (
        CSS, pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"), MIN_CELL, "".join(sections))
    with open(os.path.join(args.output, "report.html"), "w", encoding="utf-8") as f: f.write(page)
    with open(os.path.join(args.output, "run_log.txt"), "w", encoding="utf-8") as f: f.write("\n".join(log) + "\n")
    print("\nAll results written to %s in %.0fs" % (args.output, time.time() - t0))


if __name__ == "__main__":
    main()

# Reading Without Looking

Measuring public attention in media archives you cannot open, using Blind SANE.

A workshop analysis designed to run in [SURF's Blind SANE](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/96207010/Working+with+Blind+SANE+as+a+researcher) secure analysis environment. 

The data are two synthetic corpora that are similar to protected collections. One is a news archive of 293,576 Dutch articles from nine fictional outlets. The other is a social media archive of 571,538 short posts from 12,139 fictional accounts. Both cover 2015 to 2025. Everything in them is invented.

## How it works

Each group should write one request file in the `groups/` folder. A single run of `script.py` answers every request and returns one report.

A request file looks like this.

```
group = Group 5. Who posts about migration during a peak?
source = social
question = who_posts
split_by = created_year
terms = migratie, asiel, vluchteling, statushouder, azc
start = 2023-07-01
end = 2023-08-15
```

| Field | Values |
|---|---|
| `group` | any title, shown in the report |
| `source` | `news` or `social` |
| `question` | see the table below |
| `terms` | search terms separated by commas. A term in capitals, such as AI, is matched as a whole word |
| `start`, `end` | dates as YYYY-MM-DD, between 2015-01-01 and 2025-12-31 |
| `period` | `week`, `month` or `year`, for `attention_over_time` |
| `split_by` | see the table below, for the "who" questions |

| Question | Source | What comes back | `split_by` |
|---|---|---|---|
| `attention_over_time` | news, social | share of items matching the terms per period | |
| `attention_by_outlet` | news | share of articles matching the terms per outlet | |
| `who_speaks` | news | who appears and who is quoted in matching articles | `gender`, `actor_type`, `province`, `top` |
| `who_posts` | social | who writes the matching posts | `account_type`, `gender`, `province`, `created_year`, `top` |
| `who_gets_amplified` | social | whose matching posts are reposted | same as `who_posts` |
| `issue_decay` | news, social | the peak week in the window and the weeks until attention is halfway back to baseline | |
| `news_vs_social` | either | whether the press or social media moves first, and by how many days | |

Ready made term lists

- AI. `kunstmatige intelligentie, AI, algoritme, chatbot, taalmodel`
- Migration. `migratie, asiel, vluchteling, statushouder, azc`
- Mental health. `mentale gezondheid, mentalegezondheid, psychisch, ggz, depressie, burn-out`

## What the script produces

- **report.html** is a self-contained report with every group's table and chart
- **<group>/table.csv** and **<group>/chart.png** for each request
- **run_log.txt** lists what ran, what failed and how many cells were suppressed

A faulty request file does not stop the run. It appears in the report with its error message.

## Output rules

- No article or post text is ever written to the results.
- Any cell based on fewer than 10 items is replaced by "suppressed", in tables and in charts.
- Private social media accounts are never named. Only accounts in public roles appear by handle.

## How to use with Blind SANE

1. The data provider: upload the seven corpus files to `/source/` on the Blind SANE VM. These are `articles.csv.gz`, `mentions.csv.gz`, `actors.csv`, `outlets.csv`, `posts.csv.gz`, `accounts.csv` and `population_by_province.csv`. Subfolders are fine.
2. The researcher: when creating the Blind SANE workspace, provide this Git repository as the `blind_python_source`, which is `https://github.com/odissei-data/nwo_shift.git`.
3. The data provider: after the analysis completes, review `/results/` and release it.

| Field | Value |
|---|---|
| `blind_python_source` | `https://github.com/odissei-data/nwo_shift.git` |
| Recommended VM | 8 GB RAM, 2 vCPUs |
| Expected runtime | under one minute for eight requests |

### Running manually

```bash
python3 script.py -i /source/ -o /results/ -t /tmp/
```

### Dependencies

Listed in [`requirements.txt`](requirements.txt), namely `pandas`, `numpy` and `matplotlib`. Tested with Python 3.11 and pandas 2.0, and with Python 3.13 and pandas 3.0.

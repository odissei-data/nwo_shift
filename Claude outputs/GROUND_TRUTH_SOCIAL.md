# Ground truth for the reveal. Social media corpus

Keep this folder outside Blind SANE. Figures are computed from the true labels.

Corpus size is 571,538 posts from 10,667 active accounts (12,139 registered). Originals are 55 percent, reposts 30 percent and replies 15 percent.

## 1. True share per year, social against news (percent)

|   year |   ai news |   ai social |   mental_health news |   mental_health social |   migration news |   migration social |
|-------:|----------:|------------:|---------------------:|-----------------------:|-----------------:|-------------------:|
|   2015 |      0.41 |        0.63 |                 1.24 |                   4.31 |             5.67 |               7.87 |
|   2016 |      0.36 |        0.64 |                 1.47 |                   4.8  |             4.48 |               6.47 |
|   2017 |      0.35 |        0.65 |                 1.61 |                   5.05 |             4.09 |               6.25 |
|   2018 |      0.37 |        0.62 |                 1.74 |                   5.28 |             4.45 |               6.74 |
|   2019 |      0.41 |        0.62 |                 2.06 |                   5.75 |             4.14 |               6.41 |
|   2020 |      0.34 |        0.56 |                 3.3  |                   7.86 |             4.14 |               6.6  |
|   2021 |      0.39 |        0.62 |                 3.65 |                   6.07 |             4    |               6.32 |
|   2022 |      0.7  |        1.28 |                 2.92 |                   6.1  |             4.54 |               7.52 |
|   2023 |      4.11 |        5.11 |                 2.75 |                   6.33 |             4.62 |               7.1  |
|   2024 |      2.95 |        3.31 |                 3.13 |                   6.6  |             4.03 |               6.71 |
|   2025 |      2.61 |        2.91 |                 3.22 |                   6.75 |             4.25 |               7.02 |

## 2. How social media relates to the news (planted)

- AI. Social media moves 10 days before the news at the December 2022 breakthrough and at every AI flash.
- Migration. Both sources move on the same day. Social spikes are twice as high and fade in 40 percent of the time (half-lives of 3 to 18 days against 7 to 45).
- Mental health. Social media gives the topic a much larger share throughout. The broad rise is centred on June 2020 on social media and on February 2021 in the news, a gap of eight months.
- Climate. Social media leads by one day, with the same fast fade.

## 3. Who posts

Share of posts by type of account, per true topic (percent)

| account_type   |   ai |   migration |   mental_health |   all topics |
|:---------------|-----:|------------:|----------------:|-------------:|
| anonymous      | 22.4 |        24   |            20   |         22.3 |
| citizen        | 49.8 |        44.5 |            53   |         51.2 |
| expert         |  4.2 |         3.3 |             4.2 |          3.7 |
| journalist     |  9.8 |        12.2 |             8.4 |          9.4 |
| news_outlet    |  2   |         1.3 |             1.6 |          1.2 |
| organisation   |  6.1 |         9.4 |             6.4 |          6.6 |
| politician     |  5.8 |         5.4 |             6.5 |          5.6 |

Concentration. The most active 1 percent of accounts (107) write 35.2 percent of all posts, and the most active 10 percent write 71.8 percent. Of the 12,139 registered accounts, 1,472 never post.

Women as a share of posts by accounts of known gender (percent)

| true_topic    |   women |
|:--------------|--------:|
| ai            |    42   |
| migration     |    41.9 |
| mental_health |    44.5 |
| all topics    |    42   |

## 4. Who gets amplified

| account_type   |   share of posts |   share of reposts received |
|:---------------|-----------------:|----------------------------:|
| anonymous      |             22.3 |                         8.3 |
| citizen        |             51.2 |                        21.7 |
| expert         |              3.7 |                         7.9 |
| journalist     |              9.4 |                        16.3 |
| news_outlet    |              1.2 |                         4.6 |
| organisation   |              6.6 |                        17.7 |
| politician     |              5.6 |                        23.5 |

Women write 42.0 percent of posts by accounts of known gender and receive 31.9 percent of the reposts that go to such accounts. Their original posts receive 2.21 reposts on average against 3.74 for men. The planted amplification factor is 0.75.

## 5. The coordinated cluster

150 anonymous accounts, all created between January and March 2018, post only about migration and only while a migration spike is under way. They wrote 1,687 posts, which is 4.3 percent of all migration posts but 47.1 percent of migration posts on the days they are active.
They use three fixed slogans, never repost or reply, and receive almost no engagement.
A group finds them by running `who_posts` split by `created_year` inside a spike window such as 2023-07-01 to 2023-08-15. The year 2018 then stands far above its share in all topics.
Active periods follow the spikes of June 2018, September 2020, August 2022, July 2023, May 2024 and June 2025.

## 6. How well the default keyword lists measure the topic on social media

|                            |   ai |   migration |   mental_health |
|:---------------------------|-----:|------------:|----------------:|
| precision                  | 90.9 |        97.8 |            97.3 |
| recall (all posts)         | 63.3 |        65.6 |            63.3 |
| recall (excluding replies) | 74.4 |        76.6 |            74.5 |

Recall is far lower than in the news corpus, where the same lists find about 88 percent. A quarter of original posts on the focal topics use informal wording, and replies carry no topic words at all.
Informal terms that recover missed posts are *bot, robots, computer, geautomatiseerd* for AI, *opvang, Ter Apel, spreidingswet, noodopvang* for migration and *eenzaam, prestatiedruk, helemaal op, praktijkondersteuner* for mental health.

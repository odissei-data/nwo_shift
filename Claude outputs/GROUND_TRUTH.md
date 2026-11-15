# Ground truth for the reveal

Keep this folder outside Blind SANE. All figures below are computed from the true topic labels, not from keyword matches.

Corpus size is 293,576 articles, 553,326 appearances and 2,640 people who appear at least once.

## 1. True share of articles per year (percent)

|   year |   ai |   migration |   mental_health |
|-------:|-----:|------------:|----------------:|
|   2015 | 0.41 |        5.67 |            1.24 |
|   2016 | 0.36 |        4.48 |            1.47 |
|   2017 | 0.35 |        4.09 |            1.61 |
|   2018 | 0.37 |        4.45 |            1.74 |
|   2019 | 0.41 |        4.14 |            2.06 |
|   2020 | 0.34 |        4.14 |            3.3  |
|   2021 | 0.39 |        4    |            3.65 |
|   2022 | 0.7  |        4.54 |            2.92 |
|   2023 | 4.11 |        4.62 |            2.75 |
|   2024 | 2.95 |        4.03 |            3.13 |
|   2025 | 2.61 |        4.25 |            3.22 |

Planted shapes. AI is flat near 0.4 percent until a breakthrough on 2022-12-05, which decays slowly (half-life 400 days) onto a permanently higher plateau.
Migration has a stable baseline with eight spikes. Mental health rises slowly and steadily, with a broad bump centred on early 2021 and a four day blip every 10 October.

## 2. Planted events and their half-lives

| label                   | topic         | onset      |   peak_added_share |   half_life_days |
|:------------------------|:--------------|:-----------|-------------------:|-----------------:|
| ai_flash_2016           | ai            | 2016-03-10 |              0.008 |                7 |
| ai_breakthrough_2022    | ai            | 2022-12-05 |              0.035 |              400 |
| ai_flash_2023           | ai            | 2023-11-18 |              0.02  |               10 |
| ai_flash_2025           | ai            | 2025-02-03 |              0.02  |               14 |
| migration_2015          | migration     | 2015-09-01 |              0.09  |               45 |
| migration_2016          | migration     | 2016-03-18 |              0.03  |               14 |
| migration_2018          | migration     | 2018-06-20 |              0.03  |               10 |
| migration_2020          | migration     | 2020-09-09 |              0.025 |                7 |
| migration_2022          | migration     | 2022-08-24 |              0.06  |               21 |
| migration_2023          | migration     | 2023-07-07 |              0.08  |               18 |
| migration_2024          | migration     | 2024-05-16 |              0.04  |               14 |
| migration_2025          | migration     | 2025-06-03 |              0.06  |               16 |
| climate_flash_2019      | climate       | 2019-09-27 |              0.05  |                5 |
| climate_flash_2021      | climate       | 2021-07-15 |              0.07  |                9 |
| climate_flash_2023      | climate       | 2023-03-20 |              0.045 |                5 |
| housing_slow_2021       | housing       | 2021-09-12 |              0.05  |               60 |
| mental_health_week_2015 | mental_health | 2015-10-10 |              0.012 |                4 |
| mental_health_week_2016 | mental_health | 2016-10-10 |              0.012 |                4 |
| mental_health_week_2017 | mental_health | 2017-10-10 |              0.012 |                4 |
| mental_health_week_2018 | mental_health | 2018-10-10 |              0.012 |                4 |
| mental_health_week_2019 | mental_health | 2019-10-10 |              0.012 |                4 |
| mental_health_week_2020 | mental_health | 2020-10-10 |              0.012 |                4 |
| mental_health_week_2021 | mental_health | 2021-10-10 |              0.012 |                4 |
| mental_health_week_2022 | mental_health | 2022-10-10 |              0.012 |                4 |
| mental_health_week_2023 | mental_health | 2023-10-10 |              0.012 |                4 |
| mental_health_week_2024 | mental_health | 2024-10-10 |              0.012 |                4 |
| mental_health_week_2025 | mental_health | 2025-10-10 |              0.012 |                4 |

The contrast to draw out is between short issues (climate flashes at 5 to 9 days, migration at 7 to 45 days) and slow ones (housing at 60 days, AI at 400 days).

## 3. True share by outlet type (percent)

| outlet_type        |   ai |   migration |   mental_health |
|:-------------------|-----:|------------:|----------------:|
| national_popular   | 0.71 |        6.18 |            1.62 |
| national_quality   | 2.1  |        4.24 |            2.49 |
| online_popular     | 1.04 |        5.78 |            1.74 |
| public_broadcaster | 1.28 |        4.34 |            2.86 |
| regional           | 0.67 |        2.86 |            3.08 |

Popular outlets were given 1.5 to 1.6 times the migration coverage and less AI. Quality outlets were given 1.5 times the AI coverage. Regional outlets were given more mental health and half the AI.

## 4. Who appears (true topic labels)

Share of appearances by type of person (percent)

| actor_type        |   ai |   migration |   mental_health |
|:------------------|-----:|------------:|----------------:|
| advocacy          |  5.6 |        12.7 |            11.6 |
| affected          |  1.9 |         3.2 |             9.6 |
| business          | 37.9 |         1.9 |             0   |
| care_professional |  0   |         0   |            27.7 |
| citizen           |  5.2 |         8.2 |             7.2 |
| expert            | 30.8 |        10.2 |            24.6 |
| official          |  5.9 |        14.8 |             8.3 |
| politician        | 12.6 |        49   |            11   |

Women as a share of appearances and of quotes (percent)

| true_topic    |   appearances |   quotes |
|:--------------|--------------:|---------:|
| ai            |          18.2 |     14.8 |
| migration     |          37.2 |     31.4 |
| mental_health |          50.7 |     44.9 |
| all topics    |          36.4 |     30.5 |

Men are quoted in 55 percent of their appearances and women in 42 percent. People directly affected by the issue are quoted in 25 percent of theirs.

Concentration (percent of appearances going to the most frequent people within each topic)

|                  |    ai |   migration |   mental_health |
|:-----------------|------:|------------:|----------------:|
| top 1 person     |  14.4 |        14.3 |            12.4 |
| top 10 people    |  46   |        45.3 |            42.5 |
| people appearing | 220   |       220   |           220   |

Province of the people who appear, against population (percent, all topics)

| province      |   appearances |   population |   ratio |
|:--------------|--------------:|-------------:|--------:|
| Noord-Holland |         23.75 |        16.57 |    1.43 |
| Zuid-Holland  |         26.14 |        21.36 |    1.22 |
| Utrecht       |          8.57 |         7.79 |    1.1  |
| Friesland     |          3.99 |         3.71 |    1.08 |
| Groningen     |          3.46 |         3.35 |    1.03 |
| Gelderland    |         10.38 |        11.98 |    0.87 |
| Noord-Brabant |         12.41 |        14.74 |    0.84 |
| Overijssel    |          5.25 |         6.65 |    0.79 |
| Limburg       |          4.84 |         6.33 |    0.77 |
| Drenthe       |          0.66 |         2.82 |    0.23 |
| Flevoland     |          0.4  |         2.5  |    0.16 |
| Zeeland       |          0.15 |         2.2  |    0.07 |

Drenthe, Zeeland and Flevoland together hold 7.5 percent of the population. They account for 0.8 percent of appearances in national outlets and 2.1 percent in regional outlets.

## 5. How well the default keyword lists measure the topic

|                 |    ai |   migration |   mental_health |
|:----------------|------:|------------:|----------------:|
| precision       |  85.4 |        95.3 |            92.7 |
| recall          |  88.4 |        88.1 |            88.2 |
| false positives | 521   |       562   |           502   |
| missed articles | 402   |      1544   |           854   |

Around 12 percent of articles on each focal topic were written without any term from the default list, and 0.6 percent of articles on other topics contain a stray focal term.
Terms that recover the missed articles are *software, systeem, techniek, automatisering* for AI, *opvang, nieuwkomers, noodopvang* for migration and *prestatiedruk, eenzaam, jeugdhulp, hulpverleners, vertrouwenspersoon* for mental health.
The AI list is the weakest before 2023, because a small topic is easily swamped by stray mentions. That makes a good moment in the discussion on trusting a measure nobody can inspect.

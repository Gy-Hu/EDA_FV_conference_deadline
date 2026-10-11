# EDA and Formal Verification deadlines countdown

Based on [ai-deadlines](https://aideadlin.es) by @abshkdz

## Local development

Install dependencies:

```bash
bundle install
```

Build the site locally:

```bash
bundle exec jekyll build
```

Serve the site locally:

```bash
bundle exec jekyll serve
```

## 会议标签

标签由维护者配置，访客只读；仅展示有来源的信息。标签含义见网页底部，
显示规则在 `_data/tag_definitions.yml`，各会议公开标签在 `_data/conferences.yml`。

费用、投稿量和接收率的具体数字只保存在本地 `.local-research/ledger.json`，
网页仅显示颜色。更新台账后运行：

```bash
python3 scripts/render-conference-research.py
```

脚本同步公开标签，并生成 `.local-research/` 内的数值核对表和论文集核查报告。
该目录不提交、不发布，需要单独备份。详细维护备注保存在其中的
`tag-maintenance-notes.txt`；不要只改会被生成器覆盖的公开标签。

验证：`node --test tests/tag-model.test.js`。

## Adding/updating a conference

* Read the data format description below. **Note that the timezone format sign is inverted** (e.g., UTC+7 is written as `Etc/GMT-7`). It's [not a bug][0]. I hate this format too. I'd be happy to move to a different timezone JavaScript library that uses a friendlier format, but I don't have time for that.
* Update `_data/conferences.yml`. You can do that on Github or locally after forking the repo.
* Send a pull request

### Conference entry record

Example record:

```
- name: ICCAD
  year: 2023
  date: "October 29 - November 2"
  description: The International Conference on Computer-Aided Design
  link: https://iccad.com/
  deadline: ["2023-05-15 23:59"]
  place: San Francisco, California, USA
  tags: [EDA]
```

Descriptions of the fields:

| Field name    | Description                                                 |
|---------------|-------------------------------------------------------------|
| `name`\*      | Short conference name, including the cycle label when applicable, without year                         |
| `year`\*      | Year the conference is happening                            |
| `description` | Description, or long name                                   |
| `link`\*      | URL to the conference home page                             |
| `deadline`\*  | One-item list: abstract deadline, or submission deadline if no separate abstract deadline exists |
| `timezone`    | Timezone in [tz][1] format. By default is UTC-12 ([AoE][2]) |
| `date`        | When the conference is happening                            |
| `place`       | Where the conference is happening                           |
| `tags`        | One or multiple tags: `SEC`, `PRIV`, or `CRYPTO`            |

Fields marked with asterisk (\*) are required.


### Deadline format

Each conference or submission-cycle entry contains exactly one *deadline*. Use
that cycle's abstract deadline when one exists; otherwise use its paper submission
deadline.
Always display this date as `Abstract deadline`, including when the underlying
date is a paper submission, ARR submission, or mandatory paper registration
deadline. Do not add per-conference display labels.
Check each deadline against that edition's official CFP, date page, or submission
system. Use the latest extension for the same submission stage. Do not substitute
an independent extended-abstract, demo, workshop, camera-ready, or author
registration deadline for the main research-paper abstract deadline.

Supported formats:

1. The simplest option: a date and time in ISO format. Example: `["2017-08-19 23:59"]` (Note that you need to wrap even a single deadline in a list).
2. If a deadline is rolling, you can use a template date, just substitute the
   year with `%y` and the year before the conference with `%Y`. Example:
   `["%y-01-15 23:59"]` means there is a deadline on the 15th January in the
   same year as the conference.
On the page, all deadlines are displayed in the viewer's local time.

When the next edition has no published submission deadline, retain the previous
edition's complete record (year, dates, location, URL, and deadline) instead of
using `TBA` or projecting its deadline into the next year.
For conferences with multiple main research-paper submission cycles, create a
separate YAML entry for every officially dated cycle of the retained edition,
including past cycles. Include the official cycle label in `name` (for example,
`ASPLOS April`, `ASPLOS September`, `OOPSLA Round 1`, or `CHES Issue 2`). Keep the
conference year, event dates, location, URL, and tags consistent across cycles;
verify the deadline and time zone separately for each cycle. Each entry gets its
own card and is sorted by its own deadline. Do not collapse cycles into the next
open cycle or the last closed one.
Only split independent opportunities for new submissions. Abstract/full-paper
stages, extensions, rebuttals, revisions, and artifact evaluation are not separate
submission cycles. For ARR-based conferences, retain the conference's specified
latest eligible ARR submission deadline; generic earlier ARR cycles and later
commitment rounds are not additional main-paper submission cycles.
If the latest edition has no published submission date, retain the previous
edition as a reference; do not invent a date or project last year's date forward.
A published calendar date is sufficient to keep the current edition. Missing
hours or time zones alone are not a reason to roll back the edition; use the
existing 23:59 AoE default unless an official source specifies otherwise.
Keep the edition's year, dates, location, URL, and deadline together. Do not add attendance policies, registration details, or
speculative-deadline explanations to conference cards. Keep source citations in
YAML comments instead.

*Note:* If the deadline hour is `{h}:00`, it will be automatically translated into `{h-1}:59:59` to avoid pain and confusion when it happens to be midnight in local time.

### Timezones

The timezone is specified in [tz format][1]. Unlike abbreviations (e.g. EST), these are un-ambiguous. Here are tz codes for some common timezones:

| Common name                   | tz                                                                 |
|-------------------------------|--------------------------------------------------------------------|
| UTC                           | `Etc/UTC`                                                          |
| America Pacific Time          | `America/Los_Angeles`                                              |
| Pacific Standard Time (UTC-8) | `Etc/GMT+8` (Yes, the sign is inverted for some weird reason)      |
| America Eastern Time          | `America/New_York`                                                 |
| Eastern Standard Time (UTC-5) | `Etc/GMT+5`                                                        |
| American Samoa Time (UTC-11)  | `Pacific/Samoa` or `Etc/GMT+11`. This timezone does not use DST.   |
| Aleutian Islands              | `America/Adak`                                                     |

[0]: https://momentjs.com/timezone/docs/#/zone-object/offset/
[1]: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
[2]: https://www.timeanddate.com/time/zones/aoe

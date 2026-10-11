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

## 会议标签（维护者配置）

访客只能查看标签，没有标签编辑或筛选入口。仅展示有来源且已核实的标签；
没有资料就不填，页面不显示未知、待补充、示例或占位。

数值指标的完整记录保存在 `.local-research/ledger.json`；运行
`python3 scripts/render-conference-research.py` 更新可直接打开的本地核对表
`.local-research/conference-metrics-private.html` 和公开的会议标签。
该目录已通过本仓库 `.git/info/exclude` 忽略，并被 Jekyll `exclude` 排除。
不要强制添加或发布此目录。所有改动保持未提交。

私人记录的 `metrics` 包含注册费、投稿量和接收率的 `value`、`year`、`source`、
`note`，推导数据另附 `calculation`；只有 `status: verified` 的记录才用于标签。
费用必须为普通作者适用价格，包含 `currency` 和 `audience: regular_author`，
备注注明早鸟、会员、论文附加费、税费、参会方式等口径。历史统计标注实际数据年份，
不作为当前届次的预测。各会议 `review` 字段记录已核查项目和未能确认的原因。

公开 `_data/conferences.yml` 中的数值指标只保存五档颜色 `tone`、数据年份和来源链接，
不包含原始数值、计算过程或私人备注。五档颜色按 `_data/tag_definitions.yml`
中的显示范围映射为绿、黄绿、黄、橙、红：注册费越高越红，投稿量越多越红；
接收率使用 `reverse: true`，越低越红、越高越绿。费用按币种各自映射，不进行汇率换算；
未配置范围的币种为灰色。这些显示范围是可调整的设计参数，不是费用是否便宜的事实判断。
网页显示“Registration Fee”“Submissions”“Acceptance Rate”及年份，不在文字、tooltip 或 data 属性中输出具体数值。

其余标签保存在私人台账的 `labels`，再写入公开配置：

- `no_in_person`：仅在当届政策明确允许投稿作者不线下参会时设置 `value: true`。
- `tool_paper` / `short_paper`：`value: true` 且 `proceedings: true`，须有当届的
  类型和归档出版证据；不把非归档演示或随意较短的普通论文当作独立类型。
- `core_ranking` / `ccf_ranking`：保存核实的 `value`、榜单年份和官方来源。
  缺失不推断 Unranked；注意同名缩写、合并会议和评级适用的论文类型。
  等级越高越红：CORE A* 红、A 橙、B 黄、C 绿；CCF A 红、B 黄、C 绿。
  已确认的 Unranked 为灰色，配色由标签定义中的 `colors` 配置。

所有公开标签附 `source`，必要时附不包含私人数字的 `note`。多轮投稿共享同一届次
的事实时逐条对应记录；不同届次的费用与参会政策不自动继承。

验证：`node --test tests/tag-model.test.js`，`bundle exec jekyll build`。

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

# EDA and Formal Verification Deadlines

Conference deadline countdowns with source-backed tags. Based on [ai-deadlines](https://aideadlin.es).

## Run locally

```bash
bundle install
bundle exec jekyll serve
```

## Update conferences

Edit `_data/conferences.yml` using official sources. Keep each edition’s year, dates, location and URL together.

- Use one entry per independent submission cycle, including past cycles.
- Record the abstract deadline, or the paper deadline when no abstract deadline exists. For ARR, use the conference’s latest eligible ARR deadline.
- Use a one-item deadline list (`["2027-01-15 23:59"]`) and an IANA timezone. If unspecified, use 23:59 AoE. Retain the previous edition when the next has no published deadline.

## Tags

Tags are maintained in `_data/tag_definitions.yml` and conference `labels`. The page footer explains their meaning.

For local research updates, edit `.local-research/ledger.json` and run `python3 scripts/render-conference-research.py`. This regenerates public labels and private reports. Exact fees, submission counts and acceptance rates stay local; only colors, years and sources are published. Never commit `.local-research/`; back it up separately.

## Checks

```bash
node --test tests/tag-model.test.js
bundle exec jekyll build
```

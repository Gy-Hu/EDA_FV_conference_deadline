# EDA and Formal Verification Deadlines

Conference deadline countdowns with source-backed tags. Based on [ai-deadlines](https://aideadlin.es).

## Run locally

```bash
bundle install
bundle exec jekyll serve
```

## Update conferences

Edit `_data/conferences.yml` using official sources. Keep each edition’s year, dates, location and URL together.

- Keep only the latest edition with a published deadline for each conference series. Replace the previous edition when updating, including when the conference name changes (for example, IJCAI-ECAI to IJCAI).
- Within that edition, use one entry per independent submission cycle, including cycles whose deadlines have passed.
- Record the abstract deadline, or the paper deadline when no abstract deadline exists. For ARR, use the conference’s latest eligible ARR deadline.
- Use a one-item deadline list (`["2027-01-15 23:59"]`) and an IANA timezone. If unspecified, use 23:59 AoE. Retain the previous edition when the next has no published deadline.

## Tags

Tags are maintained in `_data/tag_definitions.yml` and conference `labels`. The page footer explains their meaning.

Exact fees, submission counts and acceptance rates stay in private local records; only colors, years and sources are published. Local research tools and records are not included in this repository.

## Checks

```bash
bundle exec jekyll build
```

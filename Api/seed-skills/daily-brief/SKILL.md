---
name: daily-brief
description: Generate the user's research briefs from their specs. Use this when asked to produce the daily or scheduled brief, such as a request to generate today's briefs, or to re-run a brief after editing a spec. Reads each spec in /briefs/specs/ and writes one dated brief per spec. Relevant for brief, daily-brief, digest, and what's-new requests.
---

# Daily brief

Turn each spec into a short, skimmable digest of what's new. A brief is a *morning
read*: a few new papers, one line each — not an essay, a playbook, or a checklist.

## Where things live
- `/briefs/specs/` — one Markdown file per brief the user follows. The **filename
  without `.md` is the slug**; the text says what to cover, its scope, and tone.
  Specs are free-form — read and interpret them, never copy them into the output.
- `/briefs/<slug>/<YYYY-MM-DD>.md` — where you **save** the brief: a folder named
  after the slug, a file named by today's UTC date.

## How to generate
1. Take today's UTC date (`YYYY-MM-DD`) from your system prompt — it dates each brief file.
2. List `/briefs/specs/` and read every spec.
3. For each spec (slug = filename without `.md`):
   1. Derive an arXiv query from the spec and call `search_arxiv` (search only —
      never download PDFs for a brief).
   2. Keep at most **5** papers that genuinely fit the spec's focus, and drop the
      rest. A short, on-topic brief beats a padded one; off-topic papers are noise.
   3. **Dedup against earlier days only:** list `/briefs/<slug>/` and skip papers
      already covered in briefs from *previous* dates. Do NOT count today's own
      file as prior coverage (see "Re-runs overwrite today").
   4. Write the brief to `/briefs/<slug>/<today>.md` in the format below.

## Re-runs overwrite today
If `/briefs/<slug>/<today>.md` already exists, **overwrite it** — a re-run means
the user wants today's brief refreshed, often right after editing the spec.
Regenerate it from scratch; never append to it and never skip it as "already done".

## Output format — stick to this
```
# <Brief title> — <YYYY-MM-DD>

- **<Paper title>** (arXiv:<id>) — <one line: why it matters>. https://arxiv.org/abs/<id>
- ...
```
- At most ~5 bullets, one line each. If nothing new fits the spec, write exactly
  one line instead of bullets: `No new papers today.`
- Write in the spec's language and tone (English spec → English brief).
- **Do not** add goals, methodology, evaluation protocols, checklists, "where to
  store" notes, or any section describing your own process. Only the dated heading
  and the paper bullets belong in the file.

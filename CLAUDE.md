# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python script that monitors Chinese Wikipedia's new pages RSS feed hourly (via GitHub Actions) for badminton-related articles (keywords: 羽球, 羽毛球), sends email notifications on matches, and archives results in monthly Markdown logs.

## Running Locally

```bash
pip install feedparser

export EMAIL_FROM="your-email@gmail.com"
export EMAIL_TO="recipient@gmail.com"
export SMTP_PASSWORD="your-gmail-app-password"

python zh-wikipedia-ariticle-report.py
```

Email sending is silently skipped if `EMAIL_FROM` or `SMTP_PASSWORD` are unset — useful for dry runs.

## Architecture

**Single script:** `zh-wikipedia-ariticle-report.py` — the entire pipeline lives here.

**Data flow:**
1. Fetch two Wikipedia Atom feeds (`Special:NewPages` namespace=0 and namespace=14, 50 entries each)
2. Match titles/summaries against keywords `["羽球", "羽毛球"]`
3. Deduplicate against `history.txt` (set of previously seen URLs)
4. On new matches: send Gmail SMTP email, append to `logs/YYYY-MM.md`, update `history.txt`

**Persistence files (runtime-generated, git-tracked by workflow):**
- `history.txt` — append-only URL deduplication log
- `logs/YYYY-MM.md` — monthly Markdown archives

## GitHub Actions Workflow

`.github/workflows/watchdog.yml` runs hourly (`0 * * * *` UTC). Required GitHub secrets:
- `EMAIL_FROM`, `EMAIL_TO`, `SMTP_PASSWORD`

After running, the workflow commits and pushes any new/modified files in `logs/` and `history.txt` back to `main`.

## Dependencies

Only one external dependency: `feedparser`. Everything else is Python standard library (`smtplib`, `datetime`, `os`, `email.mime.text`).

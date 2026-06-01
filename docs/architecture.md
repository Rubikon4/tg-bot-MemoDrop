# MemoDrop — Architecture

## Overview

Single-tenant self-hosted Telegram bot. User sends a message or video link →
LLM structures it → Markdown note saved to MinIO → Obsidian syncs automatically.

One allowed user (`ALLOWED_USER_ID`). Designed to run on a personal VPS via Docker Compose.

---

## Data Flow

```
Telegram
  └─ Aiogram 3 (webhook / polling)
       └─ FSM router
            ├─ text message
            │    └─ LLM client (OpenRouter via openai SDK)
            │         └─ structured note (title + tags + body)
            │              └─ MinIO (boto3)  ←──── Obsidian (Remotely Save plugin)
            │
            └─ video URL
                 └─ yt-dlp → transcript text
                      └─ (same LLM path as above)
```

---

## Layers

| Layer        | Technology        | Role |
|---|---|---|
| Transport    | Aiogram 3         | Receive messages, FSM state, send replies |
| Config       | pydantic-settings | Load `.env`, validate at startup |
| LLM          | openai SDK (OpenRouter base_url) | Prompt → structured note |
| Storage      | MinIO + boto3     | Save `.md` files; S3-compatible vault |
| Database     | SQLite + aiosqlite + SQLAlchemy async | Three roles (see below) |
| Video        | yt-dlp            | Extract transcript from video URL |
| Preview      | mistune + Telegraph API | Render md→html, send preview link |

---

## SQLite — Three Roles

1. **FSM storage** — Aiogram stores conversation state between messages.
2. **Request deduplication** — SHA-256 hash of raw input; skip if already processed.
3. **LLM response cache** — hash → cached response; avoid re-calling API for identical input.

All three use the same SQLite file via SQLAlchemy async session.

---

## Note Structure in MinIO

```
bucket: memodrop
  └─ YYYY/MM/DD/
       └─ {slug-title}.md
```

Frontmatter:
```yaml
---
title: ...
tags: [...]
source: telegram
created: 2026-06-01T19:57:00
---
```

---

## FSM Flow (text message)

```
idle
  → user sends text
  → [processing] LLM call
  → [preview] show result + buttons (Save / Regenerate / Discard)
      ├─ Save     → write to MinIO → idle
      ├─ Regenerate → re-enter [processing] (return previous user's text, re-enter input state)
      └─ Discard  → idle
```

---

## Regeneration Strategy

On "Regenerate": the previous user's text-messeage is shown to the user again as context,
then the FSM re-enters the processing state. No new LLM call unless input changes.

---

## Deployment

Bot runs in a Docker container. MinIO runs separately.
Bot connects to MinIO via S3-compatible endpoint configured in `.env`.
Obsidian connects to the same MinIO independently via Remotely Save plugin (S3 endpoint).

The storage layer uses a thin adapter over boto3 so any
S3-compatible backend works — MinIO, AWS S3, Cloudflare R2 — by changing endpoint/credentials in `.env` only. No code changes required.

---

## Key Constraints

- Single tenant: one `ALLOWED_USER_ID` checked at router level, all other users silently ignored.
- No web server exposed: bot runs in polling mode.
- Public GitHub repo: no secrets in code; all configuration via environment variables.
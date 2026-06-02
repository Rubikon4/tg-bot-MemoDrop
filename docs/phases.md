# Development Phases

## Phase 0 — Scaffold
`pyproject.toml`, pydantic-settings config, Aiogram skeleton with `ALLOWED_USER_ID` guard, polling starts.

**Done when:** bot starts, responds only to allowed user, ignores everyone else.

## Phase 1 — Text Intake
FSM router, receive text message, stub reply.

**Done when:** bot accepts text and echoes a placeholder response.

## Phase 2 — LLM Processing
OpenRouter client (openai SDK, base_url override), prompt → structured note (title + tags + body).
SQLite cache keyed by SHA-256 hash of raw input.

**Done when:** bot turns a text message into a formatted Markdown note.

## Phase 3 — Storage
Thin S3 adapter over boto3: `save_note(path, content)`.
Save `.md` to MinIO under `YYYY/MM/DD/{slug}.md`.

**Done when:** note appears in MinIO bucket and Obsidian syncs it.

## Phase 4 — UX
Inline buttons: Save / Regenerate / Discard.
Telegraph preview (mistune md→html).
`/history` command.

**Done when:** full save/discard/regenerate flow works end-to-end.

## Phase 5 — Video
yt-dlp transcript extraction, feed text into existing LLM pipeline.

**Done when:** sending a video URL produces a note identical in structure to a text note.

## Phase 6 — Deploy
`Dockerfile`, `.env.example`, public repo cleanup, README.

**Done when:** anyone can clone, fill `.env`, run `docker compose up`, and use the bot.
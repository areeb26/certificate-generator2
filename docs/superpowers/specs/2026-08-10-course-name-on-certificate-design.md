# Course name on certificate — Design

**Date:** 2026-08-10  
**Status:** Approved for planning  
**Approach:** Mirror the existing recipient-name field (position + style), without breaking existing certificate APIs.

## Goal

Let users type a course name (same pattern as recipient name), place and style it independently on the template, and generate certificates that include both name and course — while keeping today’s name-only certificate operations unchanged.

## Non-goals

- Course catalog / courses table
- Student/user picker from a database
- More than two text overlays
- Per-field language (one template language still applies to both strings)

## Architecture

Mirror the existing name pipeline for a second overlay (`course`):

| Concern | Name (existing) | Course (new) |
|---------|-----------------|--------------|
| Preview text | `previewName` | `previewCourse` |
| Position | `textPosition` / `text_x`, `text_y` | `courseTextPosition` / `course_text_x`, `course_text_y` |
| Style | `font`, `fontSize`, `alignment`, `color` | `courseFont`, `courseFontSize`, `courseAlignment`, `courseColor` |
| Generate API | `GET /api/certificate/{id}?name=` | `GET /api/certificate-with-course/{id}?name=&course=` |

Shared: template language, Urdu reshape/bidi when language is Urdu.

## Data model

Add columns to `templates` (SQLite + Postgres / Supabase setup docs):

- `course_text_x REAL`
- `course_text_y REAL`
- `course_font TEXT`
- `course_font_size INTEGER`
- `course_alignment TEXT`
- `course_color TEXT`

**Backward compatibility for old rows:** on read, if course columns are missing or null, fill defaults (same font/size/alignment/color as name; position slightly below name). Do not require a destructive migration that breaks existing templates.

Template create/update accept optional course fields; if omitted, store the same defaults. Existing clients that only send name fields keep working.

## API

### Unchanged (must not break)

- `GET /api/certificate/{template_id}?name=...` — name overlay only, identical behavior to today.

### New

- `GET /api/certificate-with-course/{template_id}?name=...&course=...`
  - Draws name using name position/style.
  - Draws course using course position/style when `course` is non-empty.
  - Empty `course` is allowed: draw name only (same visual as name-only path, but via the new endpoint).
  - Reuse existing Urdu handling for both strings.

### Template endpoints

Extend create/get (and update if present) responses/payloads with optional course position + style fields. Omitted course fields → defaults. No new template CRUD routes required.

## Frontend

### Configuration

- Field toggle: **Name** | **Course**.
- Click-to-place, drag, and style controls apply to the active field only.
- Canvas shows both overlays while configuring so layout is visible.

### Preview

- Name text input (existing).
- Course name text input (new).
- Live canvas: if course empty → name only; if filled → both.
- **Both options exposed:**
  1. Download / Copy API URL (**name only**) → existing `/api/certificate/{id}?name=...`
  2. Download / Copy API URL (**name + course**) → new `/api/certificate-with-course/{id}?name=...&course=...`

### Defaults on new upload

- Name: current defaults.
- Course: same style as name; position slightly below name so both are visible immediately.
- Language toggle may swap sample EN/UR preview strings for both fields the same way name works today.

## Error handling

- Missing template → 404 (unchanged).
- New endpoint: `name` required; `course` optional (empty string OK).
- Old templates without course config → defaults on load; both APIs remain usable.

## Testing

One small runnable check: with-course generate/draw path includes course text at course position when `course` is provided (fails if the second overlay is missing). Prefer the smallest assert-based or script check; no new test framework.

## Files likely touched

- `backend/db.py` — schema + create/get/update
- `backend/main.py` — TemplateConfig + new generate route; leave existing generate route alone
- `backend/SUPABASE_SETUP.md` — document new columns
- `frontend/src/App.jsx` — toggle, second styles/position, preview inputs, both download/copy actions

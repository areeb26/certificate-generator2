# Urdu RTL-end alignment — Design

**Date:** 2026-08-10  
**Status:** Approved  
**Approach:** New `rtl-end` alignment value (no new DB columns). Click is the left end of the Urdu run; font shrinks to stay left of the decorative border.

## Goal

Let the editor pin where an Urdu name (or course) **ends**. Text is written RTL from the right toward that pin. Long strings shrink so they do not run into the right-side pattern or past the left pin.

## Non-goals

- Second click / stored right bound
- Max-width slider
- Changing left / center / right behavior
- Wrapping to multiple lines
- English RTL

## Behavior

- Alignment value: `rtl-end` on name (`alignment`) and/or course (`course_alignment`).
- Pin `(text_x, text_y)` = **left end** (last letter / end of RTL run) on the baseline.
- Ink grows to the right. First letter is the rightmost glyph.
- If measured width would pass `image_width * 0.80`, reduce `font_size` until it fits or hit floor **16**.
- Preview and generate share `draw_text_on_image`.

## Data

Reuse existing TEXT alignment columns. Unknown old values unchanged. No migration.

## Frontend

When template language is Urdu, show a fourth alignment button: **RTL end**. English stays left / center / right.

## Testing

One assert check: rtl-end keeps leftmost ink at/after the pin; a long string’s rightmost ink stays ≤ 80% of image width.

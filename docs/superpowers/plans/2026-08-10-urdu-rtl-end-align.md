# Urdu RTL-end alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `rtl-end` alignment so Urdu text ends at the click and shrinks to stay left of the right 20% of the image.

**Architecture:** Same `alignment` / `course_alignment` strings. `draw_text_on_image` left-anchors at the pin and steps font size down. Editor shows a fourth button when language is Urdu.

**Tech Stack:** Pillow draw path, FastAPI preview/generate, React alignment toggle.

## Global Constraints

- No new DB columns or dependencies.
- left / center / right unchanged.
- Font floor 16. Right limit `0.80 * image_width`.

---

### Task 1: Draw helper — rtl-end + shrink

**Files:** `backend/main.py`, `backend/test_course_overlay.py`

- [ ] Failing tests for left-edge pin and long-name shrink
- [ ] Implement in `draw_text_on_image` (pass image width)
- [ ] Tests pass

### Task 2: Editor button

**Files:** `frontend/src/App.jsx`

- [ ] Fourth alignment **RTL end** when `language === 'ur'`
- [ ] Hit box treats `rtl-end` like left (default path already does)

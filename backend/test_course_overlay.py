"""Assert-based checks for course overlay DB + draw helpers. Run: python test_course_overlay.py"""
import os
import tempfile

# Force sqlite temp DB before importing db
_fd, _path = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ["DATABASE_TYPE"] = "sqlite"
os.environ["DATABASE_PATH"] = _path

import db as db_mod  # noqa: E402

# Re-init against temp path (module already ran init on import)
db_mod.DATABASE_PATH = _path
db_mod.db.db_path = _path
db_mod.db.db_type = "sqlite"
db_mod.db.init_database()


def test_create_and_get_includes_course_fields():
    tid = db_mod.template_db.create_template(
        name="t1",
        image_base64="data:image/png;base64,aaa",
        text_x=100,
        text_y=80,
        font="Arial",
        font_size=40,
        alignment="center",
        color="#000000",
        language="en",
        course_text_x=100,
        course_text_y=140,
        course_font="Arial",
        course_font_size=28,
        course_alignment="center",
        course_color="#333333",
    )
    assert tid is not None
    t = db_mod.template_db.get_template(tid)
    assert t["course_text_x"] == 100
    assert t["course_text_y"] == 140
    assert t["course_font"] == "Arial"
    assert t["course_font_size"] == 28
    assert t["course_alignment"] == "center"
    assert t["course_color"] == "#333333"


def test_get_fills_course_defaults_when_null():
    # Insert a row the old way (name columns only) if possible; else simulate via create then nulling
    conn = db_mod.db.get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO templates
           (name, image_base64, text_x, text_y, font, font_size, alignment, color, language)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("old", "data:image/png;base64,aaa", 50, 50, "Arial", 48, "center", "#000000", "en"),
    )
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    t = db_mod.template_db.get_template(tid)
    assert t["course_text_x"] == 50
    assert t["course_text_y"] == 50 + 60  # default: name y + 60
    assert t["course_font"] == "Arial"
    assert t["course_font_size"] == 48
    assert t["course_alignment"] == "center"
    assert t["course_color"] == "#000000"


def test_draw_helper_writes_course_pixels():
    from PIL import Image, ImageDraw
    import main as main_mod

    img = Image.new("RGB", (400, 300), "white")
    draw = ImageDraw.Draw(img)
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    main_mod.draw_text_on_image(
        draw, "Math 101", 200, 150, 32, "center", "#000000", "en", font_dir
    )
    # Near draw point should have ink
    region = [img.getpixel((x, y)) for y in range(115, 175) for x in range(170, 230)]
    assert any(px != (255, 255, 255) for px in region), "expected course text to darken pixels near draw point"


def test_urdu_uses_noori_nastaleeq_exactly():
    import main as main_mod

    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    path = main_mod.resolve_font_path("ur", font_dir)
    assert os.path.basename(path) == "Jameel Noori Nastaleeq.ttf"
    assert os.path.getsize(path) > 100_000
    with open(path, "rb") as f:
        assert f.read(4) == b"\x00\x01\x00\x00"


def test_text_sits_on_baseline_not_hanging_from_top():
    from PIL import Image, ImageDraw
    import main as main_mod

    y = 150
    img = Image.new("RGB", (400, 300), "white")
    draw = ImageDraw.Draw(img)
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    main_mod.draw_text_on_image(
        draw, "Alice", 200, y, 40, "center", "#000000", "en", font_dir
    )
    above = sum(
        1 for yy in range(y - 50, y) for xx in range(120, 280)
        if img.getpixel((xx, yy)) != (255, 255, 255)
    )
    below = sum(
        1 for yy in range(y + 1, y + 25) for xx in range(120, 280)
        if img.getpixel((xx, yy)) != (255, 255, 255)
    )
    assert above > below * 2, f"text should sit on the line (ink above y), got above={above} below={below}"


def test_postgres_execute_rolls_back_on_error():
    """A failed ALTER must not leave the shared Postgres connection aborted."""
    class FakeCursor:
        def execute(self, q, p=()):
            raise RuntimeError("column already exists")

    class FakeConn:
        def __init__(self):
            self.rolled = False
            self.closed = False

        def cursor(self):
            return FakeCursor()

        def rollback(self):
            self.rolled = True

    fake = FakeConn()
    orig_type, orig_get = db_mod.db.db_type, db_mod.db.get_connection
    db_mod.db.db_type = "postgresql"
    db_mod.db.get_connection = lambda: fake
    try:
        try:
            db_mod.db.execute("ALTER TABLE templates ADD COLUMN course_text_x REAL")
            assert False, "expected execute to raise"
        except RuntimeError:
            pass
        assert fake.rolled, "postgres execute must rollback so later queries can run"
    finally:
        db_mod.db.db_type = orig_type
        db_mod.db.get_connection = orig_get


def test_update_persists_course_position():
    tid = db_mod.template_db.create_template(
        name="upd",
        image_base64="data:image/png;base64,aaa",
        text_x=100,
        text_y=80,
        font="Arial",
        font_size=40,
        alignment="center",
        color="#000000",
        language="en",
    )
    ok = db_mod.template_db.update_template(
        tid, course_text_x=360, course_text_y=365, course_font_size=32,
    )
    assert ok
    t = db_mod.template_db.get_template(tid)
    assert t["course_text_x"] == 360
    assert t["course_text_y"] == 365
    assert t["course_font_size"] == 32


def test_put_template_route_exists():
    import main as main_mod
    found = False
    for r in main_mod.app.routes:
        if getattr(r, "path", None) != "/api/template/{template_id}":
            continue
        methods = getattr(r, "methods", None) or set()
        if "PUT" in methods:
            found = True
            break
    assert found, "PUT /api/template/{id} required so the editor can save course position in place"


def test_n8n_underscore_with_course_route_exists():
    import main as main_mod
    paths = {getattr(r, "path", None) for r in main_mod.app.routes}
    assert "/api/certificate-with-course/{template_id}" in paths
    assert "/api/certificate_with_course/{template_id}" in paths


def test_cors_regex_allows_vercel_preview():
    import re
    import main as main_mod

    preview = "https://certificate-generator2-edah3kju1-areeb26s-projects.vercel.app"
    gilt = "https://certificate-generator2-gilt.vercel.app"
    assert re.fullmatch(main_mod.VERCEL_ORIGIN_RE, preview)
    assert re.fullmatch(main_mod.VERCEL_ORIGIN_RE, gilt)
    assert not re.fullmatch(main_mod.VERCEL_ORIGIN_RE, "https://evil.example.com")


def test_render_png_matches_generate_overlays():
    """Editor preview and n8n must share one renderer (name + course ink)."""
    import base64
    import io
    from PIL import Image
    import main as main_mod

    blank = Image.new("RGB", (200, 140), "white")
    buf = io.BytesIO()
    blank.save(buf, format="PNG")
    data_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    png = main_mod.render_certificate_png(
        data_uri,
        recipient_name="Ann",
        course="Math",
        text_x=100, text_y=40, font_size=22, alignment="center", color="#000000", language="en",
        course_text_x=100, course_text_y=100, course_font_size=20,
        course_alignment="center", course_color="#000000",
    )
    out = Image.open(io.BytesIO(png)).convert("RGB")
    name_region = [out.getpixel((x, y)) for y in range(18, 50) for x in range(70, 130)]
    course_region = [out.getpixel((x, y)) for y in range(78, 115) for x in range(70, 130)]
    assert any(px != (255, 255, 255) for px in name_region), "name overlay missing"
    assert any(px != (255, 255, 255) for px in course_region), "course overlay missing"


if __name__ == "__main__":
    test_create_and_get_includes_course_fields()
    test_get_fills_course_defaults_when_null()
    test_update_persists_course_position()
    test_put_template_route_exists()
    test_n8n_underscore_with_course_route_exists()
    test_draw_helper_writes_course_pixels()
    test_urdu_uses_noori_nastaleeq_exactly()
    test_text_sits_on_baseline_not_hanging_from_top()
    test_postgres_execute_rolls_back_on_error()
    test_cors_regex_allows_vercel_preview()
    test_render_png_matches_generate_overlays()
    print("OK: course DB checks passed")
    os.remove(_path)

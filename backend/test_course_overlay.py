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


if __name__ == "__main__":
    test_create_and_get_includes_course_fields()
    test_get_fills_course_defaults_when_null()
    print("OK: course DB checks passed")
    os.remove(_path)

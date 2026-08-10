print("MAIN.PY FILE LOADED - TESTING PRINT")
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
import io
import base64
import os
from pydantic import BaseModel
from db import db, template_db

try:
    from arabic_reshaper import reshape
    from bidi.algorithm import get_display
    import arabic_reshaper
    URDU_SUPPORT = True
except ImportError:
    URDU_SUPPORT = False

# Check for libraqm support (enables complex text layout for Nastaliq fonts)
try:
    from PIL import features
    LIBRAQM_AVAILABLE = features.check('raqm')
except:
    LIBRAQM_AVAILABLE = False

app = FastAPI(title="Certificate Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://certificate-generator2-2.onrender.com",
        "https://certificate-generator2-gilt.vercel.app",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TemplateConfig(BaseModel):
    name: str
    image_base64: str
    text_position: dict
    font: str
    font_size: int
    alignment: str
    color: str
    language: str
    course_text_position: dict | None = None
    course_font: str | None = None
    course_font_size: int | None = None
    course_alignment: str | None = None
    course_color: str | None = None


NOORI_NASTALEEQ = "Jameel Noori Nastaleeq.ttf"


def resolve_font_path(language: str, font_dir: str) -> str:
    """Urdu certificates always use Jameel Noori Nastaleeq — no Tahoma/Arial fallback."""
    if language == "ur":
        path = os.path.join(font_dir, NOORI_NASTALEEQ)
        if not os.path.isfile(path) or os.path.getsize(path) < 100_000:
            raise FileNotFoundError(f"Jameel Noori Nastaleeq font missing or invalid: {path}")
        return path
    for name in ("ARIAL.TTF", "arial.ttf"):
        path = os.path.join(font_dir, name)
        if os.path.isfile(path):
            return path
    raise FileNotFoundError(f"No English font found in {font_dir}")


def draw_text_on_image(draw, text, text_x, text_y, font_size, alignment, color, language, font_dir):
    if not text:
        return

    font_path = resolve_font_path(language, font_dir)
    font = ImageFont.truetype(font_path, font_size)
    try:
        print(f"Using font: {os.path.basename(font_path)}")
    except Exception:
        pass

    # For Urdu text processing with Tahoma font
    if language == 'ur' and URDU_SUPPORT:
        try:
            # Reshape to get Arabic Presentation Forms
            reshaped = reshape(text)
            # Reverse for RTL display
            display_text = get_display(reshaped)

            try:
                print("Urdu text: reshaped for Jameel Noori Nastaleeq")
            except:
                pass
        except Exception as e:
            try:
                print(f"Urdu processing error: {repr(e)}")
            except:
                pass
            # Fallback: just reverse
            display_text = text[::-1]
    elif language == 'ur':
        # No reshape/bidi libraries, just reverse
        display_text = text[::-1]
        try:
            print("Urdu: simple reversal (libraries not available)")
        except:
            pass
    else:
        display_text = text

    # ls = left + alphabetic baseline so a click on the certificate line
    # sits the letters on that line (not hanging from the top of the em-box).
    bbox = draw.textbbox((0, 0), display_text, font=font, anchor='ls')
    text_width = bbox[2] - bbox[0]

    draw_x = text_x
    if alignment == 'center':
        draw_x = text_x - text_width / 2
    elif alignment == 'right':
        draw_x = text_x - text_width

    if language == 'ur' and LIBRAQM_AVAILABLE:
        try:
            draw.text((draw_x, text_y), text, fill=color, font=font, anchor='ls',
                     direction='rtl', language='ur', features=['liga', 'calt', 'ccmp', 'locl'])
        except:
            draw.text((draw_x, text_y), display_text, fill=color, font=font, anchor='ls')
    else:
        draw.text((draw_x, text_y), display_text, fill=color, font=font, anchor='ls')


def render_certificate_png(
    image_base64: str,
    recipient_name: str,
    course: str,
    text_x, text_y, font_size, alignment, color, language,
    course_text_x=None, course_text_y=None, course_font_size=None,
    course_alignment=None, course_color=None,
) -> bytes:
    """One draw path for n8n generate + editor preview."""
    image_data = base64.b64decode(image_base64.split(",")[1])
    image = Image.open(io.BytesIO(image_data))
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")
    draw = ImageDraw.Draw(image)
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    draw_text_on_image(
        draw, recipient_name, text_x, text_y, font_size, alignment, color, language, font_dir,
    )
    if course:
        draw_text_on_image(
            draw, course,
            course_text_x if course_text_x is not None else text_x,
            course_text_y if course_text_y is not None else text_y + 60,
            course_font_size if course_font_size is not None else font_size,
            course_alignment or alignment,
            course_color or color,
            language, font_dir,
        )
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


class PreviewRequest(BaseModel):
    image_base64: str
    recipient_name: str
    course: str = ""
    text_position: dict
    font: str = ""
    font_size: int
    alignment: str
    color: str
    language: str
    course_text_position: dict | None = None
    course_font: str | None = None
    course_font_size: int | None = None
    course_alignment: str | None = None
    course_color: str | None = None


@app.get("/")
async def root():
    try:
        count = template_db.get_template_count()
        db_info = db.get_database_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db: {e}")
    return {
        "message": "Certificate API",
        "urdu_support": URDU_SUPPORT,
        "libraqm_available": LIBRAQM_AVAILABLE,
        "urdu_font": "Jameel Noori Nastaleeq",
        "templates_count": count,
        "database": db_info["type"]
    }

@app.post("/api/template")
async def create_template(config: TemplateConfig):
    try:
        cx = (config.course_text_position or {}).get("x", config.text_position["x"])
        cy = (config.course_text_position or {}).get("y", config.text_position["y"] + 60)
        template_id = template_db.create_template(
            name=config.name,
            image_base64=config.image_base64,
            text_x=config.text_position['x'],
            text_y=config.text_position['y'],
            font=config.font,
            font_size=config.font_size,
            alignment=config.alignment,
            color=config.color,
            language=config.language,
            course_text_x=cx,
            course_text_y=cy,
            course_font=config.course_font or config.font,
            course_font_size=config.course_font_size if config.course_font_size is not None else config.font_size,
            course_alignment=config.course_alignment or config.alignment,
            course_color=config.course_color or config.color,
        )

        if template_id is None:
            raise HTTPException(status_code=500, detail="Failed to create template: No ID returned from database")

        print(f"Template created successfully with ID: {template_id}")
        return {"template_id": template_id}
    except Exception as e:
        print(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")

@app.get("/api/templates")
async def list_templates():
    templates = template_db.list_templates()
    return {"templates": templates}

@app.get("/api/template/{template_id}")
async def get_template(template_id: int):
    template = template_db.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": template["id"],
        "name": template["name"],
        "image_base64": template["image_base64"],
        "text_position": {"x": template["text_x"], "y": template["text_y"]},
        "font": template["font"],
        "font_size": template["font_size"],
        "alignment": template["alignment"],
        "color": template["color"],
        "language": template["language"],
        "course_text_position": {"x": template["course_text_x"], "y": template["course_text_y"]},
        "course_font": template["course_font"],
        "course_font_size": template["course_font_size"],
        "course_alignment": template["course_alignment"],
        "course_color": template["course_color"],
    }

@app.get("/api/debug/fonts")
async def debug_fonts():
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    files = {}
    if os.path.exists(font_dir):
        for name in os.listdir(font_dir):
            files[name] = os.path.getsize(os.path.join(font_dir, name))
    return {"font_dir": font_dir, "exists": os.path.exists(font_dir), "files": files, "urdu_support": URDU_SUPPORT}

@app.get("/api/certificate/{template_id}")
async def generate_certificate(template_id: int, name: str = Query(...)):
    try:
        print("="*50)
        print(f"Certificate generation started")
        print(f"Template ID: {template_id}")
        print(f"Name received (repr): {repr(name)}")
        print("="*50)
    except UnicodeEncodeError:
        print("Certificate generation started (Unicode name)")

    template = template_db.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        png = render_certificate_png(
            template["image_base64"], name, "",
            template["text_x"], template["text_y"],
            template["font_size"], template["alignment"], template["color"],
            template["language"],
        )
        return Response(content=png, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/certificate-with-course/{template_id}")
async def generate_certificate_with_course(
    template_id: int,
    name: str = Query(...),
    course: str = Query(""),
):
    template = template_db.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    try:
        png = render_certificate_png(
            template["image_base64"], name, course,
            template["text_x"], template["text_y"],
            template["font_size"], template["alignment"], template["color"],
            template["language"],
            template["course_text_x"], template["course_text_y"],
            template["course_font_size"], template["course_alignment"], template["course_color"],
        )
        return Response(content=png, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/preview")
async def preview_certificate(req: PreviewRequest):
    try:
        cx = (req.course_text_position or {}).get("x", req.text_position["x"])
        cy = (req.course_text_position or {}).get("y", req.text_position["y"] + 60)
        png = render_certificate_png(
            req.image_base64, req.recipient_name, req.course,
            req.text_position["x"], req.text_position["y"],
            req.font_size, req.alignment, req.color, req.language,
            cx, cy,
            req.course_font_size if req.course_font_size is not None else req.font_size,
            req.course_alignment or req.alignment,
            req.course_color or req.color,
        )
        return Response(content=png, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

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
        "https://certificate-generator2-gilt.vercel.app"
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

@app.get("/")
async def root():
    count = template_db.get_template_count()
    db_info = db.get_database_info()
    return {
        "message": "Certificate API",
        "urdu_support": URDU_SUPPORT,
        "libraqm_available": LIBRAQM_AVAILABLE,
        "urdu_font": "Nastaliq" if LIBRAQM_AVAILABLE else "Tahoma",
        "templates_count": count,
        "database": db_info["type"]
    }

@app.post("/api/template")
async def create_template(config: TemplateConfig):
    try:
        template_id = template_db.create_template(
            name=config.name,
            image_base64=config.image_base64,
            text_x=config.text_position['x'],
            text_y=config.text_position['y'],
            font=config.font,
            font_size=config.font_size,
            alignment=config.alignment,
            color=config.color,
            language=config.language
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
        "language": template["language"]
    }

@app.get("/api/debug/fonts")
async def debug_fonts():
    font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    info = {"font_dir": font_dir, "exists": os.path.exists(font_dir), "files": os.listdir(font_dir) if os.path.exists(font_dir) else [], "urdu_support": URDU_SUPPORT}
    return info

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
        image_base64 = template["image_base64"]
        text_x, text_y = template["text_x"], template["text_y"]
        font_size = template["font_size"]
        alignment, color = template["alignment"], template["color"]
        language = template["language"]
        
        image_data = base64.b64decode(image_base64.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        draw = ImageDraw.Draw(image)
        
        font = None
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        
        # For Urdu: use Nastaliq fonts if libraqm available, otherwise use Tahoma
        if language == 'ur':
            if LIBRAQM_AVAILABLE:
                # Use beautiful Nastaliq fonts with libraqm support
                font_paths = [
                    os.path.join(font_dir, 'Jameel Noori Nastaleeq.ttf'),
                    os.path.join(font_dir, 'NotoNastaliqUrdu-Regular.ttf'),
                    'C:\\Windows\\Fonts\\tahoma.ttf',
                ]
            else:
                # Use Tahoma (clean, professional, supports Arabic)
                font_paths = [
                    'C:\\Windows\\Fonts\\tahoma.ttf',
                    'C:\\Windows\\Fonts\\tahomabd.ttf',  # Tahoma Bold
                    os.path.join(font_dir, 'ARIAL.TTF'),
                ]
        else:
            font_paths = [
                os.path.join(font_dir, 'ARIAL.TTF'),
                os.path.join(font_dir, 'arial.ttf'),
            ]
        
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, font_size)
                try:
                    print(f"Using font: {os.path.basename(path)}")
                except:
                    pass
                break

        if font is None:
            font = ImageFont.load_default()
            try:
                print("Using default font (WARNING: may not support Urdu)")
            except:
                pass
        
        # Debug: Print incoming name (safe for Windows console)
        try:
            print(f"Name type: {type(name)}")
            print(f"Name repr: {repr(name)}")
        except UnicodeEncodeError:
            pass
        
        # For Urdu text processing with Tahoma font
        if language == 'ur' and URDU_SUPPORT:
            try:
                # Reshape to get Arabic Presentation Forms
                reshaped = reshape(name)
                # Reverse for RTL display
                display_name = get_display(reshaped)

                try:
                    print(f"Urdu text: reshaped and reversed with Tahoma")
                except:
                    pass
            except Exception as e:
                try:
                    print(f"Urdu processing error: {repr(e)}")
                except:
                    pass
                # Fallback: just reverse
                display_name = name[::-1]
        elif language == 'ur':
            # No reshape/bidi libraries, just reverse
            display_name = name[::-1]
            try:
                print("Urdu: simple reversal (libraries not available)")
            except:
                pass
        else:
            display_name = name
        
        # Calculate text width for alignment
        bbox = draw.textbbox((0, 0), display_name, font=font, anchor='la')
        text_width = bbox[2] - bbox[0]
        
        if alignment == 'center':
            text_x = text_x - text_width / 2
        elif alignment == 'right':
            text_x = text_x - text_width
        
        # Draw text with proper rendering
        if language == 'ur' and LIBRAQM_AVAILABLE:
            # Use PIL's advanced text rendering with libraqm
            try:
                draw.text((text_x, text_y), name, fill=color, font=font, anchor='la',
                         direction='rtl', language='ur', features=['liga', 'calt', 'ccmp', 'locl'])
            except:
                # Fallback if advanced features fail
                draw.text((text_x, text_y), display_name, fill=color, font=font, anchor='la')
        else:
            # Simple drawing (for Tahoma with reshaped text)
            draw.text((text_x, text_y), display_name, fill=color, font=font, anchor='la')
        
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return Response(content=img_bytes.getvalue(), media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
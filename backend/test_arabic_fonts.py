from PIL import Image, ImageDraw, ImageFont
import os
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# Test Urdu text
text = "علی احمد"
reshaped = reshape(text)
display_text = get_display(reshaped)

# Common Windows fonts that support Arabic
fonts_to_test = [
    # Windows system fonts
    ('C:\\Windows\\Fonts\\arial.ttf', 'Arial'),
    ('C:\\Windows\\Fonts\\times.ttf', 'Times New Roman'),
    ('C:\\Windows\\Fonts\\tahoma.ttf', 'Tahoma'),
    ('C:\\Windows\\Fonts\\segoeuil.ttf', 'Segoe UI Light'),
    ('C:\\Windows\\Fonts\\segoeui.ttf', 'Segoe UI'),
    ('C:\\Windows\\Fonts\\calibri.ttf', 'Calibri'),
    ('C:\\Windows\\Fonts\\comic.ttf', 'Comic Sans MS'),
    # Custom fonts in project
    ('fonts/ARIAL.TTF', 'Arial (Project)'),
]

# Create test image
img = Image.new('RGB', (1000, len(fonts_to_test) * 80 + 50), color='white')
draw = ImageDraw.Draw(img)

y_pos = 30
working_fonts = []

for font_path, font_name in fonts_to_test:
    try:
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 40)

            # Draw font name
            label_font = ImageFont.load_default()
            draw.text((10, y_pos), f"{font_name}:", fill='blue', font=label_font)

            # Draw the Urdu text
            draw.text((250, y_pos), display_text, fill='black', font=font)

            working_fonts.append(font_name)
            print(f"[OK] {font_name} - WORKS")
            y_pos += 80
        else:
            print(f"[SKIP] {font_name} - File not found")
    except Exception as e:
        print(f"[ERROR] {font_name} - {repr(e)}")

# Save the test image
img.save('arabic_fonts_test.png')
print(f"\n[OK] Test image saved: arabic_fonts_test.png")
print(f"[OK] Working fonts: {len(working_fonts)}")
print("\nWorking fonts that can display Urdu:")
for font in working_fonts:
    print(f"  - {font}")

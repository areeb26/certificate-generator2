from PIL import Image, ImageDraw, ImageFont
import os
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# Test Urdu text rendering
text = "علی"

print(f"Original text length: {len(text)}")

# Process with reshape and bidi
reshaped = reshape(text)
print(f"After reshape length: {len(reshaped)}")

display_text = get_display(reshaped)
print(f"After get_display length: {len(display_text)}")

# Create a test image
img = Image.new('RGB', (800, 400), color='white')
draw = ImageDraw.Draw(img)

# Try different fonts
fonts_to_test = [
    ('NotoNastaliqUrdu-Regular.ttf', 'Noto Nastaliq'),
    ('Jameel Noori Nastaleeq.ttf', 'Jameel Noori'),
    ('ARIAL.TTF', 'Arial (fallback)')
]

y_pos = 50
for font_file, font_name in fonts_to_test:
    font_path = os.path.join('fonts', font_file)
    try:
        font = ImageFont.truetype(font_path, 50)
        print(f"{font_name} font loaded")

        # Draw label
        draw.text((10, y_pos), f"{font_name}:", fill='blue', font=ImageFont.load_default())

        # Draw the processed text
        draw.text((200, y_pos), display_text, fill='black', font=font)
        print(f"{font_name} text drawn")

        y_pos += 100
    except Exception as e:
        print(f"Error with {font_name}: {e}")

# Save the test image
img.save('test_urdu_output.png')
print("Test image saved")

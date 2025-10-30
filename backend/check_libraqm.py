from PIL import features

print("Checking PIL features:")
print(f"libraqm (complex text layout): {features.check('raqm')}")
print(f"freetype (font support): {features.check('freetype')}")
print(f"harfbuzz (text shaping): {features.check('harfbuzz')}")

if features.check('raqm'):
    print("\n✓ libraqm is available! You can use Urdu Nastaliq fonts.")
else:
    print("\n✗ libraqm is NOT available. You'll need to use Arial or install libraqm.")
    print("\nTo install libraqm on Windows:")
    print("1. Download from: https://github.com/HOST-Oman/libraqm/releases")
    print("2. Or use: pip install pillow --global-option=\"build_ext\" --global-option=\"--enable-raqm\"")

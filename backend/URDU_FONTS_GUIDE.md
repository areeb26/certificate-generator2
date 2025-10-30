# Urdu Font Support Guide

## Current Status

✅ **Urdu text rendering is WORKING with Arial font**
- Characters are properly connected
- Text displays in correct RTL (right-to-left) direction
- Uses `arabic-reshaper` and `python-bidi` libraries

❌ **Beautiful Nastaliq fonts NOT available** (requires libraqm)

## Font Comparison

### Current: Arial Font
- ✅ **Works now** - No additional setup needed
- ✅ Proper character joining
- ✅ Correct RTL direction
- ⚠️ Not authentic Urdu calligraphy style
- ⚠️ Less aesthetically pleasing for Urdu

### Desired: Nastaliq Fonts (Jameel Noori / Noto Nastaliq Urdu)
- ✅ Beautiful traditional Urdu calligraphy
- ✅ Authentic Nastaliq style
- ❌ **Requires libraqm library** (not available on Windows easily)

## How to Enable Nastaliq Fonts

### Option 1: Use WSL (Windows Subsystem for Linux) - RECOMMENDED

1. Install WSL on Windows
2. Install Ubuntu from Microsoft Store
3. In Ubuntu terminal:
```bash
sudo apt-get update
sudo apt-get install python3-pip libraqm0 libraqm-dev
pip3 install pillow
```

### Option 2: Use Docker - EASIEST

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libraqm0 \
    libraqm-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Option 3: Build Pillow from Source (COMPLEX)

This requires installing Visual Studio Build Tools and many dependencies. Not recommended for most users.

## Code Behavior

The application automatically detects libraqm availability:

- **If libraqm is available**: Uses Jameel Noori Nastaleeq or Noto Nastaliq Urdu
- **If libraqm is NOT available**: Falls back to Arial font

You can check the status at: `http://localhost:8000/`

Response will show:
```json
{
  "urdu_support": true,
  "libraqm_available": false,
  "urdu_font": "Arial (fallback)"
}
```

## Recommendation

For **production use**, consider:
1. Deploy using **Docker** with libraqm support
2. This enables beautiful Nastaliq fonts automatically
3. No code changes needed - just deploy in the right environment!

For **development on Windows**:
- Current Arial solution works fine for testing
- Text is readable and properly formatted
- Can deploy to Linux server later for better fonts

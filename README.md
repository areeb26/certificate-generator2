# Certificate Generator API

A bilingual (English & Urdu) certificate generation system with Supabase PostgreSQL support.

## Features

- **Bilingual Support**: Generate certificates in English and Urdu
- **Urdu Text Processing**: Properly formatted Urdu text with connected characters (using arabic-reshaper & python-bidi)
- **Flexible Database**: Works with both SQLite (local dev) and PostgreSQL/Supabase (production)
- **Font Support**: Tahoma font for Urdu (with fallback to Nastaliq if libraqm available)
- **Web UI**: React-based frontend for template creation and certificate preview
- **REST API**: FastAPI backend for certificate generation

## Architecture

```
certificate-generator2/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── db.py                # Database abstraction layer
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variables template
│   ├── SUPABASE_SETUP.md   # Supabase setup guide
│   └── fonts/               # Font files
└── frontend/
    ├── src/
    │   ├── App.jsx          # React application
    │   └── index.css        # Styles
    └── package.json
```

## Quick Start

### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Database** (Choose one):

   **Option A: SQLite (Local Development - Default)**
   ```bash
   # No configuration needed! Works out of the box
   ```

   **Option B: PostgreSQL/Supabase (Production)**
   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit .env and set:
   # DATABASE_TYPE=postgresql
   # DATABASE_URL=your-supabase-connection-string
   ```

   See [SUPABASE_SETUP.md](backend/SUPABASE_SETUP.md) for detailed Supabase setup instructions.

3. **Run the Backend**
   ```bash
   python main.py
   ```

   Backend will be available at: `http://localhost:8000`

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the Frontend**
   ```bash
   npm run dev
   ```

   Frontend will be available at: `http://localhost:5173`

## Database Options

### SQLite (Default)
- **Best for**: Local development, testing, single-user scenarios
- **Setup**: Zero configuration
- **File**: `certificates.db` (created automatically)

### PostgreSQL/Supabase
- **Best for**: Production, multi-user, remote access
- **Setup**: Follow [SUPABASE_SETUP.md](backend/SUPABASE_SETUP.md)
- **Benefits**:
  - Cloud-hosted (no local database file)
  - Better scalability
  - Real-time features (optional)
  - Built-in authentication (optional)

The application automatically detects which database to use based on environment variables.

## API Endpoints

### Get API Info
```http
GET /
```
Returns API status, Urdu support, and database info.

### Create Template
```http
POST /api/template
Content-Type: application/json

{
  "name": "Certificate Template 1",
  "image_base64": "data:image/png;base64,...",
  "text_position": {"x": 500, "y": 300},
  "font": "Tahoma, sans-serif",
  "font_size": 48,
  "alignment": "center",
  "color": "#000000",
  "language": "ur"
}
```

### List Templates
```http
GET /api/templates
```

### Get Template Details
```http
GET /api/template/{template_id}
```

### Generate Certificate
```http
GET /api/certificate/{template_id}?name=علی%20احمد
```
Returns a PNG image with the name rendered on the certificate.

**Example (Urdu)**:
```
http://localhost:8000/api/certificate/1?name=%D8%B9%D9%84%DB%8C%20%D8%A7%D8%AD%D9%85%D8%AF
```

**Example (English)**:
```
http://localhost:8000/api/certificate/1?name=John%20Doe
```

## Urdu Font Support

### Current Setup (Working)
- **Font**: Tahoma
- **Processing**: arabic-reshaper + python-bidi
- **Features**: Connected characters, RTL direction
- **Compatibility**: Works on all platforms (Windows, Linux, Mac)

### Advanced Setup (Optional)
For beautiful Nastaliq calligraphy:
- **Requirement**: libraqm library
- **Fonts**: Jameel Noori Nastaleeq, Noto Nastaliq Urdu
- **Setup**: Use Docker or WSL (see SUPABASE_SETUP.md)
- **Auto-detection**: Application will use Nastaliq if libraqm is available

## Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Database Type: 'sqlite' or 'postgresql'
DATABASE_TYPE=sqlite

# SQLite Configuration
DATABASE_PATH=certificates.db

# PostgreSQL/Supabase Configuration (if using PostgreSQL)
# DATABASE_TYPE=postgresql
# DATABASE_URL=postgresql://postgres.[project-ref]:[password]@[host]:[port]/postgres
```

## Deployment

### Backend Deployment (Render, Railway, Fly.io)

1. **Set Environment Variables**:
   - `DATABASE_TYPE=postgresql`
   - `DATABASE_URL=your-supabase-connection-string`

2. **Deploy** using platform-specific instructions

### Frontend Deployment (Vercel, Netlify)

1. **Set Build Command**: `npm run build`
2. **Set Output Directory**: `dist`
3. **Set Environment Variable**:
   - `VITE_API_URL=https://your-backend-url.com`

## Development

### Project Structure

**Backend (FastAPI + Python)**:
- `main.py`: API routes and certificate generation logic
- `db.py`: Database abstraction supporting SQLite and PostgreSQL
- `requirements.txt`: Python dependencies

**Frontend (React + Vite)**:
- `App.jsx`: Main React component with template editor
- Canvas-based certificate preview
- Drag-and-drop text positioning

### Key Technologies

**Backend**:
- FastAPI - Modern web framework
- Pillow (PIL) - Image processing
- arabic-reshaper - Urdu character shaping
- python-bidi - Bidirectional text (RTL)
- psycopg2 - PostgreSQL driver
- python-dotenv - Environment variable management

**Frontend**:
- React 18
- Vite - Build tool
- TailwindCSS - Styling
- Lucide React - Icons

## Troubleshooting

### "Template not found" Error
- Make sure you've created a template first using POST /api/template
- Or upload a template through the web UI

### Urdu Text Not Displaying
- Check that `language` is set to `'ur'` in the template
- Verify arabic-reshaper and python-bidi are installed

### Database Connection Error (PostgreSQL)
- Verify your DATABASE_URL is correct
- Check that Supabase project is active
- Ensure the templates table exists (run SQL from SUPABASE_SETUP.md)

### Cannot See Certificate in Browser
- The API returns a PNG image directly
- Use an `<img>` tag or save the file
- Example: `<img src="http://localhost:8000/api/certificate/1?name=Ali" />`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both SQLite and PostgreSQL
5. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

- For Supabase setup: See [SUPABASE_SETUP.md](backend/SUPABASE_SETUP.md)
- For Urdu font issues: See [URDU_FONTS_GUIDE.md](backend/URDU_FONTS_GUIDE.md)
- For API documentation: Visit `http://localhost:8000/docs` (Swagger UI)

## Credits

- Urdu text processing: arabic-reshaper, python-bidi
- Fonts: Tahoma (Microsoft), Jameel Noori Nastaleeq, Noto Nastaliq Urdu (Google)

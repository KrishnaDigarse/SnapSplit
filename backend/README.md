# SnapSplit Backend

AI-powered bill scanning and expense splitting application backend.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis
- Tesseract OCR
- Groq API key

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Tesseract OCR:**
   - See [`docs/INSTALL_TESSERACT.md`](docs/INSTALL_TESSERACT.md) for detailed instructions

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required environment variables:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/snapsplit_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
GROQ_API_KEY=gsk_your_groq_key_here
```

4. **Run database migrations:**
```bash
alembic upgrade head
```

5. **Start the server:**
```bash
python -m uvicorn main:app --reload
```

Server will be available at `http://localhost:8000`

## 📋 Features

### AI Bill Scanning
- **Multi-strategy OCR** with quality scoring
- **Groq LLM** for data extraction (llama-3.3-70b-versatile)
- **Discount handling** and tax calculation
- **Validation** with auto-correction
- **100% success rate** on test images

### API Endpoints
- Authentication (register, login, logout)
- Group management
- Expense tracking
- Bill image upload and scanning
- Settlement calculations

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── ai/              # AI components (OCR, LLM, validation)
│   ├── api/             # API routes
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   └── utils/           # Utilities
├── tests/               # Test scripts and sample images
├── docs/                # Documentation
├── uploads/             # User uploaded files
├── requirements.txt     # Python dependencies
└── main.py             # Application entry point
```

## 🧪 Testing

Run batch tests on sample bills:
```bash
cd tests/debug_scripts
python batch_test_bills.py
```

See [`tests/README.md`](tests/README.md) for more testing options.

## 📚 Documentation

- **[Groq Setup Guide](docs/GROQ_SETUP.md)** - Get started with Groq API
- **[Batch Testing Guide](docs/BATCH_TESTING.md)** - Test multiple bill images
- **[Tesseract Installation](docs/INSTALL_TESSERACT.md)** - Install OCR engine
- **[API Documentation](docs/)** - Full API reference

## 🔧 Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL + SQLAlchemy
- **Cache:** Redis
- **OCR:** Tesseract + OpenCV
- **LLM:** Groq (llama-3.3-70b-versatile)
- **Image Processing:** Pillow, OpenCV

## 📊 Performance

- **OCR Speed:** ~2-3 seconds per image
- **LLM Speed:** ~1-2 seconds (Groq is fast!)
- **Total Processing:** ~5-10 seconds per bill
- **Success Rate:** 100% on test images

## 🛠️ Development

### Running in Development Mode
```bash
python -m uvicorn main:app --reload
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Environment Variables
See `.env.example` for all available configuration options.

## 🚀 Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Use a production-grade WSGI server (e.g., Gunicorn)
3. Set up proper database backups
4. Configure Redis for session management
5. Set up SSL/TLS certificates

## 📝 API Documentation

Once the server is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## 📄 License

[Your License Here]

## 🆘 Troubleshooting

### Tesseract not found
See [`docs/TESSERACT_FIX.md`](docs/TESSERACT_FIX.md)

### Database connection issues
Check your `DATABASE_URL` in `.env`

### Groq API errors
Verify your `GROQ_API_KEY` is valid

For more help, check the documentation in the `docs/` folder.

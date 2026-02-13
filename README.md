# Medical Deepfake Analyzer

A production-ready web application for medical image authenticity analysis using PyTorch models. The system analyzes knee X-ray images for authenticity and arthritis severity, and CT scans for authenticity detection.

## Architecture

- **Frontend**: SvelteKit with TypeScript, TailwindCSS, and PWA capabilities
- **Backend**: FastAPI with Python, using uv for dependency management
- **Communication**: REST API with JSON
- **Models**: PyTorch-based with mock implementations for demonstration

## Features

### Backend
- FastAPI REST API with structured logging
- Mock PyTorch models for knee X-ray and CT scan analysis
- File validation and security measures
- Rate limiting and CORS configuration
- Comprehensive error handling
- Health check endpoint

### Frontend
- Modern medical UI with drag-and-drop file upload
- Real-time analysis results with confidence indicators
- Local storage for upload history
- Progressive Web App (PWA) with offline capabilities
- Responsive design for mobile and desktop
- Medical-themed styling with DaisyUI components

## Project Structure

```
medical-deepfake-website/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration and logging
│   │   ├── models/       # PyTorch model implementations
│   │   ├── services/     # Business logic
│   │   ├── schemas/      # Pydantic models
│   │   └── utils/        # Utility functions
│   ├── tests/            # Test suite
│   ├── main.py           # FastAPI application entry point
│   ├── pyproject.toml    # Python dependencies (uv)
│   └── .env.example      # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── routes/       # SvelteKit pages
│   │   ├── lib/          # Utilities and API client
│   │   ├── components/   # Reusable components
│   │   └── styles/       # Global styles
│   ├── static/           # Static assets
│   ├── package.json      # Node.js dependencies
│   └── vite.config.ts    # Vite configuration with PWA
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- uv (Python package manager)
- Git

## Installation and Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd medical-deepfake-website/backend
```

2. Create Python environment with uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Copy environment variables:
```bash
cp .env.example .env
```

5. Start the development server:
```bash
uv run python main.py
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd medical-deepfake-website/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Health Check
- `GET /health` - Check API and model status

### Analysis Endpoints
- `POST /analyze/xray` - Analyze knee X-ray image
- `POST /analyze/ct` - Analyze CT scan image

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## Testing

### Backend Tests

Run the test suite using uv:

```bash
cd medical-deepfake-website/backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_models.py

# Run with verbose output
uv run pytest -v
```

### Frontend Tests

```bash
cd medical-deepfake-website/frontend

# Run type checking
npm run check

# Run linting
npm run lint
```

## Model Integration

### Adding Real Models

1. Replace mock implementations in `backend/app/models/`:

**For Knee X-ray Model (`xray_model.py`):**
```python
def load_model(self, model_path: str) -> None:
    # Replace with actual model loading
    self.model = torch.load(model_path, map_location=self.device)
    self.model.eval()
```

**For CT Scan Model (`ct_model.py`):**
```python
def load_model(self, model_path: str) -> None:
    # Replace with actual model loading
    self.model = torch.load(model_path, map_location=self.device)
    self.model.eval()
```

2. Update preprocessing and prediction methods as needed for your specific models.

3. Place model checkpoints in the `backend/models/` directory.

### GPU Inference

To enable GPU inference:

1. Update the `.env` file:
```env
DEVICE=cuda
```

2. Ensure CUDA-compatible PyTorch is installed:
```bash
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## Deployment

### Backend Deployment

1. **Using uvicorn (Production):**
```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

2. **Using Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml ./
RUN pip install uv && uv venv && .venv/bin/activate && uv pip install -e .

COPY . .
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

3. **Environment Variables:**
Set production environment variables:
```env
DEBUG=false
HOST=0.0.0.0
PORT=8000
DEVICE=cuda  # if GPU available
REDIS_URL=redis://redis:6379/0  # for rate limiting
```

### Frontend Deployment

1. **Build for Production:**
```bash
cd frontend
npm run build
```

2. **Deploy to Static Hosting:**
The `build/` directory can be deployed to any static hosting service (Vercel, Netlify, etc.).

3. **PWA Configuration:**
The application is pre-configured as a PWA. Service worker and manifest are automatically generated.

### Horizontal Scaling

For production scaling:

1. **Load Balancer:** Place API servers behind a load balancer
2. **Redis:** Configure Redis for shared rate limiting
3. **Model Servers:** Deploy inference workers on separate GPU servers
4. **File Storage:** Use cloud storage for uploaded files
5. **Monitoring:** Add health checks and monitoring

## Security Features

- File type and size validation
- CORS configuration
- Rate limiting with Redis
- Input sanitization
- Structured logging for audit trails
- No direct file execution risks

## Development

### Code Style

Backend uses `black` and `ruff` for formatting and linting:
```bash
uv run black app/
uv run ruff check app/
```

Frontend uses `prettier` and `eslint`:
```bash
npm run format
npm run lint
```

### Adding New Models

1. Create new model class in `backend/app/models/`
2. Implement the `BaseModel` interface
3. Add model to `ModelService`
4. Create corresponding API endpoint
5. Update frontend to support new model type

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the project for details.

## Support

For questions and support:
- Check the API documentation at `/docs`
- Review the test files for usage examples
- Check the logs for detailed error information

## Future Enhancements

- Authentication and authorization
- Real-time WebSocket updates
- Batch image processing
- Model versioning and A/B testing
- Advanced analytics dashboard
- Integration with DICOM standards
- Cloud deployment templates

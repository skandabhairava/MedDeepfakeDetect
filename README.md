# Medical Deepfake Analyzer

A comprehensive web application for medical image authenticity analysis using PyTorch models. The system analyzes knee X-ray images for authenticity and arthritis severity, and CT scans for authenticity detection with full user authentication and analysis history tracking.

## Architecture

- **Frontend**: SvelteKit with TypeScript, TailwindCSS, and component-based architecture
- **Backend**: FastAPI with Python, using uv for dependency management
- **Authentication**: JWT-based authentication with user management
- **Database**: SQLite for user data and analysis history
- **Communication**: REST API with JSON
- **Models**: PyTorch-based with mock implementations for demonstration

## Features

### Backend
- FastAPI REST API with structured logging and error handling
- JWT-based authentication system with user registration and login
- SQLite database for user management and analysis history
- Mock PyTorch models for knee X-ray and CT scan analysis
- File validation, security measures, and rate limiting
- CORS configuration and comprehensive API documentation
- Analysis history tracking with pagination
- Admin functionality for user management

### Frontend
- Modern medical UI with drag-and-drop file upload
- Real-time analysis results with confidence indicators and GradCAM visualization
- User authentication flow with login/logout functionality
- Personal dashboard and analysis history
- Profile management and password change
- Admin panel for user management
- Responsive design with mobile and desktop support
- Medical-themed styling with custom components
- Toast notifications and loading states

## Project Structure

```
medical-deepfake-website/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints (analyze, auth, health)
│   │   ├── core/         # Configuration and logging
│   │   ├── models/       # PyTorch models and database
│   │   ├── schemas/      # Pydantic models for requests/responses
│   │   ├── services/     # Business logic (auth, model service)
│   │   └── utils/        # Utility functions
│   ├── tests/            # Test suite
│   ├── main.py           # FastAPI application entry point
│   ├── pyproject.toml    # Python dependencies (uv)
│   ├── .env.example      # Environment variables template
│   └── medical_deepfake.db  # SQLite database
├── frontend/
│   ├── src/
│   │   ├── routes/       # SvelteKit pages (login, analyze, dashboard, etc.)
│   │   ├── lib/
│   │   │   ├── components/  # Reusable UI components
│   │   │   ├── services/    # API client services
│   │   │   ├── stores/       # Svelte stores for state management
│   │   │   ├── types/        # TypeScript type definitions
│   │   │   └── utils/        # Utility functions
│   │   └── app.css       # Global styles
│   ├── static/           # Static assets
│   ├── package.json      # Node.js dependencies
│   └── vite.config.ts    # Vite configuration
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

2. Create Python environment and Install dependencies using uv:
```bash
uv sync
```

3. Activate Environment:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Copy environment variables:
```bash
cp .env.example .env
```

5. Start the development server:
```bash
uv run main.py
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

3. Build the static HTML Pages:
```bash
npm run build
```

## Default Admin User

The system comes with a default admin user for initial setup:
- **Email**: admin@example.com
- **Password**: admin123

> **Important**: Change the default admin password after first login for security.

## Application Pages

### Public Pages
- **Home (`/`)**: Landing page with application overview
- **Login (`/login`)**: User authentication

### Authenticated Pages
- **Dashboard (`/dashboard`)**: User dashboard with recent analyses
- **Analysis (`/analyze`)**: Main analysis interface for X-ray and CT scans
- **History (`/history`)**: Paginated analysis history with management
- **Profile (`/profile`)**: User profile and password management

### Admin Pages
- **Admin (`/admin`)**: User management and system administration

## API Endpoints

### Authentication
- `POST /auth/login` - User login and token generation
- `POST /auth/register` - Create new user (admin only)
- `GET /auth/me` - Get current user information
- `POST /auth/change-password` - Change user password
- `GET /auth/history` - Get user analysis history
- `DELETE /auth/history/{id}` - Delete analysis history item

### Analysis
- `POST /analyze/xray` - Analyze knee X-ray image
- `POST /analyze/ct` - Analyze CT scan image

### Health Check
- `GET /health` - Check API and model status

## Analysis Features

### Knee X-Ray Analysis
- **Authenticity Detection**: Determines if the X-ray is authentic or potentially manipulated
- **Arthritis Severity**: Classifies arthritis severity (Normal, Mild, Moderate, Severe)
- **GradCAM Visualization**: Shows regions of interest for model decisions
- **Confidence Scores**: Provides confidence levels for all predictions

### CT Scan Analysis
- **Authenticity Detection**: Determines if the CT scan is authentic or potentially manipulated
- **GradCAM Visualization**: Highlights areas used for authenticity determination
- **Detailed Metrics**: Processing time, model information, and device used

## Database Schema

### Users Table
- `id`: Primary key
- `account_name`: User's display name
- `email`: Unique email address
- `password_hash`: Bcrypt hashed password
- `is_admin`: Admin flag
- `created_at`: Account creation timestamp

### Analysis History Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `analysis_type`: Type of analysis (xray/ct)
- `filename`: Original filename
- `name`: User-provided analysis name
- `image_base64`: Base64 encoded image
- `results`: JSON results from analysis
- `confidence`: Overall confidence score
- `timestamp`: Analysis timestamp

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

## Configuration

### Environment Variables

Backend configuration via `.env` file:

```env
# Application Settings
APP_NAME="Medical Deepfake Backend"
APP_VERSION="0.1.0"
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR="uploads"
ALLOWED_EXTENSIONS=["jpg", "jpeg", "png", "dicom", "dcm"]

# Model Settings
MODEL_DIR="models"
INFERENCE_TIMEOUT=30
DEVICE="cpu"  # Change to "cuda" for GPU inference

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="json"
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

### Horizontal Scaling

For production scaling:

1. **Load Balancer:** Place API servers behind a load balancer
2. **Database:** Consider PostgreSQL for multi-instance deployments
3. **Redis:** Configure Redis for shared rate limiting
4. **Model Servers:** Deploy inference workers on separate GPU servers
5. **File Storage:** Use cloud storage for uploaded files
6. **Monitoring:** Add health checks and monitoring

## Security Features

- JWT-based authentication with secure token handling
- File type and size validation
- CORS configuration
- Rate limiting with Redis support
- Input sanitization and validation
- Structured logging for audit trails
- Password hashing with bcrypt
- Role-based access control (admin/user)
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

### Adding New Pages

1. Create new Svelte component in `frontend/src/routes/`
2. Add navigation item in `Navigation.svelte`
3. Update route protection in layout if needed
4. Add any required API services

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

- DICOM file format support
- Real-time WebSocket updates for long-running analyses
- Batch image processing capabilities
- Model versioning and A/B testing
- Advanced analytics dashboard
- Integration with PACS systems
- Cloud deployment templates (AWS, GCP, Azure)
- Mobile application
- Multi-language support
- Export functionality (PDF reports)
- Integration with hospital information systems

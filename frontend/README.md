# Medical Deepfake Detection Frontend

A modern SvelteKit frontend for medical image analysis with deepfake detection and arthritis assessment capabilities.

## Features

- **JWT Authentication**: Secure login system with admin user management
- **Image Analysis**: Support for Knee X-ray and CT scan analysis
- **Deepfake Detection**: Advanced CNN-based authenticity detection
- **Arthritis Assessment**: Severity classification for knee X-rays
- **GradCAM Visualization**: Base64 decoded model explanations
- **Analysis History**: Paginated history with detailed results
- **Responsive Design**: Mobile-first UI with Tailwind CSS
- **Error Handling**: Comprehensive error notifications
- **Static Compilation**: Optimized for static deployment

## Tech Stack

- **Framework**: SvelteKit with TypeScript
- **Styling**: Tailwind CSS with custom components
- **Icons**: Lucide Svelte
- **UI Components**: Custom components with animations
- **State Management**: Svelte stores
- **API Client**: Custom fetch wrapper with error handling

## Project Structure

```
src/
├── lib/
│   ├── components/          # Reusable UI components
│   │   ├── Navigation.svelte
│   │   └── ToastContainer.svelte
│   ├── services/           # API and business logic
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── analysis.ts
│   ├── stores/             # Svelte stores
│   │   ├── auth.ts
│   │   └── toast.ts
│   ├── types/              # TypeScript definitions
│   │   └── index.ts
│   └── utils.ts            # Utility functions
├── routes/                 # SvelteKit pages
│   ├── +layout.svelte
│   ├── +page.svelte
│   ├── login/
│   ├── dashboard/
│   ├── analyze/
│   ├── history/
│   ├── profile/
│   └── admin/
└── app.css               # Global styles
```

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
```bash
VITE_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## API Integration

The frontend integrates with the FastAPI backend at `/api` endpoints:

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - Create user (admin only)
- `GET /auth/me` - Get current user
- `POST /auth/change-password` - Change password
- `GET /auth/history` - Get analysis history

### Analysis
- `POST /analyze/xray` - Analyze knee X-ray
- `POST /analyze/ct` - Analyze CT scan

## Key Features

### Authentication System
- JWT-based authentication with automatic token refresh
- Role-based access control (admin/user)
- Secure password management
- Session persistence

### Image Analysis Interface
- Drag-and-drop file upload
- Real-time analysis progress
- Comprehensive result display
- GradCAM visualization support

### Responsive Design
- Mobile-first approach
- Smooth animations and transitions
- Accessible UI components
- Dark mode support (future)

### Error Handling
- Comprehensive error notifications
- API error response handling
- User-friendly error messages
- Graceful degradation

## Deployment

The application is configured for static deployment using `@sveltejs/adapter-static`. The build output is optimized for serving from any static web server or CDN.

## Environment Variables

- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## Contributing

1. Follow the existing code style
2. Use TypeScript for type safety
3. Add proper error handling
4. Test responsive design
5. Update documentation

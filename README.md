# Protected Vision - Backend

This is the Django backend for the Protected Vision application, an AI-powered sensitive information detection and protection system.

## Features

- User authentication and profile management
- Document upload and management
- Sensitive information detection using AI/ML
- Document scanning and risk assessment
- API for mobile app integration

## Technology Stack

- Django 4.2
- Django REST Framework
- SQLite (development) / PostgreSQL (production)
- JWT Authentication
- OpenCV for image processing
- YOLO for object detection (documents, credit cards)
- Hugging Face models for text analysis

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (optional but recommended)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/protected-vision-backend.git
   cd protected-vision-backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

### API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Log in and get access token
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password

### Documents

- `GET /api/documents/` - List all user documents
- `POST /api/documents/` - Upload a new document
- `GET /api/documents/{id}/` - Get document details
- `DELETE /api/documents/{id}/` - Delete a document
- `GET /api/documents/{id}/scans/` - Get all scans for a document
- `GET /api/documents/scans/` - List all document scans

### Detection

- `POST /api/detection/analyze/` - Analyze a document for sensitive information
- `GET /api/detection/models/` - List available detection models
- `GET /api/detection/jobs/` - List detection jobs

## ML Model Integration

The backend is designed to work with custom trained ML models:

1. YOLO model for detecting credit cards, IDs, and licenses
2. Hugging Face models for detecting PII in text

Currently, the implementation uses mock detection results. To integrate your trained models:

1. Place your YOLO weights in the `detection/models/` directory
2. Update the `ML_MODELS` settings in `settings.py`
3. Implement the actual detection logic in the `detection_service.py` file

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please contact your-email@example.com 
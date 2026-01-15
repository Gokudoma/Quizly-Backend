# Quizly Backend

Quizly is a Django-based REST API that automatically generates interactive quizzes from YouTube videos using AI. It leverages **OpenAI Whisper** for audio transcription and **Google Gemini** for content analysis and question generation.

## 🚀 Features

* **AI-Powered Quiz Generation:** Converts any YouTube video into a structured quiz (Title, Description, Questions, Answers).
* **Audio Processing:** Automatically downloads and transcribes audio from YouTube videos using `yt-dlp` and `whisper`.
* **Quiz Management:** Full CRUD (Create, Read, Update, Delete) capabilities for user quizzes.
* **Authentication:** Secure JWT-based authentication via HTTP-only cookies.
* **RESTful API:** Built with Django REST Framework for easy frontend integration.

## 🛠 Tech Stack

* **Framework:** Django 5, Django REST Framework
* **AI & ML:** * `openai-whisper` (Transcription)
    * `google-genai` (Quiz Generation)
* **Utilities:** `yt-dlp` (YouTube Downloader)
* **Database:** SQLite (default) / Configurable

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

* **Python 3.10+**
* **FFmpeg** (Required for audio processing by Whisper/yt-dlp)
    * *Windows:* `choco install ffmpeg` or download binaries.
    * *Mac:* `brew install ffmpeg`
    * *Linux:* `sudo apt install ffmpeg`

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/quizly-backend.git](https://github.com/yourusername/quizly-backend.git)
    cd quizly-backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🔐 Configuration

Create a `.env` file in the root directory (same level as `manage.py`) and add the following environment variables. 

> **Note:** You need a Google Gemini API Key.

```env
# .env file
DEBUG=True
SECRET_KEY=your-secure-django-secret-key
GEMINI_API_KEY=your_google_gemini_api_key_here



🏃‍♂️ Running the Application

1. Apply database migrations:

```bash
python manage.py migrate

2. Start the development server:

```bash
python manage.py runserver


The API will be available at http://127.0.0.1:8000/.



🔌 API Endpoints
Authentication
POST /api/auth/register/ - Register a new user

POST /api/auth/login/ - Login (Returns HTTP-only JWT cookie)

POST /api/auth/refresh/ - Refresh Access Token

Quizzes
POST /api/quiz/create/ - Generate a new quiz

Body: {"url": "https://youtube.com/..."}

Process: Downloads video -> Transcribes -> Generates Quiz via AI.

GET /api/quiz/ - List all quizzes for the authenticated user

GET /api/quiz/<id>/ - Retrieve details of a specific quiz

PATCH /api/quiz/<id>/ - Update quiz details

DELETE /api/quiz/<id>/ - Delete a quiz
# EchoMind AI

**"Your intelligent personal action assistant is ready!"**

## Overview
EchoMind AI is an AI-powered personal action assistant that understands natural-language requests and converts them into useful actions like task management and reminders.

## Key Features
- **Natural Language Understanding:** Add tasks or reminders using plain English.
- **Task Management (CRUD):** Create, list, complete, and delete tasks.
- **Smart Reminders:** Set reminders with natural language dates and times.
- **Voice Interaction:** Speak directly to EchoMind using your browser's microphone.
- **Responsive Dashboard:** View a summary of your tasks and upcoming reminders.

## Technology Stack
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** HTML, CSS, JavaScript (No heavy frameworks)
- **AI Integration:** Google Generative AI (Gemini Flash) with offline fallback

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your `AI_API_KEY` (if you don't have one, it will run in fallback mode).

## Running Locally
1. Start the backend:
   ```bash
   uvicorn main:app --reload
   ```
2. Open `frontend/index.html` in your web browser.

## API Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /chat` - Send natural language text
- `GET, POST, PUT, DELETE /tasks` - Task CRUD
- `GET, POST, PUT, DELETE /reminders` - Reminder CRUD

## Future Scope
- Calendar and email integration
- Multi-user accounts
- Advanced proactive AI suggestions

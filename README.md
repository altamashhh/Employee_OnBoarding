# 🚀 OnboardAI — AI-Powered Employee Onboarding Platform

An intelligent employee onboarding platform that uses **RAG (Retrieval-Augmented Generation)** with Google Gemini to provide personalized onboarding experiences.

## ✨ Features

- **AI Chatbot** — Ask questions about company policies, benefits, and tasks (powered by RAG)
- **30-Day Onboarding Plan** — Auto-generated personalized plans based on role & experience
- **Document Upload** — Upload company documents to build the knowledge base
- **Interactive Dashboard** — Track onboarding progress and pending tasks

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, TailwindCSS, Framer Motion |
| Backend | FastAPI, Python, LangChain |
| AI/LLM | Google Gemini API |
| Vector DB | ChromaDB |
| Embeddings | Google Generative AI Embeddings |

## 📁 Project Structure

```
├── onboardai/          # React frontend
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/      # Page components (Dashboard, Chat, Plan, Profile)
│   │   ├── services/   # API service layer
│   │   └── main.tsx    # App entry point
│   └── vite.config.ts  # Vite config with proxy setup
│
├── backend/            # FastAPI backend
│   ├── core/           # Config and initialization
│   ├── routes/         # API route handlers
│   ├── services/       # Business logic (RAG, chat, plans)
│   ├── models/         # Pydantic models
│   ├── db/             # Vector store setup
│   └── main.py         # FastAPI entry point
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Google Gemini API Key

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requrement.txt
```

Create a `.env` file in the `backend/` folder:
```env
GEMINI_API_KEY=your_api_key_here
```

Start the backend:
```bash
python -m uvicorn main:app --reload --port 8001
```

### Frontend Setup
```bash
cd onboardai
npm install
npm run dev
```

The app will be available at **http://localhost:3000**

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/upload` | Upload a document |
| GET | `/documents` | List uploaded documents |
| POST | `/chat` | Send a chat message |
| GET | `/chat/history/{user_id}` | Get chat history |
| DELETE | `/chat/history/{user_id}` | Clear chat history |
| POST | `/generate-plan` | Generate 30-day plan |

## 📄 License

MIT

# Zomato AI Assistant

An intelligent, full-stack restaurant recommendation engine inspired by Zomato. The application combines structured data filtering with the power of Large Language Models (LLMs) to generate highly personalized, human-like restaurant suggestions based on user preferences.

## 🌟 Live Demo
- **Frontend (UI):** [https://zomato-ai-assistance.vercel.app/](https://zomato-ai-assistance.vercel.app/)
- **Backend API:** [Railway Deployment](https://zomato-ai-assistance-production.up.railway.app/docs)

---

## 🏗️ Architecture

The project is structured into **8 distinct phases**, demonstrating a clean progression from raw data ingestion to a fully deployed cloud application:

1. **Phase 1: Ingestion** – Streams the [Zomato Restaurant Dataset](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) from Hugging Face and cleans the data using strict `Pydantic` models.
2. **Phase 2 & 3: Preferences & Integration** – Captures user inputs (Location, Budget, Cuisines, Rating) and applies deterministic filtering (to minimize LLM hallucinations and token usage).
3. **Phase 4: LLM Engine** – Constructs an intelligent prompt payload and streams it to **Groq (Llama 3.3 70B)** to rank candidates and generate personalized explanations.
4. **Phase 5: CLI** – A rich terminal interface using `Typer` and `Rich` for local testing.
5. **Phase 6: Backend API** – A blazing-fast **FastAPI** server exposing RESTful endpoints.
6. **Phase 7: Frontend UI** – A premium, glassmorphism-styled **Next.js** application.
7. **Phase 8: Deployment** – CI/CD configurations for **Railway** (Backend) and **Vercel** (Frontend).

---

## 🛠️ Tech Stack

- **Frontend:** Next.js (App Router), React, Vanilla CSS
- **Backend:** Python 3.9+, FastAPI, Uvicorn, Pydantic
- **AI Engine:** Groq API (`llama-3.3-70b-versatile`)
- **Data Pipeline:** Hugging Face `datasets`, Pandas
- **Hosting:** Vercel (Client), Railway (Server)

---

## 🚀 Running Locally

### 1. Backend (FastAPI)
You need Python 3.9+ installed.

```bash
# Clone the repository
git clone https://github.com/Satyamp32/Zomato-Ai-Assistance.git
cd Zomato-Ai-Assistance

# Set up virtual environment
python -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -e .

# Configure environment variables
# Create a .env file and add your GROQ_API_KEY
echo "GROQ_API_KEY=your_key_here" > .env

# Run the API server
uvicorn milestone1.phase6_api.app:app --reload
```
*The backend will be live at `http://localhost:8000/docs`.*

### 2. Frontend (Next.js)
You need Node.js `v18+` installed.

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
*The UI will be live at `http://localhost:3000`.*

---

## 🧠 How the AI Works
Instead of feeding the entire dataset into the LLM (which is slow, expensive, and error-prone), we use a **RAG-inspired filtering approach**:
1. **Pre-filter:** Fast exact-match filtering on Location, minimum Rating, and Cuisine using Python.
2. **Context Assembly:** The top matching candidates are injected into a highly specific system prompt.
3. **Reasoning:** Groq evaluates the candidates against the user's specific budget and lifestyle parameters, ranking the top 5 and generating a distinct `explanation` for *why* it fits the user.

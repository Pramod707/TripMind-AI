<div align="center">

# ✈️ TripMind AI

### Multi-Agent AI Travel Planner

**Turn a travel request into a personalized itinerary with flight research, hotel research, and a consolidated travel plan.**

Built with **Python · LangGraph · Groq · Streamlit · PostgreSQL**

</div>

---

## 📸 Application Preview

> Screenshots are stored in the project's `outputs/` directory. These links work when the README is placed at the repository root and the images are committed to Git.

### Home Page

![TripMind AI home page](outputs/homepage.png)

### Travel Preferences

![TripMind AI planning inputs](outputs/planing_inputs.png)

### Generated Travel Plan

![TripMind AI generated travel plan](outputs/generated_plan.png)

## 🌍 Overview

**TripMind AI** is a multi-agent travel planning application that transforms a natural-language travel request into a structured travel recommendation. It coordinates specialized agents for flight information, hotel research, itinerary creation, and final response generation.

Users can describe their departure location, destination, dates, number of travelers, budget, and interests through a Streamlit interface. The application orchestrates the planning workflow using LangGraph and displays the generated results in a travel-focused dashboard.

## ✨ Features

- **Natural-language trip planning** — Submit travel requirements in plain English.
- **Multi-agent orchestration** — Separate flight, hotel, itinerary, and final recommendation agents.
- **Flight research** — Retrieve available flight records through AviationStack.
- **Hotel research** — Search for relevant accommodation information with Tavily.
- **Personalized itineraries** — Generate day-by-day travel suggestions using a Groq-hosted LLM.
- **Consolidated recommendation** — Present one primary travel plan with a budget breakdown.
- **Session persistence** — Use PostgreSQL-backed LangGraph checkpoints to preserve graph state.
- **Interactive interface** — Streamlit UI with travel imagery and visual presentation of results.

> **Data accuracy:** Flight status records are not the same as live ticket offers. Flight fares, hotel rates, schedules, availability, and estimated budgets must be independently verified before booking.

## 🧠 Multi-Agent Architecture

```mermaid
flowchart TD
    A[Traveler's Request] --> B[Streamlit Frontend]
    B --> C[LangGraph Workflow]
    C --> D[Flight Agent]
    D --> E[Hotel Agent]
    E --> F[Itinerary Agent]
    F --> G[Final Agent]
    G --> H[Travel Recommendation]
    H --> B

    D -.-> I[AviationStack API]
    E -.-> J[Tavily Search]
    F -.-> K[Groq LLM]
    G -.-> K
    C <-. Checkpoints .-> L[(PostgreSQL)]
```

### Agent Responsibilities

| Agent               | Responsibility                                                                     |
| ------------------- | ---------------------------------------------------------------------------------- |
| **Flight Agent**    | Requests flight records and passes available information to the planning workflow. |
| **Hotel Agent**     | Searches for accommodation information relevant to the travel request.             |
| **Itinerary Agent** | Builds a day-by-day travel itinerary using the available research.                 |
| **Final Agent**     | Combines the research and itinerary into one readable travel recommendation.       |

## 🛠️ Tech Stack

| Layer                            | Technology                                      |
| -------------------------------- | ----------------------------------------------- |
| Language                         | Python                                          |
| Agent orchestration              | LangGraph                                       |
| LLM integration                  | LangChain and Groq                              |
| Frontend                         | Streamlit                                       |
| Flight data                      | AviationStack API                               |
| Hotel / web research             | Tavily                                          |
| Checkpoint storage               | PostgreSQL with LangGraph Postgres checkpointer |
| Environment configuration        | python-dotenv                                   |
| Package / environment management | uv                                              |

## 📁 Project Structure

```text
TripMind-AI/
├── .agents/
├── .claude/
├── .github/
├── .vscode/
├── frontend/
│   └── streamlit_app.py
├── outputs/
│   ├── generated_plan.png
│   ├── homepage.png
│   └── planing_inputs.png
├── tools/
├── travel_plans/
├── .env                 # Local secrets; do not commit
├── .gitignore
├── .python-version
├── main.py              # LangGraph workflow and agents
├── pyproject.toml
├── README.md
├── req.txt
├── setting.json
├── test.py
└── uv.lock
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/TripMind-AI.git
cd TripMind-AI
```

Replace `<your-username>` with your GitHub username and adjust the repository URL if needed.

### 2. Install dependencies

Install [uv](https://docs.astral.sh/uv/) if it is not already available, then run:

```bash
uv sync
```

This installs the dependencies declared in `pyproject.toml` and uses the lockfile when available.

### 3. Configure environment variables

Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/tripmind
```

The exact database name, credentials, and PostgreSQL setup depend on your local environment. Never commit `.env` or actual credentials.

### 4. Prepare PostgreSQL

Create a PostgreSQL database and set `DATABASE_URL` to its connection string. The backend uses a LangGraph PostgreSQL checkpointer; ensure its required tables are initialized according to the project's backend setup.

### 5. Start the application

From the project root:

```bash
uv run streamlit run frontend/streamlit_app.py
```

Open the local URL shown by Streamlit, typically `http://localhost:8501`.

## 🧭 How It Works

1. **Describe your trip** — Provide the route, travel dates, travelers, budget, and preferences.
2. **Collect research** — Flight and hotel agents request information from their respective tools.
3. **Build an itinerary** — The itinerary agent uses the request and collected research to propose activities.
4. **Generate a recommendation** — The final agent formats the result into a unified travel plan.
5. **Review the results** — View the plan and available research in Streamlit, then verify booking details externally.

### Example Request

> Plan a 5-night trip from Hyderabad to London for two adults, departing December 15, 2026, with a total budget of ₹200,000. Include historical attractions, local food, and a practical day-by-day itinerary.

## 🔐 Security

Keep credentials in environment variables and exclude `.env`, local virtual environments, and sensitive checkpoint exports from Git. Do not expose API keys in screenshots, logs, or frontend responses.

## 📄 License

No license is specified in this README. Add a `LICENSE` file if you intend to grant others permission to use, modify, or redistribute the project.

---

<div align="center">

**TripMind AI — Travel planning powered by collaborative AI agents.**

</div>

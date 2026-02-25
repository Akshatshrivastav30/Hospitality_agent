# 🏨 TripMate: Agentic AI Luxury Concierge

**TripMate** is a next-generation travel orchestration system that uses a **Multi-Agent Graph (LangGraph)** to curate bespoke luxury itineraries. Unlike static chatbots, TripMate employs specialized autonomous agents to research the live web, validate domain relevance, and synthesize professional hospitality reports in real-time.

---

## 🚀 The Agentic Architecture

TripMate doesn't just "chat"; it **thinks and researches**. The system is built on a Directed Acyclic Graph (DAG) that coordinates three specialized AI agents:

1. **🛡️ The Gatekeeper:** Analyzes user intent to ensure the query is travel-related, preventing hallucinations and off-topic compute waste.

2. **🔍 The Researcher:** Powerd by **Tavily AI**, this agent browses the live web to find current events, 5-star dining, and luxury accommodations.

3. **✍️ The Executive Writer:** Consolidates research data into a high-end, Markdown-rendered itinerary tailored to the requested duration.

---

## ✨ Key Features

- **Real-Time RAG:** Uses Retrieval-Augmented Generation to ensure data is current (no 2023 training data limits).

- **Ultra-Fast Inference:** Powered by **Llama 3.3 70B on Groq LPUs**, delivering complex agentic loops in < 5 seconds.

- **Luxury Dashboard:** A bespoke Django-based web interface featuring:
  
  - Interactive loading states while agents "deliberate."
  
  - Dynamic HTML rendering of AI-generated Markdown.
  
  - Clean, "Silent Luxury" UI design.

- **Domain Guardrails:** Built-in safety nodes to keep the AI focused strictly on hospitality.

---

## 🛠️ Tech Stack

| **Layer**            | **Technology**                        |
| -------------------- | ------------------------------------- |
| **Backend**          | Django (Python)                       |
| **AI Orchestration** | LangGraph                             |
| **LLM Engine**       | Llama 3.3 70B (via Groq)              |
| **Search Engine**    | Tavily AI API                         |
| **Frontend**         | HTML5, CSS3, JavaScript               |
| **Formatting**       | Python-Markdown + Django Safe Filters |

---

## 📦 Installation & Setup

1. **Clone the repository**
   
   Bash
   
   ```
   git clone https://github.com/your-username/tripmate-ai.git
   cd tripmate-ai
   ```

2. **Set up Virtual Environment**
   
   Bash
   
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   
   Bash
   
   ```
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   
   Create a `.env` file in the root directory:
   
   Code snippet
   
   ```
   GROQ_API_KEY=your_groq_key
   TAVILY_API_KEY=your_tavily_key
   SECRET_KEY=your_django_secret_key
   ```

5. **Run the Dashboard**
   
   Bash
   
   ```
   python manage.py migrate
   python manage.py runserver
   ```

---

## 📸 Dashboard Preview

> ![](/Users/akshatshrivastav/Desktop/Screenshot%202026-02-24%20at%209.57.15 PM.png)

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🤝 Contact

**Akshat Shrivastav** - [Your LinkedIn] - [Your Email]

*Project Link: [https://github.com/your-username/tripmate-ai](https://www.google.com/search?q=https://github.com/your-username/tripmate-ai)*

# FinPulse AI - Multi-Agent Financial Research Platform

A personal multi-agent financial research and market analysis platform for the Indian Stock Market (NSE/BSE, Mutual Funds, and Technical/Fundamental Analysis). Powered by autonomous agents, Model Context Protocol (MCP) live market tools, and an asynchronous task runner with a Streamlit interface.

---

## Architecture Overview

```
+-------------------------------------------------------------+
|                     Streamlit Web UI                        |
|                         (app.py)                            |
+------------------------------+------------------------------+
                               | (HTTP / REST)
                               v
+-------------------------------------------------------------+
|                       FastAPI Backend                       |
|                          (api.py)                           |
|       +---------------------------------------------+       |
|       | Background Job Runner & SQLite Persistence  |       |
|       +----------------------+----------------------+       |
+------------------------------|------------------------------+
                               v
+-------------------------------------------------------------+
|                Supervisor Agent (LangGraph)                 |
|       Dispatches tasks across 8 specialized agents          |
+------------------------------+------------------------------+
                               |
       +-----------------------+-----------------------+
       |                       |                       |
       v                       v                       v
[Fundamental]             [Technical]             [Sentiment]
[Portfolio]               [Risk Manager]          [Valuation]
[Tax Strategist]          [Mutual Funds]          
                               |
                               v
+-------------------------------------------------------------+
|                 Model Context Protocol (MCP)                |
|                    (indian-market-mcp)                      |
|      Live NSE/BSE quotes, historical prices, AMFI NAV       |
+-------------------------------------------------------------+
```

---

## Project Structure

```text
personal/
├── app.py                     # Streamlit frontend application
├── api.py                     # FastAPI server with background job manager
├── guardrails.py              # NeMo guardrails / query safety checks
├── main.py                    # Direct CLI execution entrypoint
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Standard git exclusions
├── agents/                    # 8 specialist agents & supervisor logic
├── config/                    # System prompts and agent settings
├── llm/                       # Model client initialization
├── market_mcp/                # Client bindings for MCP tools
└── tools/
    └── indian-market-mcp/     # Standalone Docker MCP tool server
```

---

## Setup & Getting Started

### 1. Start the Market MCP Tool Server
The MCP server provides live Indian market feeds and financial data tools via Docker:

```bash
cd tools/indian-market-mcp
docker build -t indian-market-mcp .
docker run -d --name indian-market-mcp -p 8000:8000 indian-market-mcp
```

Verify that the server is active at `http://127.0.0.1:8000/mcp`.

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Set your credentials:
```env
OPENAI_API_BASE_URL=https://llmlite-cognivus.duckdns.org/v1
OPENAI_API_KEY=your_key_here
MODEL=gpt-4o
MCP_URL=http://127.0.0.1:8000/mcp
API_BASE_URL=http://127.0.0.1:8001
```

### 3. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the Backend API
```bash
python3 api.py
```
The API starts at `http://127.0.0.1:8001`.

### 5. Launch the Streamlit Frontend
In a separate terminal window:
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

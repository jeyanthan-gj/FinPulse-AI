import asyncio
import json
import sqlite3
import uuid
from contextlib import asynccontextmanager
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from guardrails import MarketGuardrails
from agents.research_synthesis_agent.agent import (
    DB_PATH,
    create_research_synthesis_supervisor,
)

# Global holder for the supervisor agent
agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    # Ensure database schema is ready on startup
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_titles (
                thread_id TEXT PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'processing',
                result TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
            """
        )
        conn.commit()

    print("Initializing Research Synthesis Supervisor for API...")
    agent = await create_research_synthesis_supervisor()
    print("Supervisor API ready.")
    yield


app = FastAPI(
    title="Indian Market Research AI API",
    description="B2B Agentic API with persistent SQLite session management and background jobs",
    version="1.1.0",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class StartSessionRequest(BaseModel):
    session_id: Optional[str] = Field(
        default=None,
        description="Optional custom session ID / topic name. Auto-generated if omitted.",
    )
    initial_message: Optional[str] = Field(
        default=None,
        description="Optional first research question to run on session creation.",
    )


class ContinueSessionRequest(BaseModel):
    message: str = Field(..., description="The user's follow-up research question.")


class SessionResponse(BaseModel):
    session_id: str
    status: str
    message: Optional[str] = None
    response: Optional[str] = None


class SessionSummary(BaseModel):
    session_id: str
    title: Optional[str] = None
    checkpoint_count: int
    last_updated: Optional[str] = None


class SubmitJobRequest(BaseModel):
    message: str = Field(..., description="User question or research prompt")
    session_id: Optional[str] = Field(default=None, description="Session ID (auto-created if None)")


class SubmitJobResponse(BaseModel):
    job_id: str
    session_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    session_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def save_session_title(session_id: str, first_message: str):
    """Save the first user message as the title of the session if not set."""
    if not first_message or not first_message.strip():
        return
    clean_title = first_message.strip().replace("\n", " ")
    if len(clean_title) > 60:
        clean_title = clean_title[:57] + "..."
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO session_titles (thread_id, title)
            VALUES (?, ?)
            """,
            (session_id, clean_title),
        )
        conn.commit()


async def run_agent_message(session_id: str, message: str) -> str:
    """Helper to invoke the agent for a given session thread and return response."""
    try:
        save_session_title(session_id, message)
    except Exception:
        pass

    # 1. Check Input Guardrails (0 tokens burned for greetings / off-topic)
    guarded_response = MarketGuardrails.check_input_rails(message)
    if guarded_response:
        return guarded_response

    # 2. Invoke full Multi-Agent Research Supervisor
    global agent
    if agent is None:
        agent = await create_research_synthesis_supervisor()

    config = {"configurable": {"thread_id": session_id}}

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )

    messages = result.get("messages", [])
    if messages:
        final_msg = messages[-1]
        return final_msg.content if hasattr(final_msg, "content") else str(final_msg)
    return "No response returned from research supervisor."


async def process_background_job(job_id: str, session_id: str, message: str):
    """Asynchronous worker that runs the full agent in background without blocking HTTP."""
    try:
        reply = await run_agent_message(session_id, message)
        with get_db_connection() as conn:
            conn.execute(
                """
                UPDATE jobs 
                SET status = 'completed', result = ?, completed_at = CURRENT_TIMESTAMP
                WHERE job_id = ?
                """,
                (reply, job_id),
            )
            conn.commit()
    except Exception as e:
        with get_db_connection() as conn:
            conn.execute(
                """
                UPDATE jobs 
                SET status = 'failed', error = ?, completed_at = CURRENT_TIMESTAMP
                WHERE job_id = ?
                """,
                (str(e), job_id),
            )
            conn.commit()


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Indian Market Research AI",
        "status": "online",
        "database": DB_PATH,
    }


# ------------------------------------------------------------
# ASYNC JOB ENDPOINTS (ZERO-TIMEOUT FOR STREAMLIT / WEB APPS)
# ------------------------------------------------------------

@app.post("/jobs/submit", response_model=SubmitJobResponse, status_code=202, tags=["Jobs"])
async def submit_job(req: SubmitJobRequest):
    """
    Submit a research inquiry asynchronously.
    Returns in <20ms with a job_id. Prevents HTTP read timeouts.
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    session_id = req.session_id.strip() if req.session_id else f"session_{uuid.uuid4().hex[:8]}"
    job_id = f"job_{uuid.uuid4().hex[:12]}"

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO jobs (job_id, session_id, message, status)
            VALUES (?, ?, ?, 'processing')
            """,
            (job_id, session_id, req.message.strip()),
        )
        conn.commit()

    # Launch agent workflow in background
    asyncio.create_task(process_background_job(job_id, session_id, req.message.strip()))

    return SubmitJobResponse(
        job_id=job_id,
        session_id=session_id,
        status="processing",
        message="Job submitted successfully. Poll /jobs/{job_id} for status.",
    )


@app.get("/jobs/{job_id}", response_model=JobStatusResponse, tags=["Jobs"])
async def get_job_status(job_id: str):
    """
    Poll the status of an asynchronous research job.
    Returns immediately with status: 'processing', 'completed', or 'failed'.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT job_id, session_id, status, result, error FROM jobs WHERE job_id = ?",
            (job_id,),
        )
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return JobStatusResponse(
        job_id=row["job_id"],
        session_id=row["session_id"],
        status=row["status"],
        result=row["result"],
        error=row["error"],
    )


# ------------------------------------------------------------
# SESSION MANAGEMENT ENDPOINTS
# ------------------------------------------------------------

@app.post("/sessions/start", response_model=SessionResponse, tags=["Sessions"])
async def start_session(req: StartSessionRequest):
    """
    Start a brand new research session synchronously.
    """
    session_id = req.session_id.strip() if req.session_id else f"session_{uuid.uuid4().hex[:8]}"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM checkpoints WHERE thread_id = ? LIMIT 1", (session_id,))
        if cursor.fetchone() and not req.initial_message:
            raise HTTPException(
                status_code=400,
                detail=f"Session '{session_id}' already exists. Use /sessions/{session_id}/continue instead.",
            )

    ai_response = None
    if req.initial_message:
        try:
            ai_response = await run_agent_message(session_id, req.initial_message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    return SessionResponse(
        session_id=session_id,
        status="active",
        message="Session created successfully.",
        response=ai_response,
    )


@app.post("/sessions/{session_id}/continue", response_model=SessionResponse, tags=["Sessions"])
async def continue_session(session_id: str, req: ContinueSessionRequest):
    """
    Continue an existing research session with memory synchronously.
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        ai_response = await run_agent_message(session_id, req.message)
        return SessionResponse(
            session_id=session_id,
            status="active",
            response=ai_response,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/sessions", response_model=List[SessionSummary], tags=["Sessions"])
async def list_sessions():
    """
    List all active sessions stored in SQLite database.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                c.thread_id, 
                COUNT(*) as checkpoint_count,
                MAX(c.checkpoint_id) as last_checkpoint,
                t.title
            FROM checkpoints c
            LEFT JOIN session_titles t ON c.thread_id = t.thread_id
            GROUP BY c.thread_id
            ORDER BY last_checkpoint DESC
            """
        )
        rows = cursor.fetchall()

    return [
        SessionSummary(
            session_id=row["thread_id"],
            title=row["title"] if row["title"] else row["thread_id"].replace("session_", "").replace("_", " "),
            checkpoint_count=row["checkpoint_count"],
            last_updated=row["last_checkpoint"],
        )
        for row in rows
    ]


@app.get("/sessions/{session_id}/history", tags=["Sessions"])
async def get_session_history(session_id: str):
    """
    Fetch the messages/state for a given session.
    """
    global agent
    if agent is None:
        agent = await create_research_synthesis_supervisor()

    config = {"configurable": {"thread_id": session_id}}
    state = await agent.aget_state(config)

    if not state or not state.values:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM checkpoints WHERE thread_id = ? LIMIT 1", (session_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    messages = state.values.get("messages", []) if state else []
    formatted = []
    for m in messages:
        role = getattr(m, "type", "message")
        content = getattr(m, "content", str(m))
        if role in ("human", "ai"):
            formatted.append({"role": role, "content": content})

    return {
        "session_id": session_id,
        "message_count": len(formatted),
        "messages": formatted,
    }


@app.delete("/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """
    Delete a specific session and all its associated checkpoints.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (session_id,))
        deleted_checkpoints = cursor.rowcount
        cursor.execute("DELETE FROM writes WHERE thread_id = ?", (session_id,))
        deleted_writes = cursor.rowcount
        cursor.execute("DELETE FROM session_titles WHERE thread_id = ?", (session_id,))
        cursor.execute("DELETE FROM jobs WHERE session_id = ?", (session_id,))
        conn.commit()

    if deleted_checkpoints == 0:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    return {
        "session_id": session_id,
        "status": "deleted",
        "deleted_checkpoints": deleted_checkpoints,
        "deleted_writes": deleted_writes,
    }


@app.delete("/sessions", tags=["Sessions"])
async def delete_all_sessions():
    """
    Delete all sessions and clear the checkpoints database completely.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checkpoints")
        deleted_checkpoints = cursor.rowcount
        cursor.execute("DELETE FROM writes")
        deleted_writes = cursor.rowcount
        cursor.execute("DELETE FROM session_titles")
        cursor.execute("DELETE FROM jobs")
        conn.commit()

    return {
        "status": "cleared",
        "message": "All sessions have been deleted successfully.",
        "deleted_checkpoints": deleted_checkpoints,
        "deleted_writes": deleted_writes,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)

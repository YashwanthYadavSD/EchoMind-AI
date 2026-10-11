
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os

import schemas
from database import init_db, get_db_connection
from services.intent_service import process_chat_message

# Initialize DB on startup
init_db()

app = FastAPI(title="EchoMind AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files (JS, CSS) at /frontend/*
_frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/frontend", StaticFiles(directory=_frontend_dir), name="frontend")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = get_db_connection()
    try:
        response = await call_next(request)
        return response
    finally:
        request.state.db.close()


@app.get("/", response_class=FileResponse)
def serve_ui():
    """Serve the frontend UI."""
    return FileResponse(os.path.join(_frontend_dir, "index.html"))


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=schemas.ChatResponse)
def chat_endpoint(request_data: schemas.ChatRequest, request: Request):
    if not request_data.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    response = process_chat_message(
        request_data.message,
        request_data.session_id,
        request.state.db
    )
    return response


# ---------------- TASK ENDPOINTS ----------------

@app.get("/tasks", response_model=List[schemas.TaskOut])
def get_tasks(request: Request):
    db = request.state.db
    tasks = db.execute("SELECT * FROM tasks").fetchall()
    return [dict(task) for task in tasks]


@app.post("/tasks", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate, request: Request):
    db = request.state.db

    cursor = db.execute(
        """
        INSERT INTO tasks (task, completed, due_date, priority)
        VALUES (?, ?, ?, ?)
        """,
        (task.task, task.completed, task.due_date, task.priority)
    )
    db.commit()

    new_task = db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (cursor.lastrowid,)
    ).fetchone()

    return dict(new_task)


@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    request: Request
):
    db = request.state.db

    db_task = db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    update_data = task.model_dump(exclude_unset=True)

    if not update_data:
        return dict(db_task)

    set_clause = ", ".join(
        [f"{key} = ?" for key in update_data.keys()]
    )
    values = list(update_data.values())
    values.append(task_id)

    db.execute(
        f"UPDATE tasks SET {set_clause} WHERE id = ?",
        values
    )
    db.commit()

    updated_task = db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    return dict(updated_task)


# DELETE A TASK BY ITS ID
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, request: Request):
    db = request.state.db

    db_task = db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )
    db.commit()

    return {
        "message": f"Task {task_id} deleted successfully"
    }


# ---------------- REMINDER ENDPOINTS ----------------

@app.get("/reminders", response_model=List[schemas.ReminderOut])
def get_reminders(request: Request):
    db = request.state.db
    reminders = db.execute(
        "SELECT * FROM reminders"
    ).fetchall()

    return [dict(reminder) for reminder in reminders]


@app.post("/reminders", response_model=schemas.ReminderOut)
def create_reminder(
    reminder: schemas.ReminderCreate,
    request: Request
):
    db = request.state.db

    cursor = db.execute(
        """
        INSERT INTO reminders (message, reminder_time, completed)
        VALUES (?, ?, ?)
        """,
        (
            reminder.message,
            reminder.reminder_time,
            reminder.completed
        )
    )
    db.commit()

    new_reminder = db.execute(
        "SELECT * FROM reminders WHERE id = ?",
        (cursor.lastrowid,)
    ).fetchone()

    return dict(new_reminder)


@app.put(
    "/reminders/{reminder_id}",
    response_model=schemas.ReminderOut
)
def update_reminder(
    reminder_id: int,
    reminder: schemas.ReminderUpdate,
    request: Request
):
    db = request.state.db

    db_reminder = db.execute(
        "SELECT * FROM reminders WHERE id = ?",
        (reminder_id,)
    ).fetchone()

    if not db_reminder:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found"
        )

    update_data = reminder.model_dump(exclude_unset=True)

    if not update_data:
        return dict(db_reminder)

    set_clause = ", ".join(
        [f"{key} = ?" for key in update_data.keys()]
    )
    values = list(update_data.values())
    values.append(reminder_id)

    db.execute(
        f"UPDATE reminders SET {set_clause} WHERE id = ?",
        values
    )
    db.commit()

    updated_reminder = db.execute(
        "SELECT * FROM reminders WHERE id = ?",
        (reminder_id,)
    ).fetchone()

    return dict(updated_reminder)


# DELETE A REMINDER BY ITS ID
@app.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, request: Request):
    db = request.state.db

    db_reminder = db.execute(
        "SELECT * FROM reminders WHERE id = ?",
        (reminder_id,)
    ).fetchone()

    if not db_reminder:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found"
        )

    db.execute(
        "DELETE FROM reminders WHERE id = ?",
        (reminder_id,)
    )
    db.commit()

    return {
        "message": f"Reminder {reminder_id} deleted successfully"
    }

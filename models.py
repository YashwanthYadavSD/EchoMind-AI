from typing import Dict, Any
import dateparser
from datetime import datetime


def handle_task_intent(intent: str, entities: Dict[str, Any], db) -> str:

    # ============================================================
    # CREATE TASK
    # ============================================================

    if intent == "CREATE_TASK":

        task_name = entities.get("task_name")

        if not task_name:
            return "What task would you like me to add?"

        priority = entities.get("priority", "normal")

        # Get date/time if provided by the AI
        due_date_str = entities.get("due_date")

        # Also support datetime if returned by the AI
        if not due_date_str:
            due_date_str = entities.get("datetime")

        due_date = None

        if due_date_str:

            try:
                due_date = dateparser.parse(
                    due_date_str,
                    settings={
                        "TIMEZONE": "local",
                        "RETURN_AS_TIMEZONE_AWARE": False,
                        "RELATIVE_BASE": datetime.now(),
                        "PREFER_DATES_FROM": "future"
                    }
                )
            except Exception:
                due_date = None

        # Save task
        db.execute(
            """
            INSERT INTO tasks
            (task, completed, due_date, priority)
            VALUES (?, ?, ?, ?)
            """,
            (
                task_name,
                0,
                due_date,
                priority
            )
        )

        db.commit()

        # Response with due date
        if due_date:

            time_formatted = due_date.strftime(
                "%I:%M %p on %b %d, %Y"
            )

            return (
                f"Done! I've added '{task_name}' "
                f"with a deadline at {time_formatted}."
            )

        return (
            f"Done! I've added '{task_name}' "
            f"to your tasks."
        )

    # ============================================================
    # LIST ALL TASKS
    # ============================================================

    elif intent == "LIST_TASKS":

        tasks = db.execute(
            "SELECT * FROM tasks"
        ).fetchall()

        if not tasks:
            return "You don't have any tasks right now."

        response = "Here are your tasks:\n"

        for t in tasks:

            status = "✓" if t["completed"] else "☐"

            due_date = t["due_date"]

            if due_date:

                try:
                    if isinstance(due_date, str):
                        parsed_due = dateparser.parse(due_date)
                    else:
                        parsed_due = due_date

                    due_text = parsed_due.strftime(
                        "%I:%M %p, %b %d, %Y"
                    )

                except Exception:
                    due_text = str(due_date)

                response += (
                    f"- [{status}] ID {t['id']}: "
                    f"{t['task']} "
                    f"(Due: {due_text})\n"
                )

            else:

                response += (
                    f"- [{status}] ID {t['id']}: "
                    f"{t['task']}\n"
                )

        return response

    # ============================================================
    # LIST PENDING TASKS
    # ============================================================

    elif intent == "LIST_PENDING_TASKS":

        tasks = db.execute(
            "SELECT * FROM tasks WHERE completed = 0"
        ).fetchall()

        if not tasks:
            return "You have no pending tasks! Great job."

        response = "Here are your pending tasks:\n"

        for t in tasks:

            due_date = t["due_date"]

            if due_date:

                try:

                    if isinstance(due_date, str):
                        parsed_due = dateparser.parse(due_date)
                    else:
                        parsed_due = due_date

                    due_text = parsed_due.strftime(
                        "%I:%M %p, %b %d, %Y"
                    )

                except Exception:

                    due_text = str(due_date)

                response += (
                    f"- ID {t['id']}: "
                    f"{t['task']} "
                    f"(Due: {due_text})\n"
                )

            else:

                response += (
                    f"- ID {t['id']}: "
                    f"{t['task']}\n"
                )

        return response

    # ============================================================
    # COMPLETE TASK
    # ============================================================

    elif intent == "COMPLETE_TASK":

        task_id = entities.get("task_id")

        if not task_id:
            return "Please provide the task ID you want to complete."

        task = db.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if not task:
            return f"I couldn't find task ID {task_id}."

        db.execute(
            """
            UPDATE tasks
            SET completed = 1
            WHERE id = ?
            """,
            (task_id,)
        )

        db.commit()

        return (
            f"Awesome! I've marked task {task_id} "
            f"('{task['task']}') as completed."
        )

    # ============================================================
    # DELETE TASK
    # ============================================================

    elif intent == "DELETE_TASK":

        task_id = entities.get("task_id")

        if not task_id:
            return "Please provide the task ID you want to delete."

        task = db.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if not task:
            return f"I couldn't find task ID {task_id}."

        db.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        db.commit()

        return f"I've deleted task {task_id}."

    # ============================================================
    # TASK SUMMARY
    # ============================================================

    elif intent == "TASK_SUMMARY":

        total = db.execute(
            "SELECT COUNT(*) as count FROM tasks"
        ).fetchone()["count"]

        completed = db.execute(
            "SELECT COUNT(*) as count "
            "FROM tasks WHERE completed = 1"
        ).fetchone()["count"]

        pending = total - completed

        return (
            f"You have {total} tasks in total: "
            f"{completed} completed and "
            f"{pending} pending."
        )

    # ============================================================
    # UNKNOWN
    # ============================================================

    return "I'm not sure how to handle that task request."
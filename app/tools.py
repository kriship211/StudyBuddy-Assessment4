from __future__ import annotations

from datetime import date
from typing import Any


TASKS: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "Finish AI assessment report",
        "due_date": "2026-09-25",
        "priority": "High",
        "completed": False,
    },
    {
        "id": 2,
        "title": "Prepare demonstration video",
        "due_date": "2026-09-27",
        "priority": "Medium",
        "completed": False,
    },
    {
        "id": 3,
        "title": "Review weekly lecture notes",
        "due_date": "2026-09-20",
        "priority": "Low",
        "completed": True,
    },
]


def lookup_task_local(task_id: int) -> str:
    """Return one stored task by numeric id."""
    for task in TASKS:
        if task["id"] == task_id:
            status = "Completed" if task["completed"] else "Pending"
            return (
                f"Task {task['id']} ('{task['title']}') is due on "
                f"{task['due_date']}. Priority: {task['priority']}. "
                f"Status: {status}."
            )
    return f"Task {task_id} was not found."


def summarise_tasks_local() -> str:
    """Summarise all stored tasks."""
    total = len(TASKS)
    completed = sum(1 for task in TASKS if task["completed"])
    outstanding = total - completed
    lines = [
        f"You have {total} tasks in total: {outstanding} outstanding and "
        f"{completed} completed."
    ]

    for task in TASKS:
        status = "Completed" if task["completed"] else "Pending"
        lines.append(
            f"ID {task['id']}: {task['title']} | Due: {task['due_date']} | "
            f"Priority: {task['priority']} | Status: {status}"
        )

    return "\n".join(lines)


def classify_priority_local(
    title: str,
    due_in_days: int,
    blocking: bool = False,
) -> str:
    """Classify priority from urgency and whether the task blocks other work."""
    if due_in_days < 0:
        raise ValueError("due_in_days cannot be negative")

    if blocking or due_in_days <= 2:
        priority = "High"
        reason = "it is blocking other work or is due within two days"
    elif due_in_days <= 7:
        priority = "Medium"
        reason = "it is due within one week"
    else:
        priority = "Low"
        reason = "the deadline is more than one week away"

    return f"'{title}' is {priority} priority because {reason}."


def days_until(iso_date: str) -> int:
    """Helper retained for future extension and testing."""
    target = date.fromisoformat(iso_date)
    return (target - date.today()).days

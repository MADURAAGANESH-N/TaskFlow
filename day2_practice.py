
# TaskFlow - Day 2
# Practising functions, lists, and dictionaries

tasks = [
    {
        "id": 1,
        "title": "Learn Python functions",
        "status": "pending",
        "priority": "high"
    },
    {
        "id": 2,
        "title": "Practise SQL",
        "status": "pending",
        "priority": "medium"
    }
]


def show_tasks():
    """Display all tasks."""
    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        print(
            f"{task['id']}. {task['title']} | "
            f"Status: {task['status']} | "
            f"Priority: {task['priority']}"
        )


def add_task(title, priority="medium"):
    """Create a new task."""
    next_id = max(
        (task["id"] for task in tasks),
        default=0
    ) + 1

    new_task = {
        "id": next_id,
        "title": title,
        "status": "pending",
        "priority": priority
    }

    tasks.append(new_task)
    print(f"Task added: {title}")


def complete_task(task_id):
    """Mark a task as completed."""
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completed"
            print(f"Task {task_id} completed!")
            return

    print(f"Task {task_id} not found.")


# Run our task manager
print("=== Initial tasks ===")
show_tasks()

print("\n=== Adding a task ===")
add_task("Build TaskFlow API", "high")

print("\n=== Completing a task ===")
complete_task(1)

print("\n=== Final tasks ===")
show_tasks()

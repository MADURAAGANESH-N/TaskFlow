
class Task:
    def __init__(self, task_id, title):
        self.id = task_id
        self.title = title
        self.status = "pending"

    def display(self):
        print(
            f"ID: {self.id} | "
            f"Title: {self.title} | "
            f"Status: {self.status}"
        )


class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title):
        task = Task(self.next_id, title)
        self.tasks.append(task)
        self.next_id += 1
        return task

    def find_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def list_tasks(self):
        if not self.tasks:
            print("No tasks found.")
            return

        print("\n--- Your Tasks ---")
        for task in self.tasks:
            task.display()

    def complete_task(self, task_id):
        task = self.find_task(task_id)

        if task is None:
            return False

        task.status = "completed"
        return True

    def delete_task(self, task_id):
        task = self.find_task(task_id)

        if task is None:
            return False

        self.tasks.remove(task)
        return True


def main():
    manager = TaskManager()

    while True:
        print("\n===== TaskFlow =====")
        print("1. Add a task")
        print("2. View all tasks")
        print("3. Complete a task")
        print("4. Delete a task")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            title = input("Enter task title: ").strip()

            if not title:
                print("Task title cannot be empty.")
                continue

            task = manager.add_task(title)
            print(f"Task {task.id} added successfully.")

        elif choice == "2":
            manager.list_tasks()

        elif choice == "3":
            try:
                task_id = int(input("Enter task ID: "))
            except ValueError:
                print("Please enter a valid numeric ID.")
                continue

            if manager.complete_task(task_id):
                print("Task completed successfully.")
            else:
                print("Task not found.")

        elif choice == "4":
            try:
                task_id = int(input("Enter task ID: "))
            except ValueError:
                print("Please enter a valid numeric ID.")
                continue

            if manager.delete_task(task_id):
                print("Task deleted successfully.")
            else:
                print("Task not found.")

        elif choice == "5":
            print("Thank you for using TaskFlow!")
            break

        else:
            print("Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()

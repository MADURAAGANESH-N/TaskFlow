
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

    def add_task(self, task):
        self.tasks.append(task)

    def find_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task

        return None

    def complete_task(self,task_id):
        task = self.find_task(task_id)
        if task is None:
            return False
        task.status = "completed"
        return True

    def delete_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                self.tasks.remove(task)
                return True
        return False
# Store multiple objects in one list
# tasks = [
#     Task(1, "Learn Python"),
#     Task(2, "Practise SQL"),
#     Task(3, "Build TaskFlow API")
# ]

# # Complete one task
# for task in tasks:
#     task.complete()

# # Display every task
# for task in tasks:
#     task.display()

manager = TaskManager()

# Add tasks
manager.add_task(Task(1, "Learn Python"))
manager.add_task(Task(2, "Practise SQL"))
manager.add_task(Task(3, "Build TaskFlow API"))

# Complete task 2
print("Completed:", manager.complete_task(2))

# Display updated task
task = manager.find_task(2)
if task:
    task.display()

# Delete task 1
print("Deleted:", manager.delete_task(1))

# Display remaining tasks
print("\nRemaining tasks:")
for task in manager.tasks:
    task.display()

# Try deleting a nonexistent task
print("\nDelete nonexistent task:", manager.delete_task(99))

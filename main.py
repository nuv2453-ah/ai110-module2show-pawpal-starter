from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler

# Create owner and pets
owner = Owner("Alice", "alice@example.com")
pet1 = Pet("Buddy", "Dog", 5)
pet2 = Pet("Whiskers", "Cat", 3)

owner.add_pet(pet1)
owner.add_pet(pet2)

# Create tasks
task1 = Task("walk", datetime.now() + timedelta(hours=2), 2)
task2 = Task("feed", datetime.now() + timedelta(minutes=30), 3)
task3 = Task("medication", datetime.now() + timedelta(hours=1), 1)

# Conflict task
conflict_task = Task("vet visit", task2.time, 2)

# Recurring task
daily_task = Task("daily feeding", datetime.now(), 3, recurrence="daily")

# Assign tasks
pet1.add_task(task1)
pet1.add_task(task2)
pet1.add_task(daily_task)

pet2.add_task(task3)
pet2.add_task(conflict_task)

# Scheduler
scheduler = Scheduler()
scheduler.load_tasks_from_owner(owner)
scheduler.sort_tasks()

# Display schedule
def print_schedule():
    print("\n=== TODAY'S SCHEDULE ===")
    for task in scheduler.get_today_tasks():
        status = "✅ Done" if task.done else "❌ Not Done"
        rec = f"({task.recurrence})" if task.recurrence else ""
        print(
            f"{task.time.strftime('%H:%M')} | "
            f"{task.task_type.upper():<15} {rec:<10} | "
            f"Priority: {task.priority} | {status}"
        )

print_schedule()

# Conflict detection
conflicts = scheduler.detect_conflicts()
if conflicts:
    print("\n⚠️ CONFLICTS DETECTED:")
    for t1, t2 in conflicts:
        print(f"{t1.task_type} conflicts with {t2.task_type} at {t1.time.strftime('%H:%M')}")
else:
    print("\nNo conflicts detected!")

# Complete a task
print("\nMarking first task as complete...\n")
scheduler.complete_task(scheduler.task_list[0])

print_schedule()
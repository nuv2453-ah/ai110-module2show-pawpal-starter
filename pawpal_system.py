from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime, timedelta, date


@dataclass
class Task:
    """Represents a single pet care task."""
    task_type: str
    time: Optional[datetime]
    priority: int
    recurrence: Optional[str] = None  # "daily", "weekly"
    done: bool = False

    def mark_done(self):
        """Mark the task as completed."""
        self.done = True

    def is_conflict_with(self, other_task: 'Task') -> bool:
        """Check if this task conflicts with another (same time)."""
        return self.time == other_task.time
    
    def get_occurrence_for_date(self, target_date: date) -> Optional['Task']:
        """Return a version of this task if it occurs on the given date."""
        if self.time is None:
            return None

        if self.time.date() == target_date:
            return self

        if self.recurrence == "daily":
            return Task(
                self.task_type,
                datetime.combine(target_date, self.time.time()),
                self.priority,
                self.recurrence
            )

        if self.recurrence == "weekly" and self.time.weekday() == target_date.weekday():
            return Task(
                self.task_type,
                datetime.combine(target_date, self.time.time()),
                self.priority,
                self.recurrence
            )

        return None


@dataclass
class Pet:
    """Represents a pet and its associated tasks."""
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to the pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from the pet."""
        if task in self.tasks:
            self.tasks.remove(task)


class Owner:
    """Represents a pet owner with multiple pets."""
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to the owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet):
        """Remove a pet from the owner."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Scheduler:
    """Central scheduler for managing and organizing tasks."""
    def __init__(self):
        self.task_list: List[Task] = []

    def load_tasks_from_owner(self, owner: Owner):
        """Load all tasks from an owner."""
        self.task_list = owner.get_all_tasks()

    def sort_tasks(self):
        """Sort tasks by time, then by priority (higher first)."""
        self.task_list.sort(key=lambda t: (t.time or datetime.max, -t.priority))

    def get_today_tasks(self) -> List[Task]:
        """Get all tasks occurring today."""
        today = datetime.now().date()
        today_tasks = []

        for task in self.task_list:
            occ = task.get_occurrence_for_date(today)
            if occ:
                today_tasks.append(occ)

        return sorted(today_tasks, key=lambda t: (t.time, -t.priority))

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Detect tasks that occur at the same time (exact datetime)."""
        conflicts = []
        seen = {}

        for task in self.task_list:
            if task.time is None:
                continue
            key = task.time  # exact datetime match
            if key in seen:
                conflicts.append((seen[key], task))
            else:
                seen[key] = task

        return conflicts

    def complete_task(self, task: Task):
        """Mark task complete and handle recurrence."""
        task.mark_done()

        if task.time is None:
            return

        if task.recurrence == "daily":
            self.task_list.append(
                Task(task.task_type, task.time + timedelta(days=1), task.priority, "daily")
            )

        elif task.recurrence == "weekly":
            self.task_list.append(
                Task(task.task_type, task.time + timedelta(weeks=1), task.priority, "weekly")
            )

    def filter_by_status(self, done: bool) -> List[Task]:
        """Filter today's tasks by completion status."""
        return [t for t in self.get_today_tasks() if t.done == done]
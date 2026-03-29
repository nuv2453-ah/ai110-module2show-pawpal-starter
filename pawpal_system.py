from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime, timedelta


@dataclass
class Task:
    task_type: str
    time: datetime
    priority: int
    recurrence: Optional[str] = None  # "daily", "weekly", etc.
    done: bool = False

    def mark_done(self):
        self.done = True

    def is_conflict_with(self, other_task: 'Task') -> bool:
        return self.time == other_task.time

    def get_occurrence_for_date(self, date: datetime.date) -> Optional['Task']:
        """Return this task for a specific date if it occurs then."""
        if self.time.date() == date:
            return Task(self.task_type, self.time, self.priority, self.recurrence, self.done)
        if self.recurrence == "daily":
            return Task(self.task_type, datetime.combine(date, self.time.time()), self.priority, self.recurrence)
        if self.recurrence == "weekly" and self.time.weekday() == date.weekday():
            return Task(self.task_type, datetime.combine(date, self.time.time()), self.priority, self.recurrence)
        return None


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, task: Task):
        if task in self.tasks:
            self.tasks.remove(task)


class Owner:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def remove_pet(self, pet: Pet):
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Scheduler:
    def __init__(self):
        self.task_list: List[Task] = []

    def load_tasks_from_owner(self, owner: Owner):
        self.task_list = owner.get_all_tasks()

    def sort_tasks(self):
        self.task_list.sort(key=lambda t: (t.time, -t.priority))

    def get_today_tasks(self) -> List[Task]:
        today = datetime.now().date()
        today_tasks = []
        for task in self.task_list:
            occ = task.get_occurrence_for_date(today)
            if occ:
                today_tasks.append(occ)
        return sorted(today_tasks, key=lambda t: (t.time, -t.priority))

    def detect_conflicts(self) -> List[Tuple[Task, Task]]:
        conflicts = []
        seen = {}
        for task in self.task_list:
            if task.time is None:
                continue
            if task.time in seen:
                conflicts.append((seen[task.time], task))
            else:
                seen[task.time] = task
        return conflicts

    def complete_task(self, task: Task):
        task.mark_done()
        if task.recurrence == "daily":
            self.task_list.append(Task(task.task_type, task.time + timedelta(days=1), task.priority, "daily"))
        elif task.recurrence == "weekly":
            self.task_list.append(Task(task.task_type, task.time + timedelta(weeks=1), task.priority, "weekly"))

    def filter_by_status(self, done: bool) -> List[Task]:
        return [t for t in self.get_today_tasks() if t.done == done]
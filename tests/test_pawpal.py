from pawpal_system import Task, Pet, Scheduler
from datetime import datetime


def test_task_completion():
    task = Task(task_type="feed", time=None, priority=1)
    assert not task.done
    task.mark_done()
    assert task.done


def test_pet_task_addition():
    pet = Pet(name="Buddy", species="Dog", age=5)
    assert len(pet.tasks) == 0

    task = Task(task_type="walk", time=None, priority=2)
    pet.add_task(task)

    assert len(pet.tasks) == 1


def test_sorting():
    scheduler = Scheduler()

    t1 = Task("feed", datetime(2026, 1, 1, 10, 0), 1)
    t2 = Task("walk", datetime(2026, 1, 1, 9, 0), 2)

    scheduler.task_list = [t1, t2]
    scheduler.sort_tasks()

    assert scheduler.task_list[0] == t2


def test_conflict_detection():
    scheduler = Scheduler()

    t1 = Task("feed", datetime(2026, 1, 1, 10, 0), 1)
    t2 = Task("walk", datetime(2026, 1, 1, 10, 0), 2)

    scheduler.task_list = [t1, t2]

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1


def test_daily_recurrence():
    scheduler = Scheduler()

    t = Task("feed", datetime.now(), 1, recurrence="daily")
    scheduler.task_list = [t]

    scheduler.complete_task(t)

    assert len(scheduler.task_list) == 2
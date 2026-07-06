"""Tests for the PawPal+ logic layer."""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


def _owner_with_tasks():
    """Build an owner with two pets and a few timed tasks for scheduler tests."""
    owner = Owner("Jordan", available_minutes=120)
    dog = Pet("Mochi", "dog")
    cat = Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Evening walk", 30, preferred_time="18:00"))
    dog.add_task(Task("Meds", 5, preferred_time="08:00"))
    cat.add_task(Task("Litter box", 5, preferred_time="08:00"))  # clashes with Meds
    return owner, dog, cat


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task's completed status to True."""
    task = Task("Morning walk", 30, priority="high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", 10, priority="medium"))

    assert len(pet.tasks) == 1


def test_sort_by_time_orders_and_puts_untimed_last():
    """sort_by_time() orders by 'HH:MM' and pushes tasks with no time to the end."""
    owner, dog, _ = _owner_with_tasks()
    dog.add_task(Task("Enrichment", 20))  # no preferred_time
    scheduler = Scheduler(owner)

    times = [task.preferred_time for _, task in scheduler.sort_by_time()]

    assert times == ["08:00", "08:00", "18:00", None]


def test_filter_by_pet_and_status():
    """Filters return only the matching pet's tasks / only unfinished tasks."""
    owner, dog, _ = _owner_with_tasks()
    scheduler = Scheduler(owner)

    assert {t.title for _, t in scheduler.filter_by_pet("Mochi")} == {
        "Evening walk",
        "Meds",
    }

    dog.tasks[0].mark_complete()
    unfinished = {t.title for _, t in scheduler.filter_by_status(completed=False)}
    assert "Evening walk" not in unfinished


def test_detect_conflicts_flags_same_time():
    """Two tasks at the same preferred_time produce a warning, not a crash."""
    owner, _, _ = _owner_with_tasks()
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_completing_recurring_task_spawns_next_occurrence():
    """Completing a daily task appends a fresh instance due one day later."""
    pet = Pet("Mochi", "dog")
    task = Task("Meds", 5, frequency="daily", due_date=date(2026, 7, 5))
    pet.add_task(task)

    upcoming = pet.complete_task(task)

    assert task.completed is True
    assert len(pet.tasks) == 2
    assert upcoming.completed is False
    assert upcoming.due_date == date(2026, 7, 6)


def test_completing_once_task_does_not_recur():
    """A 'once' task does not spawn a next occurrence."""
    pet = Pet("Mochi", "dog")
    task = Task("Vet visit", 60, frequency="once")
    pet.add_task(task)

    upcoming = pet.complete_task(task)

    assert upcoming is None
    assert len(pet.tasks) == 1

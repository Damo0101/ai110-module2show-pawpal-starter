"""PawPal+ logic layer.

Backend classes for the PawPal+ pet-care planning assistant.

Class responsibilities:
- Task:      a single care activity (description, time, frequency, completion).
- Pet:       stores pet details and its list of tasks.
- Owner:     manages multiple pets and gives access to all their tasks.
- Scheduler: the "brain" that retrieves, organizes, and plans tasks across pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# How strongly to weight each priority when ordering tasks (higher = sooner).
PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}


def _to_minutes(clock: str) -> int:
    """Convert a 'HH:MM' clock string into minutes past midnight."""
    hours, minutes = clock.split(":")
    return int(hours) * 60 + int(minutes)


def _to_clock(minutes: int) -> str:
    """Convert minutes past midnight back into a 'HH:MM' clock string."""
    minutes %= 24 * 60
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, grooming, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"          # "low" | "medium" | "high"
    category: str = "general"
    frequency: str = "daily"          # "daily" | "weekly" | "once"
    preferred_time: str | None = None  # e.g. "08:00"
    completed: bool = False

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (high=3 ... low=1)."""
        return PRIORITY_SCORES.get(self.priority.lower(), 0)

    def is_due_today(self) -> bool:
        """Return True if this task still needs to happen today.

        Completed tasks are not due. In this simplified model every remaining
        task is treated as due today; a fuller version would check the weekday
        for "weekly" tasks.
        """
        if self.completed:
            return False
        return self.frequency in {"daily", "weekly", "once"}

    def mark_complete(self) -> None:
        """Mark this task as done for today."""
        self.completed = True

    def update(self, changes: dict) -> None:
        """Apply a dict of field changes to this task."""
        for key, value in changes.items():
            if not hasattr(self, key):
                raise AttributeError(f"Task has no attribute {key!r}")
            setattr(self, key, value)


@dataclass
class Pet:
    """The animal being cared for; owns a list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet (raises ValueError if not present)."""
        self.tasks.remove(task)

    def edit_task(self, task: Task, changes: dict) -> None:
        """Edit an existing task belonging to this pet."""
        if task not in self.tasks:
            raise ValueError("Task does not belong to this pet")
        task.update(changes)

    def list_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    """The person using PawPal+; has one or more pets and time constraints."""

    name: str
    preferences: dict = field(default_factory=dict)
    available_minutes: int = 0
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner (raises ValueError if not present)."""
        self.pets.remove(pet)

    def set_preference(self, key: str, value) -> None:
        """Set an owner preference (e.g., preferred walk time)."""
        self.preferences[key] = value

    def set_available_time(self, minutes: int) -> None:
        """Set the owner's total available time for the day."""
        if minutes < 0:
            raise ValueError("available time cannot be negative")
        self.available_minutes = minutes

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all of this owner's pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds and explains a daily plan from an owner's constraints and pets' tasks."""

    def __init__(self, owner: Owner, start_time: str = "08:00") -> None:
        """Create a scheduler for an owner, planning from the given start time."""
        self.owner = owner
        self.start_time = start_time
        # Cache of the most recently built plan so explain_plan() can reuse it
        # instead of re-running the sort/filter/conflict passes.
        self._plan: list | None = None

    @property
    def available_minutes(self) -> int:
        """Single source of truth: the owner's daily time budget."""
        return self.owner.available_minutes

    @property
    def tasks(self) -> list[tuple[Pet, Task]]:
        """All (pet, task) pairs, read live from the owner's pets."""
        return self.owner.all_tasks()

    def _due_tasks(self) -> list[tuple[Pet, Task]]:
        """(pet, task) pairs that still need doing today."""
        return [(pet, task) for pet, task in self.tasks if task.is_due_today()]

    def sort_tasks(self) -> list[tuple[Pet, Task]]:
        """Return due (pet, task) pairs ordered by priority desc, then shorter first."""
        return sorted(
            self._due_tasks(),
            key=lambda pt: (-pt[1].priority_score(), pt[1].duration_minutes),
        )

    def filter_tasks(self) -> list[tuple[Pet, Task]]:
        """Greedily keep the highest-priority tasks that fit the time budget."""
        selected: list[tuple[Pet, Task]] = []
        remaining = self.available_minutes
        for pet, task in self.sort_tasks():
            if task.duration_minutes <= remaining:
                selected.append((pet, task))
                remaining -= task.duration_minutes
        return selected

    def resolve_conflicts(
        self, selected: list[tuple[Pet, Task]]
    ) -> list[tuple[int, Pet, Task]]:
        """Assign non-overlapping start times to the selected tasks.

        Tasks with a preferred_time are placed at (or after) that time first;
        the rest fill the earliest free slots from start_time. Returns a list
        of (start_minute, pet, task) sorted by start time.
        """
        occupied: list[tuple[int, int]] = []
        placements: list[tuple[int, Pet, Task]] = []

        def find_slot(desired: int, duration: int) -> int:
            """Push `desired` forward until [start, start+duration) is free."""
            start = desired
            moved = True
            while moved:
                moved = False
                for busy_start, busy_end in occupied:
                    if start < busy_end and busy_start < start + duration:
                        start = busy_end
                        moved = True
            return start

        fixed = [(p, t) for p, t in selected if t.preferred_time]
        flexible = [(p, t) for p, t in selected if not t.preferred_time]

        for pet, task in fixed:
            start = find_slot(_to_minutes(task.preferred_time), task.duration_minutes)
            occupied.append((start, start + task.duration_minutes))
            placements.append((start, pet, task))

        cursor = _to_minutes(self.start_time)
        for pet, task in flexible:
            start = find_slot(cursor, task.duration_minutes)
            occupied.append((start, start + task.duration_minutes))
            placements.append((start, pet, task))
            cursor = start + task.duration_minutes

        placements.sort(key=lambda item: item[0])
        return placements

    def build_plan(self) -> list:
        """Produce the ordered daily plan (list of scheduled items) and cache it."""
        placements = self.resolve_conflicts(self.filter_tasks())
        self._plan = [
            {
                "time": _to_clock(start),
                "pet": pet.name,
                "title": task.title,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
            }
            for start, pet, task in placements
        ]
        return self._plan

    def explain_plan(self) -> str:
        """Return a human-readable explanation of why the plan was chosen.

        Reuses the cached self._plan from build_plan() rather than recomputing.
        """
        if self._plan is None:
            self.build_plan()

        scheduled = len(self._plan)
        total_due = len(self._due_tasks())
        used = sum(item["duration_minutes"] for item in self._plan)

        lines = [
            f"Plan for {self.owner.name}: {scheduled} of {total_due} due task(s) "
            f"scheduled, using {used} of {self.available_minutes} available minutes.",
        ]
        for item in self._plan:
            lines.append(
                f"  {item['time']} — {item['title']} for {item['pet']} "
                f"({item['duration_minutes']} min) [priority: {item['priority']}]"
            )
        skipped = total_due - scheduled
        if skipped > 0:
            lines.append(
                f"{skipped} task(s) were skipped because they did not fit the "
                f"time budget; higher-priority tasks were kept first."
            )
        return "\n".join(lines)

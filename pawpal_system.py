"""PawPal+ logic layer.

Backend classes for the PawPal+ pet-care planning assistant.
This is a skeleton generated from diagrams/uml_draft.mmd: class names,
attributes, and empty method stubs only -- no scheduling logic yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, grooming, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"
    recurring: bool = False
    preferred_time: str | None = None

    def priority_score(self) -> int:
        """Return a numeric weight for the task's priority (for sorting)."""
        raise NotImplementedError

    def is_due_today(self) -> bool:
        """Return True if this task should be scheduled today."""
        raise NotImplementedError

    def update(self, changes: dict) -> None:
        """Apply a dict of field changes to this task."""
        raise NotImplementedError


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
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        raise NotImplementedError

    def edit_task(self, task: Task, changes: dict) -> None:
        """Edit an existing task's details."""
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        raise NotImplementedError


@dataclass
class Owner:
    """The person using PawPal+; has one or more pets and time constraints."""

    name: str
    preferences: dict = field(default_factory=dict)
    available_minutes: int = 0
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        raise NotImplementedError

    def set_preference(self, key: str, value) -> None:
        """Set an owner preference (e.g., preferred walk time)."""
        raise NotImplementedError

    def set_available_time(self, minutes: int) -> None:
        """Set the owner's total available time for the day."""
        raise NotImplementedError


class Scheduler:
    """Builds and explains a daily plan from an owner's constraints and tasks."""

    def __init__(
        self,
        tasks: list[Task] | None = None,
        available_minutes: int = 0,
        start_time: str = "08:00",
    ) -> None:
        self.tasks: list[Task] = tasks or []
        self.available_minutes = available_minutes
        self.start_time = start_time

    def sort_tasks(self) -> list[Task]:
        """Return tasks ordered by priority (and/or duration)."""
        raise NotImplementedError

    def filter_tasks(self) -> list[Task]:
        """Drop tasks that don't fit the available time budget."""
        raise NotImplementedError

    def resolve_conflicts(self) -> None:
        """Handle overlapping time slots."""
        raise NotImplementedError

    def build_plan(self) -> list:
        """Produce the ordered daily plan (list of scheduled items)."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Return a human-readable explanation of why the plan was chosen."""
        raise NotImplementedError

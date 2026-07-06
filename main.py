"""Manual testing ground for PawPal+.

Run with:  python main.py

Builds a small owner/pets/tasks scenario and exercises the scheduling logic
(sorting, filtering, conflict detection, recurring tasks) so we can eyeball
that it works before wiring it into the Streamlit UI.
"""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


def rule(label: str) -> None:
    """Print a labelled section divider."""
    print(f"\n{'=' * 44}\n  {label}\n{'=' * 44}")


def main() -> None:
    # An owner with a 90-minute daily care budget.
    owner = Owner("Jordan", available_minutes=90)

    mochi = Pet("Mochi", "dog", breed="Shiba Inu")
    luna = Pet("Luna", "cat", breed="Tabby")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks added intentionally OUT OF TIME ORDER to prove sort_by_time() works.
    mochi.add_task(Task("Evening walk", 30, priority="high", preferred_time="18:00"))
    mochi.add_task(Task("Meds", 5, priority="high", preferred_time="08:00"))
    mochi.add_task(Task("Lunch feeding", 10, priority="medium", preferred_time="12:00"))
    mochi.add_task(Task("Enrichment puzzle", 20, priority="low"))  # no set time

    luna.add_task(Task("Litter box", 5, priority="medium", preferred_time="08:00"))
    luna.add_task(Task("Play session", 15, priority="low", preferred_time="12:00"))

    scheduler = Scheduler(owner, start_time="08:00")

    # --- Today's Schedule --------------------------------------------------
    rule(f"Today's Schedule for {owner.name}")
    for item in scheduler.build_plan():
        print(
            f"  {item['time']}  {item['title']:<18} "
            f"{item['pet']:<7} {item['duration_minutes']:>3} min  [{item['priority']}]"
        )

    # --- Sorting by time ---------------------------------------------------
    rule("Tasks sorted by time (sort_by_time)")
    for pet, task in scheduler.sort_by_time():
        print(f"  {task.preferred_time or '  —  '}  {task.title:<18} ({pet.name})")

    # --- Filtering ---------------------------------------------------------
    rule("Filter: only Mochi's tasks (filter_by_pet)")
    for pet, task in scheduler.filter_by_pet("Mochi"):
        print(f"  {task.title} ({pet.name})")

    rule("Filter: only unfinished tasks (filter_by_status)")
    for pet, task in scheduler.filter_by_status(completed=False):
        print(f"  {task.title} ({pet.name}) — done={task.completed}")

    # --- Conflict detection ------------------------------------------------
    rule("Conflict detection (detect_conflicts)")
    # Meds (Mochi) and Litter box (Luna) are both at 08:00 -> a conflict.
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  ⚠️  {warning}")
    else:
        print("  No conflicts found.")

    # --- Recurring tasks ---------------------------------------------------
    rule("Recurring task auto-rollover (complete_task)")
    meds = mochi.tasks[1]  # the daily "Meds" task
    meds.due_date = date(2026, 7, 5)
    print(f"  Before: {len(mochi.tasks)} tasks, '{meds.title}' due {meds.due_date}")
    upcoming = mochi.complete_task(meds)
    print(f"  Marked '{meds.title}' complete (done={meds.completed}).")
    print(f"  After:  {len(mochi.tasks)} tasks — next '{upcoming.title}' due {upcoming.due_date}")


if __name__ == "__main__":
    main()

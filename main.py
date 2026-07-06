"""Manual testing ground for PawPal+.

Run with:  python main.py

Builds a small owner/pets/tasks scenario and prints Today's Schedule so we can
eyeball that the scheduling logic works before wiring it into the Streamlit UI.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # An owner with a 90-minute daily care budget.
    owner = Owner("Jordan", available_minutes=90)

    # At least two pets.
    mochi = Pet("Mochi", "dog", breed="Shiba Inu")
    luna = Pet("Luna", "cat", breed="Tabby")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # At least three tasks with different times/priorities across the pets.
    mochi.add_task(Task("Meds", 5, priority="high", preferred_time="08:00"))
    mochi.add_task(Task("Morning walk", 30, priority="high"))
    mochi.add_task(Task("Feeding", 10, priority="medium"))
    mochi.add_task(Task("Enrichment puzzle", 20, priority="low"))

    luna.add_task(Task("Feeding", 10, priority="high"))
    luna.add_task(Task("Litter box", 5, priority="medium"))
    luna.add_task(Task("Play session", 15, priority="low"))

    # Build and print Today's Schedule.
    scheduler = Scheduler(owner, start_time="08:00")
    plan = scheduler.build_plan()

    print("=" * 44)
    print(f"  Today's Schedule for {owner.name}")
    print("=" * 44)
    if not plan:
        print("  (no tasks scheduled)")
    for item in plan:
        print(
            f"  {item['time']}  {item['title']:<18} "
            f"{item['pet']:<7} {item['duration_minutes']:>3} min  "
            f"[{item['priority']}]"
        )
    print("-" * 44)
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()

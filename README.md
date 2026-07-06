# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

PawPal+ pairs a Streamlit UI with a tested Python logic layer
(`pawpal_system.py`). Implemented features:

- **Owner & pet management** — add pets to an owner and give each pet its own
  care tasks (`Owner.add_pet`, `Pet.add_task`).
- **Priority-aware daily planning** — builds a day plan that keeps the
  highest-priority tasks that fit the owner's time budget, then explains the
  choices (`Scheduler.build_plan`, `Scheduler.explain_plan`).
- **Sort by priority** — orders tasks high→low priority, shorter first
  (`Scheduler.sort_tasks`).
- **Sort by time** — orders tasks chronologically by `preferred_time`, with
  untimed tasks last (`Scheduler.sort_by_time`).
- **Filtering** — view tasks for one pet or by completion status
  (`Scheduler.filter_by_pet`, `Scheduler.filter_by_status`).
- **Conflict warnings** — flags tasks scheduled at the same start time with a
  non-crashing warning message (`Scheduler.detect_conflicts`).
- **Conflict-free timeline** — the built plan places tasks in non-overlapping
  slots, pushing clashes to the next free time (`Scheduler.resolve_conflicts`).
- **Recurring tasks** — completing a daily/weekly task automatically creates the
  next occurrence with an advanced due date via `timedelta`
  (`Pet.complete_task`, `Task.next_occurrence`).

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Terminal output from running `python main.py` (an owner with two pets and seven
tasks; the scheduler orders by priority, fits the time budget, and skips what
doesn't fit):

```
============================================
  Today's Schedule for Jordan
============================================
  08:00  Meds               Mochi     5 min  [high]
  08:05  Feeding            Luna     10 min  [high]
  08:15  Morning walk       Mochi    30 min  [high]
  08:45  Litter box         Luna      5 min  [medium]
  08:50  Feeding            Mochi    10 min  [medium]
  09:00  Play session       Luna     15 min  [low]
--------------------------------------------
Plan for Jordan: 6 of 7 due task(s) scheduled, using 75 of 90 available minutes.
  08:00 — Meds for Mochi (5 min) [priority: high]
  08:05 — Feeding for Luna (10 min) [priority: high]
  08:15 — Morning walk for Mochi (30 min) [priority: high]
  08:45 — Litter box for Luna (5 min) [priority: medium]
  08:50 — Feeding for Mochi (10 min) [priority: medium]
  09:00 — Play session for Luna (15 min) [priority: low]
1 task(s) were skipped because they did not fit the time budget; higher-priority tasks were kept first.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

The suite in `tests/test_pawpal.py` covers the core behaviors of the logic
layer:

- **Task completion** — `mark_complete()` flips a task's status to done.
- **Task addition** — adding a task increases a pet's task count.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological
  order, with untimed tasks last.
- **Filtering** — `filter_by_pet()` / `filter_by_status()` return the right
  subset of tasks.
- **Conflict detection** — `detect_conflicts()` flags two tasks at the same
  start time.
- **Recurrence logic** — completing a daily task creates a new instance due the
  next day, while a `once` task does not recur.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
collected 7 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 14%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 28%]
tests/test_pawpal.py::test_sort_by_time_orders_and_puts_untimed_last PASSED [ 42%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED               [ 57%]
tests/test_pawpal.py::test_detect_conflicts_flags_same_time PASSED       [ 71%]
tests/test_pawpal.py::test_completing_recurring_task_spawns_next_occurrence PASSED [ 85%]
tests/test_pawpal.py::test_completing_once_task_does_not_recur PASSED    [100%]

============================== 7 passed in 0.07s ==============================
```

**Confidence Level: ⭐⭐⭐⭐☆ (4/5)** — all core behaviors pass; the main gap is
duration-based overlap detection (see the tradeoff noted in `reflection.md`).

## 📐 Smarter Scheduling

All scheduling logic lives in the `Scheduler` class in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Scheduler.sort_tasks()` | Orders due tasks by priority (high→low), then shorter duration first. |
| Sort by time | `Scheduler.sort_by_time()` | Sorts by `preferred_time` ("HH:MM"); untimed tasks go last. |
| Filter by time budget | `Scheduler.filter_tasks()` | Greedily keeps the highest-priority tasks that fit `available_minutes`. |
| Filter by pet | `Scheduler.filter_by_pet(name)` | Returns only the named pet's tasks. |
| Filter by status | `Scheduler.filter_by_status(completed)` | Returns only completed / unfinished tasks. |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns (does not crash) when tasks share the exact same `preferred_time`. |
| Conflict resolution | `Scheduler.resolve_conflicts()` | Assigns non-overlapping start times; pushes clashing tasks to the next free slot. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a daily/weekly task auto-creates the next instance (`due_date` advanced via `timedelta`). |

### Sorting details

`sort_by_time()` sorts `"HH:MM"` strings directly with a `sorted()` lambda key —
because the strings are zero-padded, lexicographic order matches chronological
order (`"08:00" < "13:30"`). Tasks with no `preferred_time` are sorted last.

### Conflict handling

`detect_conflicts()` is a lightweight, non-crashing check: it groups uncompleted
tasks by exact start time and returns a warning string per shared slot. The
actual daily plan is still built safely by `resolve_conflicts()`, which places
tasks sequentially so nothing double-books.

### Recurring tasks

A `Task` carries a `frequency` (`daily` / `weekly` / `once`) and a `due_date`.
Calling `Pet.complete_task(task)` marks it done and, for recurring tasks, appends
a fresh copy via `Task.next_occurrence()` with `due_date` advanced by
`timedelta(days=1)` (daily) or `timedelta(weeks=1)` (weekly). `once` tasks do
not recur.

## 📸 Demo Walkthrough

Launch the app with `streamlit run app.py`.

### Main UI features & user actions

- **Owner section** — set the owner's name and the total minutes available for
  care today (the scheduler's time budget).
- **Add a pet** — enter a name, species, and breed to register a pet.
- **Add a task** — pick a pet, then give the task a title, duration, priority,
  frequency (daily/weekly/once), and an optional preferred time.
- **Today's tasks** — see conflict warnings, filter by pet or completion status,
  view tasks sorted by time, and mark tasks done (recurring ones roll over).
- **Build schedule** — generate the day's plan as a table plus a written
  explanation of why each task was chosen.

### Example workflow

1. Set **Time available today** to `90` minutes.
2. **Add a pet**: `Mochi` (dog). Add a second pet: `Luna` (cat).
3. **Add tasks** to Mochi — e.g. `Meds` (5 min, high, daily, 08:00),
   `Evening walk` (30 min, high, 18:00) — and to Luna — `Litter box`
   (5 min, medium, 08:00).
4. In **Today's tasks**, PawPal+ shows a ⚠️ conflict warning because Meds and
   Litter box are both at 08:00. Use the filters to view just Mochi's tasks or
   only pending ones.
5. Click **✓ Meds — Mochi** to complete it; because it's a daily task, a new
   Meds instance is automatically added for the next day.
6. Click **Generate schedule** to see today's ordered plan and the reasoning.

### Key Scheduler behaviors shown

- **Sorting** — the schedule is ordered by priority (build) and the task list by
  time (`sort_by_time`).
- **Filtering** — by pet (`filter_by_pet`) and completion status
  (`filter_by_status`).
- **Conflict warnings** — same-time tasks surface as non-blocking warnings
  (`detect_conflicts`), while the built plan stays conflict-free
  (`resolve_conflicts`).
- **Recurring tasks** — completing a daily/weekly task spawns its next
  occurrence (`Pet.complete_task` → `Task.next_occurrence`).

### Sample CLI output (`python main.py`)

The terminal demo exercises every Scheduler behavior end-to-end:

```
============================================
  Today's Schedule for Jordan
============================================
  08:00  Meds               Mochi     5 min  [high]
  08:05  Litter box         Luna      5 min  [medium]
  08:10  Enrichment puzzle  Mochi    20 min  [low]
  12:00  Lunch feeding      Mochi    10 min  [medium]
  12:10  Play session       Luna     15 min  [low]
  18:00  Evening walk       Mochi    30 min  [high]

============================================
  Tasks sorted by time (sort_by_time)
============================================
  08:00  Meds               (Mochi)
  08:00  Litter box         (Luna)
  12:00  Lunch feeding      (Mochi)
  12:00  Play session       (Luna)
  18:00  Evening walk       (Mochi)
    —    Enrichment puzzle  (Mochi)

============================================
  Filter: only Mochi's tasks (filter_by_pet)
============================================
  Evening walk (Mochi)
  Meds (Mochi)
  Lunch feeding (Mochi)
  Enrichment puzzle (Mochi)

============================================
  Filter: only unfinished tasks (filter_by_status)
============================================
  Evening walk (Mochi) — done=False
  Meds (Mochi) — done=False
  Lunch feeding (Mochi) — done=False
  Enrichment puzzle (Mochi) — done=False
  Litter box (Luna) — done=False
  Play session (Luna) — done=False

============================================
  Conflict detection (detect_conflicts)
============================================
  ⚠️  Conflict at 08:00: Meds (Mochi), Litter box (Luna)
  ⚠️  Conflict at 12:00: Lunch feeding (Mochi), Play session (Luna)

============================================
  Recurring task auto-rollover (complete_task)
============================================
  Before: 4 tasks, 'Meds' due 2026-07-05
  Marked 'Meds' complete (done=True).
  After:  5 tasks — next 'Meds' due 2026-07-06
```

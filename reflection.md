# PawPal+ Project Reflection

## 1. System Design

Some Core actions it should be able to do:
- Add/delete info of owner and pet
- set constraints
- edit task details
**a. Initial design**

My initial UML (see `diagrams/uml_draft.mmd`) uses four classes:

- **Owner** — represents the person using the app. Holds their `name`,
  `preferences`, a daily time budget (`available_minutes`), and a list of
  `pets`. Responsible for managing pets (`add_pet`, `remove_pet`) and setting
  constraints (`set_preference`, `set_available_time`).
- **Pet** — the animal being cared for. Holds `name`, `species`, `breed`,
  `age`, `notes`, and its own list of `tasks`. Responsible for managing its
  care tasks (`add_task`, `remove_task`, `edit_task`, `list_tasks`).
- **Task** — a single care activity (walk, feeding, meds, grooming). Holds
  `title`, `duration_minutes`, `priority`, `category`, `frequency`,
  `preferred_time`, and a `completed` status. Responsible for describing
  itself, scoring its own priority, and tracking completion (`priority_score`,
  `is_due_today`, `mark_complete`, `update`).
- **Scheduler** — the "brain." Given an owner's constraints and pets' tasks,
  it sorts, filters, and orders tasks into a daily plan and explains it
  (`sort_tasks`, `filter_tasks`, `resolve_conflicts`, `build_plan`,
  `explain_plan`).

Relationships: an **Owner has one-or-more Pets**, a **Pet has zero-or-more
Tasks** (composition — tasks belong to that pet), and the **Scheduler uses**
the Owner's constraints and the Pets' Tasks to produce a plan. `Task` and
`Pet` are Python dataclasses to keep the data objects clean.

**b. Design changes**

Yes. After reviewing the class skeleton I made a couple of changes to the
`Scheduler`:

1. Removed a duplicated constraint. `available_minutes` originally lived on
   both `Owner` and `Scheduler`, which is two sources of truth for the same
   fact and invites bugs when one changes and the other doesn't. The
   `Scheduler` now takes the `Owner` and exposes `available_minutes` as a
   read-only property that reads from the owner.
2. **Preserved the Pet→Task link.** The `Scheduler` first took a flat
   `list[Task]`, so once tasks from multiple pets were pooled it could no
   longer tell which pet a task belonged to. It now pools `(pet, task)` pairs
   so a multi-pet plan can label each item with its pet.
3. **Cached the built plan.** `build_plan()` and `explain_plan()` were
   independent, meaning `explain_plan()` would have to redo all the
   sort/filter/conflict work. `build_plan()` now stores the result in
   `self._plan` so `explain_plan()` reuses it instead of recomputing.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: the owner's **available time**
(`available_minutes`), each task's **priority** (high/medium/low), and each
task's **preferred time** (`preferred_time`). Priority matters most: tasks are
sorted highest-priority first, then the greedy `filter_tasks()` keeps as many
as fit the time budget, so a busy owner always gets the essential care done
(meds, feeding) before the nice-to-haves (enrichment). Completion status and
frequency also act as filters — completed tasks and non-due tasks are excluded.

**b. Tradeoffs**

My conflict detection only checks for **exact start-time matches**
(`Scheduler.detect_conflicts()` compares `preferred_time` strings), not
overlapping durations. So a 30-minute 08:00 walk and an 08:15 feeding are *not*
flagged as conflicting even though they overlap in real time. This tradeoff is
reasonable here because the detector is meant as a lightweight *warning* to the
owner, not a hard constraint — the actual timeline is still built safely by
`resolve_conflicts()`, which pushes overlapping tasks to the next free slot so
nothing double-books. Exact-match detection is simple, fast, and easy to
explain; full interval-overlap checking would add complexity for a warning that
the plan builder already handles. If I had more time I would upgrade the
detector to compare `[start, start + duration)` intervals.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

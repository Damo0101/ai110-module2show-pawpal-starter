# PawPal+ Project Reflection

## 1. System Design

Before writing any code I jotted down the core things a pet owner should be able
to do: add or remove an owner/pet, set their daily constraints (like how much
time they have), and add or edit care tasks. That short list is basically what
drove the whole design.

**a. Initial design**

My initial UML (see `diagrams/uml_draft.mmd`) came down to four classes:

- **Owner** — the person using the app. Holds their `name`, `preferences`, a
  daily time budget (`available_minutes`), and a list of `pets`. It handles
  adding/removing pets and setting constraints.
- **Pet** — the animal being cared for. Holds `name`, `species`, `breed`, `age`,
  `notes`, and its own list of `tasks`, and manages those tasks (add, remove,
  edit, list).
- **Task** — a single care activity like a walk, feeding, or meds. Holds
  `title`, `duration_minutes`, `priority`, `category`, `frequency`,
  `preferred_time`, and a `completed` flag. It can score its own priority, tell
  whether it's due today, and mark itself complete.
- **Scheduler** — the "brain." Given the owner's constraints and the pets'
  tasks, it sorts, filters, and orders everything into a daily plan and explains
  the result.

The relationships are pretty intuitive: an Owner has one or more Pets, a Pet has
zero or more Tasks, and the Scheduler reads the Owner's constraints and the pets'
tasks to build a plan. I made Task and Pet dataclasses so the data-holding
classes stay clean and I don't have to hand-write a bunch of `__init__` code.

**b. Design changes**

Yes, the design definitely shifted once I started building. The biggest changes
were all in the Scheduler:

1. I had `available_minutes` on both the Owner *and* the Scheduler at first,
   which is two copies of the same fact. That's asking for bugs when one changes
   and the other doesn't, so I made the Scheduler take the Owner and read the
   budget straight from it.
2. My first Scheduler took a flat list of tasks, and I realised that once I
   pooled tasks from more than one pet I could no longer tell which pet a task
   belonged to. I changed it to keep `(pet, task)` pairs so the plan can label
   each item with its pet.
3. `build_plan()` and `explain_plan()` were doing the same sorting/filtering work
   twice. I had `build_plan()` cache its result so `explain_plan()` just reuses
   it instead of recomputing everything.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler weighs three things: the owner's available time
(`available_minutes`), each task's priority (high/medium/low), and each task's
preferred time. Priority is the one that matters most to me — tasks get sorted
highest-priority first, and then `filter_tasks()` greedily keeps as many as fit
the time budget. That way a busy owner always gets the important stuff done
(meds, feeding) before the nice-to-haves (an enrichment puzzle). Completion
status and frequency act as filters too, so anything already done or not due
today gets left out.

**b. Tradeoffs**

The main tradeoff I made is in conflict detection: `detect_conflicts()` only
looks for **exact start-time matches** (it compares `preferred_time` strings),
not overlapping durations. So a 30-minute walk at 08:00 and a feeding at 08:15
won't be flagged even though they actually overlap. I decided that was fine here
because the detector is only meant to be a lightweight *warning* to the owner,
not a hard rule — the real timeline is still built safely by
`resolve_conflicts()`, which pushes overlapping tasks to the next free slot so
nothing ends up double-booked. Exact-match checking is simple, fast, and easy to
explain, and full interval-overlap logic would add complexity for a warning the
plan builder already handles. If I had more time I'd upgrade the detector to
compare `[start, start + duration)` intervals.

---

## 3. AI Collaboration

**a. How you used AI**

I leaned on my AI coding assistant at pretty much every stage, but for different
things. Early on it was mostly brainstorming — I described the pet-care scenario
and had it help me turn my four classes into a Mermaid UML diagram. During the
build, agent/auto-edit mode was the biggest time-saver: I could describe a method
like "sort tasks by their HH:MM time" and it would draft it and update the files.
It was also great for the boilerplate I find tedious, like generating docstrings
and drafting the pytest cases. The prompts that worked best were the specific
ones — asking "how do I use a lambda as a sort key for HH:MM strings" got me a
clean answer, whereas vague asks like "make this better" gave me generic output.

**b. Judgment and verification**

I didn't just accept everything. One example: for conflict detection the
assistant offered a version using `collections.defaultdict` and a comprehension.
It was more "Pythonic," but I found the plain `dict.setdefault` loop easier to
read at a glance, and since the performance is identical I kept the readable
version. I verified suggestions by actually running them — `python main.py` for a
quick eyeball and `python -m pytest` for the logic — rather than trusting that
code looked right. That's how I caught the duplicated `available_minutes` and the
lost pet→task link.

---

## 4. Testing and Verification

**a. What you tested**

My suite in `tests/test_pawpal.py` covers the behaviors I care most about:
marking a task complete actually flips its status, adding a task grows a pet's
task list, `sort_by_time()` returns tasks in chronological order (with untimed
ones last), the pet/status filters return the right subset, `detect_conflicts()`
flags two tasks at the same time, and completing a daily task spawns a fresh
copy due the next day (while a "once" task does not). These matter because they
are exactly the pieces of logic that would quietly give an owner a wrong plan if
they broke — the sorting, the recurrence math, and the conflict warning.

**b. Confidence**

I'm fairly confident — all 7 tests pass and the CLI demo behaves the way I
expect. If I had more time I'd add edge cases like a pet with no tasks, a
zero-minute time budget, a task longer than the whole budget, and tasks that
overlap by duration rather than starting at the exact same minute (the gap I
called out in my tradeoff).

**Confidence Level: ⭐⭐⭐⭐☆ (4/5)**

---

## 5. Reflection

**a. What went well**

I'm most happy with the Scheduler. Getting it to sort by priority, respect the
time budget, place tasks in non-overlapping slots, *and* explain its own plan
felt like the moment the app went from "a list of tasks" to something actually
useful. Doing the CLI-first approach (building `main.py` before touching the UI)
also paid off — the logic was already solid by the time I wired up Streamlit.

**b. What you would improve**

I'd make the conflict detection duration-aware so it catches real overlaps, not
just identical start times. I'd also add editing/deleting tasks in the Streamlit
UI (the backend already supports it) and let the owner set per-task preferred
times more visually instead of typing "HH:MM".

**c. AI Strategy**

A few things stood out about working with the AI assistant. Agent mode and
auto-editing were the most effective features for me — being able to describe a
method and have it drafted and dropped into the right file kept my momentum.
Keeping separate chat sessions per phase (design vs. implementation vs. testing)
genuinely helped me stay organized; the testing chat wasn't cluttered with my
early UML debate, so its suggestions stayed on-topic. The clearest example of me
overriding the AI was choosing the readable `setdefault` conflict loop over its
"cleverer" comprehension. Overall the biggest lesson was about being the "lead
architect": the AI is fast and confident even when it's subtly wrong, so my job
was to hold the design in my head, ask pointed questions, and verify everything
by running it. The AI wrote a lot of the code, but the decisions — and the
responsibility for whether it actually works — stayed with me.

**d. Key takeaway**

The most important thing I learned is that a clear design up front makes AI
collaboration way more productive. Because I'd already decided on four classes
and how they relate, I could give the assistant precise, bounded tasks and easily
tell when its output didn't fit — instead of letting it invent an architecture I
didn't understand.

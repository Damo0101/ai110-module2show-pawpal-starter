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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

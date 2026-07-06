import streamlit as st

# Step 1: Establish the connection — bring the logic-layer classes into the UI.
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care around the time you have today.")

# Step 2: Manage the application "memory".
# Streamlit reruns this whole script on every interaction, so we keep ONE Owner
# instance in st.session_state (a per-session dictionary) instead of recreating
# it each run. The `if not in` check means the Owner is created once and then
# persists — pets and tasks added to it survive reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=90)

owner = st.session_state.owner
scheduler = Scheduler(owner)

# --- Owner + daily constraints -------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.set_available_time(
    st.number_input(
        "Time available today (minutes)",
        min_value=0,
        max_value=1440,
        value=owner.available_minutes,
        step=15,
    )
)

st.divider()

# --- Step 3: Add a pet ---------------------------------------------------------
# The form data is handled by Owner.add_pet(); submitting a form triggers a
# rerun, so the pet list and selectboxes below rebuild to show the new pet.
st.subheader("Add a pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)", value="")
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(pet_name.strip(), species, breed=breed.strip()))
            st.success(f"Added {pet_name}.")
        else:
            st.warning("Please enter a pet name.")

st.divider()

# --- Step 3: Add a task to a pet ----------------------------------------------
st.subheader("Add a task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    target_name = st.selectbox("For which pet?", [p.name for p in owner.pets])
    target_pet = next(p for p in owner.pets if p.name == target_name)

    with st.form("add_task_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input(
                "Duration (min)", min_value=1, max_value=240, value=20
            )
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

        col4, col5 = st.columns(2)
        with col4:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        with col5:
            preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")

        if st.form_submit_button("Add task"):
            # Pet.add_task handles the new task (mirrors Owner.add_pet for pets).
            target_pet.add_task(
                Task(
                    task_title,
                    int(duration),
                    priority=priority,
                    frequency=frequency,
                    preferred_time=preferred_time.strip() or None,
                )
            )
            st.success(f"Added '{task_title}' to {target_pet.name}.")

# --- Current tasks: conflicts, filters, sorted view ---------------------------
st.divider()
st.subheader("Today's tasks")

if not owner.all_tasks():
    st.info("No tasks yet — add some above.")
else:
    # Conflict warnings first, so a busy owner sees clashes immediately.
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(f"⚠️ {warning} — consider moving one to another time.")
    else:
        st.success("No scheduling conflicts detected.")

    pending = len(scheduler.filter_by_status(completed=False))
    done = len(scheduler.filter_by_status(completed=True))
    st.caption(f"{pending} pending · {done} completed")

    # Filter controls, powered by the Scheduler's filter/sort methods.
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_choice = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in owner.pets]
        )
    with fcol2:
        status_choice = st.radio(
            "Show", ["All", "Pending", "Completed"], horizontal=True
        )

    pairs = scheduler.sort_by_time()  # ordered by preferred_time, untimed last
    if pet_choice != "All pets":
        pairs = [(p, t) for p, t in pairs if p.name == pet_choice]
    if status_choice == "Pending":
        pairs = [(p, t) for p, t in pairs if not t.completed]
    elif status_choice == "Completed":
        pairs = [(p, t) for p, t in pairs if t.completed]

    if pairs:
        st.table(
            [
                {
                    "Time": task.preferred_time or "—",
                    "Task": task.title,
                    "Pet": pet.name,
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority,
                    "Frequency": task.frequency,
                    "Done": "✅" if task.completed else "",
                }
                for pet, task in pairs
            ]
        )
    else:
        st.info("No tasks match this filter.")

    # Mark tasks done — recurring tasks automatically roll over to the next date.
    st.markdown("**Mark a task done** — daily/weekly tasks roll over automatically:")
    for pet_idx, pet in enumerate(owner.pets):
        for task_idx, task in enumerate(pet.tasks):
            if not task.completed:
                if st.button(
                    f"✓ {task.title} — {pet.name}", key=f"done_{pet_idx}_{task_idx}"
                ):
                    upcoming = pet.complete_task(task)
                    if upcoming is not None:
                        st.success(
                            f"Completed '{task.title}'. Next {upcoming.frequency} "
                            f"occurrence added (due {upcoming.due_date})."
                        )
                    else:
                        st.success(f"Completed '{task.title}'.")
                    st.rerun()

# --- Build schedule ------------------------------------------------------------
st.divider()
st.subheader("Build schedule")
if st.button("Generate schedule", type="primary"):
    try:
        plan = scheduler.build_plan()
    except ValueError:
        st.error("A preferred time is not in HH:MM format. Please fix it and retry.")
    else:
        for warning in scheduler.detect_conflicts():
            st.warning(f"⚠️ {warning}")
        if not plan:
            st.info("Nothing to schedule — add some tasks or increase available time.")
        else:
            st.success(
                f"Scheduled {len(plan)} task(s) within "
                f"{owner.available_minutes} available minutes."
            )
            st.markdown("### Today's Schedule")
            st.table(
                [
                    {
                        "Time": item["time"],
                        "Task": item["title"],
                        "Pet": item["pet"],
                        "Duration (min)": item["duration_minutes"],
                        "Priority": item["priority"],
                    }
                    for item in plan
                ]
            )
            st.markdown("#### Why this plan?")
            st.text(scheduler.explain_plan())

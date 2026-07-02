from datetime import datetime

import streamlit as st

from pawpal_system import Owner, Pet, PriorityLevel, Recurrence, Scheduler, Task

# Map the UI's lowercase priority strings to the PriorityLevel enum.
PRIORITY_BY_LABEL = {level.value: level for level in PriorityLevel}
# Same for the recurrence dropdown.
RECURRENCE_BY_LABEL = {level.value: level for level in Recurrence}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# Persist the Owner across reruns. Create it once, then keep refreshing the
# name so edits to the input track without wiping the owner's pets/tasks.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
else:
    st.session_state.owner.name = owner_name
owner: Owner = st.session_state.owner

st.divider()

st.subheader("Add a Pet")
pcol1, pcol2 = st.columns(2)
with pcol1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pcol2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, type=species, age=0, care_needs=""))
    st.success(f"Added {pet_name} ({species}).")

if owner.pets:
    st.write("Current pets:", ", ".join(pet.name for pet in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Schedule a Task")
st.caption("Tasks are attached to a pet and feed into the scheduler below.")

if not owner.pets:
    st.info("Add a pet first, then you can schedule tasks for it.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", list(PRIORITY_BY_LABEL.keys()), index=2)
    with col4:
        task_time = st.time_input("Time")

    pcol, rcol = st.columns(2)
    with pcol:
        pet_choice = st.selectbox("For pet", [pet.name for pet in owner.pets])
    with rcol:
        repeat = st.selectbox("Repeat", list(RECURRENCE_BY_LABEL.keys()))

    if st.button("Add task"):
        pet = next(pet for pet in owner.pets if pet.name == pet_choice)
        scheduled = datetime.combine(datetime.now().date(), task_time)
        pet.add_task(
            Task(
                title=task_title,
                priority=PRIORITY_BY_LABEL[priority],
                scheduled_time=scheduled,
                duration=int(duration),
                recurrence=RECURRENCE_BY_LABEL[repeat],
            )
        )
        st.success(f"Added '{task_title}' for {pet_choice}.")

st.divider()

scheduler = Scheduler(owner)


def repeat_label(task: Task) -> str:
    """Human-friendly recurrence label for a table cell."""
    return "—" if task.recurrence is Recurrence.NONE else task.recurrence.value.title()


st.subheader("Today's Schedule")
st.caption("Built by the Scheduler — pending tasks ordered by time, then priority.")

# Let the Scheduler decide whether anything clashes and how to phrase it.
warning = scheduler.conflict_warning()
if warning:
    st.warning(f"⚠️ {warning}")

upcoming = scheduler.upcoming_with_pets()

if not upcoming:
    st.info("Nothing pending. Add some tasks above.")
else:
    st.success(f"{len(upcoming)} task(s) planned for {owner.name}.")

    # Read-only, professional-looking schedule via st.table (ordered by the
    # Scheduler's upcoming_tasks() logic: time first, then priority).
    st.table(
        [
            {
                "Time": task.scheduled_time.strftime("%H:%M"),
                "Priority": task.priority.value.title(),
                "Pet": pet.name,
                "Task": task.title,
                "Min": task.duration,
                "Repeat": repeat_label(task),
            }
            for pet, task in upcoming
        ]
    )

    # Completion controls live below the table, since st.table is read-only.
    st.markdown("**Mark a task done**")
    task_by_label = {
        f"{task.scheduled_time.strftime('%H:%M')} · {pet.name}: {task.title}": task
        for pet, task in upcoming
    }
    done_col, btn_col = st.columns([4, 1])
    with done_col:
        choice = st.selectbox("Completed task", list(task_by_label.keys()))
    with btn_col:
        st.write("")  # spacer to align the button with the selectbox
        mark_done = st.button("Done ✓")

    # complete_task drops this task from pending_tasks and, if it recurs, adds
    # its next occurrence — so the rerun rebuilds the schedule with the
    # completed task gone and any repeat already queued.
    if mark_done:
        follow_up = scheduler.complete_task(task_by_label[choice])
        if follow_up is not None:
            st.toast(
                f"Rescheduled '{follow_up.title}' for "
                f"{follow_up.scheduled_time.strftime('%a %H:%M')}."
            )
        st.rerun()

st.divider()

st.subheader("Browse & Filter Tasks")
st.caption("Every task across all pets, narrowed with the Scheduler's filter_tasks().")

if not owner.pets:
    st.info("Add a pet and some tasks to browse them here.")
else:
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_filter = st.selectbox("Pet", ["All pets"] + [pet.name for pet in owner.pets])
    with fcol2:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])

    # Translate the UI choices into filter_tasks() keyword arguments.
    completed_arg = {"All": None, "Pending": False, "Completed": True}[status_filter]
    pet_arg = None if pet_filter == "All pets" else pet_filter

    # Pair each filtered task with its pet, then order chronologically for display.
    pet_by_id = {task.id: pet for pet in owner.pets for task in pet.tasks}
    filtered = scheduler.filter_tasks(completed=completed_arg, pet_name=pet_arg)
    filtered.sort(key=lambda task: task.scheduled_time)

    if not filtered:
        st.info("No tasks match these filters.")
    else:
        st.table(
            [
                {
                    "Time": task.scheduled_time.strftime("%H:%M"),
                    "Priority": task.priority.value.title(),
                    "Pet": pet_by_id[task.id].name,
                    "Task": task.title,
                    "Min": task.duration,
                    "Repeat": repeat_label(task),
                    "Status": "✅ Done" if task.completed else "⏳ Pending",
                }
                for task in filtered
            ]
        )

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

st.subheader("Today's Schedule")
st.caption(
    "Built by the Scheduler — pending tasks ordered by time, then priority. "
    "Check off tasks as you finish them."
)

scheduler = Scheduler(owner)
upcoming = scheduler.upcoming_with_pets()

if not upcoming:
    st.info("Nothing pending. Add some tasks above.")
else:
    pet_by_id = {task.id: pet for pet, task in upcoming}

    # Flag double-booked time windows so the owner can resolve them.
    conflicts = scheduler.conflicts()
    if conflicts:
        st.warning("⚠️ Some tasks overlap in time:")
        for earlier, later in conflicts:
            ep, lp = pet_by_id[earlier.id], pet_by_id[later.id]
            st.write(
                f"- **{ep.name}: {earlier.title}** "
                f"({earlier.scheduled_time.strftime('%H:%M')}, {earlier.duration} min) "
                f"overlaps **{lp.name}: {later.title}** "
                f"({later.scheduled_time.strftime('%H:%M')})"
            )

    widths = [2, 2, 3, 4, 2, 2, 2]
    header = st.columns(widths)
    for col, label in zip(header, ["Time", "Priority", "Pet", "Task", "Min", "Repeat", "Done"]):
        col.markdown(f"**{label}**")

    for pet, task in upcoming:
        row = st.columns(widths)
        row[0].write(task.scheduled_time.strftime("%H:%M"))
        row[1].write(task.priority.value)
        row[2].write(pet.name)
        row[3].write(task.title)
        row[4].write(str(task.duration))
        row[5].write("—" if task.recurrence is Recurrence.NONE else task.recurrence.value)
        # complete_task drops this task from pending_tasks and, if it recurs,
        # adds its next occurrence — so the rerun rebuilds the schedule with
        # the completed task gone and any repeat already queued.
        if row[6].button("Done", key=f"done_{task.id}"):
            follow_up = scheduler.complete_task(task)
            if follow_up is not None:
                st.toast(
                    f"Rescheduled '{follow_up.title}' for "
                    f"{follow_up.scheduled_time.strftime('%a %H:%M')}."
                )
            st.rerun()

"""PawPal demo — build an owner with pets and tasks, print today's schedule."""

from __future__ import annotations

from datetime import datetime

from pawpal_system import Owner, Pet, PriorityLevel, Scheduler, Task


def build_demo() -> Scheduler:
    """Create a sample owner with two pets and a handful of tasks."""
    owner = Owner("Sam")

    rex = Pet(name="Rex", type="dog", age=3, care_needs="daily walks")
    mochi = Pet(name="Mochi", type="cat", age=2, care_needs="indoor")
    owner.add_pet(rex)
    owner.add_pet(mochi)

    # Schedule against the start of the real "today" so the demo reflects the
    # day it's actually run, not a frozen calendar date.
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # Deliberately added out of chronological order (evening, then morning,
    # then back to evening) so sort_by_time has something real to reorder.
    # Note the intentional clash: Rex's "Morning walk" and Mochi's "Feed" are
    # BOTH at 08:00 — two tasks at the same time, which the Scheduler should
    # flag as a conflict.
    task_specs = [
        (mochi, "Litter cleanup", PriorityLevel.MEDIUM, 20, 15),
        (rex,   "Morning walk",   PriorityLevel.HIGH,   8,  30),
        (rex,   "Dinner",         PriorityLevel.URGENT, 18, 10),
        (mochi, "Feed",           PriorityLevel.URGENT, 8,  10),
    ]
    for pet, title, priority, hour, duration in task_specs:
        pet.add_task(
            Task(
                title=title,
                priority=priority,
                scheduled_time=today.replace(hour=hour),
                duration=duration,
            )
        )

    return Scheduler(owner)


# Column width for the priority label — driven by the enum so it stays aligned
# even if a longer priority is added later.
_PRIORITY_WIDTH = max(len(level.value) for level in PriorityLevel)


def print_todays_schedule(scheduler: Scheduler) -> None:
    """Print today's schedule, ordered by time then priority."""
    print(f"Today's Schedule for {scheduler.owner.name}")
    print("=" * 40)

    upcoming = scheduler.upcoming_with_pets()
    if not upcoming:
        print("Nothing scheduled. Enjoy the day off!")
        return

    for pet, task in upcoming:
        when = task.scheduled_time.strftime("%H:%M")
        print(
            f"{when}  [{task.priority.value.upper():<{_PRIORITY_WIDTH}}]  "
            f"{pet.name}: {task.title} ({task.duration} min)"
        )

    warning = scheduler.conflict_warning()
    if warning:
        print()
        print(warning)


def _format_task(scheduler: Scheduler, task: Task) -> str:
    """One-line task summary: time, pet, title, and completion mark."""
    pet_by_id = {t.id: pet for pet in scheduler.pets for t in pet.tasks}
    pet = pet_by_id[task.id]
    when = task.scheduled_time.strftime("%H:%M")
    status = "done" if task.completed else "pending"
    return f"  {when}  {pet.name}: {task.title} ({status})"


def print_sorted_by_time(scheduler: Scheduler) -> None:
    """Show every task reordered chronologically by sort_by_time()."""
    print("All tasks sorted by time")
    print("=" * 40)
    for task in scheduler.sort_by_time():
        print(_format_task(scheduler, task))


def print_filtered(scheduler: Scheduler) -> None:
    """Show filter_tasks() narrowing by pet name and completion status."""
    print("Rex's tasks (filter by pet name)")
    print("=" * 40)
    for task in scheduler.filter_tasks(pet_name="Rex"):
        print(_format_task(scheduler, task))

    print()
    print("Completed tasks (filter by status)")
    print("=" * 40)
    completed = scheduler.filter_tasks(completed=True)
    if not completed:
        print("  (none yet)")
    for task in completed:
        print(_format_task(scheduler, task))


def main() -> None:
    scheduler = build_demo()
    print_todays_schedule(scheduler)

    # Mark a task complete so the completion filter has something to show.
    scheduler.filter_tasks(pet_name="Rex")[0].mark_complete()

    print()
    print_sorted_by_time(scheduler)
    print()
    print_filtered(scheduler)


if __name__ == "__main__":
    main()

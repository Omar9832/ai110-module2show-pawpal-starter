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

    today = datetime(2026, 6, 28)
    rex.add_task(Task("Morning walk", PriorityLevel.HIGH, today.replace(hour=8), 30))
    rex.add_task(Task("Dinner", PriorityLevel.URGENT, today.replace(hour=18), 10))
    mochi.add_task(Task("Feed", PriorityLevel.URGENT, today.replace(hour=8), 10))
    mochi.add_task(Task("Litter cleanup", PriorityLevel.MEDIUM, today.replace(hour=20), 15))

    return Scheduler(owner)


def print_todays_schedule(scheduler: Scheduler) -> None:
    """Print today's schedule, ordered by time then priority."""
    owner = scheduler.owner
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)

    # Map each task back to the pet it belongs to, for display.
    task_owner = {
        task.id: pet for pet in owner.pets for task in pet.tasks
    }

    upcoming = scheduler.upcoming_tasks()
    if not upcoming:
        print("Nothing scheduled. Enjoy the day off!")
        return

    for task in upcoming:
        pet = task_owner[task.id]
        when = task.scheduled_time.strftime("%H:%M")
        print(
            f"{when}  [{task.priority.value.upper():<6}]  "
            f"{pet.name}: {task.title} ({task.duration} min)"
        )


def main() -> None:
    scheduler = build_demo()
    print_todays_schedule(scheduler)


if __name__ == "__main__":
    main()

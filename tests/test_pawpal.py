"""Tests for PawPal core behavior."""

from __future__ import annotations

from datetime import datetime

from pawpal_system import (
    Owner,
    Pet,
    PriorityLevel,
    Recurrence,
    Scheduler,
    Task,
)


def make_task() -> Task:
    return Task(
        title="Walk",
        priority=PriorityLevel.HIGH,
        scheduled_time=datetime(2026, 6, 28, 9, 0),
        duration=30,
    )


def make_scheduler(*pets: Pet) -> Scheduler:
    """Build a Scheduler for an owner holding the given pets."""
    owner = Owner(name="Sam")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)


def test_mark_complete_changes_status() -> None:
    """Calling mark_complete() flips a task from incomplete to complete."""
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    """Adding a task to a pet increases that pet's task count by one."""
    pet = Pet(name="Rex", type="dog", age=3, care_needs="daily walks")
    assert len(pet.tasks) == 0

    pet.add_task(make_task())

    assert len(pet.tasks) == 1


def test_sort_by_time_returns_chronological_order() -> None:
    """sort_by_time() returns every task ordered soonest-first, regardless of
    the order they were added."""
    pet = Pet(name="Rex", type="dog", age=3, care_needs="daily walks")
    # Add deliberately out of chronological order: noon, then morning, then evening.
    noon = Task(
        title="Lunch",
        priority=PriorityLevel.MEDIUM,
        scheduled_time=datetime(2026, 6, 28, 12, 0),
        duration=15,
    )
    morning = Task(
        title="Walk",
        priority=PriorityLevel.HIGH,
        scheduled_time=datetime(2026, 6, 28, 8, 0),
        duration=30,
    )
    evening = Task(
        title="Dinner",
        priority=PriorityLevel.URGENT,
        scheduled_time=datetime(2026, 6, 28, 18, 0),
        duration=10,
    )
    for task in (noon, morning, evening):
        pet.add_task(task)
    scheduler = make_scheduler(pet)

    ordered = scheduler.sort_by_time()

    assert ordered == [morning, noon, evening]
    times = [task.scheduled_time for task in ordered]
    assert times == sorted(times)


def test_completing_daily_task_schedules_next_day() -> None:
    """Completing a daily task adds a fresh, uncompleted copy scheduled one day
    later to the same pet."""
    pet = Pet(name="Rex", type="dog", age=3, care_needs="daily walks")
    daily = Task(
        title="Walk",
        priority=PriorityLevel.HIGH,
        scheduled_time=datetime(2026, 6, 28, 9, 0),
        duration=30,
        recurrence=Recurrence.DAILY,
    )
    pet.add_task(daily)
    scheduler = make_scheduler(pet)

    follow_up = scheduler.complete_task(daily)

    # Original is marked done; a brand-new task takes its place.
    assert daily.completed is True
    assert follow_up is not None
    assert follow_up.completed is False
    assert follow_up.id != daily.id
    assert follow_up.scheduled_time == datetime(2026, 6, 29, 9, 0)
    assert follow_up.recurrence is Recurrence.DAILY
    # The follow-up landed on the same pet, alongside the completed original.
    assert follow_up in pet.tasks
    assert len(pet.tasks) == 2


def test_conflicts_flags_tasks_at_same_time() -> None:
    """The Scheduler flags two tasks scheduled at the identical time as a
    conflict, even across different pets."""
    rex = Pet(name="Rex", type="dog", age=3, care_needs="daily walks")
    mochi = Pet(name="Mochi", type="cat", age=2, care_needs="indoor")
    walk = Task(
        title="Morning walk",
        priority=PriorityLevel.HIGH,
        scheduled_time=datetime(2026, 6, 28, 8, 0),
        duration=30,
    )
    feed = Task(
        title="Feed",
        priority=PriorityLevel.URGENT,
        scheduled_time=datetime(2026, 6, 28, 8, 0),
        duration=10,
    )
    rex.add_task(walk)
    mochi.add_task(feed)
    scheduler = make_scheduler(rex, mochi)

    clashes = scheduler.conflicts()

    assert len(clashes) == 1
    pair = clashes[0]
    assert walk in pair and feed in pair
    # A human-readable warning is produced when there's a clash.
    assert scheduler.conflict_warning() != ""

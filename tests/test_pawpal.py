"""Tests for PawPal core behavior."""

from __future__ import annotations

from datetime import datetime

from pawpal_system import Pet, PriorityLevel, Task


def make_task() -> Task:
    return Task(
        title="Walk",
        priority=PriorityLevel.HIGH,
        scheduled_time=datetime(2026, 6, 28, 9, 0),
        duration=30,
    )


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

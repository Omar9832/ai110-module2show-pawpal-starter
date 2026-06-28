"""PawPal — pet task tracker.

Skeleton generated from diagrams/uml.mmd.
Fill in the method bodies to implement the system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class PriorityLevel(Enum):
    """Priority of a task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    """A scheduled care task for a pet (e.g. walking, feeding)."""

    title: str
    priority: PriorityLevel
    scheduled_time: datetime
    duration: int
    completed: bool = False
    # Stable unique id, generated per instance. Because it participates in the
    # dataclass __eq__, two field-identical tasks (same title/priority/time/
    # duration) are no longer "equal" — removing the duplicate-task ambiguity
    # when adding/removing tasks.
    id: UUID = field(default_factory=uuid4)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def notify_task(self) -> None:
        """Notify about this task at its scheduled time."""
        when = self.scheduled_time.strftime("%Y-%m-%d %H:%M")
        print(f"[{self.priority.value.upper()}] {self.title} due at {when}")


@dataclass
class Pet:
    """A pet profile and its tasks."""

    name: str
    type: str
    age: int
    care_needs: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task (e.g. walking, feeding) to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Delete / remove a task from this pet, matched by its unique id."""
        self.tasks = [t for t in self.tasks if t.id != task.id]


@dataclass
class Owner:
    """A pet owner who can add pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class Scheduler:
    """The "brain" of PawPal.

    Retrieves, organizes, and manages care tasks across all of an owner's
    pets — providing a single cross-pet view the UI and notifications use.
    """

    owner: Owner

    @property
    def pets(self) -> list[Pet]:
        """The pets this scheduler manages — read live from its owner."""
        return self.owner.pets

    def all_tasks(self) -> list[Task]:
        """Return every task across all pets, flattened into one list."""
        return [task for pet in self.pets for task in pet.tasks]

    def pending_tasks(self) -> list[Task]:
        """Return all not-yet-completed tasks across pets."""
        return [task for task in self.all_tasks() if not task.completed]

    def upcoming_tasks(self) -> list[Task]:
        """Return pending tasks ordered by when/how they should be done.

        Ordered by scheduled_time first (soonest first), then by priority
        (most urgent first) to break ties at the same time.
        """
        priority_rank = {
            PriorityLevel.URGENT: 0,
            PriorityLevel.HIGH: 1,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 3,
        }
        return sorted(
            self.pending_tasks(),
            key=lambda task: (task.scheduled_time, priority_rank[task.priority]),
        )

    def run_due_notifications(self, now: datetime) -> None:
        """Notify for any task whose scheduled time has arrived.

        Calls ``notify_task()`` on each pending task whose scheduled time is at
        or before ``now``.
        """
        for task in self.pending_tasks():
            if task.scheduled_time <= now:
                task.notify_task()

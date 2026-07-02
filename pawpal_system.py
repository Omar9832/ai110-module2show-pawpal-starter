"""PawPal — pet task tracker.

Skeleton generated from diagrams/uml.mmd.
Fill in the method bodies to implement the system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4


class PriorityLevel(Enum):
    """Priority of a task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Recurrence(Enum):
    """How often a task repeats."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    """A scheduled care task for a pet (e.g. walking, feeding)."""

    title: str
    priority: PriorityLevel
    scheduled_time: datetime
    duration: int
    completed: bool = False
    recurrence: Recurrence = Recurrence.NONE
    # Stable unique id, generated per instance. Because it participates in the
    # dataclass __eq__, two field-identical tasks (same title/priority/time/
    # duration) are no longer "equal" — removing the duplicate-task ambiguity
    # when adding/removing tasks.
    id: UUID = field(default_factory=uuid4)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a fresh, uncompleted task for this one's next repeat.

        Daily/weekly tasks return a new ``Task`` (new id, ``completed=False``)
        scheduled one day/week after this one, carrying the same recurrence so
        it keeps repeating. One-off tasks (``Recurrence.NONE``) return ``None``.
        """
        step = {
            Recurrence.DAILY: timedelta(days=1),
            Recurrence.WEEKLY: timedelta(weeks=1),
        }.get(self.recurrence)
        if step is None:
            return None
        return Task(
            title=self.title,
            priority=self.priority,
            scheduled_time=self.scheduled_time + step,
            duration=self.duration,
            recurrence=self.recurrence,
        )

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

    def complete_task(self, task: Task) -> Task | None:
        """Mark ``task`` complete and roll a recurring task to its next date.

        For a daily/weekly task, a fresh instance for the next occurrence is
        added to the same pet that owned ``task``. Returns that new instance,
        or ``None`` if the task was one-off (or not owned by any pet).
        """
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is None:
            return None
        for pet in self.pets:
            if any(t.id == task.id for t in pet.tasks):
                pet.add_task(follow_up)
                return follow_up
        return None

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted by their ``scheduled_time`` (soonest first)."""
        return sorted(self.all_tasks(), key=lambda task: task.scheduled_time)

    def filter_tasks(
        self,
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Both filters are optional and combine with AND:

        - ``completed``: keep only done (``True``) or not-yet-done (``False``)
          tasks. Leave as ``None`` to ignore completion status.
        - ``pet_name``: keep only tasks belonging to the pet with this name
          (case-insensitive). Leave as ``None`` to ignore pet.

        With no arguments, returns every task (same as ``all_tasks()``).
        """
        wanted_pet = pet_name.casefold() if pet_name is not None else None
        return [
            task
            for pet in self.pets
            for task in pet.tasks
            if (completed is None or task.completed == completed)
            and (wanted_pet is None or pet.name.casefold() == wanted_pet)
        ]

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
        # Fall back to a low rank for any unexpected priority so an odd value
        # sorts last instead of raising KeyError.
        return sorted(
            self.pending_tasks(),
            key=lambda task: (task.scheduled_time, priority_rank.get(task.priority, 99)),
        )

    def upcoming_with_pets(self) -> list[tuple[Pet, Task]]:
        """Upcoming tasks in scheduled order, each paired with its owning pet."""
        pet_by_task_id = {task.id: pet for pet in self.pets for task in pet.tasks}
        return [(pet_by_task_id[task.id], task) for task in self.upcoming_tasks()]

    def conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of pending tasks whose time windows overlap.

        Each task occupies ``[scheduled_time, scheduled_time + duration]``. Two
        tasks conflict when one starts before the other ends — the owner can't
        be in two places at once. Works on the time-sorted upcoming list, so
        every pair is returned in (earlier, later) order.
        """
        ordered = self.upcoming_tasks()
        found: list[tuple[Task, Task]] = []
        for i, earlier in enumerate(ordered):
            end = earlier.scheduled_time + timedelta(minutes=earlier.duration)
            for later in ordered[i + 1 :]:
                if later.scheduled_time < end:
                    found.append((earlier, later))
                else:
                    # Sorted by start time: nothing further can start before
                    # `end`, so stop scanning ahead for this task.
                    break
        return found

    def conflict_warning(self) -> str:
        """Return a human-readable warning about scheduling clashes.

        Lightweight and non-raising: returns an empty string when there are no
        conflicts (so callers can treat a truthy result as "show this"), and
        never lets an exception escape — any unexpected problem is folded into
        the returned text instead of crashing the program.
        """
        try:
            clashes = self.conflicts()
            if not clashes:
                return ""
            pet_by_id = {task.id: pet for pet in self.pets for task in pet.tasks}
            lines = [f"Heads up - {len(clashes)} scheduling conflict(s):"]
            for earlier, later in clashes:
                # Guard against a task that isn't on any pet, so a missing
                # owner degrades to "?" rather than raising KeyError.
                en = pet_by_id[earlier.id].name if earlier.id in pet_by_id else "?"
                ln = pet_by_id[later.id].name if later.id in pet_by_id else "?"
                lines.append(
                    f"  - {en}: {earlier.title} "
                    f"({earlier.scheduled_time:%H:%M}) overlaps "
                    f"{ln}: {later.title} ({later.scheduled_time:%H:%M})"
                )
            return "\n".join(lines)
        except Exception as exc:  # detection must never take down the caller
            return f"Could not check for scheduling conflicts: {exc}"

    def same_time_tasks(self) -> list[list[Task]]:
        """Group pending tasks that share an identical ``scheduled_time``.

        Returns one inner list per start time that has two or more pending
        tasks — whether they belong to the same pet or different pets — in
        chronological order. Start times with only one task are omitted, so a
        non-empty result means something is genuinely double-booked.

        This is the strict same-start-time case of :meth:`conflicts`, which
        flags any overlapping window (not just identical start times).
        """
        by_time: dict[datetime, list[Task]] = {}
        for task in self.upcoming_tasks():
            by_time.setdefault(task.scheduled_time, []).append(task)
        return [tasks for _, tasks in sorted(by_time.items()) if len(tasks) > 1]

    def run_due_notifications(self, now: datetime) -> None:
        """Notify for any task whose scheduled time has arrived.

        Calls ``notify_task()`` on each pending task whose scheduled time is at
        or before ``now``.
        """
        for task in self.pending_tasks():
            if task.scheduled_time <= now:
                task.notify_task()
